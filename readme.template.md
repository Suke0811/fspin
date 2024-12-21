# **<PACKAGE_NAME>**
<PACKAGE_DESCRIPTION>

#### Example Badges:

[![PyPI version](https://img.shields.io/pypi/v/<PACKAGE_NAME>.svg)](https://pypi.org/project/<PACKAGE_NAME>/)
[![Python versions](https://img.shields.io/pypi/pyversions/<PACKAGE_NAME>.svg)](https://pypi.org/project/<PACKAGE_NAME>/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/<USERNAME>/<REPOSITORY_NAME>/build.yml?branch=main)](https://github.com/<USERNAME>/<REPOSITORY_NAME>/actions)
[![License](https://img.shields.io/pypi/l/<PACKAGE_NAME>.svg)](LICENSE)

---

## **Installation**

Choose one of the following methods to install the package:

---

### **1. Install from PyPI**
To install the latest stable release from [PyPI](https://pypi.org/):
```bash
pip install <PACKAGE_NAME>
````

### 2. Install from GitHub
```bash
pip install git+https://github.com/<USERNAME>/<repository-name>.git
```
#### Install from a Specific Branch
To install from a specific branch:
```bash
pip install git+https://github.com/<USERNAME>/<REPOSITORY_NAME>.git@<branch-name>
```

#### Install from a Specific Commit
To install from a specific commit:
```bash
pip install git+https://github.com/<USERNAME>/<repository-name>.git@<commit-hash>
```

#### Install from a Specific Tag
To install from a specific tag:
```bash
pip install git+https://github.com/<USERNAME>/<repository-name>.git@<tag>
```

### 3. Install from Local or Submodule Repository
If you have cloned the repository locally:
#### a) Install from the current directory:


```bash
pip install .
```
#### b) Install from a specific local path:
```bash
pip install /path/to/setup_py_folder/
```

### 4. Install in Developer Mode
#### a) Install from the current directory:
```bash
pip install -e .
```
#### b) Install from a specific local path:
```bash
pip install -e /path/to/setup_py_folder/
```
