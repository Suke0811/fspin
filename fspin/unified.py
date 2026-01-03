import inspect
import asyncio
import os
from functools import wraps
from .rate_control import RateControl
from .decorators import spin as spin_decorator
from .spin_context import spin as spin_context_manager

class UnifiedSpin:
    """
    Unified entry point for fspin.
    
    Acts as a decorator, context manager, or functional interface 
    based on how it is called.
    
    Usage:
        @spin(freq=10, condition_fn=lambda: True)
        def my_func(): ...
        
        with spin(my_func, freq=10):
            ...
    """

    def __init__(self):
        # Dynamically load the cheatsheet into the docstring if available
        try:
            # Look for fspin_cheatsheet.md in the package directory or one level up
            base_dir = os.path.dirname(os.path.dirname(__file__))
            cheatsheet_path = os.path.join(base_dir, "fspin_cheatsheet.md")
            if not os.path.exists(cheatsheet_path):
                # Try sibling directory (if installed)
                base_dir = os.path.dirname(__file__)
                cheatsheet_path = os.path.join(base_dir, "fspin_cheatsheet.md")

            if os.path.exists(cheatsheet_path):
                with open(cheatsheet_path, "r", encoding="utf-8") as f:
                    cheatsheet_content = f.read()
                    self.__class__.__doc__ = (self.__class__.__doc__ or "") + "\n\n" + cheatsheet_content
        except Exception:
            pass

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
