import time
from fspin.spin_context import spin


def test_spin_context_sync_waitable():
    calls = []

    def condition():
        return len(calls) < 5

    def work():
        calls.append(time.perf_counter())
        time.sleep(0.005)

    start = time.perf_counter()
    with spin(work, freq=100, condition_fn=condition, thread=True, wait=True) as rc:
        # If wait=True, by the time we enter the body, the loop should be done
        inside_elapsed = time.perf_counter() - start
        assert inside_elapsed >= 0.02, "Context manager should have waited before entering body"
        assert len(calls) == 5
        assert rc._thread is not None
        assert not rc._thread.is_alive()
    # After exit, still done
    assert len(calls) == 5
