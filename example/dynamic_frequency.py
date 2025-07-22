import os
import sys
import time
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
    # Report is generated automatically when report=True
