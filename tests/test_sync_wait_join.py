import time
from fspin.rate_control import RateControl


def test_sync_threaded_wait_joins_thread():
    calls = []

    def condition():
        return len(calls) < 5

    def work():
        calls.append(time.perf_counter())
        # simulate some work taking less than the loop duration
        time.sleep(0.005)

    rc = RateControl(100, is_coroutine=False, report=True, thread=True)

    # When wait=True and threaded=True, this should block until the thread completes
    t = rc.start_spinning_sync(work, condition, wait=True)

    # After returning, the background thread should have completed
    assert t is not None, "Expected a thread object to be returned"
    assert not t.is_alive(), "Thread should have finished when wait=True"

    # All iterations should have been executed
    assert len(calls) == 5, f"Expected 5 calls, got {len(calls)}"

    # Finalize should have been called
    assert rc.end_time is not None, "Expected end_time to be set after completion"

    # Mode should indicate threaded sync
    assert rc.mode == "sync-threaded", "Incorrect mode detected for threaded sync"
