#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: koo <my_email@gmail.com>
"""

import importlib.util
import os
from pathlib import Path
from setuptools import setup, find_packages
from codecs import open  # Use a consistent encoding.
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the base version from the library.  (We'll find it in the `version.py`
# file in the src directory, but we'll bypass actually loading up the library.)
vspec = importlib.util.spec_from_file_location(
  "version",
  str(Path(__file__).resolve().parent /
      'brn'/"version.py")
)
vmod = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, '__version__')

# If the environment has a build number set...
if os.getenv('buildnum') is not None:
    # ...append it to the version.
    version = "{version}.{buildnum}".format(
        version=version,
        buildnum=os.getenv('buildnum')
    )

setup(
    name='brn',
    description="This is my click command-line app project.",
    long_description=long_description,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=version,
    install_requires=[
        # Include dependencies here
        'click>=7.0,<8',
        'agraph-python',
		'agraph-python==101.0.6',
		#'alabaster==0.7.12',
		#'appdirs==1.4.4',
		#'attrs==20.2.0',
		#'Babel==2.8.0',
		#'bleach==3.2.1',
		#'#-e git+git@github.com:koo5/brn.git@2ae14633d27d6a0f22f3edbecfe12477c5bcb415#egg=brn&subdirectory=brn',
		#'cachetools==4.1.1',
		#'certifi==2020.6.20',
		#'cffi==1.14.2',
		#'chardet==3.0.4',
		#'colorama==0.4.3',
		#'coverage==5.3',
		#'cryptography==3.1',
		#'distlib==0.3.1',
		#'docutils==0.16',
		#'filelock==3.0.12',
		#'flake8==3.8.3',
		#'flake8-docstrings==1.5.0',
		#'frozendict==1.2',
		#'future==0.18.2',
		#'idna==2.10',
		#'imagesize==1.2.0',
		#'iniconfig==1.0.1',
		#'iso8601==0.1.13',
		#'jeepney==0.4.3',
		#'Jinja2==2.11.2',
		#'keyring==21.4.0',
		#'lxml==4.5.2',
		#'MarkupSafe==1.1.1',
		#'mccabe==0.6.1',
		#'more-itertools==8.5.0',
		#'mypy==0.782',
		#'mypy-extensions==0.4.3',
		#'packaging==20.4',
		#'pip-check-reqs==2.1.1',
		#'pip-licenses==2.3.0',
		#'pkginfo==1.5.0.1',
		#'pluggy==0.13.1',
		#'PTable==0.9.2',
		#'py==1.9.0',
		#'pycodestyle==2.6.0',
		#'pycparser==2.20',
		#'pydocstyle==5.1.1',
		#'pyflakes==2.2.0',
		#'Pygments==2.7.1',
		'PyLD==2.0.3',
		#'pyparsing==2.4.7',
		#'pytest==6.0.2',
		#'pytest-cov==2.10.1',
		#'pytest-pythonpath==0.7.3',
		#'pytz==2020.1',
		#'readme-renderer==26.0',
		'requests==2.24.0',
		#'requests-toolbelt==0.9.1',
		#'rfc3986==1.4.0',
		#'SecretStorage==3.1.2',
		#'six==1.15.0',
		#'snowballstemmer==2.0.0',
		#'Sphinx==3.2.1',
		#'sphinxcontrib-applehelp==1.0.2',
		#'sphinxcontrib-devhelp==1.0.2',
		#'sphinxcontrib-htmlhelp==1.0.3',
		#'sphinxcontrib-jsmath==1.0.1',
		#'sphinxcontrib-qthelp==1.0.3',
		#'sphinxcontrib-serializinghtml==1.1.4',
		#'toml==0.10.1',
		#'tox==3.20.0',
		#'tqdm==4.49.0',
		#'twine==3.2.0',
		#'typed-ast==1.4.1',
		#'typing-extensions==3.7.4.3',
		#'urllib3==1.25.10',
		#'virtualenv==20.0.31',
		#'webencodings==0.5.1',



    ],
    entry_points="""
    [console_scripts]
    brn=brn.cli:cli
    """,
    python_requires=">=0.0.1",
    license='GPLv3',
    author='koo',
    author_email='my_email@gmail.com',
    # Use the URL to the github repo.
    url= 'https://github.com/koo5/brn',
    download_url=(
        f'https://github.com/koo5/'
        f'brn/archive/{version}.tar.gz'
    ),
    keywords=[
        # Add package keywords here.
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 3 - Alpha',

      # Indicate who your project is intended for.
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Libraries',

      # Pick your license.  (It should match "license" above.)
        # noqa
      '''License :: OSI Approved :: GPLv3 License''',
        # noqa
      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True
)
