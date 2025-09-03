# File: setup.py
# Date: 3-Oct-2018
#
# Update:
#
import re

from setuptools import find_packages
from setuptools import setup

packages = []
thisPackage = 'wwpdb.utils.nmr'

with open('wwpdb/utils/nmr/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name=thisPackage,
    version=version,
    description='wwPDB NMR utilities',
    long_description="See:  README.md",
    author='Ezra Peisach',
    author_email='ezra.peisach@rcsb.org',
    url='https://github.com/wwpdb/py-wwpdb_utils_nmr',
    #
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    #
    # munkres 1.0.12 last to support python 2. Developers did not tag properly
    install_requires=['wwpdb.utils.config ~= 0.34', 'wwpdb.utils.align',
                      # "pynmrstar ~= 2.6; python_version < '3'",
                      "pynmrstar >= 3.2; python_version >= '3'",
                      # "munkres==1.0.12; python_version == '2.7'",
                      "munkres; python_version >= '3'",
                      'mmcif', 'numpy', "scikit-learn",
                      "rmsd", "packaging", "chardet",
                      "typing_extensions",  # typing_extensions was missing from rmsd 1.5 package
                      # "antlr4-python2-runtime; python_version == '2.7'",
                      "antlr4-python3-runtime ~= 4.13.0; python_version >= '3'",
                      "striprtf",
                      "datetime"],
    packages=find_packages(exclude=['wwpdb.utils.tests-nmr', 'wwpdb.utils.tests-nmr-tox', 'mock-data']),
    # Enables Manifest to be used
    include_package_data=True,
    package_data={
        # If any package contains *.md or *.rst ...  files, include them:
        '': ['*.md', '*.rst', "*.txt", "*.cfg"],
    },
    #
    # These basic tests require no database services -
    test_suite="wwpdb.utils.tests-nmr",
    tests_require=['tox'],
    #
    # Not configured ...
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    python_requires='>=3.6',
    command_options={
        'build_sphinx': {
            'project': ('setup.py', thisPackage),
            'version': ('setup.py', version),
            'release': ('setup.py', version)
        }
    },
    # This setting for namespace package support -
    zip_safe=False,
)
