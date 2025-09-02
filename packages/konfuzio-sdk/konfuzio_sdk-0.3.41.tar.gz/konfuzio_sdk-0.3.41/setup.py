"""Setup."""

import subprocess
import sys
import textwrap
from os import getenv, path

import setuptools

from konfuzio_sdk_extras_list import EXTRAS

# Define version or calculate it for nightly build.
#
# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
#   X.Y.0   # For first release after an increment in Y
#   X.Y.Z   # For bugfix releases
#
# Admissible pre-release markers:
#   X.Y.ZaN   # Alpha release
#   X.Y.ZbN   # Beta release
#   X.Y.ZrcN  # Release Candidate
#   X.Y.Z     # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
#

with open(path.join('konfuzio_sdk', 'VERSION')) as version_file:
    version_number = version_file.read().strip()

if getenv('NIGHTLY_BUILD'):
    # create a pre-release
    last_commit = subprocess.check_output(['git', 'log', '-1', '--pretty=%cd', '--date=format:%Y%m%d%H%M%S']).decode('ascii').strip()
    version = f'{version_number}.dev{last_commit}'
else:
    version = f'{version_number}'

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        textwrap.dedent(
            f"""
    ==========================
    Unsupported Python version
    ==========================
    This version of Konfuzio SDK requires Python {REQUIRED_PYTHON}, but you're trying to
    install it on Python {CURRENT_PYTHON}.
    """
        )
    )
    sys.exit(1)

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='konfuzio_sdk',
    version=version,
    author='Helm & Nagel GmbH',
    author_email='info@helm-nagel.com',
    description='Konfuzio Software Development Kit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://dev.konfuzio.com/sdk/index.html',
    packages=[
        'konfuzio_sdk',
        'konfuzio_sdk.bento',
        'konfuzio_sdk.bento.base',
        'konfuzio_sdk.bento.extraction',
        'konfuzio_sdk.bento.categorization',
        'konfuzio_sdk.bento.file_splitting',
        'konfuzio_sdk.tokenizer',
        'konfuzio_sdk.trainer',
    ],
    py_modules=['konfuzio_sdk_extras_list'],
    include_package_data=True,
    entry_points={'console_scripts': ['konfuzio_sdk=konfuzio_sdk.cli:main']},
    install_requires=[
        'bentoml>=1.4.13',
        'fastapi>=0.115.12',  # Used to serve additional endpoints in Bento services
        'certifi>=2025.4.26',
        'cloudpickle>=3.1.1',  # Used to pickle objects
        'filetype>=1.2.0',  # Used to check that files are in the correct format
        'lz4>=4.4.4',  # Used to compress pickles
        'matplotlib>=3.10.0',
        'nltk>=3.9.0',
        'numpy<2',
        'pandas<2',
        'Pillow>=11.2.1',
        'pydantic>=2.11.4',
        'python-dateutil>=2.9.0.post0',
        'python-decouple>=3.8',
        'python-dotenv>=1.1.0',
        'requests>=2.32.3',
        'regex>=2024.11.6',  # re module but better
        'scikit-learn>=1.6.1',
        'tabulate>=0.9.0',  # Used to pretty print DataFrames
        'tqdm>=4.67.1',
        'pympler>=1.1',  # Use to get pickle file size.
        'openai>=1.102.0',
    ],
    extras_require=EXTRAS,
)
