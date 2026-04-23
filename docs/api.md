# API Reference

This page summarizes the callable surface of **fspin**, including decorator usage, the context manager, and the underlying `RateControl` class.

## Unified `spin`

The top-level `spin` exported by `fspin` is a unified entry point that behaves as either a decorator or a context manager depending on how it is invoked:

- `@spin(freq=10)` wraps a function or coroutine and runs it at the given frequency when called. 
- `with spin(func, freq=10):` or `async with spin(func, freq=10):` starts looping immediately upon entering the context and stops on exit. 

### Decorator signature

```python
from fspin import spin

@spin(freq, condition_fn=None, report=False, thread=False, wait=False)
def worker(...):
    ...
```

Parameters:

- **freq (float)**: Target frequency in Hz. 
- **condition_fn (callable or coroutine, optional)**: Predicate evaluated before each iteration. Sync workers must provide a regular callable; async workers may supply a callable or coroutine and awaitable results are handled automatically. Defaults to always continue. 
- **report (bool)**: Enable performance reporting. 
- **thread (bool)**: For synchronous functions, run in a separate thread instead of blocking the caller. 
- **wait (bool)**:
  - Async: whether to await the created task (blocking) or return immediately (fire-and-forget). 
  - Sync threaded: whether to join the background thread before returning. 

Returns the managing `RateControl` instance. 

### Context manager signature

```python
from fspin import spin

with spin(func, freq, *func_args, condition_fn=None, report=False, thread=True, wait=False, **func_kwargs) as rc:
    ...

# or async with for coroutines
```

Arguments mirror the decorator, but positional and keyword arguments after `freq` are forwarded to the worker each iteration. For synchronous workers, `wait=True` blocks entering the context body until the loop completes; asynchronous contexts ignore `wait` and stop on exit. 

A deprecated alias `loop` provides the same behaviour with a warning. 

## `RateControl`

```python
from fspin import rate
rc = rate(freq, is_coroutine, report=False, thread=True)
```

Constructor arguments:

- **freq (float)**: Desired frequency in Hz (must be > 0). 
- **is_coroutine (bool)**: Whether the target callable is async. 
- **report (bool)**: Collect metrics for reporting. 
- **thread (bool)**: For synchronous functions, run in a background thread instead of blocking. 

Key attributes available after creation and during execution:

- **loop_duration**: Desired loop duration in seconds. 
- **report**: Whether reporting is enabled. 
- **thread**: Whether threading is used for synchronous functions. 
- **exceptions**: List of exceptions seen while spinning. 
- **status**: Current status (`"running"` or `"stopped"`). 
- **mode**: Execution mode (`"async"`, `"sync-threaded"`, or `"sync-blocking"`). 
- **frequency**: Current target frequency in Hz; settable to adjust runtime rate. 
- **elapsed_time**: Seconds since the loop started. 
- **exception_count**: Number of exceptions encountered. 

### Starting and stopping loops

- **start_spinning(func, condition_fn, *args, **kwargs)**: Dispatches to async or sync execution depending on `is_coroutine`. Returns an `asyncio.Task`, `threading.Thread`, or `None` depending on mode. 
- **start_spinning_sync(func, condition_fn, *args, wait=False, **kwargs)**: Run synchronously, optionally on a background thread when `thread=True`; joins the thread if `wait=True`. 
- **start_spinning_async(func, condition_fn, *args, **kwargs)**: Create an asyncio task that awaits the worker each iteration. 
- **start_spinning_async_wrapper(func, condition_fn=None, wait=False, **kwargs)**: Convenience wrapper to await completion (`wait=True`) or return immediately (`wait=False`). 
- **stop_spinning()**: Signal the loop to stop and join or cancel underlying execution where appropriate. 

### Reporting and status

- **get_report(output=True)**: Aggregate performance data (frequency, loop durations, deviations, iterations, and exceptions) and print a formatted report when `output=True`. Returns a dictionary of metrics. 
- **is_running()**: Boolean indicating if the loop is still active. 
- **__str__() / __repr__()**: Human- and developer-friendly representations summarizing mode, frequency, durations, and counters. 

## Reporting helpers

`ReportLogger` handles terminal-friendly output and histogram generation for deviation data when reporting is enabled. Users typically access it indirectly via `RateControl.get_report()`, but it is available at `fspin.reporting.ReportLogger` for advanced customization. 
