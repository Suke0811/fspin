import asyncio
import time
import types
import logging
import pytest

from fspin.RateControl import ReportLogger, RateControl, spin


def test_create_histogram():
    logger = ReportLogger(enabled=True)
    data = [0.001, 0.002, 0.003]
    hist = logger.create_histogram(data, bins=2, bar_width=10)
    lines = hist.splitlines()
    assert len(lines) == 2
    assert all("ms" in line for line in lines)


def test_create_histogram_empty():
    logger = ReportLogger(enabled=True)
    assert logger.create_histogram([], bins=2) == "No data to display."


def test_generate_report_outputs():
    class DummyLogger(ReportLogger):
        def __init__(self):
            super().__init__(enabled=True)
            self.messages = []

        def output(self, msg: str):
            self.messages.append(msg)

    logger = DummyLogger()
    logger.generate_report(
        freq=10,
        loop_duration=0.1,
        initial_duration=0.02,
        total_duration=1.0,
        total_iterations=5,
        avg_frequency=9.5,
        avg_function_duration=0.01,
        avg_loop_duration=0.105,
        avg_deviation=0.001,
        max_deviation=0.002,
        std_dev_deviation=0.0005,
        deviations=[0.001, 0.002],
    )
    joined = "\n".join(logger.messages)
    assert "RateControl Report" in joined
    assert "Set Frequency" in joined
    assert "histogram" not in joined  # ensure create_histogram didn't crash


def test_spin_sync_counts():
    calls = []

    def condition():
        return len(calls) < 2

    @spin(freq=1000, condition_fn=condition, report=True, thread=False)
    def work():
        calls.append(time.perf_counter())

    rc = work()
    assert len(calls) == 2
    assert rc.initial_duration is not None
    assert len(rc.iteration_times) == 1


def test_spin_sync_default_condition():
    calls = []

    def work():
        calls.append(1)
        if len(calls) == 2:
            rc.stop_spinning()

    rc = RateControl(freq=1000, is_coroutine=False, report=True, thread=False)
    rc.start_spinning(work, None)
    assert len(calls) == 2


def test_spin_async_counts():
    calls = []

    def condition():
        return len(calls) < 2

    @spin(freq=1000, condition_fn=condition, report=True)
    async def awork():
        calls.append(time.perf_counter())
        await asyncio.sleep(0)

    rc = asyncio.run(awork())
    assert len(calls) == 2
    assert rc.initial_duration is not None
    assert len(rc.iteration_times) == 1


def test_type_mismatch_errors():
    async def coro():
        pass

    rc_async = RateControl(freq=1, is_coroutine=True)
    with pytest.raises(TypeError):
        rc_async.start_spinning(lambda: None, None)

    rc_sync = RateControl(freq=1, is_coroutine=False)
    with pytest.raises(TypeError):
        rc_sync.start_spinning(coro, None)


def test_keyboard_interrupt_handled(caplog):
    rc = RateControl(freq=1000, is_coroutine=False, thread=False)

    def work():
        raise KeyboardInterrupt

    with caplog.at_level(logging.INFO, logger="root"):
        rc.start_spinning(work, None)

    assert rc._stop_event.is_set()


def test_stop_spinning_threaded():
    calls = []

    @spin(freq=1000, condition_fn=lambda: True, thread=True)
    def work():
        calls.append(1)
        time.sleep(0.001)

    rc = work()
    time.sleep(0.01)
    rc.stop_spinning()
    assert not rc._thread.is_alive()
    assert calls


def test_stop_spinning_async_task_cancel():
    async def awork():
        while True:
            await asyncio.sleep(0)

    rc = RateControl(freq=1000, is_coroutine=True)

    async def runner():
        task = asyncio.create_task(rc.start_spinning_async_wrapper(awork, None))
        await asyncio.sleep(0.01)
        rc.stop_spinning()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.cancelled()

    asyncio.run(runner())


def test_spin_async_exception_handling(caplog):
    async def awork():
        raise ValueError("oops")

    async def runner():
        rc = RateControl(freq=1000, is_coroutine=True, report=True)
        count = 0

        def cond():
            nonlocal count
            count += 1
            return count < 2

        with caplog.at_level(logging.INFO, logger="root"):
            await rc.start_spinning_async_wrapper(awork, cond)

    with pytest.warns(RuntimeWarning):
        asyncio.run(runner())
    assert any("Exception in spinning coroutine" in r.getMessage() for r in caplog.records)


def test_generate_report_no_iterations(caplog):
    rc = RateControl(freq=10, is_coroutine=False, report=True, thread=False)
    with caplog.at_level(logging.INFO):
        rc.generate_report()
    assert any("No iterations were recorded" in r.getMessage() for r in caplog.records)
