import time
import warnings
import threading
import asyncio
import platform
import inspect
from functools import wraps
from statistics import mean, stdev
import traceback
from contextlib import contextmanager
import logging
from .reporting import ReportLogger

# Library logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RateControl:
    """
    Controls the execution rate of a function or coroutine.

    This class provides mechanisms to run a function or coroutine at a specified 
    frequency (Hz), with optional performance reporting. It supports both synchronous 
    and asynchronous execution modes, and can run in a separate thread if desired.

    Args:
        freq (float): Target frequency in Hz (cycles per second).
        is_coroutine (bool): Whether the target function is a coroutine.
        report (bool, optional): Enable performance reporting. Defaults to False.
        thread (bool, optional): Use threading for synchronous functions. Defaults to True.

    Raises:
        ValueError: If frequency is less than or equal to zero.

    Attributes:
        loop_duration (float): Desired loop duration in seconds (1/freq).
        is_coroutine (bool): Whether the target function is a coroutine.
        report (bool): Whether performance reporting is enabled.
        thread (bool): Whether to use threading for synchronous functions.
        exceptions (list): List of exceptions raised during execution.
        status (str): Current status ("running" or "stopped").
        mode (str): Current execution mode ("async", "sync-threaded", or "sync-blocking").
        frequency (float): Current target frequency in Hz.
        elapsed_time (float): Time elapsed since start in seconds.
        exception_count (int): Number of exceptions raised during execution.
    """
    def __init__(self, freq, is_coroutine, report=False, thread=True):
        """
        Initialize RateControl.

        Args:
            freq (float): Frequency in Hz.
            is_coroutine (bool): Whether the target function is a coroutine.
            report (bool, optional): Enables performance reporting if True. Defaults to False.
            thread (bool, optional): Use threading for synchronous functions if True. Defaults to True.

        Raises:
            ValueError: If frequency is less than or equal to zero.
        """
        self.loop_start_time = time.perf_counter()
        if freq <= 0:
            raise ValueError("Frequency must be greater than zero.")
        self._freq = freq
        self.loop_duration = 1.0 / freq  # Desired loop duration (seconds)
        self.is_coroutine = is_coroutine
        self.report = report
        self.thread = thread
        self.exceptions = []
        self._own_loop = None

        # Check if running async with high frequency based on OS
        system = platform.system()
        if is_coroutine:
            if system == "Windows" and freq > 65:
                warnings.warn(
                    f"Running async with frequency {freq}Hz on Windows may not achieve desired rate. "
                    f"Windows timer resolution limits async frequency to ~65Hz. Consider using sync mode.",
                    category=RuntimeWarning,
                )
            elif system == "Linux" and freq > 925:
                warnings.warn(
                    f"Running async with frequency {freq}Hz on Linux may not achieve desired rate. "
                    f"Linux timer resolution typically limits async frequency to ~925Hz. Consider using sync mode for higher frequencies.",
                    category=RuntimeWarning,
                )
            elif system == "Darwin" and freq > 4000:  # Darwin is the system name for macOS
                warnings.warn(
                    f"Running async with frequency {freq}Hz on macOS may not achieve desired rate. "
                    f"macOS timer resolution typically limits async frequency to ~4000Hz. Consider using sync mode for higher frequencies.",
                    category=RuntimeWarning,
                )

        if is_coroutine:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                lp = asyncio.new_event_loop()
                asyncio.set_event_loop(lp)
                self._own_loop = lp
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

        self.logger = ReportLogger(report, force_terminal=True)

        # Always maintain deviation accumulator for loop compensation.
        self.deviation_accumulator = 0.0

    def _prepare_condition_fn(self, condition_fn, *, is_async):
        """
        Prepare the condition function, using a default if None is provided.

        Args:
            condition_fn (callable, optional): Regular predicate returning True to continue
                spinning. Awaitable predicates are not supported in synchronous mode.
            is_async (bool): Whether the calling context is asynchronous.

        Returns:
            callable: A function that returns True to continue spinning.
        """
        if getattr(condition_fn, "_fspin_prepared_condition", False):
            return condition_fn

        def _mark_prepared(fn):
            setattr(fn, "_fspin_prepared_condition", True)
            return fn

        if condition_fn is None:
            if is_async:
                async def default_condition():
                    return True

                return _mark_prepared(default_condition)

            def default_condition():
                return True

            return _mark_prepared(default_condition)

        if is_async:
            if inspect.iscoroutinefunction(condition_fn):
                async def async_condition():
                    return bool(await condition_fn())

                return _mark_prepared(async_condition)

            async def async_condition():
                result = condition_fn()
                if inspect.isawaitable(result):
                    result = await result
                return bool(result)

            return _mark_prepared(async_condition)

        if inspect.iscoroutinefunction(condition_fn):
            raise TypeError("Synchronous spinning does not support coroutine condition functions.")

        def sync_condition():
            result = condition_fn()
            if inspect.isawaitable(result):
                raise TypeError("Synchronous spinning does not support awaitable condition functions.")
            return bool(result)

        return _mark_prepared(sync_condition)

    def _handle_exception(self, e, func, is_coroutine=False):
        """
        Handle an exception raised during function execution.

        Args:
            e (Exception): The exception that was raised.
            func (callable): The function that raised the exception.
            is_coroutine (bool, optional): Whether the function is a coroutine. Defaults to False.
        """
        self.exceptions.append(e)
        func_name = getattr(func, "__name__", "<anonymous>")
        func_type = "coroutine" if is_coroutine else "function"
        logger.exception(f"Exception in spinning {func_type} '%s'", func_name)
        traceback.print_exc()
        warnings.warn(
            f"Exception in spinning {func_type} '{func_name}': {e}",
            category=RuntimeWarning,
        )

    def _record_function_duration(self, function_duration, first_iteration):
        """
        Record the function duration for reporting.

        Args:
            function_duration (float): The duration of the function execution in seconds.
            first_iteration (bool): Whether this is the first iteration.

        Returns:
            bool: False if this was the first iteration, otherwise the input value.
        """
        if self.report:
            if first_iteration:
                self.initial_duration = function_duration
                return False
            else:
                self.iteration_times.append(function_duration)
        return first_iteration

    def _calculate_sleep_duration(self, elapsed):
        """
        Calculate the sleep duration to maintain the desired frequency.

        Args:
            elapsed (float): The elapsed time since the start of the loop iteration.

        Returns:
            float: The sleep duration in seconds.
        """
        return max(min(self.loop_duration - elapsed - self.deviation_accumulator,
                       self.loop_duration), 0)

    def _update_metrics(self, total_loop_duration):
        """
        Update metrics after a loop iteration.

        Args:
            total_loop_duration (float): The total duration of the loop iteration.
        """
        deviation = total_loop_duration - self.loop_duration
        self.deviation_accumulator += deviation

        if self.report:
            self.deviations.append(deviation)
            self.loop_durations.append(total_loop_duration)

    def _finalize_spin(self):
        """
        Finalize the spinning process.
        """
        self.end_time = time.perf_counter()
        if self.report:
            self.get_report()

    def spin_sync(self, func, condition_fn, *args, **kwargs):
        """
        Synchronous spinning using threading with deviation compensation.

        Args:
            func (callable): The function to execute at the specified frequency.
            condition_fn (callable, optional): Regular predicate returning True to continue
                spinning. Awaitable predicates are not supported in synchronous mode.
            *args: Positional arguments to pass to func.
            **kwargs: Keyword arguments to pass to func.
        """
        condition_fn = self._prepare_condition_fn(condition_fn, is_async=False)

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True
        try:
            while not self._stop_event.is_set() and condition_fn():
                iteration_start = time.perf_counter()
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    self._handle_exception(e, func)
                iteration_end = time.perf_counter()
                function_duration = iteration_end - iteration_start

                first_iteration = self._record_function_duration(function_duration, first_iteration)

                elapsed = time.perf_counter() - loop_start_time
                sleep_duration = self._calculate_sleep_duration(elapsed)
                if sleep_duration > 0:
                    time.sleep(sleep_duration)

                loop_end_time = time.perf_counter()
                total_loop_duration = loop_end_time - loop_start_time
                self._update_metrics(total_loop_duration)

                loop_start_time = time.perf_counter()
        except KeyboardInterrupt:
            self.logger.output("KeyboardInterrupt received. Stopping spin.")
            self._stop_event.set()
        finally:
            self._finalize_spin()

    async def spin_async(self, func, condition_fn, *args, **kwargs):
        """
        Asynchronous spinning using asyncio with deviation compensation.

        Args:
            func (callable): The coroutine function to execute at the specified frequency.
            condition_fn (callable or coroutine, optional): Predicate evaluated before each
                iteration. Async predicates are awaited automatically.
            *args: Positional arguments to pass to func.
            **kwargs: Keyword arguments to pass to func.
        """
        condition_fn = self._prepare_condition_fn(condition_fn, is_async=True)

        self.start_time = time.perf_counter()
        loop_start_time = self.start_time
        first_iteration = True
        try:
            while not self._stop_event.is_set() and await condition_fn():
                iteration_start = time.perf_counter()
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    self._handle_exception(e, func, is_coroutine=True)
                iteration_end = time.perf_counter()
                function_duration = iteration_end - iteration_start

                first_iteration = self._record_function_duration(function_duration, first_iteration)

                elapsed = iteration_end - loop_start_time
                sleep_duration = self._calculate_sleep_duration(elapsed)
                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

                loop_end_time = time.perf_counter()
                total_loop_duration = loop_end_time - loop_start_time
                self._update_metrics(total_loop_duration)

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
            self._finalize_spin()

    def start_spinning_sync(self, func, condition_fn, *args, **kwargs):
        """
        Starts spinning synchronously, either blocking or in a separate thread.

        Args:
            func (callable): The function to execute at the specified frequency.
            condition_fn (callable, optional): Regular predicate returning True to continue
                spinning. Awaitable predicates are not supported in synchronous mode.
            *args: Positional arguments to pass to func.
            **kwargs: Keyword arguments to pass to func.
                Recognized keyword-only options:
                - wait (bool): If thread=True and wait=True, join the thread before returning.
                  Defaults to False for backward compatibility.

        Returns:
            threading.Thread or None: The thread object if thread=True, None otherwise.
        """
        # Backward-compatible way to accept a keyword-only 'wait' without changing signature
        wait = kwargs.pop("wait", False)

        condition_fn = self._prepare_condition_fn(condition_fn, is_async=False)

        if self.thread:
            self._thread = threading.Thread(
                target=self.spin_sync, args=(func, condition_fn) + args, kwargs=kwargs)
            self._thread.daemon = True
            self._thread.start()
            if wait:
                # Block until the spinning thread completes
                self._thread.join()
            return self._thread
        else:
            # Blocking mode: run in the current thread
            self.spin_sync(func, condition_fn, *args, **kwargs)
            return None

    async def start_spinning_async(self, func, condition_fn, *args, **kwargs):
        """
        Starts spinning asynchronously as an asyncio Task.

        Args:
            func (callable): The coroutine function to execute at the specified frequency.
            condition_fn (callable or coroutine, optional): Predicate evaluated before each
                iteration. Async predicates are awaited automatically.
            *args: Positional arguments to pass to func.
            **kwargs: Keyword arguments to pass to func.

        Returns:
            asyncio.Task: The created task.
        """
        condition_fn = self._prepare_condition_fn(condition_fn, is_async=True)

        self._task = asyncio.create_task(self.spin_async(func, condition_fn, *args, **kwargs))
        return self._task

    async def start_spinning_async_wrapper(self, func, condition_fn=None, *, wait=False, **kwargs):
        """
        Wrapper for start_spinning_async to be used with await.

        Args:
            func (callable): The coroutine function to execute at the specified frequency.
            condition_fn (callable or coroutine, optional): Predicate evaluated before each
                iteration. Async predicates are awaited automatically.
            wait (bool, optional): Whether to await the task (blocking) or return immediately
                (fire-and-forget). Defaults to False (fire-and-forget).
            **kwargs: Keyword arguments to pass to func.

        Returns:
            RateControl: The RateControl instance if wait=True, otherwise the asyncio.Task.
        """
        task = await self.start_spinning_async(func, condition_fn, **kwargs)

        if wait:
            try:
                await task
            except asyncio.CancelledError:
                # Task was cancelled, which is expected when condition is met
                pass

        return self if wait else task

    def start_spinning(self, func, condition_fn, *args, **kwargs):
        """
        Starts the spinning process based on the mode.

        Args:
            func (callable): The function or coroutine to execute at the specified frequency.
            condition_fn (callable or coroutine, optional): Predicate evaluated before each
                iteration. Async predicates are awaited automatically; sync contexts require
                a regular callable returning a truthy value.
            *args: Positional arguments to pass to func.
            **kwargs: Keyword arguments to pass to func.

        Returns:
            threading.Thread, asyncio.Task, or None: The created thread or task, or None.

        Raises:
            TypeError: If the function type does not match the mode.
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
        """
        Signals the spinning loop to stop.
        """
        self._stop_event.set()
        if self.is_coroutine:
            if self._task:
                self._task.cancel()
        else:
            if self._thread:
                # Avoid deadlock if stop_spinning is called from within the worker thread
                current = threading.current_thread()
                if self._thread.is_alive() and current is not self._thread:
                    self._thread.join()
        if self._own_loop is not None:
            self._own_loop.close()
            self._own_loop = None

    def get_report(self, output=True):
        """
        Aggregates performance data and delegates report generation to the logger.

        Args:
            output (bool, optional): Whether to print the report. Defaults to True.

        Returns:
            dict: Performance statistics as a dictionary.
        """
        if not self.report or (not self.iteration_times and self.initial_duration is None):
            self.logger.output("No iterations were recorded.")
            return {}

        end_time = self.end_time or time.perf_counter()
        total_duration = end_time - self.start_time
        total_iterations = len(self.iteration_times)
        if self.initial_duration is not None:
            total_iterations += 1
        avg_function_duration = mean(self.iteration_times) if self.iteration_times else 0
        avg_deviation = mean(self.deviations) if self.deviations else 0
        max_deviation = max(self.deviations) if self.deviations else 0
        std_dev_deviation = stdev(self.deviations) if len(self.deviations) > 1 else 0.0
        avg_loop_duration = mean(self.loop_durations) if self.loop_durations else 0
        avg_frequency = 1 / avg_loop_duration if avg_loop_duration > 0 else 0

        if output:
            self.logger.generate_report(
                freq=self._freq, loop_duration=self.loop_duration, initial_duration=self.initial_duration,
                total_duration=total_duration, total_iterations=total_iterations, avg_frequency=avg_frequency,
                avg_function_duration=avg_function_duration, avg_loop_duration=avg_loop_duration,
                avg_deviation=avg_deviation, max_deviation=max_deviation, std_dev_deviation=std_dev_deviation,
                deviations=self.deviations, exceptions=self.exceptions, mode=self.mode)

        return {"frequency": self._freq, "loop_duration": self.loop_duration, "initial_duration": self.initial_duration,
                "total_duration": total_duration, "total_iterations": total_iterations, "avg_frequency": avg_frequency,
                "avg_function_duration": avg_function_duration, "avg_loop_duration": avg_loop_duration,
                "avg_deviation": avg_deviation, "max_deviation": max_deviation, "std_dev_deviation": std_dev_deviation,
                "deviations": self.deviations, "exceptions": self.exceptions, "exception_count": self.exception_count}

    def is_running(self):
        """
        Check if the spinning loop is running.

        Returns:
            bool: True if the loop is running, False otherwise.
        """
        return not self._stop_event.is_set()

    @property
    def elapsed_time(self):
        """
        Get the elapsed time since the start of spinning.

        Returns:
            float: Elapsed time in seconds.
        """
        if self.start_time is None:
            return 0.0
        return time.perf_counter() - self.start_time

    @property
    def frequency(self):
        """
        Get the current loop frequency in Hz.

        Returns:
            float: Current frequency in Hz.
        """
        return self._freq

    @frequency.setter
    def frequency(self, value):
        """
        Set the loop frequency and update loop duration accordingly.

        Args:
            value (float): New frequency in Hz.

        Raises:
            ValueError: If frequency is less than or equal to zero.
        """
        if value <= 0:
            raise ValueError("Frequency must be greater than zero.")
        self._freq = value
        self.loop_duration = 1.0 / value

    @property
    def status(self):
        """
        Get the current status of the spinning loop.

        Returns:
            str: "running" if the loop is running, "stopped" otherwise.
        """
        return "running" if self.is_running() else "stopped"

    @property
    def mode(self):
        """
        Get the current execution mode.

        Returns:
            str: "async", "sync-threaded", or "sync-blocking".
        """
        return "async" if self.is_coroutine else "sync-threaded" if self.thread else "sync-blocking"

    @property
    def exception_count(self):
        """
        Get the number of exceptions raised during execution.

        Returns:
            int: Number of exceptions.
        """
        return len(self.exceptions)

    def __str__(self):
        """
        Get a string representation of the RateControl object.

        Returns:
            str: String representation.
        """
        lines = [
            "=== RateControl Status ===",
            f"Mode                 : {self.mode}",
            f"Target Frequency     : {self._freq:.3f} Hz",
            f"Loop Duration        : {self.loop_duration * 1e3:.3f} ms",
            f"Elapsed Time         : {self.elapsed_time:.3f} s",
            f"Running              : {self.status}",
        ]
        if self.report and self.iteration_times:
            avg_func = mean(self.iteration_times)
            avg_loop = mean(self.loop_durations)
            avg_dev = mean(self.deviations)
            lines += [
                f"Average Function Time: {avg_func * 1e3:.3f} ms",
                f"Average Loop Time    : {avg_loop * 1e3:.3f} ms",
                f"Avg Deviation        : {avg_dev * 1e3:.3f} ms",
                f"Iterations Recorded  : {len(self.iteration_times)}"
            ]
        return "\n".join(lines)

    def __repr__(self):
        """
        Get a developer-friendly representation of the RateControl object.

        Returns:
            str: Developer-friendly representation.
        """
        return (f"<RateControl _freq={self._freq:.2f}Hz, duration={self.loop_duration * 1e3:.2f}ms, "
                f"elapsed={self.elapsed_time:.2f}s, status={self.status}>")
