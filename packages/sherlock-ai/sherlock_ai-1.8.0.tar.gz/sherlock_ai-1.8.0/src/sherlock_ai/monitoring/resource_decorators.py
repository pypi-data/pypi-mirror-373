"""
Monitoring decorators for functions
"""

import time
import functools
import asyncio
import tracemalloc
from typing import Any, Callable, TypeVar, Union

from ..utils.request_context import get_request_id
from .resource_monitor import ResourceMonitor
from .utils import log_memory_usage, log_resource_usage

# Type variable for better type hints
F = TypeVar("F", bound=Callable[..., Any])

def monitor_memory(
    func: F = None,
    *,
    min_duration: float = 0.0,
    log_level: str = "INFO",
    trace_malloc: bool = True
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to monitor memory usage during function execution
    
    Args:
        func: The function to decorate
        min_duration: Only log if execution time >= this value (in seconds)
        log_level: Log level to use (INFO, DEBUG, WARNING, etc.)
        trace_malloc: Whether to use tracemalloc for detailed Python memory tracking
    
    Usage:
        @monitor_memory
        def memory_intensive_function():
            pass
        
        @monitor_memory(trace_malloc=True, min_duration=0.1)
        def critical_function():
            pass
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            # Start memory tracing if requested
            was_tracing = tracemalloc.is_tracing()
            if trace_malloc and not was_tracing:
                tracemalloc.start()
            
            start_time = time.time()
            start_memory = ResourceMonitor.capture_memory()
            function_name = f"{f.__module__}.{f.__name__}"
            
            try:
                result = await f(*args, **kwargs)
                execution_time = time.time() - start_time
                end_memory = ResourceMonitor.capture_memory()
                
                if execution_time >= min_duration:
                    log_memory_usage(function_name, start_memory, end_memory, execution_time, True, log_level)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                end_memory = ResourceMonitor.capture_memory()
                log_memory_usage(function_name, start_memory, end_memory, execution_time, False, "ERROR", str(e))
                raise
            finally:
                # Stop tracing if we started it
                if trace_malloc and not was_tracing and tracemalloc.is_tracing():
                    tracemalloc.stop()
        
        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            # Start memory tracing if requested
            was_tracing = tracemalloc.is_tracing()
            if trace_malloc and not was_tracing:
                tracemalloc.start()
            
            start_time = time.time()
            start_memory = ResourceMonitor.capture_memory()
            function_name = f"{f.__module__}.{f.__name__}"
            
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                end_memory = ResourceMonitor.capture_memory()
                
                if execution_time >= min_duration:
                    log_memory_usage(function_name, start_memory, end_memory, execution_time, True, log_level)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                end_memory = ResourceMonitor.capture_memory()
                log_memory_usage(function_name, start_memory, end_memory, execution_time, False, "ERROR", str(e))
                raise
            finally:
                # Stop tracing if we started it
                if trace_malloc and not was_tracing and tracemalloc.is_tracing():
                    tracemalloc.stop()
        
        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)
    

def monitor_resources(
    func: F = None,
    *,
    min_duration: float = 0.0,
    log_level: str = "INFO",
    include_io: bool = True,
    include_network: bool = False
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to monitor comprehensive resource usage during function execution
    
    Args:
        func: The function to decorate
        min_duration: Only log if execution time >= this value (in seconds)
        log_level: Log level to use (INFO, DEBUG, WARNING, etc.)
        include_io: Whether to include I/O statistics
        include_network: Whether to include network statistics
    
    Usage:
        @monitor_resources
        def resource_intensive_function():
            pass
        
        @monitor_resources(include_io=True, include_network=True)
        def network_function():
            pass
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_resources = ResourceMonitor.capture_resources()
            function_name = f"{f.__module__}.{f.__name__}"
            
            try:
                result = await f(*args, **kwargs)
                execution_time = time.time() - start_time
                end_resources = ResourceMonitor.capture_resources()
                
                if execution_time >= min_duration:
                    log_resource_usage(function_name, start_resources, end_resources, execution_time, 
                                      True, log_level, include_io, include_network)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                end_resources = ResourceMonitor.capture_resources()
                log_resource_usage(function_name, start_resources, end_resources, execution_time, 
                                  False, "ERROR", include_io, include_network, str(e))
                raise
        
        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            start_resources = ResourceMonitor.capture_resources()
            function_name = f"{f.__module__}.{f.__name__}"
            
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                end_resources = ResourceMonitor.capture_resources()
                
                if execution_time >= min_duration:
                    log_resource_usage(function_name, start_resources, end_resources, execution_time, 
                                      True, log_level, include_io, include_network)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                end_resources = ResourceMonitor.capture_resources()
                log_resource_usage(function_name, start_resources, end_resources, execution_time, 
                                  False, "ERROR", include_io, include_network, str(e))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)