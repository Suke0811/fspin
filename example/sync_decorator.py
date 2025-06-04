import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fspin import spin

# stop after five iterations
counter = {'count': 0}

def condition():
    return counter['count'] < 5

@spin(freq=2, condition_fn=condition, report=True, thread=False)
def main_loop():
    counter['count'] += 1
    print(f"sync decorator tick {counter['count']}")
    time.sleep(0.1)

if __name__ == "__main__":
    main_loop()
