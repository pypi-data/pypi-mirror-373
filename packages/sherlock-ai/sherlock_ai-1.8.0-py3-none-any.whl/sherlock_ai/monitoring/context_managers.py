"""
Context managers for monitoring code blocks
"""

import time
import tracemalloc

from .resource_monitor import ResourceMonitor
from .utils import log_memory_usage, log_resource_usage

class MemoryTracker:
    """
    Context manager for tracking memory usage of code blocks
    
    Usage:
        with MemoryTracker("data_processing"):
            # Your memory-intensive code here
            data = load_large_dataset()
            processed = process_data(data)
    """
    
    def __init__(self, name: str, min_duration: float = 0.0, trace_malloc: bool = True):
        self.name = name
        self.min_duration = min_duration
        self.trace_malloc = trace_malloc
        self.start_time = None
        self.start_memory = None
        self.was_tracing = False
    
    def __enter__(self):
        self.was_tracing = tracemalloc.is_tracing()
        if self.trace_malloc and not self.was_tracing:
            tracemalloc.start()
        
        self.start_time = time.time()
        self.start_memory = ResourceMonitor.capture_memory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        end_memory = ResourceMonitor.capture_memory()
        
        if execution_time >= self.min_duration:
            success = exc_type is None
            log_level = "INFO" if success else "ERROR"
            error_msg = str(exc_val) if exc_val else None
            log_memory_usage(self.name, self.start_memory, end_memory, execution_time, success, log_level, error_msg)
        
        # Stop tracing if we started it
        if self.trace_malloc and not self.was_tracing and tracemalloc.is_tracing():
            tracemalloc.stop()
        
        return False  # Don't suppress exceptions


class ResourceTracker:
    """
    Context manager for tracking comprehensive resource usage of code blocks
    
    Usage:
        with ResourceTracker("api_processing", include_io=True):
            # Your resource-intensive code here
            response = api_call()
            result = process_response(response)
    """
    
    def __init__(self, name: str, min_duration: float = 0.0, include_io: bool = True, include_network: bool = False):
        self.name = name
        self.min_duration = min_duration
        self.include_io = include_io
        self.include_network = include_network
        self.start_time = None
        self.start_resources = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.start_resources = ResourceMonitor.capture_resources()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        end_resources = ResourceMonitor.capture_resources()
        
        if execution_time >= self.min_duration:
            success = exc_type is None
            log_level = "INFO" if success else "ERROR"
            error_msg = str(exc_val) if exc_val else None
            log_resource_usage(self.name, self.start_resources, end_resources, execution_time, 
                              success, log_level, self.include_io, self.include_network, error_msg)
        
        return False  # Don't suppress exceptions