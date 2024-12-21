PACKAGE_NAME = 'template-pip-repo'
PACKAGE_AUTHOR = 'Yusuke Tanaka'
PACKAGE_DESCRIPTION = 'Pip installable lib'
REPOSITORY_NAME = 'template-pip-repo'



PYTHON_REQUIRES = '>=3.7, <4.0'  # Specify Python version compatibility
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Robot Framework',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
]

######################################
# we need setuptools_scm for tag/commit based auto versioning
SETUP_REQUIRES = ["setuptools_scm"]
