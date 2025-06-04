import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
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
