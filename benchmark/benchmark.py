import os
import sys
import time
import asyncio
import json
import platform
import statistics
from fspin import spin, loop

# Frequencies to test
FREQUENCIES = [10, 100, 1000, 2000, 5000, 10000]
# Duration for each test in seconds
TEST_DURATION = 3
# Number of iterations for each frequency
NUM_ITERATIONS = 1

def get_system_info():
    """Get system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
    }

class ResultCollector:
    """Collect and store benchmark results."""
    def __init__(self):
        self.results = {
            "system_info": get_system_info(),
            "sync_results": {},
            "async_results": {},
        }

    def add_sync_result(self, freq, result):
        """Add a synchronous benchmark result."""
        if freq not in self.results["sync_results"]:
            self.results["sync_results"][freq] = []
        self.results["sync_results"][freq].append(result)

    def add_async_result(self, freq, result):
        """Add an asynchronous benchmark result."""
        if freq not in self.results["async_results"]:
            self.results["async_results"][freq] = []
        self.results["async_results"][freq].append(result)

    def calculate_statistics(self):
        """Calculate statistics for all results."""
        stats = {
            "system_info": self.results["system_info"],
            "sync_stats": {},
            "async_stats": {},
        }

        # Calculate statistics for sync results
        for freq, results in self.results["sync_results"].items():
            actual_freqs = [r["avg_frequency"] for r in results]
            deviations = [r["std_dev_deviation"] for r in results]
            stats["sync_stats"][freq] = {
                "mean_frequency": statistics.mean(actual_freqs),
                "mean_deviation": statistics.mean(deviations),
           }

        # Calculate statistics for async results
        for freq, results in self.results["async_results"].items():
            actual_freqs = [r["avg_frequency"] for r in results]
            deviations = [r["std_dev_deviation"] for r in results]
            stats["async_stats"][freq] = {
                "mean_frequency": statistics.mean(actual_freqs),
                "mean_deviation": statistics.mean(deviations),
            }

        return stats

    def save_results(self, filename):
        """Save results to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

    def save_statistics(self, filename):
        """Save statistics to a JSON file."""
        stats = self.calculate_statistics()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)

# Synchronous benchmark
def run_sync_benchmark(collector):
    """Run synchronous benchmarks for all frequencies."""
    print("Running synchronous benchmarks...")

    for freq in FREQUENCIES:
        print(f"Testing frequency: {freq} Hz")

        for i in range(NUM_ITERATIONS):
            print(f"  Iteration {i+1}/{NUM_ITERATIONS}")

            # Create a timer to stop the benchmark after TEST_DURATION seconds
            stop_time = time.time() + TEST_DURATION

            # Define the test function
            def sync_test():
                # No sleep to allow maximum frequency
                return time.time() >= stop_time

            # Run the benchmark using loop context manager
            with loop(sync_test, freq=freq, report=True, thread=True) as rc:
                # Wait until the test duration is complete
                time.sleep(TEST_DURATION)

            # Extract results using get_report method
            report = rc.get_report(output=False)

            # Use the correct keys from the report
            result = {
                "avg_frequency": report.get("avg_frequency", 0),
                "avg_function_duration": report.get("avg_function_duration", 0),
                "avg_loop_duration": report.get("avg_loop_duration", 0),
                "avg_deviation": report.get("avg_deviation", 0),
                "max_deviation": report.get("max_deviation", 0),
                "std_dev_deviation": report.get("std_dev_deviation", 0),
                "total_iterations": report.get("total_iterations", len(rc.iteration_times) if hasattr(rc, "iteration_times") else 0),
            }

            collector.add_sync_result(freq, result)

# Asynchronous benchmark
async def run_async_benchmark(collector):
    """Run asynchronous benchmarks for all frequencies."""
    print("Running asynchronous benchmarks...")

    for freq in FREQUENCIES:
        print(f"Testing frequency: {freq} Hz")

        for i in range(NUM_ITERATIONS):
            print(f"  Iteration {i+1}/{NUM_ITERATIONS}")

            # Create a timer to stop the benchmark after TEST_DURATION seconds
            stop_time = time.time() + TEST_DURATION

            # Define the test function
            async def async_test():
                # Simple function that simulates some work
                await asyncio.sleep(0.0001)  # Small sleep to simulate work
                return time.time() >= stop_time

            # Run the benchmark using async loop context manager
            async with loop(async_test, freq=freq, report=True, thread=True) as rc:
                # Wait until the test duration is complete
                await asyncio.sleep(TEST_DURATION)

            # Extract results using get_report method
            report = rc.get_report(output=False)

            # Use the correct keys from the report
            result = {
                "avg_frequency": report.get("avg_frequency", 0),
                "avg_function_duration": report.get("avg_function_duration", 0),
                "avg_loop_duration": report.get("avg_loop_duration", 0),
                "avg_deviation": report.get("avg_deviation", 0),
                "max_deviation": report.get("max_deviation", 0),
                "std_dev_deviation": report.get("std_dev_deviation", 0),
                "total_iterations": report.get("total_iterations", len(rc.iteration_times) if hasattr(rc, "iteration_times") else 0),
            }

            collector.add_async_result(freq, result)

def generate_markdown_report(stats_file, output_file):
    """Generate a markdown report from the statistics."""
    with open(stats_file, 'r') as f:
        stats = json.load(f)

    system_info = stats["system_info"]

    with open(output_file, 'w') as f:
        # Write header
        f.write("# fspin Benchmark Results\n\n")

        # Write system information
        f.write("## System Information\n\n")
        f.write(f"- OS: {system_info['os']} {system_info['os_version']}\n")
        f.write(f"- Python Version: {system_info['python_version']}\n")
        f.write(f"- Processor: {system_info['processor']}\n\n")

        # Write synchronous results
        f.write("## Synchronous Results\n\n")
        f.write("| Frequency (Hz) | Actual Frequency (Hz) |  Mean Deviation (ms) |\n")
        f.write("|----------------|------------------------|------------------------|\n")

        for freq in sorted(stats["sync_stats"].keys()):
            result = stats["sync_stats"][str(freq)]
            f.write(f"| {freq} | {result['mean_frequency']:.2f} |  {result['mean_deviation'] * 1000:.3f} | \n")

        f.write("\n")

        # Write asynchronous results
        f.write("## Asynchronous Results\n\n")
        f.write("| Frequency (Hz) | Actual Frequency (Hz) | Mean Deviation (ms) | \n")
        f.write("|----------------|------------------------|------------------------|\n")

        for freq in sorted(stats["async_stats"].keys()):
            result = stats["async_stats"][str(freq)]
            f.write(f"| {freq} | {result['mean_frequency']:.2f} |  {result['mean_deviation'] * 1000:.3f} |\n")

async def main():
    """Main function."""
    collector = ResultCollector()

    # Run synchronous benchmarks
    run_sync_benchmark(collector)

    # Run asynchronous benchmarks
    await run_async_benchmark(collector)

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Save results with absolute paths
    collector.save_results(os.path.join(script_dir, "benchmark_results.json"))
    collector.save_statistics(os.path.join(script_dir, "benchmark_stats.json"))

    # Generate markdown report with absolute paths
    generate_markdown_report(
        os.path.join(script_dir, "benchmark_stats.json"), 
        os.path.join(script_dir, "benchmark_report.md")
    )

    results_path = os.path.join(script_dir, "benchmark_results.json")
    stats_path = os.path.join(script_dir, "benchmark_stats.json")
    report_path = os.path.join(script_dir, "benchmark_report.md")

    print(f"Benchmarks completed. Results saved to {results_path} and {stats_path}.")
    print(f"Markdown report saved to {report_path}.")

if __name__ == "__main__":
    asyncio.run(main())
