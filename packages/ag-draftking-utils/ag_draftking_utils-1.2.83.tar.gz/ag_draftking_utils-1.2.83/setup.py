from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Read version from __version__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'ag_draftking_utils', '__version__.py')
    with open(version_file) as f:
        version_line = next(line for line in f if line.startswith('__version__'))
        delim = '"' if '"' in version_line else "'"
        return version_line.split(delim)[1]

VERSION = "1.2.83"
DESCRIPTION = 'AG Draftking Utilities'
LONG_DESCRIPTION = 'Simple Utility Functions called in most places'

# Setting up
setup(
    name="ag_draftking_utils",
    version=VERSION,
    author="no thanks",
    author_email="giantsrule93@yahoo.com>",
    url="https://github.com/akashgoyal119/DraftKingUtils",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'pymysql',
        'selenium==3.141.0',
        ### packages needed but ones we don't want to include in build
        ### due to a large file size... 
        #'boto3',
        #'pandas',
        #'sklearn',
        #'lightgbm'
    ],
    keywords=['python', 'sql'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)