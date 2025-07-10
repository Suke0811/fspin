# Examples

This directory contains simple usage examples for **fspin**. Each example demonstrates using `RateControl` either via the `@spin` decorator or by directly creating the class. Both synchronous and asynchronous approaches are shown.

| File                   | Description                                                 |
|------------------------|-------------------------------------------------------------|
| `sync_decorator.py`    | Run a synchronous function at a fixed rate using the `@spin` decorator. |
| `sync_manual.py`       | Use `rate` directly with a synchronous function.            |
| `async_decorator.py`   | Run an asynchronous coroutine with the decorator.           |
| `async_manual.py`      | Use `rate` directly with an async coroutine.                |
| `loop_in_place.py`     | Use context manager `with loop(...):`.                      |
| `dynamic_frequency.py` | Change the loop frequency at runtime.                       |

Run any example with `python <file>` to see the behaviour.

Note that the scripts modify `sys.path` so they work when executed directly from this repository without installation.

---

## Library Cheatsheet

Below is a reference for the main classes and helpers provided by `fspin`.
You can copy‑paste this section into a large language model to get help or quick reminders when using the library.

### `spin`

```python
@spin(freq, condition_fn=None, report=False, thread=False)
```

- Decorator that repeatedly calls the decorated function at `freq` Hz.
- Automatically detects synchronous vs. asynchronous functions.
- `condition_fn` *(optional)* – function returning `True` to keep looping.
- `report` – when `True`, execution statistics are recorded and printed when the loop stops.
- `thread` – if `True`, synchronous functions run in a background thread so the call immediately returns.

### `loop`

```python
with loop(func, freq, condition_fn=None, report=False, thread=True, *args, **kwargs) as rc:
    ...
```

- Context manager that starts `func` looping on entry and automatically stops on exit.
- Provides the same options as `spin` but always runs in the background.
- The returned object `rc` is an instance of `RateControl` which can be queried or manually stopped.

### `rate` / `RateControl`

```python
rc = rate(freq, is_coroutine=False, report=False, thread=True)
```

`rate` is an alias for the `RateControl` class which offers manual control.
Important methods and properties include:

- `start_spinning(func, condition_fn=None, *args, **kwargs)` – begin the loop.
- `stop_spinning()` – request the loop to stop.
- `frequency` *(property)* – get or set the target frequency in Hz at runtime.
- `is_running()` – return `True` if the loop is active.
- `elapsed_time` *(property)* – seconds since `start_spinning` was called.
- `get_report(output=True)` – return performance stats and optionally print them.
- `exception_count` *(property)* – number of exceptions raised by the looped function.
- `mode` *(property)* – indicates if running in async, sync-threaded, or sync-blocking mode.
- String representation (`str(rc)`) summarises the current status.

Use `rate` when you need to start and stop spinning manually or change the frequency while running.

---
