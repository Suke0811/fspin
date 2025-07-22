# fspin Benchmark Workflow

This repository includes a GitHub Actions workflow for benchmarking the maximum frequency that can be achieved with fspin on different Python versions and operating systems.

## Running the Benchmark

To run the benchmark:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Benchmark" workflow from the left sidebar
3. Click the "Run workflow" button
4. Configure the parameters:
   - **Test Duration**: Duration of each test in seconds (default: 3)
   - **Iterations**: Number of iterations for each test (default: 3)
5. Click "Run workflow"

## Benchmark Configuration

The benchmark tests:
- **Operating Systems**: Ubuntu, Windows, macOS
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12 (3.13 and 3.14 are configured but excluded as they might not be available yet)
- **Frequencies**: 10 Hz, 100 Hz, 1000 Hz, 2000 Hz, 5000 Hz, 10000 Hz
- **Modes**: Synchronous and Asynchronous

## Understanding the Results

After the workflow completes, you can download the results:

1. Go to the completed workflow run
2. Scroll down to the "Artifacts" section
3. Download the "combined-benchmark-report" artifact
4. Extract and open the `combined_benchmark_report.md` file

The report includes:
- System information for each test environment
- Tables showing the actual frequency achieved and deviation statistics for each target frequency
- Results for both synchronous and asynchronous modes

### Metrics Explained

- **Actual Frequency (Hz)**: The average frequency actually achieved during the test
- **Std Dev Frequency (Hz)**: Standard deviation of the frequency across iterations
- **Mean Deviation (ms)**: Average deviation from the desired loop duration
- **Std Dev Deviation (ms)**: Standard deviation of the deviations

## Performance Considerations

- **Synchronous Mode**: Generally achieves higher accuracy across all platforms
- **Asynchronous Mode**: Performance varies significantly by OS:
  - Windows: Limited by timer granularity (~15 ms)
  - Linux: Generally provides finer sleep resolution
  - macOS: Performance varies by Python version

## Customizing the Benchmark

To modify the benchmark:

1. Edit `benchmark.py` to change the frequencies tested or other parameters
2. Edit `.github/workflows/benchmark.yml` to change the matrix of Python versions and operating systems
