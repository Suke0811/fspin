import os
import sys
import time
import asyncio
from functools import partial

from fspin import loop

# ===== Synchronous Examples =====

def heartbeat(prefix='main'):
    print(f"{prefix}: Heartbeat at {time.strftime('%H:%M:%S')}")

def run_sync_examples():
    print("\n===== Synchronous Examples =====\n")

    # After 1 second, the loop will exist
    print("Basic usage:")
    with loop(heartbeat, freq=5, report=True):
        time.sleep(1)
        # after 1sec it will exist.
        # if report is true, then report shows up
    # Report is generated automatically when report=True

    # if you want to hand over the args
    print("\nPassing arguments:")
    with loop(heartbeat, freq=5, report=True, prefix='my_loop'):
        time.sleep(1)
    # Report is generated automatically when report=True

    # or use functools
    print("\nUsing functools.partial:")
    hb = partial(heartbeat, 'my_another_loop')
    with loop(hb, freq=5, report=True):
        time.sleep(1)
    # Report is generated automatically when report=True

    # Manually terminating the looping. report info accessible from lp instance.
    print("\nManually stopping the loop:")
    with loop(heartbeat, freq=50, report=True) as lp:
        # Let it run for 1 s, then stop spinning manually
        time.sleep(1)
        lp.stop_spinning()
        print("Manually stopped after 1 s")

    # Once out of the with-block, lp is still available:
    print(f"Total iterations recorded: {len(lp.iteration_times)}")
    print("Deviations (s):", lp.deviations)
    # lp.get_report()

# ===== Asynchronous Examples =====

async def async_heartbeat(prefix='main'):
    print(f"{prefix}: Async Heartbeat at {time.strftime('%H:%M:%S')}")
    await asyncio.sleep(0.01)  # Small delay to simulate async work

async def run_async_examples():
    print("\n===== Asynchronous Examples =====\n")

    # Basic usage with async function
    print("Basic usage with async function:")
    async with loop(async_heartbeat, freq=5, report=True):
        await asyncio.sleep(1)
        # after 1sec it will exist.
        # if report is true, then report shows up
    # Report is generated automatically when report=True
    # All other functions are the same as sync


# Run both synchronous and asynchronous examples
if __name__ == "__main__":
    # Run synchronous examples
    run_sync_examples()

    # Run asynchronous examples
    asyncio.run(run_async_examples())
