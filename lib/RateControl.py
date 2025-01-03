import time
import warnings
import threading
import asyncio
from functools import wraps
from statistics import mean, stdev
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def spin(freq, condition_fn=None, report=False, thread=False):
    """
    Decorator to run the decorated function at a specified frequency (Hz).
    Supports both fixed frequencies and dynamically settable frequencies through callables.

    :param freq: Frequency in Hertz at which to execute the function, or a callable returning the frequency.
    :param condition_fn: Optional callable that returns True to continue spinning.
    :param report: If True, generates a performance report upon completion.
    :param thread: If False, use a blocking while loop; if True, use a separate thread.
    """
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Determine whether `freq` is callable or fixed
            frequency = freq() if callable(freq) else freq
            rc = RateControl(frequency, is_coroutine=False, report=report, thread=thread)
            rc.start_spinning(func, condition_fn, *args, **kwargs)
            return rc  # Return the RateControl instance

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Determine whether `freq` is callable or fixed
            frequency = freq() if callable(freq) else freq
            rc = RateControl(frequency, is_coroutine=True, report=report, thread=thread)
            await rc.start_spinning_async(func, condition_fn, *args, **kwargs)
            return rc  # Return the RateControl instance

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator


class RateControl:
    def __init__(self, freq, is_coroutine, report=False, thread=True):
        """
        Initialize the RateControl.

        :param freq: Frequency in Hertz at which to execute the function.
        :param is_coroutine: Boolean indicating if the function is a coroutine.
        :param report: Boolean indicating if performance reporting is enabled.
        :param thread: Boolean indicating if threading should be used for synchronous functions.
        """
        self.freq = freq
        self.loop_duration = 1.0 / freq  # Desired loop duration in seconds
        self.is_coroutine = is_coroutine
        self.report = report
        self.thread = thread
        self.loop_start_time = time.perf_counter()
        self._stop_event = threading.Event() if not is_coroutine else asyncio.Event()
        self._task = None  # For asyncio
        self._thread = None  # For threading

        # Performance metrics
        self.iteration_times = []      # Function execution durations (seconds)
        self.loop_durations = []       # Actual loop durations (seconds)
        self.deviations = []           # Deviations from desired loop duration (seconds)
        self.initial_duration = None   # First function execution duration (seconds)
        self.start_time = None
        self.end_time = None

        self.deviation_accumulator = 0.0  # the deviation accumulator

    def spin_sync(self, func, condition_fn, *args, **kwargs):
        """
        Synchronous spinning using threading with deviation compensation.

        :param func: The function to execute.
        :param condition_fn: A callable that returns True to continue spinning.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        """
        if condition_fn is None:
            condition_fn = lambda: True  # Default to infinite loop

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True

        while not self._stop_event.is_set() and condition_fn():
            iteration_start = time.perf_counter()
            try:
                func(*args, **kwargs)
            except Exception as e:
                warnings.warn(f"Exception in spinning function: {e}", category=RuntimeWarning)

            iteration_end = time.perf_counter()
            function_duration = iteration_end - iteration_start

            if first_iteration:
                self.initial_duration = function_duration
                first_iteration = False
            else:
                self.iteration_times.append(function_duration)

            # Calculate sleep duration with deviation compensation
            elapsed = time.perf_counter() - loop_start_time
            sleep_duration = self.loop_duration - elapsed - self.deviation_accumulator

            # Limit sleep_duration to prevent negative or excessively large sleep times
            sleep_duration = max(min(sleep_duration, self.loop_duration), 0)

            if sleep_duration > 0:
                time.sleep(sleep_duration)

            loop_end_time = time.perf_counter()
            total_loop_duration = loop_end_time - loop_start_time

            # Calculate deviation and update accumulator
            deviation = total_loop_duration - self.loop_duration
            self.deviations.append(deviation)
            self.deviation_accumulator += deviation

            # Cap the accumulator
            max_accumulator = self.loop_duration
            self.deviation_accumulator = max(min(self.deviation_accumulator, max_accumulator), -max_accumulator)

            # Update loop_end_time and calculate total loop duration
            loop_end_time = time.perf_counter()
            total_loop_duration = loop_end_time - loop_start_time
            self.loop_durations.append(total_loop_duration) # Update with total loop duration

            loop_start_time = time.perf_counter()


        self.end_time = time.perf_counter()
        if self.report:
            self.generate_report()

    async def spin_async(self, func, condition_fn, *args, **kwargs):
        """
        Asynchronous spinning using asyncio with deviation compensation.

        :param func: The coroutine function to execute.
        :param condition_fn: A callable that returns True to continue spinning.
        :param args: Positional arguments for the coroutine.
        :param kwargs: Keyword arguments for the coroutine.
        """
        if condition_fn is None:
            condition_fn = lambda: True  # Default to infinite loop

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True

        while not self._stop_event.is_set() and condition_fn():
            iteration_start = time.perf_counter()
            try:
                await func(*args, **kwargs)
            except Exception as e:
                warnings.warn(f"Exception in spinning coroutine: {e}", category=RuntimeWarning)
            iteration_end = time.perf_counter()
            function_duration = iteration_end - iteration_start

            if first_iteration:
                self.initial_duration = function_duration
                first_iteration = False
            else:
                self.iteration_times.append(function_duration)

            # Calculate sleep duration with deviation compensation
            elapsed = iteration_end - loop_start_time
            sleep_duration = self.loop_duration - elapsed - self.deviation_accumulator

            # Limit sleep_duration to prevent negative or excessively large sleep times
            sleep_duration = max(min(sleep_duration, self.loop_duration), 0)

            if sleep_duration > 0:
                await asyncio.sleep(sleep_duration)

            loop_end_time = time.perf_counter()
            total_loop_duration = loop_end_time - loop_start_time

            # Calculate deviation and update accumulator
            deviation = total_loop_duration - self.loop_duration
            self.deviations.append(deviation)
            self.deviation_accumulator += deviation

            # Cap the accumulator
            max_accumulator = self.loop_duration
            self.deviation_accumulator = max(min(self.deviation_accumulator, max_accumulator), -max_accumulator)
            # Update loop_start_time for next iteration
            loop_start_time += self.loop_duration

            # Record the actual loop duration
            self.loop_durations.append(total_loop_duration)

        self.end_time = time.perf_counter()
        if self.report:
            self.generate_report()

    def start_spinning_sync(self, func, condition_fn, *args, **kwargs):
        """
        Starts the spinning process either in a separate thread or blocking mode based on the thread flag.

        :param func: The function to execute.
        :param condition_fn: A callable that returns True to continue spinning.
        :return: The thread object or None for blocking mode.
        """
        if self.thread:
            self._thread = threading.Thread(target=self.spin_sync, args=(func, condition_fn) + args, kwargs=kwargs)
            self._thread.daemon = True
            self._thread.start()
            return self._thread
        else:
            self.spin_sync(func, condition_fn, *args, **kwargs)

    async def start_spinning_async(self, func, condition_fn, *args, **kwargs):
        """
        Starts the spinning process as an asyncio Task (asynchronous mode).

        :param func: The coroutine function to execute.
        :param condition_fn: A callable that returns True to continue spinning.
        :param args: Positional arguments for the coroutine.
        :param kwargs: Keyword arguments for the coroutine.
        :return: The asyncio Task object.
        """
        self._task = asyncio.create_task(self.spin_async(func, condition_fn, *args, **kwargs))
        await self._task
        return self._task

    async def start_spinning_async_wrapper(self, func, condition_fn, *args, **kwargs):
        """
        Wrapper to ensure that start_spinning_async is properly awaited.
        """
        await self.start_spinning_async(func, condition_fn, *args, **kwargs)

    def start_spinning(self, func, condition_fn, *args, **kwargs):
        """
        Starts the spinning process based on the mode.

        :param func: The function or coroutine function to execute.
        :param condition_fn: A callable that returns True to continue spinning.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: The thread or asyncio Task object.
        """
        if self.is_coroutine:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("Detected async_mode, but the function is not a coroutine.")
            return self.start_spinning_async(func, condition_fn, *args, **kwargs)
        else:
            if asyncio.iscoroutinefunction(func):
                raise TypeError("Detected sync_mode, but the function is a coroutine.")
            return self.start_spinning_sync(func, condition_fn, *args, **kwargs)

    def stop_spinning(self):
        """
        Signals the spinning loop to stop.
        """
        self._stop_event.set()
        if self.is_coroutine:
            if self._task:
                self._task.cancel()
        else:
            if self._thread:
                self._thread.join()

    def generate_report(self):
        """
        Generates and prints the performance report, including function execution durations,
        average loop duration, and deviation histogram.
        """
        if not self.iteration_times and self.initial_duration is None:
            print("No iterations were recorded.")
            return

        total_duration = self.end_time - self.start_time  # In seconds
        total_iterations = len(self.iteration_times)
        average_function_duration = mean(self.iteration_times) if self.iteration_times else 0  # seconds
        average_deviation = mean(self.deviations) if self.deviations else 0  # seconds
        max_deviation = max(self.deviations) if self.deviations else 0  # seconds
        std_dev_deviation = stdev(self.deviations) if len(self.deviations) > 1 else 0.0  # seconds

        average_loop_duration = mean(self.loop_durations) if self.loop_durations else 0  # seconds
        average_frequency = 1/average_loop_duration if average_loop_duration > 0 else 0  # Hz

        # Generate distribution histogram based on deviations
        histogram = self.create_histogram(self.deviations)

        print("\n=== RateControl Report ===")
        print(f"Set Frequency                  : {self.freq} Hz")
        print(f"Set Loop Duration              : {self.loop_duration * 1e3:.3f} ms")
        if self.initial_duration is not None:
            print(f"Initial Function Duration      : {self.initial_duration * 1e3:.3f} ms")
        print(f"Total Duration                 : {total_duration:.3f} seconds")
        print(f"Total Iterations               : {total_iterations}")
        print(f"Average Frequency              : {average_frequency:.2f} Hz")
        print(f"Average Function Duration      : {average_function_duration * 1e3:.3f} ms")
        print(f"Average Loop Duration          : {average_loop_duration * 1e3:.3f} ms")
        print(f"Average Deviation from Desired : {average_deviation * 1e3:.3f} ms")
        print(f"Maximum Deviation              : {max_deviation * 1e3:.3f} ms")
        print(f"Std Dev of Deviations          : {std_dev_deviation * 1e3:.3f} ms")
        print("\nDistribution of Deviation from Desired Loop Duration (ms):")
        print(histogram)
        print("===========================\n")

    def create_histogram(self, data, bins=10, bar_width=50):
        """
        Creates a textual histogram for the provided data.

        :param data: List of numerical deviation values in seconds.
        :param bins: Number of bins in the histogram.
        :param bar_width: Maximum width of the histogram bars.
        :return: A string representing the histogram.
        """
        if not data:
            return "No data to display."
        data_ms = [d * 1e3 for d in data]  # Convert to milliseconds
        min_val = min(data_ms)
        max_val = max(data_ms)
        bin_size = (max_val - min_val) / bins if bins > 0 else 1
        bin_edges = [min_val + i * bin_size for i in range(bins + 1)]
        bin_counts = [0 for _ in range(bins)]

        for value in data_ms:
            for i in range(bins):
                if bin_edges[i] <= value < bin_edges[i + 1]:
                    bin_counts[i] += 1
                    break
            else:
                bin_counts[-1] += 1  # Edge case for max_val

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
