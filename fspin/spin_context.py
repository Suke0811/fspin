import asyncio
from .rate_control import RateControl

class spin:
    """
    Context manager for running a function at a specified frequency.

    This context manager creates a RateControl instance and starts spinning the provided
    function at the specified frequency. Any additional positional or keyword arguments
    after ``freq`` are forwarded to the target function on every iteration. When the
    context is exited, the spinning is automatically stopped.

    This context manager automatically detects if the function is a coroutine and
    configures itself accordingly. Use with the appropriate syntax:
    - For synchronous functions: `with spin(func, freq) as sp:`
    - For asynchronous functions: `async with spin(func, freq) as sp:`

    Args:
        func (callable): The function to execute at the specified frequency.
        freq (float): Target frequency in Hz (cycles per second).
        *func_args: Positional arguments passed to ``func`` every iteration.
        condition_fn (callable or coroutine, optional): Predicate evaluated before each
            iteration. In synchronous contexts it must be a regular callable returning a
            truthy value. In asynchronous contexts it may be either a regular callable
            or a coroutine function/awaitable; results are awaited automatically. Defaults
            to None (always continue).
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to True.
        wait (bool, optional): Whether to block until the underlying worker completes
            before entering the context when ``thread=True``. Defaults to False.
        **func_kwargs: Keyword arguments to pass to ``func``.

    Yields:
        RateControl: The RateControl instance managing the spinning.

    Example:
        >>> counter = 0
        >>> def heartbeat():
        ...     nonlocal counter
        ...     counter += 1
        ...     print("Beat")
        >>> # Preferred usage with lambda condition
        >>> with spin(heartbeat, freq=5, condition_fn=lambda: counter < 5) as sp:
        ...     while sp.is_running():
        ...         time.sleep(0.1)
        >>> # Automatically stops spinning when counter reaching 5 or exiting the context

        >>> count = 0
        >>> async def async_heartbeat():
        ...     nonlocal count
        ...     count += 1
        ...     print("Async Beat")
        ...     await asyncio.sleep(0)
        >>> # Preferred usage with lambda condition
        >>> async with spin(async_heartbeat, freq=5, condition_fn=lambda: count < 5) as sp:
        ...     await asyncio.sleep(1)  # Let it run
        >>> # Automatically stops spinning when count reaching 5 or exiting the context

        >>> async def background_task():
        ...     print("Running in the background")
        >>> async with spin(background_task, freq=5) as sp:
        ...     print("Continuing with other work while task runs in background")
        ...     await asyncio.sleep(1)  # Do other work
        >>> # Task is stopped when exiting the context

        >>> def with_arguments(arg, *, kw=None):
        ...     print(arg, kw)
        >>> with spin(with_arguments, 10, "value", kw=123):
        ...     time.sleep(0.1)
    """
    def __init__(self, func, freq, *func_args, condition_fn=None, report=False, thread=True, wait=False, **func_kwargs):
        # Automatically detect if the function is a coroutine
        is_coroutine = asyncio.iscoroutinefunction(func)

        self.rc = RateControl(freq, is_coroutine=is_coroutine, report=report, thread=thread)
        self.func = func
        self.condition_fn = condition_fn
        self.args = func_args
        self.kwargs = func_kwargs
        self.is_coroutine = is_coroutine
        self.wait = wait

    def __enter__(self):
        if self.is_coroutine:
            raise TypeError("For coroutine functions, use 'async with spin(...)' instead.")

        self.rc.start_spinning(self.func, self.condition_fn, *self.args, wait=self.wait, **self.kwargs)
        return self.rc

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rc.stop_spinning()

    async def __aenter__(self):
        if not self.is_coroutine:
            raise TypeError("For regular functions, use 'with spin(...)' instead.")

        # Store the task and start it in fire-and-forget mode
        self._task = await self.rc.start_spinning_async(self.func, self.condition_fn, *self.args, **self.kwargs)
        return self.rc

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.rc.stop_spinning()
