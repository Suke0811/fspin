import os
import sys
import asyncio
import time
from fspin import rate

# This example demonstrates using the rate class (RateControl) directly with async functions
# showing both blocking and non-blocking (fire-and-forget) patterns

print("=== Async Manual Control with RateControl ===")

# Counter to track iterations
counter = {'count': 0}

def condition():
    # Continue until we have 5 iterations
    return counter['count'] < 5

async def main_loop():
    counter['count'] += 1
    print(f"Async manual tick {counter['count']} at {time.strftime('%H:%M:%S')}")
    await asyncio.sleep(0.1)  # Simulate some async work

async def run_blocking():
    print("\n--- Blocking mode (wait=True) ---")

    # Create a RateControl instance for async functions
    rc = rate(freq=2, is_coroutine=True, report=True)

    # Start spinning with wait=True (blocking)
    # This will wait until all iterations are complete
    await rc.start_spinning_async_wrapper(main_loop, condition, wait=True)

    print(f"Completed {counter['count']} iterations")
    print("This line is executed after all iterations are complete")

    # Reset counter for the next example
    counter['count'] = 0

async def run_non_blocking():
    print("\n--- Fire-and-forget mode (wait=False) ---")

    # Create a RateControl instance for async functions
    rc = rate(freq=2, is_coroutine=True, report=True)

    # Start spinning with wait=False (fire-and-forget)
    # This will return immediately without waiting for all iterations
    task = await rc.start_spinning_async_wrapper(main_loop, condition, wait=False)

    print("Continuing with other work while background task runs...")

    # Do some other work
    for i in range(3):
        print(f"Main task working... ({i+1}/3)")
        await asyncio.sleep(0.5)

    # Wait a bit more to ensure the background task completes
    await asyncio.sleep(1)

    print(f"Background task completed {counter['count']} iterations")

    # Clean up (though the task should have completed by now)
    rc.stop_spinning()

async def run():
    # Run both examples
    await run_blocking()
    await run_non_blocking()

if __name__ == "__main__":
    asyncio.run(run())
