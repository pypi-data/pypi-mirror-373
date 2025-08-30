import functools
import traceback
import inspect
from typing import Callable, TypeVar, Any
from typing import Union
from .utils import get_llm_cause
import logging
import asyncio
from ..storage import MongoManager

# Type variable for better type hints
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger("ErrorInsightsLogger")

mongo_manager = MongoManager()

def sherlock_error_handler(func: F = None) -> Union[F, Callable[[F], F]]:
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)

            except Exception as e:
                error_message = str(e)
                stack = traceback.format_exc()

                # Call LLM to analyze the error:
                probable_cause = get_llm_cause(error_message, stack)

                # Prepare log entry:
                log_entry = {
                    "function_name": f.__name__,
                    "error_message": error_message,
                    "stack_trace": stack,
                    "probable_cause": probable_cause
                }

                # Save to MongoDB:
                mongo_manager.save(log_entry, "error-insights")

                logger.info(probable_cause)
                # Re-raise or handle as needed
                # raise e

        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                error_message = str(e)
                stack = traceback.format_exc()

                # Call LLM to analyze the error:
                probable_cause = get_llm_cause(error_message, stack)

                # Prepare log entry:
                log_entry = {
                    "function_name": f.__name__,
                    "error_message": error_message,
                    "stack_trace": stack,
                    "probable_cause": probable_cause
                }

                # Save to MongoDB:
                mongo_manager.save(log_entry, "error-insights")

                logger.info(probable_cause)
                # Re-raise or handle as needed
                # raise e

        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper

    return decorator(func) if func else decorator