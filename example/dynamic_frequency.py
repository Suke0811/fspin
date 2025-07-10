import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fspin import rate


def tick():
    print(f"tick at {time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    rc = rate(freq=2, is_coroutine=False, report=True, thread=True)
    rc.start_spinning(tick, None)
    time.sleep(2)
    print("\nChanging frequency to 4 Hz\n")
    rc.frequency = 4
    time.sleep(2)
    rc.stop_spinning()
    rc.get_report()
