import time
import asyncio
import pytest
from fspin import spin, loop, rate

def test_spin_decorator():
    """Test that the spin decorator works correctly."""
    counter = {'count': 0}
    
    def condition():
        return counter['count'] < 3
    
    @spin(freq=10, condition_fn=condition, report=True, thread=False)
    def test_function():
        counter['count'] += 1
        time.sleep(0.01)
    
    # Call the decorated function
    rc = test_function()
    assert counter['count'] == 3
    assert rc.status == "stopped"

def test_spin_context_manager():
    """Test that the spin context manager works correctly."""
    counter = {'count': 0}

    def test_function():
        counter['count'] += 1
        time.sleep(0.01)

    # Use the context manager
    with spin(test_function, freq=10, report=True) as sp:
        time.sleep(0.25)  # Should allow for ~2-3 iterations

    assert counter['count'] >= 2
    assert sp.status == "stopped"


def test_spin_context_manager_with_args_kwargs():
    """Context manager should forward positional and keyword arguments."""
    captured = []

    def worker(arg1, arg2, *, flag):
        captured.append((arg1, arg2, flag))

    def condition():
        return not captured

    with spin(worker, 50, "alpha", "beta", flag=True, condition_fn=condition, thread=True) as rc:
        # Wait for the worker to run once in the background thread
        while not captured:
            time.sleep(0.01)

    assert captured == [("alpha", "beta", True)]
    assert rc.status == "stopped"

def test_loop_context_manager_deprecated():
    """Test that the loop context manager works but is deprecated."""
    counter = {'count': 0}
    
    def test_function():
        counter['count'] += 1
        time.sleep(0.01)
    
    # Use the deprecated context manager
    with pytest.warns(DeprecationWarning):
        with loop(test_function, freq=10, report=True) as lp:
            time.sleep(0.25)  # Should allow for ~2-3 iterations
    
    assert counter['count'] >= 2
    assert lp.status == "stopped"

@pytest.mark.asyncio
async def test_async_spin_decorator():
    """Test that the spin decorator works with async functions."""
    counter = {'count': 0}
    
    def condition():
        return counter['count'] < 3
    
    @spin(freq=10, condition_fn=condition, report=True, wait=True)
    async def test_function():
        counter['count'] += 1
        await asyncio.sleep(0.01)
    
    # Call the decorated function
    rc = await test_function()
    assert counter['count'] == 3
    assert rc.status == "stopped"

@pytest.mark.asyncio
async def test_async_spin_context_manager():
    """Test that the spin context manager works with async functions."""
    counter = {'count': 0}

    async def test_function():
        counter['count'] += 1
        await asyncio.sleep(0.01)

    # Use the context manager
    async with spin(test_function, freq=10, report=True) as sp:
        await asyncio.sleep(0.25)  # Should allow for ~2-3 iterations

    assert counter['count'] >= 2
    assert sp.status == "stopped"


@pytest.mark.asyncio
async def test_async_spin_context_manager_with_args_kwargs():
    """Async context manager should forward positional and keyword arguments."""
    captured = []

    async def worker(value, *, suffix):
        captured.append(f"{value}-{suffix}")

    def condition():
        return not captured

    async with spin(worker, 40, "reading", suffix="ok", condition_fn=condition) as rc:
        while not captured:
            await asyncio.sleep(0.01)

    assert captured == ["reading-ok"]
    assert rc.status == "stopped"


@pytest.mark.asyncio
async def test_async_spin_context_manager_accepts_coroutine_condition():
    """Async spin contexts should await coroutine condition functions."""
    ticks = []
    condition_checks = 0

    async def worker():
        ticks.append(object())

    async def condition():
        nonlocal condition_checks
        condition_checks += 1
        await asyncio.sleep(0)
        return condition_checks < 3

    async def wait_for_condition_to_complete():
        while condition_checks < 3:
            await asyncio.sleep(0.005)

    async with spin(worker, 200, condition_fn=condition) as rc:
        await asyncio.wait_for(wait_for_condition_to_complete(), timeout=0.5)

    assert condition_checks == 3
    assert len(ticks) == 2
    assert rc.status == "stopped"


@pytest.mark.asyncio
async def test_async_spin_decorator_accepts_coroutine_condition():
    """Async spin decorator should handle coroutine condition functions."""
    call_count = 0
    condition_checks = 0

    async def condition():
        nonlocal condition_checks
        condition_checks += 1
        await asyncio.sleep(0)
        return condition_checks < 3

    @spin(freq=200, condition_fn=condition, wait=True)
    async def worker():
        nonlocal call_count
        call_count += 1

    rc = await worker()

    assert condition_checks == 3
    assert call_count == 2
    assert rc.status == "stopped"


def test_sync_spin_context_rejects_coroutine_condition():
    """Passing coroutine conditions to sync spin should raise an error."""

    async def condition():
        return True

    def worker():
        pass

    with pytest.raises(TypeError, match="condition functions"):
        with spin(worker, 50, condition_fn=condition, thread=False):
            pass

@pytest.mark.asyncio
async def test_async_loop_context_manager_deprecated():
    """Test that the loop context manager works with async functions but is deprecated."""
    counter = {'count': 0}
    
    async def test_function():
        counter['count'] += 1
        await asyncio.sleep(0.01)
    
    # Use the deprecated context manager
    with pytest.warns(DeprecationWarning):
        async with loop(test_function, freq=10, report=True) as lp:
            await asyncio.sleep(0.25)  # Should allow for ~2-3 iterations
    
    assert counter['count'] >= 2
    assert lp.status == "stopped"
