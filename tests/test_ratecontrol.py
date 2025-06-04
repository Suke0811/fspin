import asyncio
import time
import types
import pytest

from fspin.RateControl import ReportLogger, RateControl, spin


def test_create_histogram():
    logger = ReportLogger(enabled=True)
    data = [0.001, 0.002, 0.003]
    hist = logger.create_histogram(data, bins=2, bar_width=10)
    lines = hist.splitlines()
    assert len(lines) == 2
    assert all("ms" in line for line in lines)


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
