"""
Modular monitoring package for Sherlock AI

This package provides decorators and context managers for monitoring:
- Memory usage (Python heap, RSS, VMS)
- CPU utilization
- Disk I/O operations
- Network I/O operations
- Process resource consumption
"""

# Import all public classes and functions
from .resource_decorators import monitor_memory, monitor_resources
from .performance import log_performance, PerformanceTimer
from .context_managers import MemoryTracker, ResourceTracker
from .resource_monitor import ResourceMonitor
from .snapshots import ResourceSnapshot, MemorySnapshot
from .error_insights import sherlock_error_handler
from .monitoring_insights import sherlock_performance_insights
from .utils import log_memory_usage, log_resource_usage

# Export public API
__all__ = [
    # Decorators
    "monitor_memory",
    "monitor_resources",
    "sherlock_error_handler",
    "log_performance",
    "PerformanceTimer",
    "sherlock_performance_insights",
    
    # Context managers
    "MemoryTracker",
    "ResourceTracker",
    
    # Utility classes
    "ResourceMonitor",
    
    # Data classes
    "ResourceSnapshot",
    "MemorySnapshot",
    
    # Utility functions
    "log_memory_usage",
    "log_resource_usage",
]