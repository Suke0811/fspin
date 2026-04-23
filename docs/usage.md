# Usage Examples

These examples mirror the patterns provided in the repository and demonstrate synchronous and asynchronous spinning, blocking versus fire-and-forget behaviour, and the context manager interface.

## Sync threaded: blocking vs fire-and-forget

```python
import time
from fspin import spin

counter = {"n": 0}

def cond():
    return counter["n"] < 5

# Fire-and-forget: returns immediately while the background thread runs
@spin(freq=50, condition_fn=cond, thread=True, wait=False)
def sync_bg():
    counter["n"] += 1

rc = sync_bg()          # returns immediately
# ... do other work ...
rc.stop_spinning()      # stop when ready

# Blocking: call does not return until cond() becomes False
@spin(freq=50, condition_fn=cond, thread=True, wait=True)
def sync_blocking():
    counter["n"] += 1

counter["n"] = 0
rc2 = sync_blocking()   # blocks until 5 iterations complete
```

## Async decorator: blocking vs fire-and-forget

```python
import asyncio
from fspin import spin

# Blocking version (wait=True)
@spin(freq=2, report=True, wait=True)
async def blocking_loop():
    await asyncio.sleep(0.1)

# Fire-and-forget version (wait=False)
@spin(freq=2, report=True, wait=False)
async def non_blocking_loop():
    await asyncio.sleep(0.1)

async def run_both():
    rc1 = await blocking_loop()   # awaits completion before returning
    rc2 = await non_blocking_loop()  # returns immediately; remember to stop later
    rc2.stop_spinning()
```

## Context manager for synchronous functions

```python
import time
from fspin import spin

def heartbeat():
    print(f"Heartbeat at {time.strftime('%H:%M:%S')}")

# Runs in background thread at 2Hz, auto-stops on exit, prints report
with spin(heartbeat, freq=2, report=True, thread=True):
    time.sleep(5)  # keep the block alive for 5s
    print("exiting the loop")
print("Loop exited")
```

## Context manager with async predicate support

```python
import asyncio
from fspin import spin

ticks = []

async def predicate():
    await asyncio.sleep(0)  # simulate async state checks
    return len(ticks) < 3

@spin(freq=100, condition_fn=predicate, wait=True)
async def monitored_task():
    ticks.append("tick")

async def main():
    rc = await monitored_task()
    assert len(ticks) == 2
    assert rc.status == "stopped"

asyncio.run(main())
```

## Manual control with `rate`

```python
import time
from fspin import rate

# Create a rate control for a simple function
rc = rate(freq=10, is_coroutine=False, report=True, thread=True)

# Start spinning your function in background
rc.start_spinning(lambda: print("Tick"), None)

# Let it run 3 seconds
time.sleep(3)

# Stop the loop and print report
rc.stop_spinning()
```

For more runnable scripts, see the files under `example/` in the repository.
