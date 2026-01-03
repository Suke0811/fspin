# **fspin**
A small utility for running Python functions or coroutines at a fixed rate. It offers ROS-like rate control with optional performance reporting.

## Latest Version
[![Version](https://img.shields.io/badge/version-0.3.x-blue.svg)](https://github.com/Suke0811/fspin/releases)
[![PyPI Downloads](https://static.pepy.tech/badge/fspin)](https://pypi.org/project/fspin/)
[![Tests](https://github.com/Suke0811/fspin/actions/workflows/ci.yml/badge.svg)](https://github.com/Suke0811/fspin/actions/workflows/ci.yml)
![Coverage](coverage.svg)

---
## **Installation**
Choose one of the following methods to install the package:
To install the latest stable release, use pip: [![PyPI Downloads](https://static.pepy.tech/badge/fspin)](https://pypi.org/project/fspin/)
```bash
pip install fspin
```

### Development dependencies
To run the test suite locally, install the development requirements which include the
`pytest-asyncio` and `pytest-timeout` plugins used by the repository configuration:

```bash
pip install -r requirements-dev.txt
```

## Features
- `spin()` context manager for scoped background loops
- `@spin` decorator to easily loop sync or async functions
- `rate` / `RateControl` class for manual control
- Adjustable frequency at runtime
- Optional detailed performance reports
- Auto-detection of coroutines (no need to specify `is_async=True`)
- Support for both blocking and fire-and-forget patterns for async functions
- Threaded sync mode with optional blocking join via `wait=True` (or non-blocking with `wait=False`)

## Library Cheatsheet
A [comprehensive cheatsheet](fspin_cheatsheet.md) is available for developers and LLMs to quickly understand how to use the fspin library correctly. 
The cheatsheet includes detailed API references, common use cases, best practices, and troubleshooting guidance. 
Give this cheatsheet to your LLM, then it should be able to use and debug the library correctly.  


## Usage
```python
from fspin import spin

counter = 0

# Using a lambda function as a condition (Preferred)
@spin(freq=10, condition_fn=lambda: counter < 5)
def my_loop():
    nonlocal counter
    counter += 1
    print(f"Iteration {counter}")

my_loop() # Blocks until counter reaches 5
```

### Sync threaded: blocking vs fire-and-forget
```python
import time
from fspin import spin

counter = 0

# Fire-and-forget: returns immediately while the background thread runs
@spin(freq=50, condition_fn=lambda: counter < 5, thread=True, wait=False)
def sync_bg():
    nonlocal counter
    counter += 1

rc = sync_bg()          # returns immediately
# ... do other work ...
rc.stop_spinning()      # stop when ready

# Blocking: call does not return until condition becomes False
@spin(freq=50, condition_fn=lambda: counter < 5, thread=True, wait=True)
def sync_blocking():
    nonlocal counter
    counter += 1

counter = 0
rc2 = sync_blocking()   # blocks until 5 iterations complete
```

### Async decorator: blocking vs fire-and-forget
```python
import asyncio
from fspin import spin

# Blocking version (wait=True)
@spin(freq=2, report=True, wait=True)
async def blocking_loop():
    await asyncio.sleep(0.1)

# Fire-and-forget version (wait=False)
@spin(freq=2, report=True, wait=False)
async def non_blocking_loop():
    await asyncio.sleep(0.1)

async def run_both():
    rc1 = await blocking_loop()   # awaits completion before returning
    rc2 = await non_blocking_loop()  # returns immediately; remember to stop later
    rc2.stop_spinning()
```

### with Context-Manager
```python
import time
from fspin import spin

counter = 0

# Runs in background thread as long as counter < 5
# condition_fn uses a lambda for concise state checking
with spin(lambda: print("Beat"), freq=10, condition_fn=lambda: counter < 5) as rc:
    while rc.is_running():
        counter += 1
        time.sleep(0.1)

print(f"Loop stopped at counter={counter}")
```

Note:
- For synchronous functions with threading, pass `wait=True` to block entering the with-body until the loop completes (the internal thread is joined before returning). With `wait=False` (default here), the loop runs in the background while inside the context.
- For asynchronous functions used with `async with`, the `wait` flag is not used; the task runs while inside the context and stops on exit.
- Using a lambda for `condition_fn` is the preferred way to define simple stop conditions.
- Named functions and coroutines are also fully supported for more complex logic:
  ```python
  def complex_condition():
      # logic involving multiple variables or state
      return some_state.is_valid and counter < 10

  @spin(freq=10, condition_fn=complex_condition)
  def my_loop():
      ...
  ```
- Synchronous contexts require it to be a regular callable. For async contexts you can supply a coroutine or other awaitable predicate—fspin will await it automatically.

### Async predicates for condition_fn
```python
import asyncio
from fspin import spin

count = 0

# Async workflow using a lambda for the condition
@spin(freq=100, condition_fn=lambda: count < 3, wait=True)
async def monitored_task():
    nonlocal count
    count += 1
    print(f"Tick {count}")

async def main():
    rc = await monitored_task()
    assert count == 3
    assert rc.status == "stopped"

asyncio.run(main())
```

### Using Rate Class directly
```python
import time
from fspin import rate

# Create a rate control for a simple function
rc = rate(freq=10, is_coroutine=False, report=True, thread=True)

# Start spinning your function in background
rc.start_spinning(lambda: print("Tick"), None)

# Let it run 3 seconds
time.sleep(3)

# Stop the loop and print report
rc.stop_spinning()
```

### Async with Fire-and-Forget Pattern
```python
import asyncio
from fspin import spin

# Using the @spin decorator with wait=False for fire-and-forget
@spin(freq=10, report=True, wait=False)
async def background_task():
    print("Running in the background")
    await asyncio.sleep(0.1)

async def main():
    # This returns immediately without waiting for all iterations
    rc = await background_task()
    print("Continuing with other work while task runs in background")
    await asyncio.sleep(1)  # Do other work
    rc.stop_spinning()  # Stop the background task when done

# Using the async spin context manager
# Note: `wait` is not used for the async context manager; the loop runs while inside the context and stops on exit.
async def another_task():
    print("Another background task")
    await asyncio.sleep(0.1)

async def another_main():
    async with spin(another_task, freq=10, report=True) as sp:
        print("Context manager returned immediately")
        await asyncio.sleep(1)  # Do other work
    # Task is stopped when exiting the context
```

### More Examples
See [the examples](example/README.md) for complete synchronous and asynchronous demos.

## Performance & Accuracy

The RateControl library is designed to maintain a desired loop frequency by compensating for deviations. Here's a summary of observed performance:

- **Synchronous Mode:**  
  - Any loop frequency (10-10000 Hz) should be able to achieve high average loop precision (99.98-100%).
  - On both Windows and Linux, synchronous loops using `time.sleep()` can achieve high accuracy. For example, a loop
    targeting 1000 Hz reached an average of ~999.81 Hz with minimal deviations. 

- **Asynchronous Mode:**  
  - Using `asyncio.sleep()`, asynchronous loops are more affected by OS-level timer resolutions.  
  - **Windows:** Often limited by a timer granularity of around 15 ms, so a loop set to 500 Hz may only reach ~65 Hz. The library will automatically warn you if you set a frequency higher than 65 Hz on Windows in async mode.
  - **Linux/macOS:** Generally provides finer sleep resolution, allowing asynchronous loops to run closer to the target frequency. Linux can achieve ~925 Hz and macOS up to ~4000 Hz in async mode.

- **Python Version Differences:**  
  - On **Windows** newer Python versions like 3.12 will have better accuracy due to different implementation of time.sleep

For detailed benchmark results across different operating systems and Python versions, see our [comprehensive benchmark report](benchmark/unified_benchmark_report.md).


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


