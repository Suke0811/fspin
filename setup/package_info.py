PACKAGE_NAME = 'fspin'
PACKAGE_AUTHOR = 'Yusuke Tanaka'
PACKAGE_DESCRIPTION = 'ROS like rate control through python decorator'
REPOSITORY_NAME = 'fspin'



PYTHON_REQUIRES = '>=3.7, <4.0'  # Specify Python version compatibility
CLASSIFIERS = [
    'Framework :: Robot Framework',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
]

######################################
# we need setuptools_scm for tag/commit based auto versioning
SETUP_REQUIRES = ["setuptools_scm"]
