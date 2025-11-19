# fspin

**fspin** provides ROS-like rate control for Python functions and coroutines so they execute at a consistent frequency. The library automatically detects whether a callable is synchronous or asynchronous and runs it with optional threading support, run-time frequency adjustments, and performance reporting.

## Features

- Spin functions at a target frequency with optional performance reports and deviation compensation. 
- Use the unified `spin` entry point as a decorator or as a context manager for both sync and async callables. 
- Adjust loop frequency during execution while inspecting current status and elapsed time. 
- Support both blocking usage and fire-and-forget patterns for threaded or asynchronous workloads. 

## Quickstart

Create a loop that runs a synchronous function in a background thread at 1 kHz and prints a report:

```python
import time
from fspin import spin

@spin(freq=1000, report=True)
def function_to_loop():
    # things to loop
    time.sleep(0.0005)  # a fake task to take 0.5ms

# call the function
function_to_loop()  # this will be blocking, and start looping
# it'll automatically catch the keyboard interrupt
```

For an asynchronous worker, you can block or return immediately:

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
    rc1 = await blocking_loop()      # awaits completion before returning
    rc2 = await non_blocking_loop()  # returns immediately; remember to stop later
    rc2.stop_spinning()
```

See the [Usage Examples](usage.md) for more scenarios and the [API Reference](api.md) for complete argument details.
