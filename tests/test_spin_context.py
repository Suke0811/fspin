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
