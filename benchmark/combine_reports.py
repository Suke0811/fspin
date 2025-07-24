import os
import json
import glob
import sys

def create_unified_report(artifacts_dir, output_file, test_duration, iterations):
    """
    Create a unified benchmark report from all benchmark_stats.json files.

    Args:
        artifacts_dir: Directory containing the artifacts
        output_file: Path to the output markdown file
        test_duration: Duration of each test in seconds
        iterations: Number of iterations for each test
    """
    # Find all stats files
    stats_files = glob.glob(os.path.join(artifacts_dir, 'benchmark-results-*/benchmark_stats.json'))

    if not stats_files:
        print(f"No benchmark_stats.json files found in {artifacts_dir}")
        return

    # Create a dictionary to store all results
    all_results = {
        'sync': {},  # Will be a nested dict: {frequency: {os_python: result}}
        'async': {}  # Will be a nested dict: {frequency: {os_python: result}}
    }

    # Create dictionaries to store results by OS and Python version
    results_by_os = {
        'sync': {},  # Will be a nested dict: {os: {frequency: {python_version: result}}}
        'async': {}  # Will be a nested dict: {os: {frequency: {python_version: result}}}
    }

    # Create dictionary for accuracy table (Python version rows, OS columns)
    accuracy_table = {
        'sync': {},  # Will be a nested dict: {python_version: {os: accuracy}}
        'async': {}  # Will be a nested dict: {python_version: {os: accuracy}}
    }

    # Process each stats file
    for stats_file in stats_files:
        # Extract OS and Python version from the path
        parts = os.path.normpath(stats_file).split(os.path.sep)
        artifact_name = [p for p in parts if p.startswith('benchmark-results-')][0]
        artifact_parts = artifact_name.split('-')

        # The artifact name format is benchmark-results-{os_name}-python-{python_version}
        # So the OS name is at index 2, and the Python version is at index 5
        os_name = artifact_parts[2]
        python_version = artifact_parts[5]

        # Create a key for this OS/Python combination
        # Extract the OS name without 'latest' and the Python version
        os_key = os_name.split('-')[0]  # Remove '-latest' if present
        os_python_key = f"{os_key}-{python_version}"

        # Load the stats
        with open(stats_file, 'r') as f:
            stats = json.load(f)

        # Process synchronous results
        for freq, result in stats['sync_stats'].items():
            # For the original table format
            if freq not in all_results['sync']:
                all_results['sync'][freq] = {}
            all_results['sync'][freq][os_python_key] = result

            # For the OS-grouped tables
            if os_key not in results_by_os['sync']:
                results_by_os['sync'][os_key] = {}
            if freq not in results_by_os['sync'][os_key]:
                results_by_os['sync'][os_key][freq] = {}
            results_by_os['sync'][os_key][freq][python_version] = result

            # For the accuracy table (Python version rows, OS columns)
            if python_version not in accuracy_table['sync']:
                accuracy_table['sync'][python_version] = {}
            # Calculate accuracy as percentage (actual / target * 100)
            target_freq = int(freq)
            actual_freq = result["mean_frequency"]
            accuracy = (actual_freq / target_freq) * 100
            accuracy_table['sync'][python_version][os_key] = accuracy

        # Process asynchronous results
        for freq, result in stats['async_stats'].items():
            # For the original table format
            if freq not in all_results['async']:
                all_results['async'][freq] = {}
            all_results['async'][freq][os_python_key] = result

            # For the OS-grouped tables
            if os_key not in results_by_os['async']:
                results_by_os['async'][os_key] = {}
            if freq not in results_by_os['async'][os_key]:
                results_by_os['async'][os_key][freq] = {}
            results_by_os['async'][os_key][freq][python_version] = result

            # For the accuracy table (Python version rows, OS columns)
            if python_version not in accuracy_table['async']:
                accuracy_table['async'][python_version] = {}
            # Calculate accuracy as percentage (actual / target * 100)
            target_freq = int(freq)
            actual_freq = result["mean_frequency"]
            accuracy = (actual_freq / target_freq) * 100
            accuracy_table['async'][python_version][os_key] = accuracy

    # Create the report
    with open(output_file, 'w') as report:
        report.write('# fspin Benchmark Results\n\n')
        report.write('## Test Configuration\n\n')
        report.write(f'- Test Duration: {test_duration} seconds\n')
        report.write(f'- Iterations per Test: {iterations}\n\n')

        # Create accuracy tables (Python version rows, OS columns)
        report.write('## Accuracy Tables (% of Target Frequency)\n\n')

        # Get all unique OS and Python versions
        all_os = set()
        all_python_versions = set()
        for mode in ['sync', 'async']:
            for python_version in accuracy_table[mode]:
                all_python_versions.add(python_version)
                for os_key in accuracy_table[mode][python_version]:
                    all_os.add(os_key)

        all_os = sorted(all_os)
        all_python_versions = sorted(all_python_versions, key=lambda v: [int(x) for x in v.split('.')])

        # Synchronous accuracy table
        report.write('### Synchronous Accuracy\n\n')

        # Table header
        report.write('| Python Version |')
        for os_key in all_os:
            report.write(f' {os_key} (%) |')
        report.write('\n')

        # Table separator
        report.write('|----------------|')
        for _ in all_os:
            report.write('----------------|')
        report.write('\n')

        # Table rows
        for python_version in all_python_versions:
            report.write(f'| {python_version} |')
            for os_key in all_os:
                if python_version in accuracy_table['sync'] and os_key in accuracy_table['sync'][python_version]:
                    accuracy = accuracy_table['sync'][python_version][os_key]
                    report.write(f' {accuracy:.2f} |')
                else:
                    report.write(' N/A |')
            report.write('\n')

        report.write('\n')

        # Asynchronous accuracy table
        report.write('### Asynchronous Accuracy\n\n')

        # Table header
        report.write('| Python Version |')
        for os_key in all_os:
            report.write(f' {os_key} (%) |')
        report.write('\n')

        # Table separator
        report.write('|----------------|')
        for _ in all_os:
            report.write('----------------|')
        report.write('\n')

        # Table rows
        for python_version in all_python_versions:
            report.write(f'| {python_version} |')
            for os_key in all_os:
                if python_version in accuracy_table['async'] and os_key in accuracy_table['async'][python_version]:
                    accuracy = accuracy_table['async'][python_version][os_key]
                    report.write(f' {accuracy:.2f} |')
                else:
                    report.write(' N/A |')
            report.write('\n')

        report.write('\n')

        # Include detailed results organized by OS with Python versions as columns
        report.write('## Detailed Results by Operating System\n\n')

        # Process each OS
        for os_key in sorted(results_by_os['sync'].keys()):
            report.write(f'### {os_key}\n\n')

            # Get all Python versions for this OS
            os_python_versions = set()
            for freq in results_by_os['sync'][os_key]:
                os_python_versions.update(results_by_os['sync'][os_key][freq].keys())
            for freq in results_by_os['async'][os_key]:
                os_python_versions.update(results_by_os['async'][os_key][freq].keys())

            os_python_versions = sorted(os_python_versions, key=lambda v: [int(x) for x in v.split('.')])

            # Synchronous results table
            report.write('#### Synchronous Results\n\n')

            # Table header
            report.write('| Frequency (Hz) |')
            for python_version in os_python_versions:
                report.write(f' Python {python_version} (Hz) |')
            report.write('\n')

            # Table separator
            report.write('|----------------|')
            for _ in os_python_versions:
                report.write('----------------------|')
            report.write('\n')

            # Table rows
            for freq in sorted([int(f) for f in results_by_os['sync'][os_key].keys()]):
                freq_str = str(freq)
                report.write(f'| {freq} |')
                for python_version in os_python_versions:
                    if python_version in results_by_os['sync'][os_key][freq_str]:
                        result = results_by_os['sync'][os_key][freq_str][python_version]
                        report.write(f' {result["mean_frequency"]:.2f} |')
                    else:
                        report.write(' N/A |')
                report.write('\n')

            report.write('\n')

            # Asynchronous results table
            report.write('#### Asynchronous Results\n\n')

            # Table header
            report.write('| Frequency (Hz) |')
            for python_version in os_python_versions:
                report.write(f' Python {python_version} (Hz) |')
            report.write('\n')

            # Table separator
            report.write('|----------------|')
            for _ in os_python_versions:
                report.write('----------------------|')
            report.write('\n')

            # Table rows
            for freq in sorted([int(f) for f in results_by_os['async'][os_key].keys()]):
                freq_str = str(freq)
                report.write(f'| {freq} |')
                for python_version in os_python_versions:
                    if python_version in results_by_os['async'][os_key][freq_str]:
                        result = results_by_os['async'][os_key][freq_str][python_version]
                        report.write(f' {result["mean_frequency"]:.2f} |')
                    else:
                        report.write(' N/A |')
                report.write('\n')

            report.write('\n')

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python combine_reports.py <artifacts_dir> <output_file> <test_duration> <iterations>")
        sys.exit(1)

    artifacts_dir = sys.argv[1]
    output_file = sys.argv[2]
    test_duration = sys.argv[3]
    iterations = sys.argv[4]

    create_unified_report(artifacts_dir, output_file, test_duration, iterations)
    print(f"Unified benchmark report created at {output_file}")
