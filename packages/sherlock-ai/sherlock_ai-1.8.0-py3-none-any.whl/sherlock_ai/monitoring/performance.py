# app > utils > performance.py
import time
import functools
import asyncio
import logging
from typing import Any, Callable, TypeVar, Union
from sherlock_ai.utils.request_context import get_request_id

# Create a logger specifically for performance metrics
logger = logging.getLogger("PerformanceLogger")

# Type variable for better type hints
F = TypeVar("F", bound=Callable[..., Any])


def log_performance(
    func: F = None,
    *,
    min_duration: float = 0.0,
    include_args: bool = True,
    log_level: str = "INFO"
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to log function execution time

    Args:
        func: The function to decorate (when used without parentheses)
        min_duration: Only log if execution time >= this value (in seconds)
        include_args: Whether to include function arguments in the log
        log_level: Log level to use (INFO, DEBUG, WARNING, etc.)

    Usage:
        @log_performance
        def my_function():
            pass

        @log_performance(min_duration=0.1, include_args=True)
        def slow_function(param1, param2):
            pass
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = f"{f.__module__}.{f.__name__}"
            request_id = get_request_id()

            # Log function arguments if requested
            args_info = ""
            if include_args:
                args_str = str(args)[:100] if args else ""
                kwargs_str = str(kwargs)[:100] if kwargs else ""
                args_info = f" | Args: {args_str} | Kwargs: {kwargs_str}"

            try:
                # Execute the async function
                result = await f(*args, **kwargs)
                execution_time = time.time() - start_time

                # Only log if execution time meets minimum threshold
                if execution_time >= min_duration:
                    log_method = getattr(logger, log_level.lower())
                    log_method(
                        f"PERFORMANCE | {function_name} | SUCCESS | {execution_time:.3f}s{args_info}"
                    )
                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"PERFORMANCE | {function_name} | ERROR | {execution_time:.3f}s | {str(e)}{args_info}"
                )
                raise

        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = f"{f.__module__}.{f.__name__}"
            request_id = get_request_id()

            # Log function arguments if requested
            args_info = ""
            if include_args:
                args_str = str(args)[:100] if args else ""
                kwargs_str = str(kwargs)[:100] if kwargs else ""
                args_info = f" | Args: {args_str} | Kwargs: {kwargs_str}"

            try:
                # Execute the sync function
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time

                # Only log if execution time meets minimum threshold
                if execution_time >= min_duration:
                    log_method = getattr(logger, log_level.lower())
                    log_method(
                        f"PERFORMANCE | {function_name} | SUCCESS | {execution_time:.3f}s{args_info}"
                    )
                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"PERFORMANCE | {function_name} | ERROR | {execution_time:.3f}s | {str(e)}{args_info}"
                )
                raise

        # Return the appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper

    # Handle both @log_performance and @log_performance(...) usage
    if func is None:
        return decorator
    else:
        return decorator(func)


def log_execution_time(name: str, start_time: float, success: bool = True, error: str = None):
    """
    Manual function to log execution time for code blocks

    Usage:
        start_time = time.time()
        try:
            # Your code here
            log_execution_time("database_query", start_time, success=True)
        except Exception as e:
            log_execution_time("database_query", start_time, success=False, error=str(e))
    """
    execution_time = time.time() - start_time
    status = "SUCCESS" if success else "ERROR"
    error_info = f" | {error}" if error else ""

    if success:
        logger.info(f"PERFORMANCE | {name} | {status} | {execution_time:.3f}s{error_info}")
    else:
        logger.error(f"PERFORMANCE | {name} | {status} | {execution_time:.3f}s{error_info}")


# Context manager for measuring code blocks
class PerformanceTimer:
    """
    Context manager for measuring execution time of code blocks

    Usage:
        with PerformanceTimer("database_operation"):
            # Your code here
            pass
    """
    def __init__(self, name: str, min_duration: float = 0.0):
        self.name = name
        self.min_duration = min_duration
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        if execution_time >= self.min_duration:
            if exc_type is None:
                logger.info(f"PERFORMANCE | {self.name} | SUCCESS | {execution_time:.3f}s")
            else:
                logger.error(f"PERFORMANCE | {self.name} | ERROR | {execution_time:.3f}s | {str(exc_val)}")
        return False  # Don’t suppress exceptions
