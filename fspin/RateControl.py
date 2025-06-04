import time
import warnings
import threading
import asyncio
from functools import wraps
from statistics import mean, stdev
import traceback

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class ReportLogger:
    """Holds all logging/reporting related functions and data formatting."""
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def output(self, msg: str):
        if self.enabled:
            logging.info(msg)
            # print(msg)

    def create_histogram(self, data, bins=10, bar_width=50):
        if not data:
            return "No data to display."
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
        return "\n".join(histogram_lines)

    def generate_report(self, freq, loop_duration, initial_duration, total_duration,
                        total_iterations, avg_frequency, avg_function_duration,
                        avg_loop_duration, avg_deviation, max_deviation, std_dev_deviation,
                        deviations):
        self.output("\n=== RateControl Report ===")
        self.output(f"Set Frequency                  : {freq} Hz")
        self.output(f"Set Loop Duration              : {loop_duration * 1e3:.3f} ms")
        if initial_duration is not None:
            self.output(f"Initial Function Duration      : {initial_duration * 1e3:.3f} ms")
        self.output(f"Total Duration                 : {total_duration:.3f} seconds")
        self.output(f"Total Iterations               : {total_iterations}")
        self.output(f"Average Frequency              : {avg_frequency:.2f} Hz")
        self.output(f"Average Function Duration      : {avg_function_duration * 1e3:.3f} ms")
        self.output(f"Average Loop Duration          : {avg_loop_duration * 1e3:.3f} ms")
        self.output(f"Average Deviation from Desired : {avg_deviation * 1e3:.3f} ms")
        self.output(f"Maximum Deviation              : {max_deviation * 1e3:.3f} ms")
        self.output(f"Std Dev of Deviations          : {std_dev_deviation * 1e3:.3f} ms")
        self.output("\nDistribution of Deviation from Desired Loop Duration (ms):")
        self.output(self.create_histogram(deviations))
        self.output("===========================\n")


def spin(freq, condition_fn=None, report=False, thread=False):
    """
    Decorator to run the decorated function at a specified frequency (Hz).
    Automatically detects if the function is a coroutine and runs it accordingly.
    Optionally generates a performance report upon completion if report is True.
    """
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)
        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=True, report=report, thread=thread)
                await rc.start_spinning(func, condition_fn, *args, **kwargs)
                return rc
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                rc = RateControl(freq, is_coroutine=False, report=report, thread=thread)
                rc.start_spinning(func, condition_fn, *args, **kwargs)
                return rc
            return sync_wrapper
    return decorator


class RateControl:
    def __init__(self, freq, is_coroutine, report=False, thread=True):
        """
        Initialize RateControl.
        :param freq: Frequency in Hz.
        :param is_coroutine: Whether the target function is a coroutine.
        :param report: Enables performance reporting if True.
        :param thread: Use threading for synchronous functions if True.
        """
        self.freq = freq
        self.loop_duration = 1.0 / freq  # Desired loop duration (seconds)
        self.is_coroutine = is_coroutine
        self.report = report
        self.thread = thread
        self.loop_start_time = time.perf_counter()
        if is_coroutine:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self._stop_event = asyncio.Event()
        else:
            self._stop_event = threading.Event()
        self._task = None
        self._thread = None

        # Only record performance metrics if reporting is enabled.
        if self.report:
            self.iteration_times = []
            self.loop_durations = []
            self.deviations = []
            self.initial_duration = None
            self.start_time = None
            self.end_time = None
        else:
            self.iteration_times = None
            self.loop_durations = None
            self.deviations = None
            self.initial_duration = None
            self.start_time = None
            self.end_time = None

        # Logger handles all reporting functions.
        self.logger = ReportLogger(report)

        # Always maintain deviation accumulator for loop compensation.
        self.deviation_accumulator = 0.0

    def spin_sync(self, func, condition_fn, *args, **kwargs):
        """Synchronous spinning using threading with deviation compensation."""
        if condition_fn is None:
            condition_fn = lambda: True

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True
        try:
            while not self._stop_event.is_set() and condition_fn():
                iteration_start = time.perf_counter()
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    func_name = getattr(func, "__name__", "<anonymous>")
                    logging.exception("Exception in spinning function '%s'", func_name)
                    traceback.print_exc()
                    warnings.warn(
                        f"Exception in spinning function '{func_name}': {e}",
                        category=RuntimeWarning,
                    )
                iteration_end = time.perf_counter()
                function_duration = iteration_end - iteration_start

                if self.report:
                    if first_iteration:
                        self.initial_duration = function_duration
                        first_iteration = False
                    else:
                        self.iteration_times.append(function_duration)

                elapsed = time.perf_counter() - loop_start_time
                sleep_duration = max(min(self.loop_duration - elapsed - self.deviation_accumulator,
                                         self.loop_duration), 0)
                if sleep_duration > 0:
                    time.sleep(sleep_duration)

                loop_end_time = time.perf_counter()
                total_loop_duration = loop_end_time - loop_start_time
                deviation = total_loop_duration - self.loop_duration
                # Always update accumulator for proper loop timing.
                self.deviation_accumulator += deviation

                if self.report:
                    self.deviations.append(deviation)
                    self.loop_durations.append(total_loop_duration)

                loop_start_time = time.perf_counter()
        except KeyboardInterrupt:
            self.logger.output("KeyboardInterrupt received. Stopping spin.")
            self._stop_event.set()
        finally:
            self.end_time = time.perf_counter()
            if self.report:
                self.generate_report()

    async def spin_async(self, func, condition_fn, *args, **kwargs):
        """Asynchronous spinning using asyncio with deviation compensation."""
        if condition_fn is None:
            condition_fn = lambda: True  # Default to infinite loop

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True
        try:

            while not self._stop_event.is_set() and condition_fn():
                iteration_start = time.perf_counter()
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    func_name = getattr(func, "__name__", "<anonymous>")
                    logging.exception("Exception in spinning coroutine '%s'", func_name)
                    traceback.print_exc()
                    warnings.warn(
                        f"Exception in spinning coroutine '{func_name}': {e}",
                        category=RuntimeWarning,
                    )
                iteration_end = time.perf_counter()
                function_duration = iteration_end - iteration_start

                if self.report:
                    if first_iteration:
                        self.initial_duration = function_duration
                        first_iteration = False
                    else:
                        self.iteration_times.append(function_duration)

                elapsed = iteration_end - loop_start_time
                sleep_duration = max(min(self.loop_duration - elapsed - self.deviation_accumulator,
                                         self.loop_duration), 0)
                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

                loop_end_time = time.perf_counter()
                total_loop_duration = loop_end_time - loop_start_time
                deviation = total_loop_duration - self.loop_duration
                self.deviation_accumulator += deviation

                if self.report:
                    self.deviations.append(deviation)
                    self.loop_durations.append(total_loop_duration)

                # Update loop_start_time to the current time for the next iteration
                loop_start_time = time.perf_counter()
        except KeyboardInterrupt:
            self.logger.output("KeyboardInterrupt received. Stopping spin.")
            self._stop_event.set()
        except asyncio.CancelledError:
            self.logger.output("Spin task cancelled. Generating report before exit.")
            self._stop_event.set()
            raise
        finally:
            self.end_time = time.perf_counter()
            if self.report:
                self.generate_report()

    def start_spinning_sync(self, func, condition_fn, *args, **kwargs):
        """Starts spinning synchronously, either blocking or in a separate thread."""
        if self.thread:
            self._thread = threading.Thread(
                target=self.spin_sync, args=(func, condition_fn) + args, kwargs=kwargs)
            self._thread.daemon = True
            self._thread.start()
            return self._thread
        else:
            self.spin_sync(func, condition_fn, *args, **kwargs)

    async def start_spinning_async(self, func, condition_fn, *args, **kwargs):
        """Starts spinning asynchronously as an asyncio Task."""
        self._task = asyncio.create_task(self.spin_async(func, condition_fn, *args, **kwargs))
        await self._task
        return self._task

    async def start_spinning_async_wrapper(self, func, condition_fn, *args, **kwargs):
        await self.start_spinning_async(func, condition_fn, *args, **kwargs)

    def start_spinning(self, func, condition_fn, *args, **kwargs):
        """
        Starts the spinning process based on the mode.
        Raises a TypeError if the function type does not match the mode.
        """
        if self.is_coroutine:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("Expected a coroutine function for async mode.")
            return self.start_spinning_async(func, condition_fn, *args, **kwargs)
        else:
            if asyncio.iscoroutinefunction(func):
                raise TypeError("Expected a regular function for sync mode.")
            return self.start_spinning_sync(func, condition_fn, *args, **kwargs)

    def stop_spinning(self):
        """Signals the spinning loop to stop."""
        self._stop_event.set()
        if self.is_coroutine:
            if self._task:
                self._task.cancel()
        else:
            if self._thread:
                self._thread.join()

    def generate_report(self):
        """Aggregates performance data and delegates report generation to the logger."""
        if not self.report or not self.iteration_times:
            self.logger.output("No iterations were recorded.")
            return

        total_duration = self.end_time - self.start_time
        total_iterations = len(self.iteration_times)
        avg_function_duration = mean(self.iteration_times) if self.iteration_times else 0
        avg_deviation = mean(self.deviations) if self.deviations else 0
        max_deviation = max(self.deviations) if self.deviations else 0
        std_dev_deviation = stdev(self.deviations) if len(self.deviations) > 1 else 0.0
        avg_loop_duration = mean(self.loop_durations) if self.loop_durations else 0
        avg_frequency = 1 / avg_loop_duration if avg_loop_duration > 0 else 0

        self.logger.generate_report(
            freq=self.freq,
            loop_duration=self.loop_duration,
            initial_duration=self.initial_duration,
            total_duration=total_duration,
            total_iterations=total_iterations,
            avg_frequency=avg_frequency,
            avg_function_duration=avg_function_duration,
            avg_loop_duration=avg_loop_duration,
            avg_deviation=avg_deviation,
            max_deviation=max_deviation,
            std_dev_deviation=std_dev_deviation,
            deviations=self.deviations
        )
