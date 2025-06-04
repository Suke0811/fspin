import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
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

if __name__ == "__main__":
    asyncio.run(run())
