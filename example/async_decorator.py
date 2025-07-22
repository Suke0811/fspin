import os
import sys
import asyncio
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
    rc = asyncio.run(main_loop())
    # Report is generated automatically when report=True
