import os
from typing import Any
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

    _cheatsheet_loaded = False

    def __init__(self) -> None:
        self._load_cheatsheet()

    @classmethod
    def _load_cheatsheet(cls) -> None:
        if cls._cheatsheet_loaded:
            return
        
        try:
            # Look for fspin_cheatsheet.md in the package directory
            base_dir = os.path.dirname(__file__)
            cheatsheet_path = os.path.join(base_dir, "fspin_cheatsheet.md")
            
            if os.path.exists(cheatsheet_path):
                with open(cheatsheet_path, "r", encoding="utf-8") as f:
                    cheatsheet_content = f.read()
                    cls.__doc__ = (cls.__doc__ or "") + "\n\n" + cheatsheet_content
                cls._cheatsheet_loaded = True
        except Exception:
            pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Main entry point for spin.
        
        Determines usage based on arguments:
        1. @spin(...) -> decorator usage
        2. with spin(func, freq, ...) -> sync context manager
        3. async with spin(func, freq, ...) -> async context manager
        """
        # Determine how spin is being called

        # Case 1: First arg is a callable (function or coroutine)
        # This is context manager usage: with spin(func, freq=10)
        # Or direct call: spin(func, freq=10)
        if args and callable(args[0]):
            return spin_context_manager(*args, **kwargs)

        # Case 2: Called with no args (using defaults) or first arg is freq, or only kwargs
        # This is decorator usage: @spin(freq=10)
        return spin_decorator(*args, **kwargs)

# Create a singleton instance
spin = UnifiedSpin()
