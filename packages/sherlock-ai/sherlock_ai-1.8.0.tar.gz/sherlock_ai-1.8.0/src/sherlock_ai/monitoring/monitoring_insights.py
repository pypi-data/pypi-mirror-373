"""
This module contains the logic for generating insights from the monitoring data.
"""
# TODO: Add a way to get only the user called function and injest in the  llm call to generate insights instead of the whole function source which include the sherlock_ai code

from typing import List, TypeVar, Callable, Any, Union
import functools
from ..storage import MongoManager
import asyncio
import time
from .utils import generate_performance_insights, FunctionSource
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

F = TypeVar("F", bound=Callable[..., Any])

mongo_manager = MongoManager()

def sherlock_performance_insights(
    func: F = None,
    *,
    monitoring_type: str = "function",
    latency: int = 5,
    include_args: bool = True,
    log_level: str = "INFO"
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to generate performance insights.

    Args:
        func: The function to decorate (when used without parentheses)
        monitoring_type: The type of monitoring to perform (function, endpoint, etc.)
        latency: The minimum latency to consider for insights (in seconds)
        include_args: Whether to include function arguments in the insights
        log_level: The log level to use for the insights

    Usage:
        @sherlock_performance_insights(latency=3, include_args=True)
        def my_function():
            pass
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await f(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            if duration >= latency:
                async def run_insight_job():
                    # print(f.__code__)
                    function_source = FunctionSource._extract_user_function_sources_only(f)
                    function_source_str = "\n\n".join(function_source.values())
                    insights = generate_performance_insights(f.__name__, args, kwargs, duration, function_source_str)
                    performance_insights_entry = {
                        "function_name": f.__name__,
                        # "args": args,
                        "kwargs": kwargs,
                        "duration": duration,
                        "function_source": function_source_str,
                        "insights": insights,
                        "created_at": datetime.now(timezone.utc) # get local time
                    }
                    mongo_manager.save(performance_insights_entry, "performance-insights")

                asyncio.create_task(run_insight_job())  # Run in background for async functions

            return result
        
        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = f(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            if duration >= latency:
                async def run_insight_job():
                    print("Running insight job")
                    # print(f.__code__)
                    function_source = FunctionSource._extract_user_function_sources_only(f)
                    function_source_str = "\n\n".join(function_source.values())
                    insights = generate_performance_insights(f.__name__, args, kwargs, duration, function_source_str)
                    performance_insights_entry = {
                        "function_name": f.__name__,
                        # "args": args,
                        "kwargs": kwargs,
                        "duration": duration,
                        "function_source": function_source_str,
                        "insights": insights,
                        "created_at": datetime.now(timezone.utc) # get local time
                    }
                    mongo_manager.save(performance_insights_entry, "performance-insights")

                def run_in_executor(): # Run in background for sync functions
                    # loop = asyncio.new_event_loop()
                    # asyncio.set_event_loop(loop)
                    # loop.run_until_complete(run_insight_job())
                    # loop.close()
                    asyncio.run(run_insight_job())


                with ThreadPoolExecutor() as executor:
                    executor.submit(run_in_executor)  # Run in background for sync functions

            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper
    
    return decorator if func is None else decorator(func)