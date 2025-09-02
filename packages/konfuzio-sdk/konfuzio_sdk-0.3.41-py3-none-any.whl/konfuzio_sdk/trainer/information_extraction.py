"""Extract information from Documents.

Conventional template matching based approaches fail to generalize well to document images of unseen templates,
and are not robust against text recognition errors.

We follow the approach proposed by Sun et al. (2021) to encode both the visual and textual
features of detected text regions, and edges of which represent the spatial relations between neighboring text
regions. Their experiments validate that all information including visual features, textual
features and spatial relations can benefit key information extraction.

We reduce the hardware requirements from 1 NVIDIA Titan X GPUs with 12 GB memory to a 1 CPU and 16 GB memory by
replacing the end-to-end pipeline into two parts.

Sun, H., Kuang, Z., Yue, X., Lin, C., & Zhang, W. (2021). Spatial Dual-Modality Graph Reasoning for Key Information
Extraction. arXiv. https://doi.org/10.48550/ARXIV.2103.14470
"""

import collections
import difflib
import functools
import json
import logging
import os
import shutil
import tempfile
import time
import re
import unicodedata
from copy import deepcopy
from heapq import nsmallest
from inspect import signature
from typing import Dict, List, Optional, Tuple, Union

import bentoml
import numpy
import pandas
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted

from konfuzio_sdk.data import Annotation, AnnotationSet, Category, Document, Label, LabelSet, Span, AnnotationsContainer
from konfuzio_sdk.evaluate import ExtractionEvaluation
from konfuzio_sdk.normalize import (
    normalize_to_date,
    normalize_to_float,
    normalize_to_percentage,
    normalize_to_positive_float,
)
from konfuzio_sdk.regex import regex_matches
from konfuzio_sdk.tokenizer.base import ListTokenizer
from konfuzio_sdk.tokenizer.paragraph_and_sentence import ParagraphTokenizer, SentenceTokenizer
from konfuzio_sdk.trainer.base import BaseModel
from konfuzio_sdk.utils import get_bbox, get_latest_bento_schema, get_timestamp, memory_size_of, sdk_isinstance, slugify, add_count_in_document, flag_rows_below_max_in_page_bottom

logger = logging.getLogger(__name__)

"""Multiclass classifier for document extraction."""
CANDIDATES_CACHE_SIZE = 100


# Function to determine if a value can be formed from sums of higher y-values (WITHIN THE SAME marker_area)
def can_be_formed_with_higher_y_dp(
    group: pandas.DataFrame,
    max_subset_size_for_higher_others: int
) -> pandas.DataFrame:
    """
    Determine whether each value in the group can be formed from the sum of higher y0 values
    within the same marker_area.

    Parameters:
    - group: A group of rows (e.g., grouped by 'marker_area') to analyze.
    - max_subset_size_for_higher_others: Limits the number of values considered to form sums.

    Returns:
    - DataFrame with 'is_sum_of_higher_others' boolean column, indexed as original.
    """
    if isinstance(group, pandas.Series):  # Ensure group is a DataFrame
        raise TypeError("Expected DataFrame, got Series. Check groupby selection.")

    # ✅ Exclude rows where "is_below_vorjahr" is True
    valid_rows = group[~group["is_below_vorjahr"].fillna(False)].copy()

    group = group.sort_values("y0", ascending=False).reset_index()  # ✅ Keep original index for alignment
    valid_rows = valid_rows.sort_values("y0", ascending=False).reset_index()

    possible_sums = set()
    results = {}

    limited_numbers = []

    for idx, row in valid_rows.iterrows():
        value = round(row["normalized_to_float"], 2)  # ✅ Fix floating point precision issues
        current_y0 = row["y0"]

        # ✅ If value is 0.0, it should **ALWAYS** be False
        if value == 0.0:
            results[row["index"]] = False
            continue

        # ✅ Check if the value can be formed from sums of **only higher values within the same marker_area**
        is_sum = value in possible_sums
        results[row["index"]] = is_sum

        # ✅ Limit the number of tracked sums to prevent excessive calculations
        if len(limited_numbers) < max_subset_size_for_higher_others:
            limited_numbers.append(value)
            new_sums = {round(value + s, 2) for s in possible_sums} | {value}
            possible_sums.update(new_sums)

    # ✅ Apply results only to the rows that were considered
    group["is_sum_of_higher_others"] = group["index"].map(results).fillna(False)

    return group.set_index("index")[["is_sum_of_higher_others"]]  # ✅ Restore index for proper alignment


def convert_to_feat(offset_string_list: list, ident_str: str = '') -> pandas.DataFrame:
    """Return a df containing all the features generated using the offset_string."""
    df = {}  # pandas.DataFrame()

    # strip all accents
    offset_string_list_accented = offset_string_list
    offset_string_list = [strip_accents(s) for s in offset_string_list]

    # gets the return lists for all the features
    df[ident_str + 'feat_vowel_len'] = [vowel_count(s) for s in offset_string_list]
    df[ident_str + 'feat_special_len'] = [special_count(s) for s in offset_string_list]
    df[ident_str + 'feat_space_len'] = [space_count(s) for s in offset_string_list]
    df[ident_str + 'feat_digit_len'] = [digit_count(s) for s in offset_string_list]
    df[ident_str + 'feat_len'] = [len(s) for s in offset_string_list]
    df[ident_str + 'feat_upper_len'] = [upper_count(s) for s in offset_string_list]
    df[ident_str + 'feat_date_count'] = [date_count(s) for s in offset_string_list]
    df[ident_str + 'feat_num_count'] = [num_count(s) for s in offset_string_list]
    df[ident_str + 'feat_as_float'] = [normalize_to_python_float(offset_string) for offset_string in offset_string_list]
    df[ident_str + 'feat_unique_char_count'] = [unique_char_count(s) for s in offset_string_list]
    df[ident_str + 'feat_duplicate_count'] = [duplicate_count(s) for s in offset_string_list]
    df[ident_str + 'accented_char_count'] = [count_string_differences(s1, s2) for s1, s2 in zip(offset_string_list, offset_string_list_accented)]

    (
        df[ident_str + 'feat_year_count'],
        df[ident_str + 'feat_month_count'],
        df[ident_str + 'feat_day_count'],
    ) = year_month_day_count(offset_string_list)

    df[ident_str + 'feat_substring_count_slash'] = substring_count(offset_string_list, '/')
    df[ident_str + 'feat_substring_count_percent'] = substring_count(offset_string_list, '%')
    df[ident_str + 'feat_substring_count_e'] = substring_count(offset_string_list, 'e')
    df[ident_str + 'feat_substring_count_g'] = substring_count(offset_string_list, 'g')
    df[ident_str + 'feat_substring_count_a'] = substring_count(offset_string_list, 'a')
    df[ident_str + 'feat_substring_count_u'] = substring_count(offset_string_list, 'u')
    df[ident_str + 'feat_substring_count_i'] = substring_count(offset_string_list, 'i')
    df[ident_str + 'feat_substring_count_f'] = substring_count(offset_string_list, 'f')
    df[ident_str + 'feat_substring_count_s'] = substring_count(offset_string_list, 's')
    df[ident_str + 'feat_substring_count_oe'] = substring_count(offset_string_list, 'ö')
    df[ident_str + 'feat_substring_count_ae'] = substring_count(offset_string_list, 'ä')
    df[ident_str + 'feat_substring_count_ue'] = substring_count(offset_string_list, 'ü')
    df[ident_str + 'feat_substring_count_er'] = substring_count(offset_string_list, 'er')
    df[ident_str + 'feat_substring_count_str'] = substring_count(offset_string_list, 'str')
    df[ident_str + 'feat_substring_count_k'] = substring_count(offset_string_list, 'k')
    df[ident_str + 'feat_substring_count_r'] = substring_count(offset_string_list, 'r')
    df[ident_str + 'feat_substring_count_y'] = substring_count(offset_string_list, 'y')
    df[ident_str + 'feat_substring_count_en'] = substring_count(offset_string_list, 'en')
    df[ident_str + 'feat_substring_count_g'] = substring_count(offset_string_list, 'g')
    df[ident_str + 'feat_substring_count_ch'] = substring_count(offset_string_list, 'ch')
    df[ident_str + 'feat_substring_count_sch'] = substring_count(offset_string_list, 'sch')
    df[ident_str + 'feat_substring_count_c'] = substring_count(offset_string_list, 'c')
    df[ident_str + 'feat_substring_count_ei'] = substring_count(offset_string_list, 'ei')
    df[ident_str + 'feat_substring_count_on'] = substring_count(offset_string_list, 'on')
    df[ident_str + 'feat_substring_count_ohn'] = substring_count(offset_string_list, 'ohn')
    df[ident_str + 'feat_substring_count_n'] = substring_count(offset_string_list, 'n')
    df[ident_str + 'feat_substring_count_m'] = substring_count(offset_string_list, 'm')
    df[ident_str + 'feat_substring_count_j'] = substring_count(offset_string_list, 'j')
    df[ident_str + 'feat_substring_count_h'] = substring_count(offset_string_list, 'h')

    df[ident_str + 'feat_substring_count_plus'] = substring_count(offset_string_list, '+')
    df[ident_str + 'feat_substring_count_minus'] = substring_count(offset_string_list, '-')
    df[ident_str + 'feat_substring_count_period'] = substring_count(offset_string_list, '.')
    df[ident_str + 'feat_substring_count_comma'] = substring_count(offset_string_list, ',')

    df[ident_str + 'feat_starts_with_plus'] = starts_with_substring(offset_string_list, '+')
    df[ident_str + 'feat_starts_with_minus'] = starts_with_substring(offset_string_list, '-')

    df[ident_str + 'feat_ends_with_plus'] = ends_with_substring(offset_string_list, '+')
    df[ident_str + 'feat_ends_with_minus'] = ends_with_substring(offset_string_list, '-')

    df = pandas.DataFrame(df)

    return df


def substring_count(list_of_strings: list, substring: str) -> list:
    """Given a list of strings returns the occurrence of a certain substring and returns the results as a list."""
    r_list = [0] * len(list_of_strings)

    for index in range(len(list_of_strings)):
        r_list[index] = list_of_strings[index].lower().count(substring)

    return r_list


def starts_with_substring(list_of_strings: list, substring: str) -> list:
    """Given a list of strings return 1 if string starts with the given substring for each item."""
    return [1 if s.lower().startswith(substring) else 0 for s in list_of_strings]


def ends_with_substring(list_of_strings: list, substring: str) -> list:
    """Given a list of strings return 1 if string starts with the given substring for each item."""
    return [1 if s.lower().endswith(substring) else 0 for s in list_of_strings]


def digit_count(s: str) -> int:
    """Return the number of digits in a string."""
    return sum(c.isdigit() for c in s)


def space_count(s: str) -> int:
    """Return the number of spaces in a string."""
    return sum(c.isspace() for c in s) + s.count('\t') * 3  # Tab is already counted as one whitespace


def special_count(s: str) -> int:
    """Return the number of special (non-alphanumeric) characters in a string."""
    return sum(not c.isalnum() for c in s)


def strip_accents(s) -> str:
    """
    Strip all accents from a string.

    Source: http://stackoverflow.com/a/518232/2809427
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def vowel_count(s: str) -> int:
    """Return the number of vowels in a string."""
    return sum(is_vowel(c) for c in s)


def count_string_differences(s1: str, s2: str) -> int:
    """Return the number of differences between two strings."""
    if len(s2) > len(s1):  # the longer string has to be s1 to catch all differences
        s1, s2 = s2, s1

    return len(''.join(x[2:] for x in difflib.ndiff(s1, s2) if x.startswith('- ')))


def is_vowel(c: str) -> bool:
    """Given a char this function returns a bool that represents if the char is a vowel or not."""
    return c.lower() in 'aeiou'


def upper_count(s: str) -> int:
    """Return the number of uppercase characters in a string."""
    return sum(c.isupper() for c in s)


def date_count(s: str) -> int:
    """
    Given a string this function tries to read it as a date (if not possible returns 0).

    If possible it returns the relative difference to 01.01.2010 in days.
    """
    # checks the format
    if len(s) > 5:
        if (s[2] == '.' and s[5] == '.') or (s[2] == '/' and s[5] == '/'):
            date1 = pandas.to_datetime('01.01.2010', dayfirst=True)
            date2 = normalize_to_date(s)
            if not date2:
                return 0
            date2 = pandas.to_datetime(date2, errors='ignore')
            if date2 == s:
                return 0
            else:
                try:
                    diff = int((date2 - date1) / numpy.timedelta64(1, 'D'))
                except TypeError as e:
                    logger.debug(f'Could not substract for string {s} because of >>{e}<<.')
                    return 0

            if diff == 0:
                return 1
            else:
                return diff

        else:
            return 0
    return 0


def year_month_day_count(offset_string_list: list) -> Tuple[List[int], List[int], List[int]]:
    """Given a list of offset-strings extracts the according dates, months and years for each string."""
    year_list = []
    month_list = []
    day_list = []

    assert isinstance(offset_string_list, list)

    for s in offset_string_list:
        _normalization = normalize_to_date(s)
        if _normalization:
            year_list.append(int(_normalization[:4]))
            month_list.append(int(_normalization[5:7]))
            day_list.append(int(_normalization[8:10]))
        else:
            year_list.append(0)
            month_list.append(0)
            day_list.append(0)

    return year_list, month_list, day_list


# checks if the string is a number and gives the number a value
def num_count(s: str) -> float:
    """
    Given a string this function tries to read it as a number (if not possible returns 0).

    If possible it returns the number as a float.
    """
    num = normalize_to_float(s)

    if num:
        return num
    else:
        return 0


def normalize_to_python_float(s: str) -> float:
    """
    Given a string this function tries to read it as a number using python float (if not possible returns 0).

    If possible it returns the number as a float.
    """
    try:
        f = float(s)
        if f < numpy.finfo('float32').max:
            return f
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0


def duplicate_count(s: str) -> int:
    """Given a string this function returns the number of duplicate characters."""
    count = {}
    for c in s:
        if c in count:
            count[c] += 1
        else:
            count[c] = 1

    counter = 0
    for key in count:
        if count[key] > 1:
            counter += count[key]

    return counter


def unique_char_count(s: str) -> int:
    """Given a string returns the number of unique characters."""
    return len(set(s))


def get_first_candidate(document_text, document_bbox, line_list):
    """Get the first candidate in a document."""
    for line_num, _line in enumerate(line_list):
        line_start_offset = _line['start_offset']
        line_end_offset = _line['end_offset']
        # todo
        tokenize_fn = functools.partial(regex_matches, regex='[^ \n\t\f]+')
        for candidate in tokenize_fn(document_text[line_start_offset:line_end_offset]):
            candidate_start_offset = candidate['start_offset'] + line_start_offset
            candidate_end_offset = candidate['end_offset'] + line_start_offset
            candidate_bbox = dict(
                **get_bbox(document_bbox, candidate_start_offset, candidate_end_offset),
                offset_string=document_text[candidate_start_offset:candidate_end_offset],
                start_offset=candidate_start_offset,
                end_offset=candidate_end_offset,
            )
            return candidate_bbox


def get_line_candidates(document_text, document_bbox, line_list, line_num, candidates_cache):
    """Get the candidates from a given line_num."""
    if line_num in candidates_cache:
        return candidates_cache[line_num], candidates_cache
    line = line_list[line_num]
    line_start_offset = line['start_offset']
    line_end_offset = line['end_offset']
    line_candidates = []
    # todo see get_first_candidate
    tokenize_fn = functools.partial(regex_matches, regex='[^ \n\t\f]+')
    for candidate in tokenize_fn(document_text[line_start_offset:line_end_offset]):
        candidate_start_offset = candidate['start_offset'] + line_start_offset
        candidate_end_offset = candidate['end_offset'] + line_start_offset
        # todo: the next line is memory heavy
        #  https://gitlab.com/konfuzio/objectives/-/issues/9342
        candidate_bbox = dict(
            **get_bbox(document_bbox, candidate_start_offset, candidate_end_offset),
            offset_string=document_text[candidate_start_offset:candidate_end_offset],
            start_offset=candidate_start_offset,
            end_offset=candidate_end_offset,
        )
        line_candidates.append(candidate_bbox)
    if len(candidates_cache) >= CANDIDATES_CACHE_SIZE:
        earliest_line = min(candidates_cache.keys())
        candidates_cache.pop(earliest_line)
    candidates_cache[line_num] = line_candidates
    return line_candidates, candidates_cache


def process_document_data(
    document: Document,
    spans: List[Span],
    n_nearest: Union[int, List, Tuple] = 2,
    first_word: bool = True,
    n_nearest_across_lines: bool = False,
    area_keywords: Optional[Dict] = None,
    marker_keywords: Optional[Dict] = None,
    column_keywords: Optional[Dict] = None,
    max_subset_size_for_higher_others: int = 24,
    advanced_number_features: bool = False
) -> Tuple[pandas.DataFrame, List, pandas.DataFrame]:
    """
    Convert the json_data from one Document to a DataFrame that can be used for training or prediction.

    args: max_subset_size_for_higher_others ✅ Set a maximum number of values to consider for subset sums

    Additionally, returns the fake negatives, errors and conflicting annotations as a DataFrames and of course the
    column_order for training
    """
    logger.info(f'Start generating features for document {document}.')

    area_keywords = {} if area_keywords is None else area_keywords
    marker_keywords = {} if marker_keywords is None else marker_keywords
    closest_marker_keywords = {} if marker_keywords is None else marker_keywords
    column_keywords = {} if column_keywords is None else column_keywords

    if area_keywords:
        area_spans: List[Dict] = document.find_keyword_spans_per_document(area_keywords)
        areas = document.define_areas(area_spans)
        marker_spans: Dict[int, Dict[str, Optional[Span]]] = document.find_keyword_spans_for_per_page(marker_keywords, return_all=False)
        all_marker_spans: Dict[int, Dict[str, Optional[Span]]] = document.find_keyword_spans_for_per_page(closest_marker_keywords, return_all=True)

    marker_features = []
    closest_marker_features = []
    if marker_keywords:
        closest_marker_features = []
        for key, _ in marker_keywords.items():
            marker_features += [f'marker_{key}_x_distance', f'marker_{key}_y_distance', f'marker_{key}_line_distance',
                                f'marker_{key}_is_same_or_below']
        for key, _ in closest_marker_keywords.items():
            closest_marker_features += [f'closest_marker_{key}_x_distance', f'closest_marker_{key}_y_distance',
                                        f'closest_marker_{key}_line_distance']
    column_keywords_features = []
    if column_keywords:
        for key, _ in column_keywords.items():
            column_keywords_features += [f'is_below_{key.lower()}']
        column_reference_words_spans: Dict[int, Dict[str, List[Span]]] = document.find_keyword_spans_for_per_page(column_keywords, return_all=True)

    assert spans == sorted(spans)  # should be already sorted

    file_error_data = []
    file_data_raw = []

    if isinstance(n_nearest, int):
        n_left_nearest = n_nearest
        n_right_nearest = n_nearest
    else:
        assert isinstance(n_nearest, (tuple, list)) and len(n_nearest) == 2
        n_left_nearest, n_right_nearest = n_nearest

    l_keys = ['l_dist' + str(x) for x in range(n_left_nearest)]
    r_keys = ['r_dist' + str(x) for x in range(n_right_nearest)]

    if n_nearest_across_lines:
        l_keys += ['l_pos' + str(x) for x in range(n_left_nearest)]
        r_keys += ['r_pos' + str(x) for x in range(n_right_nearest)]

    document_bbox = document.get_bbox()
    document_text = document.text
    document_n_pages = document.number_of_pages

    if document_text is None or document_bbox == {} or len(spans) == 0:
        # if the document text is empty or if there are no ocr'd characters
        # then return an empty dataframe for the data, an empty feature list and an empty dataframe for the "error" data
        raise NotImplementedError

    line_list: List[Dict] = []
    char_counter = 0
    for line_text in document_text.replace('\f', '\n').split('\n'):
        n_chars_on_line = len(line_text)
        line_list.append({'start_offset': char_counter, 'end_offset': char_counter + n_chars_on_line})
        char_counter += n_chars_on_line + 1

    if first_word:
        first_candidate = get_first_candidate(document_text, document_bbox, line_list)
        first_word_string = first_candidate['offset_string']
        first_word_x0 = first_candidate['x0']
        first_word_y0 = first_candidate['y0']
        first_word_x1 = first_candidate['x1']
        first_word_y1 = first_candidate['y1']
    else:
        first_word_string = None
        first_word_x0 = None
        first_word_y0 = None
        first_word_x1 = None
        first_word_y1 = None

    candidates_cache = {}
    for span in spans:
        line_num = span.line_index
        line_candidates, candidates_cache = get_line_candidates(document_text, document_bbox, line_list, line_num, candidates_cache)

        l_list = []
        r_list = []

        # todo add way to calculate distance features between spans consistently
        # https://gitlab.com/konfuzio/objectives/-/issues/9688
        for candidate in line_candidates:
            try:
                span.bbox()
                if candidate['end_offset'] <= span.start_offset:
                    candidate['dist'] = span.bbox().x0 - candidate['x1']
                    candidate['pos'] = 0
                    l_list.append(candidate)
                elif candidate['start_offset'] >= span.end_offset:
                    candidate['dist'] = candidate['x0'] - span.bbox().x1
                    candidate['pos'] = 0
                    r_list.append(candidate)
            except ValueError as e:
                logger.error(f'{candidate}: {str(e)}')

        if n_nearest_across_lines:
            prev_line_candidates = []
            i = 1
            while (line_num - i) >= 0:
                line_candidates, candidates_cache = get_line_candidates(
                    document_text,
                    document_bbox,
                    line_list,
                    line_num - i,
                    candidates_cache,
                )
                for candidate in line_candidates:
                    candidate['dist'] = min(
                        abs(span.bbox().x0 - candidate['x0']),
                        abs(span.bbox().x0 - candidate['x1']),
                        abs(span.bbox().x1 - candidate['x0']),
                        abs(span.bbox().x1 - candidate['x1']),
                    )
                    candidate['pos'] = -i
                prev_line_candidates.extend(line_candidates)
                if len(prev_line_candidates) >= n_left_nearest - len(l_list):
                    break
                i += 1

            next_line_candidates = []
            i = 1
            while line_num + i < len(line_list):
                line_candidates, candidates_cache = get_line_candidates(
                    document_text,
                    document_bbox,
                    line_list,
                    line_num + i,
                    candidates_cache,
                )
                for candidate in line_candidates:
                    candidate['dist'] = min(
                        abs(span.bbox().x0 - candidate['x0']),
                        abs(span.bbox().x0 - candidate['x1']),
                        abs(span.bbox().x1 - candidate['x0']),
                        abs(span.bbox().x1 - candidate['x1']),
                    )
                    candidate['pos'] = i
                next_line_candidates.extend(line_candidates)
                if len(next_line_candidates) >= n_right_nearest - len(r_list):
                    break
                i += 1

        n_smallest_l_list = nsmallest(n_left_nearest, l_list, key=lambda x: x['dist'])
        n_smallest_r_list = nsmallest(n_right_nearest, r_list, key=lambda x: x['dist'])

        if n_nearest_across_lines:
            n_smallest_l_list.extend(prev_line_candidates[::-1])
            n_smallest_r_list.extend(next_line_candidates)

        while len(n_smallest_l_list) < n_left_nearest:
            n_smallest_l_list.append({'offset_string': '', 'dist': 100000, 'pos': 0})

        while len(n_smallest_r_list) < n_right_nearest:
            n_smallest_r_list.append({'offset_string': '', 'dist': 100000, 'pos': 0})

        r_list = n_smallest_r_list[:n_right_nearest]
        l_list = n_smallest_l_list[:n_left_nearest]

        # set first word features
        if first_word:
            span.first_word_x0 = first_word_x0
            span.first_word_y0 = first_word_y0
            span.first_word_x1 = first_word_x1
            span.first_word_y1 = first_word_y1
            span.first_word_string = first_word_string

        span_dict = span.eval_dict()
        if area_keywords:
            span_dict['marker_area'] = document.query_area(areas, span)
        if marker_keywords:
            span_dict = span.get_closest_marker_feature_for_span(closest_marker_keywords, span_dict, all_marker_spans)
            span_dict = span.get_marker_feature_for_span(marker_keywords, span_dict, marker_spans)
        if column_keywords:
            span_dict = document.check_if_below_and_overlapping_references(span, span_dict, column_reference_words_spans[span.page.index])

        for index, item in enumerate(l_list):
            span_dict['l_dist' + str(index)] = item['dist']
            span_dict['l_offset_string' + str(index)] = item['offset_string']
            if n_nearest_across_lines:
                span_dict['l_pos' + str(index)] = item['pos']
        for index, item in enumerate(r_list):
            span_dict['r_dist' + str(index)] = item['dist']
            span_dict['r_offset_string' + str(index)] = item['offset_string']
            if n_nearest_across_lines:
                span_dict['r_pos' + str(index)] = item['pos']

        # checks for ERRORS
        if span_dict['confidence'] is None and not (span_dict['revised'] is False and span_dict['is_correct'] is True):
            file_error_data.append(span_dict)

        # adds the sample_data to the list
        if span_dict['page_index'] is not None:
            file_data_raw.append(span_dict)

    # creates the dataframe
    df = pandas.DataFrame(file_data_raw)
    df_errors = pandas.DataFrame(file_error_data)

    # first word features
    if first_word:
        df['first_word_x0'] = first_word_x0
        df['first_word_x1'] = first_word_x1
        df['first_word_y0'] = first_word_y0
        df['first_word_y1'] = first_word_y1
        df['first_word_string'] = first_word_string

        # first word string features
        df_string_features_first = convert_to_feat(list(df['first_word_string']), 'first_word_')
        string_features_first_word = df_string_features_first.columns.to_list()
        df = df.join(df_string_features_first, lsuffix='_caller', rsuffix='_other')
        first_word_features = ['first_word_x0', 'first_word_y0', 'first_word_x1', 'first_word_y1']
        first_word_features += string_features_first_word
    else:
        first_word_features = []

    # creates all the features from the offset string
    df_string_features_real = convert_to_feat(list(df['offset_string']))
    string_feature_column_order = df_string_features_real.columns.to_list()

    # joins it to the main DataFrame
    df = df.join(df_string_features_real, lsuffix='_caller', rsuffix='_other')
    relative_string_feature_list = []

    for index in range(n_left_nearest):
        df_string_features_l = convert_to_feat(list(df['l_offset_string' + str(index)]), 'l' + str(index) + '_')
        relative_string_feature_list += df_string_features_l.columns.to_list()
        df = df.join(df_string_features_l, lsuffix='_caller', rsuffix='_other')

    for index in range(n_right_nearest):
        df_string_features_r = convert_to_feat(list(df['r_offset_string' + str(index)]), 'r' + str(index) + '_')
        relative_string_feature_list += df_string_features_r.columns.to_list()
        df = df.join(df_string_features_r, lsuffix='_caller', rsuffix='_other')

    # De-fragment Dataframe
    df = df.copy()

    df['relative_position_in_page'] = df['page_index'] / document_n_pages

    abs_pos_feature_list = ['x0', 'y0', 'x1', 'y1', 'page_index', 'area_quadrant_two', 'area']
    relative_pos_feature_list = [
        'x0_relative',
        'x1_relative',
        'y0_relative',
        'y1_relative',
        'relative_position_in_page',
    ]

    feature_list = string_feature_column_order + abs_pos_feature_list + l_keys + r_keys + relative_string_feature_list + relative_pos_feature_list
    if first_word:
        feature_list += first_word_features

    if advanced_number_features:
        # Add 'normalized_to_float', and 'count_in_document' columns to the DataFrame.
        df = add_count_in_document(df)
        feature_list += ['normalized_to_float', 'count_in_document']

        # Flag rows that are visually below the highest float value in the bottom half of each page
        df = df.groupby("page_index", group_keys=False).apply(flag_rows_below_max_in_page_bottom)
        feature_list += ['below_highest_float_value']

    # ✅ Compute values **WITHOUT modifying df structure**
    if area_keywords:
        is_sum_values = (
            df[df["marker_area"].notna()]
            .groupby("marker_area", group_keys=False)
            .apply(can_be_formed_with_higher_y_dp,
                   max_subset_size_for_higher_others=max_subset_size_for_higher_others)
        )
        df["is_sum_of_higher_others"] = False  # Default to False

        # try:
        # ✅ Ensure correct boolean type
        is_sum_values["is_sum_of_higher_others"] = is_sum_values["is_sum_of_higher_others"].astype(bool)

        # ✅ Assign **ONLY** to `df["is_sum_of_higher_others"]` using `.loc[]`
        df.loc[is_sum_values.index, "is_sum_of_higher_others"] = is_sum_values["is_sum_of_higher_others"]
        # except:
        #    pass

        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        df['marker_area_encoded'] = encoder.fit_transform(df['marker_area'])
        feature_list += ['marker_area_encoded', 'is_sum_of_higher_others']

    feature_list += marker_features + closest_marker_features + column_keywords_features
    return df, feature_list, df_errors


def substring_on_page(substring, annotation, page_text_list) -> bool:
    """Check if there is an occurrence of the word on the according page."""
    if not hasattr(annotation, 'page_index'):
        logger.warning('Annotation has no page_index!')
        return False
    elif annotation.page_index > len(page_text_list) - 1:
        logger.warning("Annotation's page_index does not match given text.")
        return False
    else:
        return substring in page_text_list[annotation.page_index]


class AbstractExtractionAI(BaseModel):
    """Parent class for all Extraction AIs, to extract information from unstructured human-readable text."""

    requires_text = True
    requires_images = False

    def __init__(self, category: Category, *args, **kwargs):
        """Initialize ExtractionModel."""
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        super().__init__()
        self.category = category
        self.clf = None
        self.label_feature_list = None  # will be set later

        self.df_train = None

        self.evaluation = None

    def build_bento(self, bento_model):
        """Build BentoML service for the model."""
        bento_base_dir = os.path.dirname(os.path.abspath(__file__)) + '/../bento'
        dict_metadata = self.project.create_project_metadata_dict()

        with tempfile.TemporaryDirectory() as temp_dir:
            # copy bento_module_dir to temp_dir
            shutil.copytree(bento_base_dir + '/extraction', temp_dir + '/extraction')
            shutil.copytree(bento_base_dir + '/base', temp_dir + '/base')
            # copy __init__.py file
            shutil.copy(bento_base_dir + '/__init__.py', temp_dir + '__init__.py')
            # include metadata
            with open(f'{temp_dir}/categories_and_label_data.json5', 'w') as f:
                json.dump(dict_metadata, f, indent=2, sort_keys=True)
            # include the AI model name so the service can load it correctly
            with open(f'{temp_dir}/AI_MODEL_NAME', 'w') as f:
                f.write(self._pkl_name)

            built_bento = bentoml.bentos.build(
                name=f"extraction_{self.category.id_ if self.category else '0'}",
                service=f'extraction.{self.name_lower()}_service:ExtractionService',
                include=[
                    '__init__.py',
                    'base/*.py',
                    'extraction/*.py',
                    'categories_and_label_data.json5',
                    'AI_MODEL_NAME',
                ],
                labels=self.bento_metadata,
                python={
                    'packages': [f'konfuzio-sdk<={self.konfuzio_sdk_version}'],
                    'lock_packages': True,
                },
                build_ctx=temp_dir,
                models=[str(bento_model.tag)],
            )

        return built_bento

    @property
    def project(self):
        """Get RFExtractionAI Project."""
        if not self.category:
            raise AttributeError(f'{self} has no Category.')
        return self.category.project

    @property
    def entrypoint_methods(self) -> dict:
        """Methods that will be exposed in a bento-saved instance of a model."""
        return {
            'extract': {'batchable': False},
            'evaluate': {'batchable': False},
        }

    @property
    def bento_metadata(self) -> dict:
        """Metadata to include into the bento-saved instance of a model."""
        return {
            'requires_images': getattr(self, 'requires_images', False),
            'requires_segmentation': getattr(self, 'requires_segmentation', False),
            'requires_text': getattr(self, 'requires_text', False),
            'requires_raw_ocr': getattr(self, 'requires_raw_ocr', False),
            'request': get_latest_bento_schema(base_schema_name='ExtractRequest', module_path='konfuzio_sdk.bento.extraction.schemas'),
            'response': get_latest_bento_schema(base_schema_name='ExtractResponse', module_path='konfuzio_sdk.bento.extraction.schemas'),
        }

    def check_is_ready(self):
        """
        Check if the ExtractionAI is ready for the inference.

        It is assumed that the model is ready if a Category is set, and is ready for extraction.

        :raises AttributeError: When no Category is specified.
        """
        logger.info(f'Checking if {self} is ready for extraction.')
        if not self.category:
            raise AttributeError(f'{self} requires a Category.')

    def fit(self):
        """Use as placeholder Function because the Abstract AI does not train a classifier."""
        logger.warning(f'{self} does not train a classifier.')
        pass

    def evaluate(self):
        """Use as placeholder Function."""
        logger.warning(f'{self} does not evaluate results.')
        pass

    def extract(self, document: Document) -> Document:
        """Perform preliminary extraction steps."""
        logger.info(f'Starting extraction of {document}.')

        self.check_is_ready()  # check if the model is ready for extraction

        document = deepcopy(document)  # to get a Virtual Document with no Annotations

        # So that the Document belongs to the Category that is saved with the ExtractionAI
        document._category = self.project.no_category
        document.set_category(self.category)

        return document

    def extraction_result_to_document(self, document: Document, extraction_result: dict) -> Document:
        """Return a virtual Document annotated with AI Model output."""
        virtual_doc = deepcopy(document)
        virtual_annotation_set_id = 1  # counter for across mult. Annotation Set groups of a Label Set

        # define Annotation Set for the Category Label Set: todo: this is unclear from API side
        # default Annotation Set will be always added even if there are no predictions for it
        category_label_set = self.category.project.get_label_set_by_id(self.category.id_)
        virtual_default_annotation_set = AnnotationSet(document=virtual_doc, label_set=category_label_set, id_=virtual_annotation_set_id)
        virtual_annotation_set_id += 1
        for label_or_label_set_name, information in extraction_result.items():
            if isinstance(information, pandas.DataFrame):
                if information.empty:
                    continue

                # annotations belong to the default Annotation Set
                label = self.category.project.get_label_by_name(label_or_label_set_name)
                self.add_extractions_as_annotations(
                    document=virtual_doc,
                    extractions=information,
                    label=label,
                    label_set=category_label_set,
                    annotation_set=virtual_default_annotation_set,
                )
            # process multi Annotation Sets that are not part of the category Label Set
            else:
                label_set = self.category.project.get_label_set_by_name(label_or_label_set_name)

                if not isinstance(information, list):
                    information = [information]

                for entry in information:  # represents one of pot. multiple annotation-sets belonging of one LabelSet
                    if label_set is not category_label_set:
                        virtual_annotation_set = AnnotationSet(document=virtual_doc, label_set=label_set, id_=virtual_annotation_set_id)
                        virtual_annotation_set_id += 1
                    else:
                        virtual_annotation_set = virtual_default_annotation_set

                    for label_name, extractions in entry.items():
                        label = self.category.project.get_label_by_name(label_name)
                        self.add_extractions_as_annotations(
                            document=virtual_doc,
                            extractions=extractions,
                            label=label,
                            label_set=label_set,
                            annotation_set=virtual_annotation_set,
                        )

        return virtual_doc

    @staticmethod
    def add_extractions_as_annotations(
        extractions: pandas.DataFrame,
        document: Document,
        label: Label,
        label_set: LabelSet,
        annotation_set: AnnotationSet,
    ) -> None:
        """Add the extraction of a model to the document."""
        if not isinstance(extractions, pandas.DataFrame):
            raise TypeError(f'Provided extraction object should be a Dataframe, got a {type(extractions)} instead')
        if not extractions.empty:
            # TODO: define required fields
            required_fields = ['start_offset', 'end_offset', 'confidence']
            if not set(required_fields).issubset(extractions.columns):
                raise ValueError(
                    f'Extraction do not contain all required fields: {required_fields}.' f' Extraction columns: {extractions.columns.to_list()}'
                )

            extracted_spans = extractions[required_fields].sort_values(by='confidence', ascending=False)

            for span in extracted_spans.to_dict('records'):
                try:
                    annotation = Annotation(
                        document=document,
                        label=label,
                        confidence=span['confidence'],
                        label_set=label_set,
                        annotation_set=annotation_set,
                        spans=[Span(start_offset=span['start_offset'], end_offset=span['end_offset'])],
                    )
                    if annotation.spans[0].offset_string is None:
                        raise NotImplementedError(f'Extracted {annotation} does not have a correspondence in the ' f'text of {document}.')
                except ValueError as e:
                    if 'is a duplicate of' in str(e):
                        # Second duplicate Span is lower confidence since we sorted spans earlier, so we can ignore it
                        logger.warning(f'Could not add duplicated {span}: {str(e)}')
                    else:
                        raise e

    def merge_horizontal(self, res_dict: Dict, doc_text: str, exclude_data_types_from_horizontal_merge = None) -> Dict:
        """Merge contiguous spans with same predicted label.

        See more details at https://dev.konfuzio.com/sdk/explanations.html#horizontal-merge
        """
        logger.info('Horizontal merge.')
        merged_res_dict = {}  # stores final results

        if exclude_data_types_from_horizontal_merge is None:
            exclude_data_types_from_horizontal_merge = []
        for label, items in res_dict.items():
            res_dicts = []
            buffer = []
            end = None

            for _, row in items.iterrows():  # iterate over the rows in the DataFrame
                # Skip merging for numbers: directly flush any current buffer and add this row as-is
                if self.category and self.category.project:
                    try:
                        data_type = self.category.project.get_label_by_name(label.split('__')[-1]).data_type
                    except (AttributeError, ValueError, IndexError) as e:
                        logger.warning(f"Could not determine data_type for label '{label}': {e}. Proceeding with horizontal merge.")
                        data_type = None

                    if data_type and data_type in exclude_data_types_from_horizontal_merge:
                        if buffer:
                            res_dict = self.flush_buffer(buffer, doc_text)
                            res_dicts.append(res_dict)
                            buffer = []
                        res_dicts.append({
                            "label_name": row["label_name"],
                            "start_offset": row["start_offset"],
                            "end_offset": row["end_offset"],
                            "data_type": row["data_type"],
                            "confidence": row["confidence"],
                            "value": doc_text[row["start_offset"]:row["end_offset"]],
                        })
                        logger.info(f"Skip horizontal merge for data type {row['data_type']} for {row}")
                        continue

                # if they are valid merges then add to buffer
                if end and self.is_valid_horizontal_merge(row, buffer, doc_text):
                    buffer.append(row)
                    end = row['end_offset']
                else:  # else, flush the buffer by creating a res_dict
                    if buffer:
                        res_dict = self.flush_buffer(buffer, doc_text)
                        res_dicts.append(res_dict)
                    buffer = []
                    buffer.append(row)
                    end = row['end_offset']
            if buffer:  # flush buffer at the very end to clear anything left over
                res_dict = self.flush_buffer(buffer, doc_text)
                res_dicts.append(res_dict)
            merged_df = pandas.DataFrame(res_dicts)  # convert the list of res_dicts created by `flush_buffer` into a DataFrame

            merged_res_dict[label] = merged_df

        return merged_res_dict

    @staticmethod
    def flush_buffer(buffer: List[pandas.Series], doc_text: str) -> Dict:
        """
        Merge a buffer of entities into a dictionary (which will eventually be turned into a DataFrame).

        A buffer is a list of pandas.Series objects.
        """
        assert 'label_name' in buffer[0]
        label = buffer[0]['label_name']

        starts = buffer[0]['start_offset']
        ends = buffer[-1]['end_offset']
        text = doc_text[starts:ends]

        res_dict = {}
        res_dict['start_offset'] = starts
        res_dict['end_offset'] = ends
        res_dict['label_name'] = label
        res_dict['offset_string'] = text
        res_dict['confidence'] = numpy.mean([b['confidence'] for b in buffer])
        return res_dict

    @staticmethod
    def is_valid_horizontal_merge(
        row: pandas.Series,
        buffer: List[pandas.Series],
        doc_text: str,
        max_offset_distance: int = 5,
    ) -> bool:
        """
        Verify if the merging that we are trying to do is valid.

        A merging is valid only if:
          * All spans have the same predicted Label
          * Confidence of predicted Label is above the Label threshold
          * All spans are on the same line
          * No extraneous characters in between spans
          * A maximum of 5 spaces in between spans
          * The Label type is not one of the following: 'Number', 'Positive Number', 'Percentage', 'Date'
            OR the resulting merging create a span normalizable to the same type

        :param row: Row candidate to be merged to what is already in the buffer.
        :param buffer: Previous information.
        :param doc_text: Text of the document.
        :param max_offset_distance: Maximum distance between two entities that can be merged.
        :return: If the merge is valid or not.
        """
        if row['confidence'] < row['label_threshold']:
            return False

        # sanity checks
        if buffer[-1]['label_name'] != row['label_name']:
            return False
        elif buffer[-1]['confidence'] < buffer[-1]['label_threshold']:
            return False

        # Do not merge if any character in between the two Spans
        if not all(c == ' ' for c in doc_text[buffer[-1]['end_offset'] : row['start_offset']]):
            return False

        # Do not merge if the difference in the offsets is bigger than the maximum offset distance
        if row['start_offset'] - buffer[-1]['end_offset'] > max_offset_distance:
            return False

        # only merge if text is on same line
        if '\n' in doc_text[buffer[0]['start_offset'] : row['end_offset']]:
            return False

        # Do not merge overlapping spans
        if row['start_offset'] < buffer[-1]['end_offset']:
            return False

        data_type = row['data_type']
        # always merge if not one of these data types
        if data_type not in {'Number', 'Positive Number', 'Percentage', 'Date'}:
            return True

        merge = None
        text = doc_text[buffer[0]['start_offset'] : row['end_offset']]

        # only merge percentages/dates/(positive) numbers if the result is still normalizable to the type
        if data_type == 'Percentage':
            merge = normalize_to_percentage(text)
        elif data_type == 'Date':
            merge = normalize_to_date(text)
        elif data_type == 'Number':
            merge = normalize_to_float(text)
        elif data_type == 'Positive Number':
            merge = normalize_to_positive_float(text)

        return merge is not None

    @staticmethod
    def has_compatible_interface(other) -> bool:
        """
        Validate that an instance of an Extraction AI implements the same interface as AbstractExtractionAI.

        An Extraction AI should implement methods with the same signature as:
        - AbstractExtractionAI.__init__
        - AbstractExtractionAI.fit
        - AbstractExtractionAI.extract
        - AbstractExtractionAI.check_is_ready

        :param other: An instance of an Extraction AI to compare with.
        """
        try:
            return (
                signature(other.__init__).parameters['category'].annotation.__name__ == 'Category'
                and signature(other.extract).parameters['document'].annotation.__name__ == 'Document'
                and signature(other.extract).return_annotation.__name__ == 'Document'
                and signature(other.fit)
                and signature(other.check_is_ready)
            )
        except KeyError:
            return False
        except AttributeError:
            return False

    @property
    def pkl_name(self) -> str:
        """Generate a name for the pickle file."""
        # Bento tag names must be 63 characters or less.
        # To ensure this and not lose relevant information, we first build separate parts of the name that do not
        # include the category name, which is the only thing that can be reasonably truncated to fit.
        prefix = f'{self.name_lower()}_{self.category.id_ if self.category.id_ else 0}_'
        suffix = f'_{get_timestamp()}'
        # The category name is the only part that can be truncated, so we truncate it to 63 - len(prefix) - len(suffix).
        category_name = slugify(self.category.name)[: 63 - len(prefix) - len(suffix)]
        # Put all the pieces back together to form the final, 63 character or less name.
        return f'{prefix}{category_name}{suffix}'

    @property
    def temp_pkl_file_path(self) -> str:
        """Generate a path for temporary pickle file."""
        temp_pkl_file_path = os.path.join(self.output_dir, f'{self.pkl_name}_tmp.cloudpickle')
        return temp_pkl_file_path

    @property
    def pkl_file_path(self) -> str:
        """Generate a path for a resulting pickle file."""
        pkl_file_path = os.path.join(self.output_dir, f'{self.pkl_name}.pkl')
        return pkl_file_path

    @staticmethod
    def load_model(pickle_path: str, max_ram: Union[None, str] = None):
        """
        Load the model and check if it has the interface compatible with the class.

        :param pickle_path: Path to the pickled model.
        :type pickle_path: str
        :raises FileNotFoundError: If the path is invalid.
        :raises OSError: When the data is corrupted or invalid and cannot be loaded.
        :raises TypeError: When the loaded pickle isn't recognized as a Konfuzio AI model.
        :return: Extraction AI model.
        """
        model = super(AbstractExtractionAI, AbstractExtractionAI).load_model(pickle_path, max_ram)
        if not AbstractExtractionAI.has_compatible_interface(model):
            raise TypeError(
                "Loaded model's interface is not compatible with any AIs. Please provide a model that has all the " 'abstract methods implemented.'
            )
        return model


class GroupAnnotationSets:
    """Groups Annotation into Annotation Sets."""

    def __init__(self):
        """Initialize TemplateClf."""
        self.label_set_max_depth = 100
        self.label_set_n_estimators = 100
        self.label_set_n_nearest_template = 5
        self.label_set_clf = None

    def fit_label_set_clf(self) -> Tuple[Optional[object], Optional[List['str']]]:
        """
        Fit classifier to predict start lines of Sections.

        :param documents:
        :return:
        """
        # Only train template clf is there are non default templates
        logger.info('Start training of LabelSet Classifier.')

        LabelSetInfo = collections.namedtuple('LabelSetInfo', ['is_default', 'name', 'has_multiple_annotation_sets', 'target_names'])
        self.label_sets_info = [
            LabelSetInfo(
                **{
                    'is_default': label_set.is_default,
                    'name': label_set.name,
                    'has_multiple_annotation_sets': label_set.has_multiple_annotation_sets,
                    'target_names': label_set.get_target_names(self.use_separate_labels),
                }
            )
            for label_set in self.category.label_sets
        ]

        if not [lset for lset in self.category.label_sets if not lset.is_default]:
            # todo see https://gitlab.com/konfuzio/objectives/-/issues/2247
            # todo check for NO_LABEL_SET if we should keep it
            return None
        logger.info('Start training of Multi-class Label Set Classifier.')
        # ignores the section count as it actually worsens results
        # todo check if no category labels should be ignored
        self.template_feature_list = list(self.clf.classes_)  # list of label classifier targets
        # logger.warning("template_feature_list:", self.template_feature_list)
        n_nearest = self.label_set_n_nearest_template
        # Pretty long feature generation
        df_train_label = self.df_train

        df_train_label_list = list(df_train_label.groupby('document_id'))

        df_train_template_list = []
        df_train_ground_truth_list = []
        for document_id, df_doc in df_train_label_list:
            document = self.category.project.get_document_by_id(document_id)
            df_train_template_list.append(self.convert_label_features_to_template_features(df_doc, document.text))
            df_train_ground_truth_list.append(self.build_document_template_feature(document))

        df_train_expanded_features_list = [
            self.generate_relative_line_features(n_nearest, pandas.DataFrame(df, columns=self.template_feature_list)) for df in df_train_template_list
        ]

        df_train_ground_truth = pandas.DataFrame(pandas.concat(df_train_ground_truth_list), columns=self.template_feature_list + ['y'])

        self.template_expanded_feature_list = list(df_train_expanded_features_list[0].columns)

        df_train_expanded_features = pandas.DataFrame(pandas.concat(df_train_expanded_features_list), columns=self.template_expanded_feature_list)

        y_train = numpy.array(df_train_ground_truth['y']).astype('str')
        x_train = df_train_expanded_features[self.template_expanded_feature_list]

        # fillna(0) is used here as not every label is found in every document at least once
        x_train.fillna(0, inplace=True)

        # No features available
        if x_train.empty:
            logger.error('No features available to train template classifier, ' 'probably because there are no annotations.')
            return None, None

        label_set_clf = RandomForestClassifier(n_estimators=self.label_set_n_estimators, max_depth=self.label_set_max_depth, random_state=420)
        label_set_clf.fit(x_train, y_train)

        self.label_set_clf = label_set_clf
        return self.label_set_clf, self.template_feature_list

    def generate_relative_line_features(self, n_nearest: int, df_features: pandas.DataFrame) -> pandas.DataFrame:
        """Add the features of the n_nearest previous and next lines."""
        if n_nearest == 0:
            return df_features

        min_row = 0
        max_row = len(df_features.index) - 1

        df_features_new_list = []

        for index, row in df_features.iterrows():
            row_dict = row.to_dict()

            # get a relevant lines and add them to the dict_list
            for i in range(n_nearest):
                if index + (i + 1) <= max_row:
                    d_next = df_features.iloc[index + (i + 1)].to_dict()
                else:
                    d_next = row.to_dict()
                    d_next = {k: 0 for k, v in d_next.items()}
                d_next = {f'next_line_{i + 1}_{k}': v for k, v in d_next.items()}

                if index - (i + 1) >= min_row:
                    d_prev = df_features.iloc[index - (i + 1)].to_dict()
                else:
                    d_prev = row.to_dict()
                    d_prev = {k: 0 for k, v in d_prev.items()}
                d_prev = {f'prev_line_{i + 1}_{k}': v for k, v in d_prev.items()}
                # merge the line into the row dict
                row_dict = {**row_dict, **d_next, **d_prev}

            df_features_new_list.append(row_dict)

        return pandas.DataFrame(df_features_new_list)

    def convert_label_features_to_template_features(self, feature_df_label: pandas.DataFrame, document_text) -> pandas.DataFrame:
        """
        Convert the feature_df for the label_clf to a feature_df for the label_set_clf.

        The input is the Feature-Dataframe and text for one document.
        """
        # reset indices to avoid bugs with stupid NaN's as label_text
        feature_df_label.reset_index(drop=True, inplace=True)

        # predict and transform the DataFrame to be compatible with the other functions
        results = pandas.DataFrame(data=self.clf.predict_proba(X=feature_df_label[self.label_feature_list]), columns=self.clf.classes_)

        # Remove no_label predictions
        # if 'NO_LABEL' in results.columns:
        #     results = results.drop(['NO_LABEL'], axis=1)

        # if self.no_label_name in results.columns:
        #     results = results.drop([self.no_label_name], axis=1)

        # Store most likely prediction and its accuracy in separated columns
        feature_df_label['result_name'] = results.idxmax(axis=1)
        feature_df_label['confidence'] = results.max(axis=1)

        # convert the transformed df to the new template features
        feature_df_template = self.build_document_template_feature_X(document_text, feature_df_label).filter(self.template_feature_list, axis=1)
        feature_df_template = feature_df_template.reindex(columns=self.template_feature_list).fillna(0)

        return feature_df_template

    def build_document_template_feature(self, document) -> pandas.DataFrame():
        """Build document feature for template classifier given ground truth."""
        df = pandas.DataFrame()
        char_count = 0

        document_annotations = [
            annotation for annotation_set in document.annotation_sets() for annotation in annotation_set.annotations(use_correct=True)
        ]

        # Loop over lines
        for i, line in enumerate(document.text.replace('\f', '\n').split('\n')):
            matched_annotation_set = None
            new_char_count = char_count + len(line)
            assert line == document.text[char_count:new_char_count]
            # TODO: Currently we can't handle
            for annotation_set in document.annotation_sets():
                if annotation_set.start_offset and char_count <= annotation_set.start_offset < new_char_count:
                    matched_annotation_set: AnnotationSet = annotation_set
                    break

            line_annotations = [x for x in document_annotations if char_count <= x.spans[0].start_offset < new_char_count]
            annotations_dict = {x.label.name: True for x in line_annotations}
            counter_dict = dict(collections.Counter(annotation.annotation_set.label_set.name for annotation in line_annotations))
            y = matched_annotation_set.label_set.name if matched_annotation_set else 'No'
            tmp_df = pandas.DataFrame([{'line': i, 'y': y, 'document': document.id_, **annotations_dict, **counter_dict}])
            df = pandas.concat([df, tmp_df], ignore_index=True)
            char_count = new_char_count + 1
        df['text'] = document.text.replace('\f', '\n').split('\n')
        return df.fillna(0)

    def build_document_template_feature_X(self, text, df) -> pandas.DataFrame():
        """
        Calculate features for a document given the extraction results.

        :param text:
        :param df:
        :return:
        """
        if self.category.name == 'NO_CATEGORY':
            raise AttributeError(f'{self} does not provide a Category.')

        global_df = pandas.DataFrame()
        char_count = 0
        # Using OptimalThreshold is a bad idea as it might defer between training (actual treshold from the label)
        # and runtime (default treshold.

        # df = df[df['confidence'] >= 0.1]  # df['OptimalThreshold']]
        lines = text.replace('\f', '\n').split('\n')
        for i, line in enumerate(lines):
            new_char_count = char_count + len(line)
            assert line == text[char_count:new_char_count]
            line_df = df[(char_count <= df['start_offset']) & (df['end_offset'] <= new_char_count)]
            spans = [row for index, row in line_df.iterrows()]
            spans_dict = {x['result_name']: True for x in spans}
            # counter_dict = {}  # why?
            # annotations_accuracy_dict = defaultdict(lambda: 0)
            # for annotation in annotations:
            # annotations_accuracy_dict[f'{annotation["label"]}_accuracy'] += annotation['confidence']
            # try:

            #     label = next(x for x in self.category.project.labels if x.name == annotation['result_name'])
            # except StopIteration:
            #     continue
            # for label_set in self.label_sets:
            #     if label in label_set.labels:
            #         if label_set.name in counter_dict.keys():
            #             counter_dict[label_set.name] += 1
            #         else:
            #             counter_dict[label_set.name] = 1
            tmp_df = pandas.DataFrame([spans_dict])  # ([{**spans_dict, **counter_dict}])
            global_df = pandas.concat([global_df, tmp_df], ignore_index=True)
            char_count = new_char_count + 1
        global_df['text'] = lines
        return global_df.fillna(0)

    @classmethod
    def dict_to_dataframe(cls, res_dict):
        """Convert a Dict to Dataframe add label as column."""
        df = pandas.DataFrame()
        for name in res_dict.keys():
            label_df = res_dict[name]
            label_df['result_name'] = name
            df = df.append(label_df, sort=True)
        return df

    def extract_template_with_clf(self, text, res_dict):
        """Run LabelSet classifier to find AnnotationSets."""
        logger.info('Extract AnnotationSets.')
        if not res_dict:
            logger.warning('res_dict is empty')
            return res_dict
        n_nearest = (
            self.label_set_n_nearest_template
            if hasattr(self, 'label_set_n_nearest_template')
            else (self.n_nearest_template if hasattr(self, 'n_nearest_template') else 0)
        )
        feature_df = self.build_document_template_feature_X(text, self.dict_to_dataframe(res_dict)).filter(self.template_feature_list, axis=1)
        feature_df = feature_df.reindex(columns=self.template_feature_list).fillna(0)
        feature_df = self.generate_relative_line_features(n_nearest, feature_df)

        res_series = self.label_set_clf.predict(feature_df)
        res_templates = pandas.DataFrame(res_series)
        # res_templates['text'] = text.replace('\f', '\n').split('\n')  # Debug code.

        # TODO improve ordering. What happens if Annotations are not matched?
        logger.info('Building new res dict')
        new_res_dict = {}
        text_replaced = text.replace('\f', '\n')

        # Add extractions from non-default sections.
        for label_set in [x for x in self.label_sets_info if not x.is_default]:
            # Add Extraction from SectionLabels with multiple sections (as list).
            if label_set.has_multiple_annotation_sets:
                new_res_dict[label_set.name] = []
                detected_sections = res_templates[res_templates[0] == label_set.name]
                # List of tuples, e.g. [(1, DefaultSectionName), (14, DetailedSectionName), ...]
                # line_list = [(index, row[0]) for index, row in detected_sections.iterrows()]
                if not detected_sections.empty:
                    i = 0
                    # for each line of a certain section label
                    for line_number, section_name in detected_sections.iterrows():
                        section_dict = {}
                        # we try to find the labels that match that section
                        for target_label_name in label_set.target_names:
                            if target_label_name in res_dict.keys():
                                label_df = res_dict[target_label_name]
                                if label_df.empty:
                                    continue
                                # todo: the next line is memory heavy
                                #  https://gitlab.com/konfuzio/objectives/-/issues/9342
                                label_df['line'] = label_df['start_offset'].apply(lambda x: text_replaced[: int(x)]).str.count('\n')
                                try:
                                    next_section_start: int = detected_sections.index[i + 1]  # line_list[i + 1][0]
                                except IndexError:  # ?
                                    next_section_start: int = text_replaced.count('\n') + 1
                                except Exception:
                                    raise

                                # we get the label df that is contained within the section
                                label_df = label_df[(line_number <= label_df['line']) & (label_df['line'] < next_section_start)]
                                if label_df.empty:
                                    continue
                                section_dict[target_label_name] = label_df  # Add to new result dict
                                # Remove from input dict
                                res_dict[target_label_name] = res_dict[target_label_name].drop(label_df.index)
                        i += 1
                        new_res_dict[label_set.name].append(section_dict)
            # Add Extraction from SectionLabels with single section (as dict).
            else:
                _dict = {}
                for target_label_name in label_set.target_names:
                    if target_label_name in res_dict.keys():
                        _dict[target_label_name] = res_dict[target_label_name]
                        del res_dict[target_label_name]  # ?
                if _dict:
                    new_res_dict[label_set.name] = _dict
                continue

        # Finally add remaining extractions to default section (if they are allowed to be there).
        for label_set in [x for x in self.label_sets_info if x.is_default]:
            for target_label_name in label_set.target_names:
                if target_label_name in res_dict.keys():
                    new_res_dict[target_label_name] = res_dict[target_label_name]
                    del res_dict[target_label_name]  # ?
            continue

        return new_res_dict


class RFExtractionAI(AbstractExtractionAI, GroupAnnotationSets):
    """Encode visual and textual features to extract text regions.

    Fit an extraction pipeline to extract linked Annotations.

    Both Label and Label Set classifiers are using a RandomForestClassifier from scikit-learn to run in a low memory and
    single CPU environment. A random forest classifier is a group of decision trees classifiers, see:
    https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

    The parameters of this class allow to select the Tokenizer, to configure the Label and Label Set classifiers and to
    select the type of features used by the Label and Label Set classifiers.

    They are divided in:
    - tokenizer selection
    - parametrization of the Label classifier
    - parametrization of the Label Set classifier
    - features for the Label classifier
    - features for the Label Set classifier

    By default, the text of the Documents is split into smaller chunks of text based on whitespaces
    ('WhitespaceTokenizer'). That means that all words present in the text will be shown to the AI. It is possible to
    define if the splitting of the text into smaller chunks should be done based on regexes learned from the
    Spans of the Annotations of the Category ('tokenizer_regex') or if to use a model from Spacy library for German
    language ('tokenizer_spacy'). Another option is to use a pre-defined list of tokenizers based on regexes
    ('tokenizer_regex_list') and, on top of the pre-defined list, to create tokenizers that match what is missed
    by those ('tokenizer_regex_combination').

    Some parameters of the scikit-learn RandomForestClassifier used for the Label and/or Label Set classifier
    can be set directly in Konfuzio Server ('label_n_estimators', 'label_max_depth', 'label_class_weight',
    'label_random_state', 'label_set_n_estimators', 'label_set_max_depth').

    Features are measurable pieces of data of the Annotation. By default, a combination of features is used that
    includes features built from the text of the Annotation ('string_features'), features built from the position of
    the Annotation in the Document ('spatial_features') and features from the Spans created by a WhitespaceTokenizer on
    the left or on the right of the Annotation ('n_nearest_left', 'n_nearest_right', 'n_nearest_across_lines).
    It is possible to exclude any of them ('spatial_features', 'string_features', 'n_nearest_left', 'n_nearest_right')
    or to specify the number of Spans created by a WhitespaceTokenizer to consider
    ('n_nearest_left', 'n_nearest_right').

    While extracting, the Label Set classifier takes the predictions from the Label classifier as input.
    The Label Set classifier groups them into Annotation sets.
    """

    def __init__(
        self,
        n_nearest: int = 2,
        first_word: bool = True,
        n_estimators: int = 100,
        max_depth: int = 100,
        no_label_limit: Union[int, float, None] = None,
        n_nearest_across_lines: bool = False,
        use_separate_labels: bool = True,
        category: Category = None,
        tokenizer=None,
        area_keywords=None,
        marker_keywords=None,
        column_keywords=None,
        exclude_data_types_from_horizontal_merge=None,
        exclude_non_machine_readable_annotations=False,
        select_top_annotations=False,
        advanced_number_features=False,
        *args,
        **kwargs,
    ):
        """RFExtractionAI."""
        logger.info('Initializing RFExtractionAI.')
        super().__init__(category, *args, **kwargs)
        GroupAnnotationSets.__init__(self)

        self.label_feature_list = None

        logger.info('RFExtractionAI settings:')
        logger.info(f'{use_separate_labels=}')
        logger.info(f'{category=}')
        logger.info(f'{n_nearest=}')
        logger.info(f'{first_word=}')
        logger.info(f'{max_depth=}')
        logger.info(f'{n_estimators=}')
        logger.info(f'{no_label_limit=}')
        logger.info(f'{n_nearest_across_lines=}')

        self.n_nearest = n_nearest
        self.max_depth = max_depth
        self.n_estimators = n_estimators
        self.use_separate_labels = use_separate_labels
        self.no_label_limit = no_label_limit
        self.first_word = first_word
        self.n_nearest_across_lines = n_nearest_across_lines

        self.area_keywords = area_keywords
        self.marker_keywords = marker_keywords
        self.column_keywords = column_keywords
        self.exclude_data_types_from_horizontal_merge = exclude_data_types_from_horizontal_merge
        self.exclude_non_machine_readable_annotations = exclude_non_machine_readable_annotations
        self.select_top_annotations = select_top_annotations
        self.advanced_number_features = advanced_number_features

        # label set clf hyperparameters
        self.label_set_n_nearest_template = kwargs.get('label_set_n_nearest_template', 5)
        self.label_set_max_depth = kwargs.get('label_set_max_depth', 100)
        self.label_set_n_estimators = kwargs.get('label_set_n_estimators', 100)
        logger.info(f'label_set_n_nearest_template={self.label_set_n_nearest_template}')
        logger.info(f'label_set_max_depth={self.label_set_max_depth}')
        logger.info(f'label_set_n_estimators={self.label_set_n_estimators}')

        self.tokenizer = tokenizer
        logger.info(f'{tokenizer=}')

        self.clf = None

        self.no_label_set_name = None
        self.no_label_name = None

        self.output_dir = None

    @property
    def requires_segmentation(self) -> bool:
        """Return True if the Extraction AI requires detectron segmentation results to process Documents."""
        if (
            sdk_isinstance(self.tokenizer, ParagraphTokenizer) or sdk_isinstance(self.tokenizer, SentenceTokenizer)
        ) and self.tokenizer.mode == 'detectron':
            return True
        elif self.tokenizer is None:
            logger.warning('Tokenizer is not set. Assuming no segmentation results is required.')
        return False

    def features(self, document: Document):
        """Calculate features using the best working default values that can be overwritten with self values."""
        logger.info(f'Starting {document} feature calculation.')
        if self.no_label_name is None or self.no_label_set_name is None:
            self.no_label_name = document.project.no_label.name_clean
            self.no_label_set_name = document.project.no_label_set.name_clean
        df, _feature_list, _temp_df_raw_errors = process_document_data(
            document=document,
            spans=document.spans(use_correct=False),
            n_nearest=self.n_nearest,
            first_word=self.first_word,
            n_nearest_across_lines=self.n_nearest_across_lines,
            area_keywords=self.area_keywords if hasattr(self, 'area_keywords') else None,
            marker_keywords=self.marker_keywords if hasattr(self, 'marker_keywords') else None,
            column_keywords=self.column_keywords if hasattr(self, 'column_keywords') else None,
            advanced_number_features=self.advanced_number_features if hasattr(self, 'advanced_number_features') else None,
        )

        if self.use_separate_labels:
            df['target'] = df['label_set_name'] + '__' + df['label_name']
        else:
            df['target'] = df['label_name']
        return df, _feature_list, _temp_df_raw_errors

    def check_is_ready(self):
        """
        Check if the ExtractionAI is ready for the inference.

        It is assumed that the model is ready if a Tokenizer and a Category were set, Classifiers were set and trained.

        :raises AttributeError: When no Tokenizer is specified.
        :raises AttributeError: When no Category is specified.
        :raises AttributeError: When no Label Classifier has been provided.
        """
        super().check_is_ready()
        if self.tokenizer is None:
            raise AttributeError(f'{self} missing Tokenizer.')

        if self.clf is None:
            raise AttributeError(f'{self} does not provide a Label Classifier. Please add it.')
        else:
            check_is_fitted(self.clf)

        if self.label_set_clf is None:
            logger.warning(f'{self} does not provide a LabelSet Classfier.')

    def extract(self, document: Document) -> Document:
        """
        Infer information from a given Document.

        :param document: Document object
        :return: Document with predicted labels

        :raises:
         AttributeError: When missing a Tokenizer
         NotFittedError: When CLF is not fitted

        """
        # 1. create Virtual inference Document with Category set to the Category of the ExtractionAI
        inference_document = super().extract(document)

        # 2. tokenize
        self.tokenizer.tokenize(inference_document)
        if not inference_document.spans():
            if inference_document.text.strip() == '':
                logger.warning(f'{self.tokenizer} does not provide Spans due to empty {document}.')
            else:
                logger.error(f'{self.tokenizer} does not provide Spans for {document}, even though it contains text.')
            return inference_document

        # 3. preprocessing
        df, _feature_names, _raw_errors = self.features(inference_document)
        inference_document = self.extract_from_df(df, inference_document)

        # 4. Select only machine_readable Annotations
        exclude_non_machine_readable_annotations = self.exclude_non_machine_readable_annotations if hasattr(self, 'exclude_non_machine_readable_annotations') else False
        if exclude_non_machine_readable_annotations:
            selected_annotations = []
            for x in inference_document.annotations(use_correct=False):
                if all(span.normalized is not None for span in x.spans):
                    selected_annotations.append(x)
                else:
                    if x.confidence > 0.1:
                        print("Excluded because not machine readable", x.label.name, x.offset_string, x.confidence,
                              document.id_)
        else:
            selected_annotations = inference_document.annotations(use_correct=False)

        select_top_annotations = self.select_top_annotations if hasattr(self, 'select_top_annotations') else False
        if select_top_annotations:
            # 5. Collect best annotations, respecting has_multiple_top_candidates
            # Sort by confidence (descending)
            # TODO can we re-use view_annotations here?
            best_annotations = {}
            for annotation in sorted(selected_annotations, key=lambda x: x.confidence, reverse=True):
                label = annotation.label
                if label.has_multiple_top_candidates:
                    # Always keep multiple candidates for such labels
                    best_annotations.setdefault(label, []).append(annotation)
                else:
                    # Only keep the top one
                    if label not in best_annotations:
                        best_annotations[label] = [annotation]

            # Flatten the dict values into a final list
            final_annotations = [ann for anns in best_annotations.values() for ann in anns]

            # 6. Boost low-confidence
            inference_document._annotations = AnnotationsContainer()
            for annotation in final_annotations:
                if 0.1 <= annotation.confidence <= 0.2:
                    annotation.confidence += 0.1
                inference_document._annotations.append(annotation)

        return inference_document

    def extract_from_df(self, df: pandas.DataFrame, inference_document: Document) -> Document:
        """Predict Labels from features."""
        try:
            independent_variables = df[self.label_feature_list]
        except KeyError:
            raise KeyError(f'Features of {inference_document} do not match the features of the pipeline.')
            # todo calculate features of Document as defined in pipeline and do not check afterwards
        # 4. prediction and store most likely prediction and its accuracy in separated columns
        results = pandas.DataFrame(data=self.clf.predict_proba(X=independent_variables), columns=self.clf.classes_)

        # Remove no_label predictions
        if self.no_label_name in results.columns:
            results = results.drop([self.no_label_name], axis=1)

        if self.no_label_set_name in results.columns:
            results = results.drop([self.no_label_set_name], axis=1)

        separate_no_label_target = self.no_label_set_name + '__' + self.no_label_name
        if separate_no_label_target in results.columns:
            results = results.drop([separate_no_label_target], axis=1)

        res_dict = {}
        no_label_res_dict = {}

        # Main Logic -------------------------
        if not results.empty:
            df['result_name'] = results.idxmax(axis=1)
            df['confidence'] = results.max(axis=1)

            # Convert DataFrame to Dict with labels as keys and label dataframes as value.
            for result_name in set(df['result_name']):
                result_df = df[(df['result_name'] == result_name) & (df['confidence'] >= df['label_threshold'])].copy()

                if not result_df.empty:
                    res_dict[result_name] = result_df

            for result_name in set(df['result_name']):
                result_df = df[(df['result_name'] == result_name) & (df['confidence'] < df['label_threshold'])].copy()

                if not result_df.empty:
                    no_label_res_dict[result_name] = result_df

        res_dict = self.remove_empty_dataframes_from_extraction(res_dict)
        no_label_res_dict = self.remove_empty_dataframes_from_extraction(no_label_res_dict)

        if not sdk_isinstance(self.tokenizer, ParagraphTokenizer) and not sdk_isinstance(self.tokenizer, SentenceTokenizer):
            # We assume that Paragraph or Sentence tokenizers have correctly tokenized the Document
            exclude_data_types = self.exclude_data_types_from_horizontal_merge if hasattr(self, 'exclude_data_types_from_horizontal_merge') else []
            res_dict = self.merge_horizontal(res_dict, inference_document.text, exclude_data_types)

        # Try to calculate sections based on template classifier.
        if self.label_set_clf is not None and res_dict:  # todo smarter handling of multiple clf
            res_dict = self.extract_template_with_clf(inference_document.text, res_dict)
        res_dict[self.no_label_set_name] = no_label_res_dict

        if self.use_separate_labels:
            res_dict = self.separate_labels(res_dict)

        virtual_doc = self.extraction_result_to_document(inference_document, res_dict)

        self.tokenizer.found_spans(virtual_doc)

        if sdk_isinstance(self.tokenizer, ParagraphTokenizer) or sdk_isinstance(self.tokenizer, SentenceTokenizer):
            # When using the Paragraph or Sentence tokenizer, we restore the multi-line Annotations they created.
            virtual_doc = self.merge_vertical_like(virtual_doc, inference_document)
        else:
            # join document Spans into multi-line Annotation
            virtual_doc = self.merge_vertical(virtual_doc)

        return virtual_doc

    def merge_vertical(self, document: Document, only_multiline_labels=True):
        """
        Merge Annotations with the same Label.

        See more details at https://dev.konfuzio.com/sdk/explanations.html#vertical-merge

        :param document: Document whose Annotations should be merged vertically
        :param only_multiline_labels: Only merge if a multiline Label Annotation is in the Category Training set
        """
        logger.info('Vertical merging Annotations.')
        if not self.category:
            raise AttributeError(f'{self} merge_vertical requires a Category.')
        labels_dict = {}
        for label in self.category.labels:
            if not only_multiline_labels or label.has_multiline_annotations():
                labels_dict[label.name] = []

        for annotation in document.annotations(use_correct=False, ignore_below_threshold=True):
            if annotation.label.name in labels_dict:
                labels_dict[annotation.label.name].append(annotation)

        for label_id in labels_dict:
            buffer = []
            for annotation in labels_dict[label_id]:
                for span in annotation.spans:
                    # remove all spans in buffer more than 1 line apart
                    while buffer and span.line_index > buffer[0].line_index + 1:
                        buffer.pop(0)

                    if buffer and buffer[-1].page != span.page:
                        buffer = [span]
                        continue

                    if len(annotation.spans) > 1:
                        buffer.append(span)
                        continue

                    for candidate in buffer:
                        # only looking for elements in line above
                        if candidate.line_index == span.line_index:
                            break

                        # Merge if there is overlap in the horizontal direction or if only separated by a line break
                        # AND if the AnnotationSets are the same or if the Annotation is alone in its AnnotationSet
                        if (
                            (not (span.bbox().x0 > candidate.bbox().x1 or span.bbox().x1 < candidate.bbox().x0))
                            or document.text[candidate.end_offset : span.start_offset].replace(' ', '').replace('\n', '') == ''
                        ) and (
                            span.annotation.annotation_set is candidate.annotation.annotation_set
                            or len(span.annotation.annotation_set.annotations(use_correct=False, ignore_below_threshold=True)) == 1
                        ):
                            span.annotation.delete(delete_online=False)
                            span.annotation = None
                            candidate.annotation.add_span(span)
                            buffer.remove(candidate)
                    buffer.append(span)
        return document

    def merge_vertical_like(self, document: Document, template_document: Document):
        """
        Merge Annotations the same way as in another copy of the same Document.

        All single-Span Annotations in the current Document (self) are matched with corresponding multi-line
        Spans in the given Document and are merged in the same way.
        The Label of the new multi-line Annotations is taken to be the most common Label among the original
        single-line Annotations that are being merged.

        :param document: Document with multi-line Annotations
        """
        logger.info(f'Vertical merging Annotations like {template_document}.')
        assert document.text == template_document.text, f'{self} and {template_document} need to have the same ocr text.'
        span_to_annotation = {(span.start_offset, span.end_offset): hash(span.annotation) for span in template_document.spans(use_correct=False)}
        ann_to_anns = collections.defaultdict(list)
        for annotation in document.annotations(use_correct=False):
            assert len(annotation.spans) == 1, f'Cannot use merge_verical_like in {document} with multi-span {annotation}.'
            span_offset_key = (annotation.spans[0].start_offset, annotation.spans[0].end_offset)
            if span_offset_key in span_to_annotation:
                ann_to_anns[span_to_annotation[span_offset_key]].append(annotation)
        for _, self_annotations in ann_to_anns.items():
            if len(self_annotations) == 1:
                continue
            else:
                self_annotations = sorted(self_annotations)
                keep_annotation = self_annotations[0]
                annotation_labels = [keep_annotation.label]
                for to_merge_annotation in self_annotations[1:]:
                    annotation_labels.append(to_merge_annotation.label)
                    span = to_merge_annotation.spans[0]
                    to_merge_annotation.delete(delete_online=False)
                    span.annotation = None
                    keep_annotation.add_span(span)
                most_common_label = collections.Counter(annotation_labels).most_common(1)[0][0]
                keep_annotation.label = most_common_label

        return document

    def separate_labels(self, res_dict: 'Dict') -> 'Dict':
        """
        Undo the renaming of the labels.

        In this way we have the output of the extraction in the correct format.
        """
        new_res = {}
        for key, value in res_dict.items():
            # if the value is a list, is because the key corresponds to a section label with multiple sections
            # the key has already the name of the section label
            # we need to go to each element of the list, which is a dictionary, and
            # rewrite the label name (remove the section label name) in the keys
            if isinstance(value, list):
                label_set = key
                if label_set not in new_res.keys():
                    new_res[label_set] = []

                for found_section in value:
                    new_found_section = {}
                    for label, df in found_section.items():
                        if '__' in label:
                            label = label.split('__')[1]
                            df.label_name = label
                            df.label = label
                        new_found_section[label] = df

                    new_res[label_set].append(new_found_section)

            # if the value is a dictionary, is because the key corresponds to a section label without multiple sections
            # we need to rewrite the label name (remove the section label name) in the keys
            elif isinstance(value, dict):
                label_set = key
                if label_set not in new_res.keys():
                    new_res[label_set] = {}

                for label, df in value.items():
                    if '__' in label:
                        label = label.split('__')[1]
                        df.label_name = label
                        df.label = label
                    new_res[label_set][label] = df

            # otherwise the value must be directly a dataframe and it will correspond to the default section
            # can also correspond to labels which the template clf couldn't attribute to any template.
            # so we still check if we have the changed label name
            elif '__' in key:
                label_set = key.split('__')[0]
                if label_set not in new_res.keys():
                    new_res[label_set] = {}
                key = key.split('__')[1]
                value.label_name = key
                value.label = key
                # if the section label already exists and allows multi sections
                if isinstance(new_res[label_set], list):
                    new_res[label_set].append({key: value})
                else:
                    new_res[label_set][key] = value
            else:
                new_res[key] = value

        return new_res

    def remove_empty_dataframes_from_extraction(self, result: Dict) -> Dict:
        """Remove empty dataframes from the result of an Extraction AI.

        The input is a dictionary where the values can be:
        - dataframe
        - dictionary where the values are dataframes
        - list of dictionaries  where the values are dataframes
        """
        for k in list(result.keys()):
            if isinstance(result[k], pandas.DataFrame) and result[k].empty:
                del result[k]
            elif isinstance(result[k], list):
                for e, element in enumerate(result[k]):
                    for sk in list(element.keys()):
                        if isinstance(element[sk], pandas.DataFrame) and element[sk].empty:
                            del result[k][e][sk]
            elif isinstance(result[k], dict):
                for ssk in list(result[k].keys()):
                    if isinstance(result[k][ssk], pandas.DataFrame) and result[k][ssk].empty:
                        del result[k][ssk]

        return result

    def filter_low_confidence_extractions(self, result: Dict) -> Dict:
        """Remove extractions with confidence below the threshold defined for the respective label.

        The input is a dictionary where the values can be:
        - dataframe
        - dictionary where the values are dataframes
        - list of dictionaries  where the values are dataframes

        :param result: Extraction results
        :returns: Filtered dictionary.
        """
        for k in list(result.keys()):
            if isinstance(result[k], pandas.DataFrame):
                filtered = self.filter_dataframe(result[k])
                if filtered.empty:
                    del result[k]
                else:
                    result[k] = filtered

            elif isinstance(result[k], list):
                for e, element in enumerate(result[k]):
                    for sk in list(element.keys()):
                        if isinstance(element[sk], pandas.DataFrame):
                            filtered = self.filter_dataframe(result[k][e][sk])
                            if filtered.empty:
                                del result[k][e][sk]
                            else:
                                result[k][e][sk] = filtered

            elif isinstance(result[k], dict):
                for ssk in list(result[k].keys()):
                    if isinstance(result[k][ssk], pandas.DataFrame):
                        filtered = self.filter_dataframe(result[k][ssk])
                        if filtered.empty:
                            del result[k][ssk]
                        else:
                            result[k][ssk] = filtered

        return result

    def filter_dataframe(self, df: pandas.DataFrame) -> pandas.DataFrame:
        """Filter dataframe rows accordingly with the confidence value.

        Rows (extractions) where the accuracy value is below the threshold defined for the label are removed.

        :param df: Dataframe with extraction results
        :returns: Filtered dataframe
        """
        filtered = df[df['confidence'] >= df['label_threshold']]
        return filtered

    def label_train_document(self, virtual_document: Document, original_document: Document):
        """Assign Labels to Annotations in newly tokenized virtual training Document."""
        doc_spans = original_document.spans(use_correct=True)
        s_i = 0
        for span in virtual_document.spans():
            while s_i < len(doc_spans) and span.start_offset > doc_spans[s_i].end_offset:
                s_i += 1
            if s_i >= len(doc_spans):
                break
            if span.end_offset < doc_spans[s_i].start_offset:
                continue

            r = range(doc_spans[s_i].start_offset, doc_spans[s_i].end_offset + 1)
            if span.start_offset in r and span.end_offset in r:
                span.annotation.label = doc_spans[s_i].annotation.label
                span.annotation.annotation_set = doc_spans[s_i].annotation.annotation_set

    def feature_function(
        self,
        documents: List[Document],
        no_label_limit: Union[None, int, float] = None,
        retokenize: Optional[bool] = None,
        require_revised_annotations: bool = False,
    ) -> Tuple[List[pandas.DataFrame], list]:
        """Calculate features per Span of Annotations.

        :param documents: List of Documents to extract features from.
        :param no_label_limit: Int or Float to limit number of new Annotations to create during tokenization.
        :param retokenize: Bool for whether to recreate Annotations from scratch or use already existing Annotations.
        :param require_revised_annotations: Only allow calculation of features if no unrevised Annotation present.
        :return: Dataframe of features and list of feature names.
        """
        logger.info(f'Start generating features for {len(documents)} Documents.')
        logger.info(f'{no_label_limit=}')
        logger.info(f'{retokenize=}')
        logger.info(f'{require_revised_annotations=}')

        if retokenize is None:
            if sdk_isinstance(self.tokenizer, ListTokenizer):
                retokenize = False
            else:
                retokenize = True
            logger.info(f'retokenize option set to {retokenize} with Tokenizer {self.tokenizer}')

        df_real_list = []
        df_raw_errors_list = []
        feature_list = []

        for label in self.category.labels:
            label.has_multiline_annotations(categories=[self.category])

        for document in documents:
            for span in document.spans(use_correct=False):
                if span.annotation.id_:
                    # we use "<" below because we don't want to have unconfirmed annotations in the training set,
                    # and the ones below threshold wouldn't be considered anyway
                    if (
                        span.annotation.is_correct
                        or (not span.annotation.is_correct and span.annotation.revised)
                        or (
                            span.annotation.confidence
                            and hasattr(span.annotation.label, 'threshold')
                            and span.annotation.confidence < span.annotation.label.threshold
                        )
                    ):
                        pass
                    else:
                        if require_revised_annotations:
                            raise ValueError(
                                f"{span.annotation} is unrevised in this dataset and can't be used for training!"
                                f'Please revise it manually by either confirming it, rejecting it, or modifying it.'
                            )
                        else:
                            logger.error(
                                f'{span.annotation} is unrevised in this dataset and may impact model '
                                f'performance! Please revise it manually by either confirming it, rejecting '
                                f'it, or modifying it.'
                            )

            virtual_document = deepcopy(document)
            if retokenize:
                # Retokenize the Document from scratch and add correct Label the new matching Annotations.
                # This may not include exact matches for the training data, but will include all Annotations actually
                # found by the Tokenizer
                self.tokenizer.tokenize(virtual_document)
                self.label_train_document(virtual_document, document)
            else:
                # Copy existing Annotations in training Document and then tokenize and add NO_LABEL Annotations to
                # the virtual Document. This will include exact matches for the training data, but these might not
                # actually be exactly found by the Tokenizer during inference.
                for annotation in document.annotations():
                    new_spans = []
                    for span in annotation.spans:
                        new_span = Span(start_offset=span.start_offset, end_offset=span.end_offset)
                        new_spans.append(new_span)

                    # Retrieve copy of AnnotationSet from virtual Document or create new one
                    try:
                        annotation_set = virtual_document.get_annotation_set_by_id(annotation.annotation_set.id_)
                    except IndexError:
                        annotation_set = AnnotationSet(document=virtual_document, label_set=annotation.label_set, id_=annotation.annotation_set.id_)
                    _ = Annotation(
                        document=virtual_document,
                        annotation_set=annotation_set,
                        label=annotation.label,
                        category=self.category,
                        spans=new_spans,
                    )

                self.tokenizer.tokenize(virtual_document)

            no_label_annotations = virtual_document.annotations(use_correct=False, label=virtual_document.project.no_label)
            label_annotations = [x for x in virtual_document.annotations(use_correct=False) if x.label.id_]

            # We calculate features of documents as long as they have IDs, even if they are offline.
            # The assumption is that if they have an ID, then the data came either from the API or from the DB.
            if virtual_document.id_ is None and virtual_document.copy_of_id is None:
                # inference time todo reduce shuffled complexity
                assert not label_annotations, "Documents that don't come from the server have no human revised Annotations."
                raise NotImplementedError(f'{virtual_document} does not come from the server, please use process_document_data function.')
            else:
                # training time: todo reduce shuffled complexity
                if isinstance(no_label_limit, int):
                    n_no_labels = no_label_limit
                elif isinstance(no_label_limit, float):
                    n_no_labels = int(len(label_annotations) * no_label_limit)
                else:
                    assert no_label_limit is None

                if no_label_limit is not None:
                    no_label_annotations = self.get_best_no_label_annotations(n_no_labels, label_annotations, no_label_annotations)
                    logger.info(f'Document {virtual_document} NO_LABEL annotations reduced to {len(no_label_annotations)}')

            logger.info(f'Document {virtual_document} has {len(label_annotations)} labeled annotations')
            logger.info(f'Document {virtual_document} has {len(no_label_annotations)} NO_LABEL annotations')

            # todo: check if eq method of Annotation prevents duplicates
            # annotations = self._filter_annotations_for_duplicates(label_annotations + no_label_annotations)

            t0 = time.monotonic()

            temp_df_real, _feature_list, temp_df_raw_errors = self.features(virtual_document)

            logger.info(f'Document {virtual_document} processed in {time.monotonic() - t0:.1f} seconds.')

            virtual_document.delete(delete_online=False)  # reduce memory from virtual doc

            feature_list += _feature_list
            df_real_list.append(temp_df_real)
            df_raw_errors_list.append(temp_df_raw_errors)

        feature_list = list(dict.fromkeys(feature_list))  # remove duplicates while maintaining order

        if df_real_list:
            df_real_list = pandas.concat(df_real_list).reset_index(drop=True)
        else:
            raise NotImplementedError

        logger.info(f'Size of feature dict {memory_size_of(df_real_list)/1000} KB.')

        return df_real_list, feature_list

    def fit(self) -> RandomForestClassifier:
        """Given training data and the feature list this function returns the trained regression model."""
        logger.info('Start training of Multi-class Label Classifier.')

        # balanced gives every label the same weight so that the sample_number doesn't effect the results
        self.clf = RandomForestClassifier(class_weight='balanced', n_estimators=self.n_estimators, max_depth=self.max_depth, random_state=420)

        self.clf.fit(self.df_train[self.label_feature_list], self.df_train['target'])

        logger.info(f'Size of Label classifier: {memory_size_of(self.clf)/1000} KB.')

        self.fit_label_set_clf()

        logger.info(f'Size of LabelSet classifier: {memory_size_of(self.label_set_clf)/1000} KB.')

        return self.clf

    def evaluate_full(self, strict: bool = True, use_training_docs: bool = False, use_view_annotations: bool = True) -> ExtractionEvaluation:
        """
        Evaluate the full pipeline on the pipeline's Test Documents.

        :param strict: Evaluate on a Character exact level without any postprocessing.
        :param use_training_docs: Bool for whether to evaluate on the training documents instead of testing documents.
        :return: Evaluation object.
        """
        eval_list = []
        if not use_training_docs:
            eval_docs = self.test_documents
        else:
            eval_docs = self.documents

        for document in eval_docs:
            predicted_doc = self.extract(document=document)
            eval_list.append((document, predicted_doc))

        full_evaluation = ExtractionEvaluation(eval_list, strict=strict, use_view_annotations=use_view_annotations)

        return full_evaluation

    def evaluate_tokenizer(self, use_training_docs: bool = False) -> ExtractionEvaluation:
        """Evaluate the tokenizer."""
        if not use_training_docs:
            eval_docs = self.test_documents
        else:
            eval_docs = self.documents

        evaluation = self.tokenizer.evaluate_dataset(eval_docs)

        return evaluation

    def evaluate_clf(self, use_training_docs: bool = False) -> ExtractionEvaluation:
        """Evaluate the Label classifier."""
        eval_list = []
        if not use_training_docs:
            eval_docs = self.test_documents
        else:
            eval_docs = self.documents

        for document in eval_docs:
            virtual_doc = deepcopy(document)

            for ann in document.annotations():
                new_spans = []
                for span in ann.spans:
                    new_span = Span(start_offset=span.start_offset, end_offset=span.end_offset)
                    new_spans.append(new_span)

                _ = Annotation(
                    document=virtual_doc,
                    annotation_set=virtual_doc.no_label_annotation_set,
                    label=virtual_doc.project.no_label,
                    label_set=virtual_doc.project.no_label_set,
                    category=virtual_doc.category,
                    spans=new_spans,
                )

            feats_df, _, _ = self.features(virtual_doc)
            predicted_doc = self.extract_from_df(feats_df, virtual_doc)
            eval_list.append((document, predicted_doc))

        clf_evaluation = ExtractionEvaluation(eval_list, use_view_annotations=False)

        return clf_evaluation

    def evaluate_label_set_clf(self, use_training_docs: bool = False) -> ExtractionEvaluation:
        """Evaluate the LabelSet classifier."""
        if self.label_set_clf is None:
            raise AttributeError(f'{self} does not provide a LabelSet Classifier.')
        else:
            check_is_fitted(self.label_set_clf)

        eval_list = []
        if not use_training_docs:
            eval_docs = self.test_documents
        else:
            eval_docs = self.documents

        for document in eval_docs:
            df, _feature_names, _raw_errors = self.features(document)

            df['result_name'] = df['target']

            # Convert DataFrame to Dict with labels as keys and label dataframes as value.
            res_dict = {}
            for result_name in set(df['result_name']):
                result_df = df[(df['result_name'] == result_name)].copy()

                if not result_df.empty:
                    res_dict[result_name] = result_df

            res_dict = self.extract_template_with_clf(document.text, res_dict)

            if self.use_separate_labels:
                res_dict = self.separate_labels(res_dict)

            predicted_doc = self.extraction_result_to_document(document, res_dict)

            eval_list.append((document, predicted_doc))

        label_set_clf_evaluation = ExtractionEvaluation(eval_list, use_view_annotations=False)

        return label_set_clf_evaluation

    def reduce_model_weight(self):
        """Remove all non-strictly necessary parameters before saving."""
        super().reduce_model_weight()
        self.df_train = None


class LLMRfExtractionAI(RFExtractionAI):

    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key")
        self.base_url = kwargs.get("base_url")
        self.version = kwargs.get("version")
        self.model = kwargs.get("model")

        if not all([self.api_key, self.base_url, self.version, self.model]):
            raise ValueError("Missing one or more required Azure LLM parameters.")

        # client is lazy-loaded, not created immediately
        self._client = None
        super().__init__(**kwargs)  # ensure base class init is called

    @property
    def name(self):
        """Model class name."""
        return "RFExtractionAI"

    def build_bento(self, bento_model):
        """Build BentoML service for the model."""
        bento_base_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../konfuzio_sdk/bento'
        dict_metadata = self.project.create_project_metadata_dict()

        with tempfile.TemporaryDirectory() as temp_dir:
            # copy bento_module_dir to temp_dir
            shutil.copytree(bento_base_dir + '/extraction', temp_dir + '/extraction')
            shutil.copytree(bento_base_dir + '/base', temp_dir + '/base')

            # copy __init__.py file
            shutil.copy(bento_base_dir + '/__init__.py', temp_dir + '__init__.py')
            # include metadata
            with open(f'{temp_dir}/categories_and_label_data.json5', 'w') as f:
                json.dump(dict_metadata, f, indent=2, sort_keys=True)
            # include the AI model name so the service can load it correctly
            with open(f'{temp_dir}/AI_MODEL_NAME', 'w') as f:
                f.write(self._pkl_name)

            built_bento = bentoml.bentos.build(
                name=f"extraction_{self.category.id_ if self.category else '0'}",
                service=f'extraction.{self.name_lower()}_service:ExtractionService',
                include=[
                    '__init__.py',
                    'base/*.py',
                    'extraction/*.py',
                    'categories_and_label_data.json5',
                    'AI_MODEL_NAME',
                ],
                labels=self.bento_metadata,
                python={
                    'packages': [f'konfuzio-sdk<={self.konfuzio_sdk_version}', 'openai==1.79.0'],
                    'lock_packages': True,
                },
                build_ctx=temp_dir,
                models=[str(bento_model.tag)],
            )

        return built_bento

    def label_based_prompt_generator(self, category):
        prompt = """
        Please extract the following information from the attached document:

        1. Use {"label": "value"} pairs for all label data
        2. Unite labels into label sets and reflect the hierarchy in the JSON.
        3. Use ONLY label/label set names presented to you in the schema below. Do not change ANYTHING.
        4. Capture ALL relevant content visible in the image
        5. If any label is not found, just don't mention it in the JSON
        6. Create nested structures where relevant.
        7. Label sets that have multiple occurrence = True can repeat so store all label sets as a list of dicts.
        8. Keep in mind that sometimes information is speread accross text lines, not just single-line.
        9. The documents can be in any language
        10. Do not create new label and label set names. NEVER.
        11. You can only use labels and label sets that are provided in the schema below.

        An example output:

        {
        "label_sets": [
            {"label_set_name_1": [
            {"label_name_1": "value_1"},
            {"label_name_2": "value_2"}
            ]},
            {"label_set_name_2": [
            {"label_name_3": "value_3"},
            {"label_name_4": "value_4"}
            ]
            },...
        ]
        }

        Schema:

        """
        # try out code by CHELM
        # Initialize the dictionary to hold category details
        extraction_structure = {
            'name': category.name,  # todo add description to SDK
            'description': '',
            'label_sets': [],
        }

        # Iterate over each label set in the category
        for label_set in category.label_sets:
            # Skip NO_LABEL_SET
            if label_set.name == "NO_LABEL_SET":
                continue

            # Create a dictionary for the current label set
            label_set_dict = {
                'name': label_set.name,
                'can_occur_multiple_times': label_set.has_multiple_annotation_sets,
                # 'description': label_set.description, todo add description to SDK
                'labels': []
            }

            # Iterate over the labels in the current label set
            for label in label_set.labels:
                # Skip NO_LABEL
                if label.name == "NO_LABEL":
                    continue

                # Append label details to the label set's labels list
                label_set_dict['labels'].append({
                    'name': label.name,
                    'description': label.description,
                    'data_type': label.data_type
                })

            # Only add label sets that have labels after filtering
            if label_set_dict['labels']:
                # Add the label set dictionary to the main dictionary
                extraction_structure['label_sets'].append(label_set_dict)

        print('EXTRACTION SPECIFICATION - START')
        print(json.dumps(extraction_structure, indent=2))
        print('EXTRACTION SPECIFICATION - END')

        prompt += str(json.dumps(extraction_structure, indent=2))
        prompt += """\n\n Return ONLY valid JSON, with the values extracted."""
        return prompt

    def check_is_ready(self):
        pass

    def extract(self, document: Document) -> Document:
        """
        Infer information from a given Document.

        :param document: Document object
        :return: Document with predicted labels
        """
        from copy import deepcopy

        logger.info(f'Starting extraction of {document}.')

        self.check_is_ready()  # check if the model is ready for extraction

        inference_document = deepcopy(document)  # to get a Virtual Document with no Annotations

        # So that the Document belongs to the Category that is saved with the ExtractionAI
        inference_document._category = self.project.no_category
        inference_document.set_category(self.category)


        print(f"\nProcessing document {document.id_}...")
        try:
            # Generate the prompt if not already generated
            self.prompt = self.label_based_prompt_generator(self.category)

            # Debug: Print the prompt
            print("\nGenerated Prompt:")
            print("-" * 50)
            print(self.prompt)
            print("-" * 50)

            # Call LLM with the prompt and document text
            data_dict = self.run_llm(self.prompt, document.text)

            # Convert data_dict to JSON string and use parse_json_to_annotations
            json_str = json.dumps(data_dict)
            self.parse_json_to_annotations(json_str, inference_document)

            # Get all annotations
            annotations = list(inference_document.annotations(use_correct=False))
            num_annotations = len(annotations)

            # Print detailed statistics
            print("\nAnnotation Statistics:")
            print("-" * 50)
            print(f"Total annotations created: {num_annotations}")

            # Group annotations by label set
            label_set_stats = {}
            for annotation in annotations:
                label_set_name = annotation.label_set.name
                if label_set_name not in label_set_stats:
                    label_set_stats[label_set_name] = []
                label_set_stats[label_set_name].append(annotation)

            # Print statistics per label set
            print("\nAnnotations per Label Set:")
            print("-" * 50)
            for label_set_name, label_set_annotations in label_set_stats.items():
                print(f"\nLabel Set: {label_set_name}")
                print(f"Number of annotations: {len(label_set_annotations)}")
                for annotation in label_set_annotations:
                    print(f"  - Label: {annotation.label.name}")
                    print(f"    Value: {annotation.offset_string} - {annotation.normalized}")
                    print(f"    Span: {annotation.spans[0].start_offset}-{annotation.spans[0].end_offset}")

            return inference_document

        except Exception as e:
            print(f"Error processing document {document.id_}: {str(e)}")
            raise  # Re-raise the exception instead of falling back

    def parse_json_to_annotations(self, json_str: str, document: Document) -> None:
        """
        Parse a JSON string containing extracted information and create annotations for the document.
        Creates annotations even if exact text matches cannot be found.

        Args:
            json_str: JSON string containing extracted information
            document: Document to add annotations to
        """
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                logger.warning(f"Expected dict but got {type(data)}")
                return

            # annotation_set = document.default_annotation_set
            text = document.text.lower()  # Convert text to lowercase
            logger.info(f"Document text length: {len(text)}")
            my_annotation_sets = {}

            # Process each label set in the response
            for label_set_data in data.get('label_sets', []):
                for label_set_name, labels in label_set_data.items():
                    # Find the label set in the category
                    label_set = next((ls for ls in document.category.label_sets if ls.name == label_set_name), None)

                    if label_set.is_default:
                        annotation_set = document.default_annotation_set
                    else:
                        if label_set.has_multiple_annotation_sets:
                            # create a new annotation set for this label set and document
                            annotation_set = AnnotationSet(label_set=label_set, document=document)
                        else:
                            # try to get from existing mapping
                            annotation_set = my_annotation_sets.get(label_set_name)
                            if annotation_set is None:
                                # not present, so create and register it
                                annotation_set = AnnotationSet(label_set=label_set, document=document)
                                my_annotation_sets[label_set_name] = annotation_set

                    if not label_set:
                        logger.warning(f"Label set '{label_set_name}' not found in category")
                        continue

                    # Process each label in the label set
                    for label_data in labels:
                        for label_name, value in label_data.items():
                            # Find the label in the label set
                            label = next((l for l in label_set.labels if l.name == label_name), None)
                            if not label:
                                logger.warning(f"Label '{label_name}' not found in label set '{label_set_name}'")
                                continue

                            if not isinstance(value, str):
                                logger.warning(f"Expected string value for {label_name} but got {type(value)}")
                                continue

                            # Try to find the value in the text
                            value = value.strip()
                            custom_offset_string = value  # Store original value

                            # Convert value to lowercase and split into words
                            value_words = value.lower().split()

                            # Try to match from the beginning of the document
                            best_match = None
                            best_match_len = 0
                            best_match_phrase = None

                            # Debug: Print what we're trying to match
                            logger.info(f"Trying to match value: '{value}'")

                            # Try matching from the start of the document
                            for i in range(len(value_words)):
                                # Build pattern for current word sequence
                                current_words = value_words[:i + 1]
                                pattern = r'\s*'.join(re.escape(word) for word in current_words)

                                # Search for this pattern at the start of the document
                                match = re.search(pattern, text)
                                if match:
                                    # Calculate score based on number of words matched
                                    score = len(current_words) * 2

                                    # Boost score if it's at the start of the document
                                    if match.start() < 50:  # Within first 50 chars
                                        score *= 1.5

                                    if score > best_match_len:
                                        best_match = match
                                        best_match_len = score
                                        best_match_phrase = ' '.join(current_words)
                                        logger.info(f"Found match: '{best_match_phrase}' at position {match.start()}")

                            if best_match:
                                start_offset = best_match.start()
                                end_offset = best_match.end()
                                matched_text = text[start_offset:end_offset].strip()
                                logger.info(
                                    f"Found match for {label_name} at offsets {start_offset}-{end_offset}: '{matched_text}'")

                                # Calculate confidence based on how much of the value we matched
                                match_ratio = len(best_match_phrase.split()) / len(value_words)
                                confidence = 0.9 * match_ratio
                                logger.info(f"Match confidence: {confidence:.2f} (matched {match_ratio:.2f} of words)")

                                # Create a single span for the entire match
                                spans = [Span(start_offset=start_offset, end_offset=end_offset,
                                              offset_string=custom_offset_string)]
                                logger.info(f"Created span for match: '{matched_text}' at {start_offset}-{end_offset}")

                                # Create the annotation with the span
                                annotation = Annotation(
                                    document=document,
                                    label=label,
                                    confidence=confidence,
                                    label_set=label_set,
                                    annotation_set=annotation_set,
                                    spans=spans,
                                    translated_string=custom_offset_string,
                                    normalized=custom_offset_string
                                )
                                logger.info(
                                    f"Created annotation for {label_name}: {value} (confidence: {confidence:.2f})")
                            else:
                                # If no match found, use first word of document
                                first_word_match = re.search(r'\S+', text)
                                if first_word_match:
                                    start_offset = first_word_match.start()
                                    end_offset = first_word_match.end()
                                    logger.info(
                                        f"No match found for {label_name}, using first word span: '{text[start_offset:end_offset]}'")
                                    confidence = 0.5

                                    # Create single span for first word
                                    spans = [Span(start_offset=start_offset, end_offset=end_offset)]

                                    annotation = Annotation(
                                        document=document,
                                        label=label,
                                        confidence=confidence,
                                        label_set=label_set,
                                        annotation_set=annotation_set,
                                        spans=spans,
                                        translated_string=custom_offset_string,
                                        normalized=custom_offset_string
                                    )
                                    logger.info(f"Created fallback annotation for {label_name} with single span")
                                else:
                                    logger.warning(f"Could not find any text in document for {label_name}")
                                    continue

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing annotations: {str(e)}")

    def run_llm(self, instruction, text):
        """
        Call OpenAI API with the provided instruction and text.

        Args:
            instruction (str): The instruction for the LLM
            text (str): The input text to process

        Returns:
            dict: The parsed JSON response from the LLM
        """
        from openai import AzureOpenAI
        try:
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.version,
                azure_endpoint=self.base_url,
            )

            # Call the OpenAI API using the client
            response = client.chat.completions.create(
                model=self.model,  # Using GPT-4 as it's better for structured data extraction
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts structured information from text and returns it in JSON format."},
                    {"role": "user", "content": f"{instruction}\n\nText to process:\n{text}"}
                ],
                temperature=0.0,  # Use 0 temperature for deterministic results
                max_tokens=2000,  # Increased token limit for longer responses
            )

            # Get the response content
            response_text = response.choices[0].message.content
            logger.info(f"LLM Response: {response_text}")

            # Try to parse the response as JSON
            try:
                # First try parsing as is
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    logger.error("No valid JSON found in response")
                    return {}

            return result

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {}

