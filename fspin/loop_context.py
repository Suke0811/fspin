import asyncio
import warnings
from .spin_context import spin

# For backward compatibility
class loop(spin):
    """
    Context manager for running a function at a specified frequency.

    DEPRECATED: Use 'spin' instead. This class is maintained for backward compatibility.

    This context manager creates a RateControl instance and starts spinning the provided
    function at the specified frequency. When the context is exited, the spinning is
    automatically stopped.

    This context manager automatically detects if the function is a coroutine and
    configures itself accordingly. Use with the appropriate syntax:
    - For synchronous functions: `with loop(func, freq) as lp:`
    - For asynchronous functions: `async with loop(func, freq) as lp:`
    """
    def __init__(self, func, freq, *, condition_fn=None, report=False, thread=True, **kwargs):
        warnings.warn(
            "The 'loop' context manager is deprecated. Use 'spin' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(func, freq, condition_fn=condition_fn, report=report, thread=thread, **kwargs)
