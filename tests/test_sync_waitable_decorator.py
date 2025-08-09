import time
from fspin.decorators import spin


def test_sync_decorator_threaded_wait_joins_thread():
    calls = []

    def condition():
        return len(calls) < 5

    @spin(freq=100, condition_fn=condition, thread=True, wait=True)
    def work():
        calls.append(time.perf_counter())
        time.sleep(0.005)

    start = time.perf_counter()
    rc = work()
    elapsed = time.perf_counter() - start

    # Should have blocked roughly for the loop duration * iterations
    assert elapsed >= 0.02, f"Expected blocking behavior, elapsed={elapsed:.3f}s"

    assert len(calls) == 5
    # Thread should have finished if it existed
    # In blocking mode (thread=False), _thread may be None; but here thread=True
    assert rc._thread is not None
    assert not rc._thread.is_alive()
