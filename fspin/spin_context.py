import asyncio
from .rate_control import RateControl

class spin:
    """
    Context manager for running a function at a specified frequency.

    This context manager creates a RateControl instance and starts spinning the provided
    function at the specified frequency. When the context is exited, the spinning is
    automatically stopped.

    This context manager automatically detects if the function is a coroutine and
    configures itself accordingly. Use with the appropriate syntax:
    - For synchronous functions: `with spin(func, freq) as sp:`
    - For asynchronous functions: `async with spin(func, freq) as sp:`

    Args:
        func (callable): The function to execute at the specified frequency.
        freq (float): Target frequency in Hz (cycles per second).
        condition_fn (callable, optional): Function returning True to continue spinning.
            Defaults to None (always continue).
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to True.
        **kwargs: Keyword arguments to pass to func.

    Yields:
        RateControl: The RateControl instance managing the spinning.

    Example:
        >>> def heartbeat():
        ...     print("Beat")
        >>> with spin(heartbeat, freq=5, report=True) as sp:
        ...     time.sleep(1)  # Let it run for 1 second
        >>> # Automatically stops spinning when exiting the context

        >>> async def async_heartbeat():
        ...     print("Async Beat")
        ...     await asyncio.sleep(0)
        >>> async with spin(async_heartbeat, freq=5, report=True) as sp:
        ...     await asyncio.sleep(1)  # Let it run for 1 second
        >>> # Automatically stops spinning when exiting the context

        >>> async def background_task():
        ...     print("Running in the background")
        >>> async with spin(background_task, freq=5) as sp:
        ...     print("Continuing with other work while task runs in background")
        ...     await asyncio.sleep(1)  # Do other work
        >>> # Task is stopped when exiting the context
    """
    def __init__(self, func, freq, *, condition_fn=None, report=False, thread=True, **kwargs):
        # Automatically detect if the function is a coroutine
        is_coroutine = asyncio.iscoroutinefunction(func)

        self.rc = RateControl(freq, is_coroutine=is_coroutine, report=report, thread=thread)
        self.func = func
        self.condition_fn = condition_fn
        self.kwargs = kwargs
        self.is_coroutine = is_coroutine

    def __enter__(self):
        if self.is_coroutine:
            raise TypeError("For coroutine functions, use 'async with spin(...)' instead.")

        self.rc.start_spinning(self.func, self.condition_fn, **self.kwargs)
        return self.rc

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rc.stop_spinning()

    async def __aenter__(self):
        if not self.is_coroutine:
            raise TypeError("For regular functions, use 'with spin(...)' instead.")

        # Store the task and start it in fire-and-forget mode
        self._task = await self.rc.start_spinning_async(self.func, self.condition_fn, **self.kwargs)
        return self.rc

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.rc.stop_spinning()
