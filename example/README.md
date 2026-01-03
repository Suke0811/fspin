# Examples

This directory contains simple usage examples for **fspin**. Each example demonstrates using `RateControl` either via the `@spin` decorator or by directly creating the class. Both synchronous and asynchronous approaches are shown.

| File                   | Description                                                 |
|------------------------|-------------------------------------------------------------|
| `sync_decorator.py`    | Run a synchronous function at a fixed rate using the `@spin` decorator. |
| `sync_manual.py`       | Use `rate` directly with a synchronous function.            |
| `async_decorator.py`   | Run an async function with the `@spin` decorator, showing both blocking and non-blocking patterns. |
| `async_manual.py`      | Use `rate` directly with an async function, showing both blocking and non-blocking patterns. |
| `async_fire_and_forget.py` | Demonstrate the fire-and-forget pattern with both the `@spin` decorator and the `spin` context manager. |
| `async_loop_context.py`| Use the `spin` context manager with async functions, showing auto-detection of coroutines and both blocking and non-blocking patterns. |
| `loop_in_place.py`     | Use context manager `with spin(...):`.                      |
| `dynamic_frequency.py` | Change the loop frequency at runtime.                       |
| `lambda_condition.py`  | Use a lambda function as a condition to stop the loop.      |

Run any example with `python <file>` to see the behaviour.

Note that the scripts modify `sys.path` so they work when executed directly from this repository without installation.

---
