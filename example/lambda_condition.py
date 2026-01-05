import time
import sys
import os

# Add the project root to sys.path so we can import fspin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fspin import rate

def lambda_sync_example():
    print("--- Synchronous Lambda Condition Example ---")
    counter = 0
    
    def work():
        nonlocal counter
        counter += 1
        print(f"Iteration {counter}")
        time.sleep(0.1)

    # Initialize rate control at 10 Hz
    rc = rate(freq=10, is_coroutine=False)
    
    # Use a lambda function as the condition
    # The loop will continue as long as the counter is less than 5
    rc.spin_sync(work, condition_fn=lambda: counter < 5)
    
    print(f"Loop finished after {counter} iterations.")

async def lambda_async_example():
    print("\n--- Asynchronous Lambda Condition Example ---")
    counter = 0
    
    async def work():
        nonlocal counter
        counter += 1
        print(f"Iteration {counter}")
        await asyncio.sleep(0.1)

    # Initialize rate control at 10 Hz
    rc = rate(freq=10, is_coroutine=True)
    
    # Use a lambda function as the condition
    # The loop will continue as long as the counter is less than 5
    await rc.spin_async(work, condition_fn=lambda: counter < 5)
    
    print(f"Loop finished after {counter} iterations.")

if __name__ == "__main__":
    import asyncio
    lambda_sync_example()
    asyncio.run(lambda_async_example())
