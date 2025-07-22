import asyncio
from functools import wraps
from .rate_control import RateControl

def spin(freq, condition_fn=None, report=False, thread=False):
    """
    Decorator to run the decorated function at a specified frequency (Hz).

    This decorator automatically detects if the function is a coroutine and runs it 
    accordingly. It creates a RateControl instance to manage the execution rate and
    returns it after the function completes or starts running (depending on the mode).

    Args:
        freq (float): Target frequency in Hz (cycles per second).
        condition_fn (callable, optional): Function returning True to continue spinning.
            Defaults to None (always continue).
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to False.

    Returns:
        callable: A decorated function that will run at the specified frequency.

    Example:
        >>> @spin(freq=10)
        ... def my_function():
        ...     print("Running at 10Hz")
        >>> 
        >>> @spin(freq=5, report=True)
        ... async def my_coroutine():
        ...     print("Running at 5Hz with reporting")
    """
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)
        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=True, report=report, thread=thread)
                await rc.start_spinning(func, condition_fn, *args, **kwargs)
                return rc
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=False, report=report, thread=thread)
                rc.start_spinning(func, condition_fn, *args, **kwargs)
                return rc
            return sync_wrapper
    return decorator
