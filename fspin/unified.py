import inspect
import asyncio
from functools import wraps
from .rate_control import RateControl
from .decorators import spin as spin_decorator
from .spin_context import spin as spin_context_manager

class UnifiedSpin:
    """
    Unified entry point for fspin that intelligently selects between decorator,
    context manager, or direct class usage based on how it's called.

    Usage:
        # As a decorator
        @spin(freq=10)
        def my_function():
            pass

        # As a context manager
        with spin(my_function, freq=10):
            # Code to run while function is spinning
            pass
    """

    def __call__(self, *args, **kwargs):
        # Determine how spin is being called

        # Case 1: Called with no positional args or first arg is a number (freq)
        # This is decorator usage: @spin(freq=10)
        if not args or isinstance(args[0], (int, float)):
            return spin_decorator(*args, **kwargs)

        # Case 2: First arg is a callable (function or coroutine)
        # This is context manager usage: with spin(func, freq=10)
        if callable(args[0]):
            return spin_context_manager(*args, **kwargs)

        # Default case - should not reach here
        raise TypeError("Invalid usage of spin. Use as decorator (@spin) or context manager (with spin()).")

# Create a singleton instance
spin = UnifiedSpin()
