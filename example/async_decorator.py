import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fspin import spin

counter = {'count': 0}

def condition():
    return counter['count'] < 5

@spin(freq=2, condition_fn=condition, report=True)
async def main_loop():
    counter['count'] += 1
    print(f"async decorator tick {counter['count']}")
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
