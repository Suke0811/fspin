# **fspin**
ROS like rate control through python decorator

## Latest Version 
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/Suke0811/fspin/releases), [![PyPI Downloads](https://static.pepy.tech/badge/fspin)](https://pypi.org/project/fspin/)


## Usage

```python
import time
from fspin import spin


@spin(freq=1000, report=True)
def function_to_loop():
  # things to loop
  time.sleep(0.0005) # a fake task to take 0.5ms

  
# call the function
function_to_loop() # this will be blocking, and start looping
# it'll automatically catch the keyboard interrupt
# we have async version too
```

See [the examples](example/README.md) for complete synchronous and asynchronous demos.

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
To install the latest stable release using pip. [![PyPI Downloads](https://static.pepy.tech/badge/fspin)](https://pypi.org/project/fspin/)
```bash
pip install fspin
````


