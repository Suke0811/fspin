"""
fspin: A utility for running Python functions at a fixed rate.

The fspin library provides tools to execute functions or coroutines repeatedly 
at a consistent frequency, supporting both synchronous and asynchronous workflows.

Main Features:
- @spin decorator for easy loop creation.
- spin context manager for scoped background loops.
- Automatic detection of sync vs async functions.
- Support for lambda functions as stop conditions (Preferred).
- High-precision rate control with deviation compensation.

Quick Start:
    from fspin import spin
    import time

    counter = 0
    # Preferred usage: use a lambda for the condition
    @spin(freq=10, condition_fn=lambda: counter < 5)
    def my_loop():
        nonlocal counter
        counter += 1
        print(f"Iteration {counter}")

    my_loop() # Blocks until counter reaches 5

For detailed documentation and best practices, run 'python -m fspin' 
to view the full cheatsheet.
"""
from .rate_control import RateControl as rate
from .decorators import spin as spin_decorator
from .spin_context import spin as spin_context_manager
from .loop_context import loop
from .unified import spin
