import functools
from typing import Callable, TypeVar, Any, Union

from .resource_decorators import monitor_memory, monitor_resources
from .error_insights import sherlock_error_handler
from .performance import log_performance

# Type variable for better type hints
F = TypeVar("F", bound=Callable[..., Any])

def global_monitor(
    func: F = None,
    *,
    # Global toggles for each monitoring type
    memory: bool = True,
    resources: bool = True,
    performance: bool = True,
    error_handling: bool = True,

    # Memory monitoring parameters
    memory_min_duration: float = 0.0,
    memory_log_level: str = "INFO",
    trace_malloc: bool = True,

    # Resources monitoring parameters
    resources_min_duration: float = 0.0,
    resources_log_level: str = "INFO",
    include_io: bool = True,
    include_network: bool = True,

    # Performance monitoring parameters
    performance_min_duration: float = 0.0,
    performance_log_level: str = "INFO",
    include_args: bool = True,

    # Global settings
    global_min_duration: float = None,
    global_log_level: str = None,
) -> Union[F, Callable[[F], F]]:
    def decorator(f: F) -> F:
        # Apply global overrides if specified
        final_memory_min_duration = global_min_duration if global_min_duration is not None else memory_min_duration
        final_memory_log_level = global_log_level if global_log_level is not None else memory_log_level
        
        final_resources_min_duration = global_min_duration if global_min_duration is not None else resources_min_duration
        final_resources_log_level = global_log_level if global_log_level is not None else resources_log_level
        
        final_performance_min_duration = global_min_duration if global_min_duration is not None else performance_min_duration
        final_performance_log_level = global_log_level if global_log_level is not None else performance_log_level
        
        # Start with the original function
        decorated_func = f

        # Apply decorators in reverse order (outermost last)
        # Order: error_handling -> performance -> resources -> memory -> original_function

        if performance:
            decorated_func = log_performance(
                decorated_func,
                min_duration=final_performance_min_duration,
                include_args=include_args,
                log_level=final_performance_log_level
            )
            
        if memory:
            decorated_func = monitor_memory(
                decorated_func,
                min_duration=final_memory_min_duration,
                log_level=final_memory_log_level,
                trace_malloc=trace_malloc,
            )

        if resources:
            decorated_func = monitor_resources(
                decorated_func,
                min_duration=final_resources_min_duration,
                log_level=final_resources_log_level,
                include_io=include_io,
                include_network=include_network,
            )

        if error_handling:
            decorated_func = sherlock_error_handler(decorated_func)

        return decorated_func
    
    # Handle both @global_monitor and @global_monitor(...) usage
    if func is None:
        return decorator
    else:
        return decorator(func)
    
# Convenience presets for common use cases
def monitor_all(func: F = None, **kwargs) -> Union[F, Callable[[F], F]]:
    """Convenience decorator that applies all monitoring with default settings"""
    return global_monitor(func, **kwargs)

def monitor_critical(func: F = None, **kwargs) -> Union[F, Callable[[F], F]]:
    """Convenience decorator for critical functions with comprehensive monitoring"""
    defaults = {
        'memory': True,
        'resources': True, 
        'performance': True,
        'error_handling': True,
        'global_min_duration': 0.01,  # Log everything that takes > 10ms
        'global_log_level': 'WARNING',
        'include_args': True,
        'include_io': True,
        'include_network': True,
        'trace_malloc': True
    }
    defaults.update(kwargs)  # Allow overrides
    return global_monitor(func, **defaults)

def monitor_performance_only(func: F = None, **kwargs) -> Union[F, Callable[[F], F]]:
    """Convenience decorator for performance monitoring only"""
    defaults = {
        'memory': False,
        'resources': False,
        'performance': True,
        'error_handling': False,
        'include_args': False
    }
    defaults.update(kwargs)  # Allow overrides
    return global_monitor(func, **defaults)

def monitor_errors_only(func: F = None, **kwargs) -> Union[F, Callable[[F], F]]:
    """Convenience decorator for error handling only"""
    defaults = {
        'memory': False,
        'resources': False,
        'performance': False,
        'error_handling': True
    }
    defaults.update(kwargs)  # Allow overrides
    return global_monitor(func, **defaults)