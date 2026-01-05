# fspin Library Cheatsheet for LLMs

## Overview

fspin is a Python library for running functions at a specified frequency (rate control). It provides tools to execute functions repeatedly at a consistent rate, with support for both synchronous and asynchronous functions. The library is useful for tasks that need to run at a specific frequency, such as simulation loops, polling operations, or any periodic task.

## Key Features

- Run functions at a specified frequency (Hz)
- Support for both synchronous and asynchronous functions
- Lambda support for condition functions
- Automatic detection of function type (sync vs async)
- Multiple execution modes: blocking, threaded, and fire-and-forget
- Performance reporting and statistics
- Dynamic frequency adjustment
- Exception handling and logging

## Main Components

### 1. `@spin` Decorator

The primary way to use fspin is through the `@spin` decorator, which automatically runs a function at the specified frequency.

```python
from fspin import spin

# Sync function examples
@spin(freq=10, condition_fn=None, report=False, thread=True, wait=False)
def my_function_non_blocking():
    # Runs at 10Hz in a background thread and returns immediately (fire-and-forget)
    print("Hello")

@spin(freq=10, condition_fn=None, report=False, thread=True, wait=True)
def my_function_blocking():
    # Runs at 10Hz in a background thread but the call blocks until completion (thread join)
    print("Hello")

# Async function examples
@spin(freq=5, report=True, wait=True)
async def my_async_function_blocking():
    # Runs at 5Hz; awaiting the decorated function blocks until completion
    print("Async hello")
    await asyncio.sleep(0.01)

@spin(freq=5, report=True, wait=False)
async def my_async_function_non_blocking():
    # Runs at 5Hz and returns immediately (fire-and-forget); remember to stop later
    print("Async hello")
    await asyncio.sleep(0.01)
```

### 2. `spin` Context Manager

The context manager provides a way to run a function at a specified frequency within a specific scope. Using lambdas for the condition function is preferred for simple logic.

```python
# For synchronous functions (threaded, fire-and-forget)
# Preferred usage with lambda condition
count = 0
with spin(my_function, freq=10, condition_fn=lambda: count < 5) as rc:
    while rc.is_running():
        count += 1
        time.sleep(0.1)

# For synchronous functions (threaded, blocking)
# When wait=True, entering the with-body is delayed until the loop finishes.
with spin(my_function, freq=10, thread=True, wait=True, condition_fn=lambda: count < 10) as rc:
    # By the time we get here, the loop has already completed.
    pass

# For asynchronous functions (always runs in background while inside the context)
async with spin(my_async_function, freq=5, condition_fn=lambda: count < 15) as rc:
    # Function runs in the background at 5Hz
    await asyncio.sleep(1)  # Let it run for 1 second
# Function stops when exiting the context or when condition becomes False
```

### 3. `rate` / `RateControl` Class

For more manual control, you can use the `RateControl` class directly (or its alias `rate`).

```python
from fspin import rate

# For synchronous functions
rc = rate(freq=10, is_coroutine=False, report=True, thread=True)
rc.start_spinning(my_function, condition_fn=None)
time.sleep(1)  # Let it run for 1 second
rc.stop_spinning()

# For asynchronous functions
rc = rate(freq=5, is_coroutine=True, report=True)
await rc.start_spinning_async(my_async_function, condition_fn=None)
await asyncio.sleep(1)  # Let it run for 1 second
rc.stop_spinning()
```

## API Reference

### `@spin` Decorator

```python
@spin(freq, condition_fn=None, report=False, thread=False, wait=False)
```

- `freq` (float): Target frequency in Hz (cycles per second)
- `condition_fn` (callable or coroutine, optional): Predicate evaluated before each iteration. For synchronous functions it must
  be a regular callable returning a truthy value. For async functions it may be a regular callable or coroutine; awaitable
  results are awaited automatically.
- `report` (bool): When True, performance statistics are recorded and printed
- `thread` (bool): For sync functions, if True, runs in a background thread
- `wait` (bool): For async functions, if True, awaits completion; if False (default), returns immediately. For sync threaded functions, if True, joins the thread; default is False (fire-and-forget).

Returns:
- The decorated function returns a `RateControl` instance. For async with `wait=False`, it returns immediately while running; for async with `wait=True`, it returns after completion (stopped). For sync with `thread=True, wait=False`, it returns immediately while running; with `wait=True` or `thread=False`, it returns after completion.

### `spin` Context Manager

```python
# For synchronous functions
with spin(func, freq, *args, condition_fn=None, report=False, thread=True, wait=False, **kwargs) as rc:
    # rc is a RateControl instance
    ...

# For asynchronous functions
async with spin(async_func, freq, *args, condition_fn=None, report=False, **kwargs) as rc:
    # rc is a RateControl instance
    ...
```

- `func` (callable): The function to execute at the specified frequency
- `freq` (float): Target frequency in Hz
- `*args` / `**kwargs`: Additional positional and keyword arguments forwarded to the worker
- `condition_fn` (callable or coroutine, optional): Predicate evaluated before each iteration. Sync contexts require a regular
  callable; async contexts accept coroutine/awaitable predicates that are awaited automatically.
- `report` (bool): When True, performance statistics are recorded and printed
- `thread` (bool): For sync functions, if True (default), runs in a background thread
- `wait` (bool, sync only): When `thread=True` and `wait=True`, entering the with-body is blocked until the loop completes (the internal thread is joined before returning). When `wait=False`, the body executes while the loop runs in the background. For async functions used with `async with`, `wait` is not applicable; the loop runs while inside the context and is stopped on exit.

Returns:
- A `RateControl` instance that can be used to control the spinning process

### `rate` / `RateControl` Class

```python
rc = rate(freq, is_coroutine=False, report=False, thread=True)
```

- `freq` (float): Target frequency in Hz
- `is_coroutine` (bool): Whether the target function is a coroutine
- `report` (bool): When True, performance statistics are recorded and printed
- `thread` (bool): For sync functions, if True, runs in a background thread

Important methods:
- `start_spinning(func, condition_fn=None, *args, **kwargs)`: Start the spinning process
- `start_spinning_sync(func, condition_fn, *, wait=False, **kwargs)`: Sync start; if `thread=True` and `wait=True`, joins the thread before returning (blocking). If `thread=False`, runs in the current thread (blocking by definition). The condition must be a regular callable.
- `start_spinning_async(func, condition_fn, **kwargs)`: Async start; returns an asyncio.Task immediately (fire-and-forget). Async conditions (coroutines or other awaitables) are awaited before each iteration.
- `start_spinning_async_wrapper(func, condition_fn=None, *, wait=False, **kwargs)`: Async helper that can be `await`ed. If `wait=True`, it awaits the task to completion (blocking the caller coroutine) and returns the RateControl; otherwise returns the Task. Async predicates are awaited automatically.
- `stop_spinning()`: Stop the spinning process
- `get_report(output=True)`: Generate and optionally print a performance report
- `is_running()`: Check if the spinning process is running

Important properties:
- `frequency` (float): Get or set the target frequency in Hz
- `elapsed_time` (float): Time elapsed since start in seconds
- `exception_count` (int): Number of exceptions raised during execution
- `mode` (str): Current execution mode ("async", "sync-threaded", or "sync-blocking")
- `status` (str): Current status ("running" or "stopped")

### Blocking vs fire-and-forget (wait) quick reference

- Sync + thread=True + wait=False:
  - Starts a background thread and returns immediately (fire-and-forget). Use context manager or call `rc.stop_spinning()` to stop.
- Sync + thread=True + wait=True:
  - Starts a background thread but blocks the caller until the loop completes (internally joins the thread before returning). In a `with spin(..., wait=True)` context, the with-body executes only after completion.
- Sync + thread=False:
  - Always blocks in the current thread until completion (no background thread).
- Async decorator with wait=False:
  - `await decorated()` returns a RateControl immediately while the task continues running in the background. Remember to stop later.
- Async decorator with wait=True:
  - `await decorated()` awaits the internal task to completion and returns after it finishes.
- Async context manager (async with spin(...)):
  - Starts the task when entering the context, runs while inside, and stops on exit. The `wait` flag is not used here.

## Common Use Cases

### 1. Run a function at a fixed rate

```python
@spin(freq=10)
def heartbeat():
    print("Beat")

rc = heartbeat()  # Starts running at 10Hz
time.sleep(5)     # Let it run for 5 seconds
rc.stop_spinning()  # Stop the function
```

### 2. Run a function until a condition is met (Prefer Lambdas)

```python
counter = 0

# Using a lambda function as a condition (Preferred)
@spin(freq=2, condition_fn=lambda: counter < 5, report=True)
def limited_loop():
    nonlocal counter
    counter += 1
    print(f"Iteration {counter}")

rc = limited_loop()  # Runs for 5 iterations then stops
# Report is generated automatically when report=True
```

Async workflows can use lambda predicates as well:

```python
import asyncio
from fspin import spin

count = 0

@spin(freq=50, condition_fn=lambda: count < 4, wait=True)
async def async_limited_loop():
    nonlocal count
    count += 1
    print(f"Async tick {count}")

async def main():
    rc = await async_limited_loop()  # Stops once count reaches 4
    assert count == 4
    assert rc.status == "stopped"

asyncio.run(main())
```

### 3. Run an async function in the background (fire-and-forget)

```python
@spin(freq=2, wait=False, report=True)
async def background_task():
    print("Running in the background")
    await asyncio.sleep(0.1)

# This returns immediately without waiting for all iterations
rc = await background_task()

# Continue with other work
print("Continuing with other work while task runs in background")
await asyncio.sleep(3)

# Clean up when done
rc.stop_spinning()
```

### 3b. Synchronous threaded: blocking vs fire-and-forget

```python
counter = {"n": 0}

def cond():
    return counter["n"] < 5

# Fire-and-forget: returns immediately while the background thread runs
@spin(freq=50, condition_fn=cond, thread=True, wait=False)
def sync_bg():
    counter["n"] += 1

rc = sync_bg()          # returns immediately
# ... do other work ...
rc.stop_spinning()      # stop when ready

# Blocking: call does not return until cond() becomes False
@spin(freq=50, condition_fn=cond, thread=True, wait=True)
def sync_blocking():
    counter["n"] += 1

counter["n"] = 0
rc2 = sync_blocking()   # blocks until 5 iterations complete
```

### 3c. Async manual: explicit blocking with wrapper

```python
rc = rate(freq=5, is_coroutine=True)

async def work():
    ...

# Block until loop finishes
await rc.start_spinning_async_wrapper(work, wait=True)
# Returns the RateControl after completion

# Or fire-and-forget
task = await rc.start_spinning_async_wrapper(work, wait=False)
# task is an asyncio.Task; remember to stop later with rc.stop_spinning()
```

### 4. Change frequency at runtime

```python
rc = rate(freq=2, is_coroutine=False, report=True, thread=True)
rc.start_spinning(my_function)
time.sleep(2)
print("Changing frequency to 4 Hz")
rc.frequency = 4  # Dynamically change the frequency
time.sleep(2)
rc.stop_spinning()
```

### 5. Use with context manager

```python
def heartbeat():
    print("Beat")

# Runs in a background thread for 1 second
with spin(heartbeat, freq=5, report=True) as rc:
    time.sleep(1)
# Automatically stops when exiting the context
```

## Best Practices and Warnings

### 1. Choose the right execution mode

- For CPU-bound tasks: Use synchronous mode with `thread=True` for better performance
- For I/O-bound tasks: Use asynchronous mode for better efficiency
- For high-frequency tasks (>100Hz): Synchronous mode generally performs better

### 2. Platform-specific limitations

- Windows: Async mode is limited to ~65Hz due to timer resolution
- Linux: Async mode is limited to ~925Hz due to timer resolution
- macOS: Async mode is limited to ~4000Hz due to timer resolution

### 3. Exception handling

- Exceptions in the target function are caught and logged
- The function continues to run even if exceptions occur
- Check `rc.exception_count` or `rc.exceptions` to monitor errors

### 4. Performance reporting

- Enable `report=True` to get detailed performance statistics
- Use `rc.get_report()` to generate a report manually
- Reports include actual frequency achieved, deviations, and function execution time

### 5. Type matching

- Ensure you use synchronous functions with `is_coroutine=False`
- Ensure you use asynchronous functions with `is_coroutine=True`
- The library will raise TypeError if there's a mismatch

### 6. Prefer Lambda Functions for Conditions

- Use lambda functions for simple `condition_fn` logic to keep code concise.
- Example: `condition_fn=lambda: counter < 10`
- **Named functions and coroutines** are also supported and recommended for more complex state checks that don't fit in a single line.
- Remember to use `nonlocal` if the lambda or inner function checks a variable modified inside the looped function.

### 7. Context manager syntax

- For synchronous functions: Use `with spin(...)`
- For asynchronous functions: Use `async with spin(...)`
- Using the wrong syntax will raise TypeError

## Edge Cases and Troubleshooting

### 1. Function takes longer than the cycle time

If your function takes longer to execute than the cycle time (1/freq), the actual frequency will be lower than requested. The library will try to compensate, but cannot achieve the target frequency.

```python
# This function takes 0.2s but we want to run at 10Hz (0.1s cycle time)
@spin(freq=10, report=True)
def slow_function():
    time.sleep(0.2)  # Too slow for 10Hz
    print("Tick")

# The report will show the actual frequency achieved (around 5Hz)
```

### 2. Very high frequencies

For very high frequencies (>1000Hz), be aware of:
- System timer resolution limitations
- CPU overhead of the rate control mechanism
- Use synchronous mode with thread=False for best performance at high frequencies

### 3. Memory usage with long-running tasks

For long-running tasks with `report=True`, memory usage can grow due to storing timing data. Consider:
- Periodically stopping and restarting the spinning process
- Using `report=False` for very long-running tasks

### 4. Cleanup in fire-and-forget mode

When using async functions with `wait=False`, always call `stop_spinning()` when done:

```python
@spin(freq=10, wait=False)
async def background_task():
    print("Background work")

rc = await background_task()  # Returns immediately
# ... do other work ...
rc.stop_spinning()  # Important cleanup!
```

## Import Patterns

```python
# Recommended import pattern
from fspin import spin, rate

# Alternative import patterns
from fspin import RateControl  # Direct import of the class
from fspin.decorators import spin  # Import specific module
from fspin.rate_control import RateControl  # Import from specific module
```

Remember that fspin automatically detects whether your function is synchronous or asynchronous, but you must use the appropriate syntax (with/async with) for context managers.
