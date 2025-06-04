# Examples

This directory contains simple usage examples for **fspin**. Each example demonstrates using `RateControl` either via the `@spin` decorator or by directly creating the class. Both synchronous and asynchronous approaches are shown.

| File | Description |
| ---- | ----------- |
| `sync_decorator.py` | Run a synchronous function at a fixed rate using the `@spin` decorator. |
| `sync_manual.py`    | Use `RateControl` directly with a synchronous function. |
| `async_decorator.py`| Run an asynchronous coroutine with the decorator. |
| `async_manual.py`   | Use `RateControl` directly with an async coroutine. |

Run any example with `python <file>` to see the behaviour.

Note that the scripts modify `sys.path` so they work when executed directly from
this repository without installation.
