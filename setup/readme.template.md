# **<PACKAGE_NAME>**
<PACKAGE_DESCRIPTION>

## Latest Version 
### [![Version](https://img.shields.io/badge/version-<PACKAGE_VERSION>-blue.svg)](https://github.com/<USERNAME>/<REPOSITORY_NAME>/releases)



## Performance & Accuracy

The RateControl library is designed to maintain a desired loop frequency by compensating for deviations. Here’s a summary of observed performance:

- **Synchronous Mode:**  
  - On both Windows and Linux, synchronous loops using `time.sleep()` can achieve high accuracy. For example, a loop targeting 1000 Hz reached an average of ~999.81 Hz with minimal deviations.

- **Asynchronous Mode:**  
  - Using `asyncio.sleep()`, asynchronous loops are more affected by OS-level timer resolutions.  
  - **Windows:** Often limited by a timer granularity of around 15 ms, so a loop set to 500 Hz may only reach ~65 Hz.  
  - **Linux:** Generally provides finer sleep resolution, allowing asynchronous loops to run closer to the target frequency.

- **Python Version Differences:**  
  - On **Windows** newer Python versions like 3.12 will have better accuracy due to different implementation of time.sleep


### Report Example
```bash
2025-02-14 13:21:12,281 - 
=== RateControl Report ===
2025-02-14 13:21:12,281 - Set Frequency                  : 1000 Hz
2025-02-14 13:21:12,281 - Set Loop Duration              : 1.000 ms
2025-02-14 13:21:12,281 - Initial Function Duration      : 0.531 ms
2025-02-14 13:21:12,281 - Total Duration                 : 3.000 seconds
2025-02-14 13:21:12,281 - Total Iterations               : 2995
2025-02-14 13:21:12,281 - Average Frequency              : 999.83 Hz
2025-02-14 13:21:12,281 - Average Function Duration      : 0.534 ms
2025-02-14 13:21:12,281 - Average Loop Duration          : 1.000 ms
2025-02-14 13:21:12,281 - Average Deviation from Desired : 0.000 ms
2025-02-14 13:21:12,281 - Maximum Deviation              : 0.535 ms
2025-02-14 13:21:12,281 - Std Dev of Deviations          : 0.183 ms
2025-02-14 13:21:12,281 - 
Distribution of Deviation from Desired Loop Duration (ms):
2025-02-14 13:21:12,282 - -0.499 - -0.396 ms | ████████ (388)
-0.396 - -0.292 ms |  (17)
-0.292 - -0.189 ms |  (0)
-0.189 - -0.085 ms |  (0)
-0.085 - 0.018 ms | █ (60)
0.018 - 0.122 ms | ██████████████████████████████████████████████████ (2319)
0.122 - 0.225 ms | ████ (210)
0.225 - 0.328 ms |  (0)
0.328 - 0.432 ms |  (0)
0.432 - 0.535 ms |  (2)
2025-02-14 13:21:12,282 - ===========================
```


---
## **Installation**
Choose one of the following methods to install the package:

### **1. Install from PyPI**
To install the latest stable release from [PyPI](https://pypi.org/):
```bash
pip install <PACKAGE_NAME>
````

### **2. Install from GitHub**
```bash
pip install git+https://github.com/<USERNAME>/<REPOSITORY_NAME>.git
```
#### a) Install from a Specific Branch
To install from a specific branch:
```bash
pip install git+https://github.com/<USERNAME>/<REPOSITORY_NAME>.git@<branch-name>
```

#### b) Install from a Specific Commit
To install from a specific commit:
```bash
pip install git+https://github.com/<USERNAME>/<REPOSITORY_NAME>.git@<commit-hash>
```

#### Install from a Specific Tag
To install from a specific tag:
```bash
pip install git+https://github.com/<USERNAME>/<REPOSITORY_NAME>.git@<tag>
```

### **3. Install from Local or Submodule Repository**
If you have cloned the repository locally:
#### a) Install from the current directory:

```bash
pip install .
```
#### b) Install from a specific local path:
```bash
pip install /path/to/setup_py_folder/
```

### **4. Install in Developer Mode**
#### a) Install from the current directory:
```bash
pip install -e .
```
#### b) Install from a specific local path:
```bash
pip install -e /path/to/setup_py_folder/
```

