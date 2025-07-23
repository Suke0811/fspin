import os
import re

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
benchmark_path = os.path.join(script_dir, 'benchmark.py')

# Read the benchmark.py file
with open(benchmark_path, 'r') as f:
    content = f.read()

# Get environment variables with defaults
test_duration = os.environ.get('TEST_DURATION', '3')
num_iterations = os.environ.get('NUM_ITERATIONS', '1')

# Replace the hardcoded values using regex to be more flexible with the actual values
content = re.sub(r'TEST_DURATION = \d+', f'TEST_DURATION = {test_duration}', content)
content = re.sub(r'NUM_ITERATIONS = \d+', f'NUM_ITERATIONS = {num_iterations}', content)

# Write the updated content back to the file
with open(benchmark_path, 'w') as f:
    f.write(content)

print(f"Updated benchmark.py with TEST_DURATION={test_duration} and NUM_ITERATIONS={num_iterations}")
