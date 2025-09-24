import asyncio
from functools import wraps
from .rate_control import RateControl

def spin(freq, condition_fn=None, report=False, thread=False, wait=False):
    """
    Decorator to run the decorated function at a specified frequency (Hz).

    This decorator automatically detects if the function is a coroutine and runs it 
    accordingly. It creates a RateControl instance to manage the execution rate and
    returns it after the function completes or starts running (depending on the mode).

    Args:
        freq (float): Target frequency in Hz (cycles per second).
        condition_fn (callable or coroutine, optional): Predicate evaluated before each
            iteration. For synchronous functions it must be a regular callable returning
            a truthy value. For async functions it may be a regular callable or coroutine;
            awaitable results are handled automatically. Defaults to None (always
            continue).
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to False.
        wait (bool, optional):
            - For async functions: whether to await the task (blocking) or return immediately
              (fire-and-forget). Defaults to False (fire-and-forget).
            - For sync functions with thread=True: whether to join the thread before returning
              (i.e., block until completion). Defaults to False (fire-and-forget).

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
        >>> 
        >>> @spin(freq=5, wait=False)
        ... async def background_task():
        ...     print("Running in the background")
    """
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)
        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=True, report=report, thread=thread)
                task = await rc.start_spinning_async(func, condition_fn, *args, **kwargs)

                if wait:
                    try:
                        await task
                    except asyncio.CancelledError:
                        # Task was cancelled, which is expected when condition is met
                        pass
                    finally:
                        # Ensure it's stopped after task completes
                        rc.stop_spinning()

                return rc
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=False, report=report, thread=thread)
                # Forward wait for sync threaded mode; if wait=True it will join before returning
                rc.start_spinning(func, condition_fn, *args, wait=wait, **kwargs)
                # If we waited (thread join or blocking mode), ensure stopped; otherwise leave running
                if wait or not thread:
                    rc.stop_spinning()
                return rc

            return sync_wrapper
    return decorator
