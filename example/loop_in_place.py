import os
import sys
import time

from fspin import loop

def heartbeat(prefix='main'):
    print(f"{prefix}: Heartbeat at {time.strftime('%H:%M:%S')}")

# After 1 second, the loop will exist
with loop(heartbeat, freq=5, report=True):
    time.sleep(1)
    # after 1sec it will exist.
    # if report is true, then report shows up
# Report is generated automatically when report=True

# if you want to hand over the args
with loop(heartbeat, freq=5, report=True, prefix='my_loop'):
    time.sleep(1)
# Report is generated automatically when report=True

# or use functools
from functools import partial
hb = partial(heartbeat, 'my_another_loop')
with loop(hb, freq=5, report=True):
    time.sleep(1)
# Report is generated automatically when report=True

# Manually terminating the looping. report info accessible from lp instance.
with loop(heartbeat, freq=50, report=True) as lp:
    # Let it run for 1 s, then stop spinning manually
    time.sleep(1)
    lp.stop_spinning()
    print("Manually stopped after 3 s")

# Once out of the with-block, lp is still available:
print(f"Total iterations recorded: {len(lp.iteration_times)}")
print("Deviations (s):", lp.deviations)
# lp.get_report()
