from setuptools import setup, find_packages
import sys
sys.path.append(".")
import codecs
import os
from setup.package_info import PACKAGE_NAME, PACKAGE_AUTHOR, PACKAGE_DESCRIPTION, PYTHON_REQUIRES, CLASSIFIERS, SETUP_REQUIRES

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r', encoding='utf-8') as fp:
        return fp.read()

# Read the README.md file
long_description = read('readme.md')

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name=PACKAGE_NAME,
    use_scm_version={"fallback_version": "0.0.0"},
    setup_requires=SETUP_REQUIRES,
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=PACKAGE_AUTHOR,
    url="https://github.com/Suke0811/fspin",
    project_urls={
        "Source": "https://github.com/Suke0811/fspin",
        "Tracker": "https://github.com/Suke0811/fspin/issues",
    },
    license='MIT',
    packages=find_packages(include=[PACKAGE_NAME, PACKAGE_NAME + '.*']),
    install_requires=requirements,
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
)
