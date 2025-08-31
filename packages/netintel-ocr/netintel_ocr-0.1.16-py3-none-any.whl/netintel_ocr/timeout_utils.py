"""Timeout utilities for handling long-running operations."""

import signal
import time
from contextlib import contextmanager
from typing import Optional, Any, Callable


class TimeoutException(Exception):
    """Exception raised when an operation times out."""
    pass


@contextmanager
def timeout(seconds: int, error_message: str = "Operation timed out"):
    """
    Context manager for adding timeout to operations.
    
    Args:
        seconds: Timeout in seconds
        error_message: Error message to display on timeout
    """
    def timeout_handler(signum, frame):
        raise TimeoutException(error_message)
    
    # Set the timeout handler
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def with_progress_message(message: str, done_message: str = "Done"):
    """
    Decorator to print progress messages before and after a function.
    
    Args:
        message: Message to print before function execution
        done_message: Message to print after completion
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            print(f"    {message}...", end="", flush=True)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                print(f" {done_message} ({elapsed:.1f}s)")
                return result
            except TimeoutException:
                print(f" TIMEOUT!")
                raise
            except Exception as e:
                print(f" ERROR: {str(e)[:50]}")
                raise
        return wrapper
    return decorator


def retry_with_timeout(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    timeout_seconds: int = 30,
    max_retries: int = 1,
    fallback: Optional[Callable] = None
) -> Any:
    """
    Execute a function with timeout and retry logic.
    
    Args:
        func: Function to execute
        args: Function arguments
        kwargs: Function keyword arguments
        timeout_seconds: Timeout for each attempt
        max_retries: Maximum number of retry attempts
        fallback: Fallback function if all attempts fail
        
    Returns:
        Function result or fallback result
    """
    if kwargs is None:
        kwargs = {}
    
    for attempt in range(max_retries + 1):
        try:
            with timeout(timeout_seconds, f"Operation timed out after {timeout_seconds}s"):
                return func(*args, **kwargs)
        except TimeoutException:
            if attempt < max_retries:
                print(f"    Timeout on attempt {attempt + 1}, retrying...")
            else:
                print(f"    Operation timed out after {max_retries + 1} attempts")
                if fallback:
                    print(f"    Using fallback method...")
                    return fallback(*args, **kwargs)
                raise
        except Exception as e:
            if attempt < max_retries:
                print(f"    Error on attempt {attempt + 1}: {str(e)[:50]}, retrying...")
            else:
                raise


class ProgressTracker:
    """Track and display progress for multi-step operations."""
    
    def __init__(self, total_steps: int = 0):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.step_times = []
    
    def start_step(self, description: str):
        """Start a new step with description."""
        self.current_step += 1
        step_start = time.time()
        if self.total_steps > 0:
            print(f"    Step {self.current_step}/{self.total_steps}: {description}...", end="", flush=True)
        else:
            print(f"    {description}...", end="", flush=True)
        return step_start
    
    def end_step(self, step_start: float, status: str = "Done"):
        """End current step and show elapsed time."""
        elapsed = time.time() - step_start
        self.step_times.append(elapsed)
        print(f" {status} ({elapsed:.1f}s)")
    
    def get_total_time(self) -> float:
        """Get total elapsed time."""
        return time.time() - self.start_time
    
    def get_average_step_time(self) -> float:
        """Get average time per step."""
        if not self.step_times:
            return 0
        return sum(self.step_times) / len(self.step_times)