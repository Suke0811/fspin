import logging

# Library logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def _setup_terminal_logging():
    root_logger = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

class ReportLogger:
    """Holds all logging/reporting related functions and data formatting."""
    def __init__(self, enabled: bool, force_terminal: bool = True):
        self.enabled = enabled
        self.report_generated = False
        if force_terminal:
            _setup_terminal_logging()

    def output(self, msg: str):
        if self.enabled:
            logger.info(msg)
            print(msg)

    def create_histogram(self, data, bins=10, bar_width=50):
        if not data:
            return "No data to display."
        if bins <= 0:
            raise ValueError("bins must be greater than zero")
        data_ms = [d * 1e3 for d in data]  # Convert seconds to ms
        min_val = min(data_ms)
        max_val = max(data_ms)
        bin_size = (max_val - min_val) / bins if bins > 0 else 1
        bin_edges = [min_val + i * bin_size for i in range(bins + 1)]
        bin_counts = [0] * bins

        for value in data_ms:
            for i in range(bins):
                if bin_edges[i] <= value < bin_edges[i + 1]:
                    bin_counts[i] += 1
                    break
            else:
                bin_counts[-1] += 1  # Edge case for max value

        max_count = max(bin_counts) if bin_counts else 0
        histogram_lines = []
        for i in range(bins):
            lower = bin_edges[i]
            upper = bin_edges[i + 1]
            count = bin_counts[i]
            bar_length = int((count / max_count) * bar_width) if max_count > 0 else 0
            bar = '█' * bar_length
            histogram_lines.append(f"{lower:.3f} - {upper:.3f} ms | {bar} ({count})")
        return "\n" + "\n".join(histogram_lines)

    def generate_report(self, freq, loop_duration, initial_duration, total_duration,
                        total_iterations, avg_frequency, avg_function_duration,
                        avg_loop_duration, avg_deviation, max_deviation, std_dev_deviation,
                        deviations, exceptions, mode=None):
        self.report_generated = True
        self.output("\n=== RateControl Report ===")
        if mode:
            self.output(f"Execution Mode                 : {mode}")
        self.output(f"Set Frequency                  : {freq} Hz")
        self.output(f"Set Loop Duration              : {loop_duration * 1e3:.3f} ms")
        if initial_duration is not None:
            self.output(f"Initial Function Duration      : {initial_duration * 1e3:.3f} ms")
        self.output(f"Total Duration                 : {total_duration:.3f} seconds")
        self.output(f"Total Iterations               : {total_iterations}")
        self.output(f"Average Frequency              : {avg_frequency:.3f} Hz")
        self.output(f"Average Function Duration      : {avg_function_duration * 1e3:.3f} ms")
        self.output(f"Average Loop Duration          : {avg_loop_duration * 1e3:.3f} ms")
        self.output(f"Average Deviation from Desired : {avg_deviation * 1e3:.3f} ms")
        self.output(f"Maximum Deviation              : {max_deviation * 1e3:.3f} ms")
        self.output(f"Std Dev of Deviations          : {std_dev_deviation * 1e3:.3f} ms")
        self.output(f"Exception Thrown               : {len(exceptions)} times")
        self.output("Distribution of Deviation from Desired Loop Duration (ms):")
        self.output(self.create_histogram(deviations))
        self.output("===========================\n")
