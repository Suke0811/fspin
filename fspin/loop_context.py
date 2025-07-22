import asyncio
from contextlib import contextmanager
from .rate_control import RateControl

@contextmanager
def loop(func, freq, condition_fn=None, report=False, thread=True, *args, **kwargs):
    """
    Context manager for running a function at a specified frequency.
    
    This context manager creates a RateControl instance and starts spinning the provided
    function at the specified frequency. When the context is exited, the spinning is
    automatically stopped.
    
    Args:
        func (callable): The function or coroutine to execute at the specified frequency.
        freq (float): Target frequency in Hz (cycles per second).
        condition_fn (callable, optional): Function returning True to continue spinning.
            Defaults to None (always continue).
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to True.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.
        
    Yields:
        RateControl: The RateControl instance managing the spinning.
        
    Example:
        >>> def heartbeat():
        ...     print("Beat")
        >>> with loop(heartbeat, freq=5, report=True) as lp:
        ...     time.sleep(1)  # Let it run for 1 second
        >>> # Automatically stops spinning when exiting the context
    """
    rc = RateControl(freq, is_coroutine=asyncio.iscoroutinefunction(func), report=report, thread=thread)
    rc.start_spinning(func, condition_fn, *args, **kwargs)
    try:
        yield rc
    finally:
        rc.stop_spinning()
