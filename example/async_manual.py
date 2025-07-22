import os
import sys
import asyncio
from fspin import rate

counter = {'count': 0}

def condition():
    return counter['count'] < 5

async def main_loop():
    counter['count'] += 1
    print(f"async manual tick {counter['count']}")
    await asyncio.sleep(0.1)

async def run():
    rc = rate(freq=2, is_coroutine=True, report=True)
    await rc.start_spinning_async_wrapper(main_loop, condition)
    # Report is generated automatically when report=True

if __name__ == "__main__":
    asyncio.run(run())
