import logging
import os
import sys
import pytest
import platform
import asyncio
from unittest.mock import patch, MagicMock
from fspin.rate_control import RateControl
import fspin.reporting as reporting

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fspin.RateControl import spin


def test_exception_logging_and_warning(caplog, capsys):
    call_count = 0

    def condition():
        nonlocal call_count
        call_count += 1
        # run only once
        return call_count <= 1

    @spin(freq=1000, condition_fn=condition, report=False, thread=False)
    def faulty():
        raise ValueError("boom")

    with caplog.at_level(logging.ERROR):
        with pytest.warns(RuntimeWarning) as record:
            faulty()
        stderr = capsys.readouterr().err

    # Ensure warning contains function name
    assert any("faulty" in str(w.message) for w in record), record
    # Ensure log contains error with function name
    assert any("faulty" in r.getMessage() for r in caplog.records), caplog.text
    # Stderr should contain the traceback
    assert "Traceback" in stderr
    assert "ValueError: boom" in stderr


def test_rate_control_os_warnings():
    """Test OS-specific warnings in RateControl.__init__"""
    with patch('platform.system', return_value='Linux'):
        with pytest.warns(RuntimeWarning, match="Linux timer resolution"):
            rc = RateControl(freq=1000, is_coroutine=True)
            rc.stop_spinning()

    with patch('platform.system', return_value='Darwin'):
        with pytest.warns(RuntimeWarning, match="macOS timer resolution"):
            rc = RateControl(freq=5000, is_coroutine=True)
            rc.stop_spinning()


@pytest.mark.asyncio
async def test_rate_control_prepare_condition_edge_cases():
    """Test edge cases in _prepare_condition_fn"""
    rc = RateControl(freq=10, is_coroutine=False)

    # Test sync spinning with awaitable result
    async def async_res(): return True
    res_coro = async_res()
    def sync_returning_awaitable(): return res_coro

    cond = rc._prepare_condition_fn(sync_returning_awaitable, is_async=False)
    with pytest.raises(TypeError, match="Synchronous spinning does not support awaitable condition functions"):
        cond()
    await res_coro  # Clean up coroutine


def test_reporting_setup_terminal_logging():
    """Test _setup_terminal_logging (lines 10-14 in reporting.py)"""
    with patch('logging.getLogger') as mock_get_logger:
        mock_root = MagicMock()
        mock_root.handlers = []  # No handlers
        mock_get_logger.return_value = mock_root

        reporting._setup_terminal_logging()

        mock_root.addHandler.assert_called()
        mock_root.setLevel.assert_called_with(logging.INFO)


@pytest.mark.asyncio
async def test_rate_control_extra_coverage():
    """Test remaining uncovered lines in rate_control.py"""
    # 1. fspin/rate_control.py:170 (inspect.isawaitable(result) in async context)
    rc_async = RateControl(freq=10, is_coroutine=True)
    async def async_res(): return False
    res_coro = async_res()
    def sync_returning_awaitable(): return res_coro
    cond_async = rc_async._prepare_condition_fn(sync_returning_awaitable, is_async=True)
    assert await cond_async() == False

    # 2. fspin/rate_control.py:438-440 (asyncio.CancelledError in start_spinning_async_wrapper)
    async def awork(): await asyncio.sleep(0.1)
    rc_wait = RateControl(freq=100, is_coroutine=True)
    task = asyncio.create_task(rc_wait.start_spinning_async_wrapper(awork, wait=True))
    await asyncio.sleep(0.01)
    # We need to cancel the task that is AWAITING the spinning task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    rc_wait.stop_spinning()

    # 3. fspin/rate_control.py:465 (asyncio.run_coroutine_threadsafe)
    # This happens when self._own_loop is not None
    with patch('asyncio.get_running_loop', side_effect=RuntimeError):
        rc_own = RateControl(freq=10, is_coroutine=True)
        assert rc_own._own_loop is not None
        async def mock_func(): pass

        coro = mock_func()
        # USE MagicMock instead of default Mock for start_spinning_async to avoid AsyncMock issues
        with patch('fspin.rate_control.RateControl.start_spinning_async', MagicMock(return_value=coro)):
            with patch('asyncio.run_coroutine_threadsafe') as mock_run:
                rc_own.start_spinning(mock_func, None)
                mock_run.assert_called()

        # Manually close/cleanup coro to avoid warning if it wasn't awaited
        coro.close()

        rc_own.stop_spinning()
