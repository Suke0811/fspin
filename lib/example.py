import asyncio
import time
from RateControl import spin

# ---------------------------
# Synchronous Tests
# ---------------------------
def test_sync_with_report():
    start = time.perf_counter()
    # Run for 3 seconds.
    condition = lambda: time.perf_counter() - start < 3

    @spin(freq=1000, condition_fn=condition, report=True)
    def work():
        # Do a minimal operation.
        time.sleep(0.00005)

    print("\nRunning test_sync_with_report...")
    rc = work()  # Starts spinning in a separate thread.
    # Allow enough time for the spin loop to run.
    time.sleep(3.2)
    rc.stop_spinning()
    print("test_sync_with_report completed.\n")


def test_sync_without_report():
    start = time.perf_counter()
    condition = lambda: time.perf_counter() - start < 3

    @spin(freq=1000, condition_fn=condition, report=False)
    def work():
        time.sleep(0.0005)

    print("\nRunning test_sync_without_report...")
    rc = work()  # No report will be printed.
    time.sleep(3.2)
    rc.stop_spinning()
    print("test_sync_without_report completed.\n")


# ---------------------------
# Asynchronous Tests
# ---------------------------
async def test_async_with_report():
    start = time.perf_counter()
    condition = lambda: time.perf_counter() - start < 3

    @spin(freq=50, condition_fn=condition, report=True)
    async def async_work():
        # Minimal async operation.
        await asyncio.sleep(0.001)

    print("\nRunning test_async_with_report...")
    rc = await async_work()  # Starts spinning as an asyncio Task.
    await asyncio.sleep(3.2)
    rc.stop_spinning()
    print("test_async_with_report completed.\n")


async def test_async_without_report():
    start = time.perf_counter()
    condition = lambda: time.perf_counter() - start < 3

    @spin(freq=50, condition_fn=condition, report=False)
    async def async_work():
        await asyncio.sleep(0.001)

    print("\nRunning test_async_without_report...")
    rc = await async_work()  # No report will be printed.
    await asyncio.sleep(3.2)
    rc.stop_spinning()
    print("test_async_without_report completed.\n")


# ---------------------------
# Main Test Runner
# ---------------------------
def main():
    print("=== Starting Synchronous Tests ===")
    test_sync_with_report()
    test_sync_without_report()

    print("=== Starting Asynchronous Tests ===")
    asyncio.run(test_async_with_report())
    asyncio.run(test_async_without_report())
    print("All tests completed.")


if __name__ == "__main__":
    main()
