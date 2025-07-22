import os
import sys
import time
from fspin import rate

counter = {'count': 0}

def condition():
    return counter['count'] < 5

def main_loop():
    counter['count'] += 1
    print(f"sync manual tick {counter['count']}")
    time.sleep(0.1)

if __name__ == "__main__":
    rc = rate(freq=2, is_coroutine=False, report=True, thread=False)
    rc.start_spinning(main_loop, condition)
    # Report is generated automatically when report=True
