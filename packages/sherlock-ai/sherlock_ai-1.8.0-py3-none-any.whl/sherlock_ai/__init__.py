"""
Sherlock AI - Your AI assistant package
"""

__version__ = "1.8.0"

# Import main components for easy access
from .logging_setup import sherlock_ai, get_logger, get_logging_stats, get_current_config, SherlockAI
from .config import LoggingConfig, LoggingPresets, LogFileConfig, LoggerConfig
from .utils import set_request_id, get_request_id, clear_request_id
from .monitoring import (
    monitor_memory,
    monitor_resources,
    MemoryTracker,
    ResourceTracker,
    ResourceMonitor,
    log_performance,
    PerformanceTimer,
)
from .analysis import hardcoded_value_detector, CodeAnalyzer
from .auto import enable_auto_instrumentation

# ✅ Logger name constants 
class LoggerNames:
    """Available logger names for use with get_logger()"""
    API = "ApiLogger"
    DATABASE = "DatabaseLogger"
    SERVICES = "ServiceLogger"
    PERFORMANCE = "PerformanceLogger"
    MONITORING = "MonitoringLogger"
    ERRORINSIGHTS = "ErrorInsightsLogger"
    AUTO_INSTRUMENTATION = "AutoInstrumentationLogger"
# ✅ Convenience function
def list_available_loggers():
    """Get list of all available logger names"""
    return [
        LoggerNames.API,
        LoggerNames.DATABASE,
        LoggerNames.SERVICES,
        LoggerNames.PERFORMANCE,
        LoggerNames.MONITORING,
        LoggerNames.ERRORINSIGHTS,
        LoggerNames.AUTO_INSTRUMENTATION
    ]

__all__ = [
    # Performance Logging
    "log_performance", 
    "PerformanceTimer",

    # Memory and Resource Monitoring
    "monitor_memory",
    "monitor_resources",
    "MemoryTracker",
    "ResourceTracker",
    "ResourceMonitor",

    # Logging Configuration
    "SherlockAI",
    "sherlock_ai",
    "get_logger",
    "get_logging_stats",
    "get_current_config",
    "LoggingConfig",
    "LoggingPresets",
    "LogFileConfig",
    "LoggerConfig",

    # Request ID
    "set_request_id",
    "get_request_id",
    "clear_request_id",
    
    # Logger utilities
    "LoggerNames",
    "list_available_loggers",

    # Auto-instrumentation
    "enable_auto_instrumentation",

    # Analysis
    "hardcoded_value_detector",
    "CodeAnalyzer",

    # Package info
    "__version__",
]