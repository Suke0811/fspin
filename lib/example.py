import asyncio, time
from .RateControl import spin

start_time_sync = None

def keep_running_sync():
    # Example condition: run for 5 seconds
    return time.perf_counter() - start_time_sync < 5

@spin(freq=1000, condition_fn=keep_running_sync, report=True)
def some_function_that_needs_to_run_at_1000Hz():
    # Perform a minimal operation to ensure measurable function duration
    time.sleep(0.0009)


@spin(freq=500, condition_fn=None, report=True)
async def some_async_function_that_runs_at_500Hz():
    # Perform a minimal asynchronous operation
    await asyncio.sleep(0.001)  # Simulate async work


async def run_async_spinning():
    rc_async = await some_async_function_that_runs_at_500Hz()  # Starts spinning as an asyncio Task
    try:
    # Let the asynchronous spinning run for 6 seconds
        await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass
    finally:
        rc_async.stop_spinning()
        print("Async: Spinning stopped.")


def main():
    global start_time_sync
    start_time_sync = time.perf_counter()
    rc_sync = some_function_that_needs_to_run_at_1000Hz()  # Starts spinning in a separate thread

    try:
        # Run the asynchronous spinning within the asyncio event loop
        asyncio.run(run_async_spinning())
    except KeyboardInterrupt:
        pass
    finally:
        rc_sync.stop_spinning()
        print("Sync: Spinning stopped.")


if __name__ == "__main__":
    main()
