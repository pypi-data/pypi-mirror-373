# Sherlock AI

A Python package for performance monitoring and logging utilities that helps you track execution times and debug your applications with ease.

## Features

- 🎯 **Performance Decorators**: Easy-to-use decorators for tracking function execution times
- 🧠 **Memory Monitoring**: Track Python memory usage with detailed heap and tracemalloc integration
- 📊 **Resource Monitoring**: Monitor CPU, memory, I/O, and network usage during function execution
- ⏱️ **Context Managers**: Monitor code block execution with simple context managers
- 🔧 **Advanced Configuration System**: Complete control over logging with dataclass-based configuration
- ⚡ **Simplified Configuration**: Auto-expanding file paths - just specify base names instead of full paths
- 🎛️ **Configuration Presets**: Pre-built setups for development, production, and testing environments
- 🔄 **Async/Sync Support**: Works seamlessly with both synchronous and asynchronous functions
- 📈 **Request Tracking**: Built-in request ID tracking for distributed systems
- 📁 **Flexible Log Management**: Enable/disable log files, custom directories, and rotation settings
- 🏷️ **Logger Name Constants**: Easy access to available logger names with autocomplete support
- 🔍 **Logger Discovery**: Programmatically discover available loggers in your application
- 🐛 **Development-Friendly**: Optimized for FastAPI auto-reload and development environments
- 🎨 **Modular Architecture**: Clean, focused modules for different monitoring aspects
- 🏗️ **Class-Based Architecture**: Advanced `SherlockAI` class for instance-based logging management
- 🔄 **Runtime Reconfiguration**: Change logging settings without application restart
- 🧹 **Resource Management**: Automatic cleanup and context manager support
- 🔍 **Logging Introspection**: Query current logging configuration and statistics
- 📋 **JSON Format Support**: Choose between standard log format or structured JSON output for better parsing and analysis
- 🔍 **Code Analysis**: Automatic detection and refactoring of hardcoded values using AST parsing and LLM suggestions
- 🗄️ **MongoDB Integration**: Automatic error insights storage with MongoDB support
- 🚨 **Error Analysis**: AI-powered error analysis with automatic probable cause detection
- 💡 **Performance Insights**: AI-powered performance analysis that intelligently extracts user-defined function source code.
- 🔄 **Auto-Instrumentation**: Zero-code setup for popular frameworks like FastAPI, automatically instrumenting routes with monitoring decorators.

## Installation

```bash
pip install sherlock-ai
```

## Authors

- **Pranaw Mishra** - [pranawmishra73@gmail.com](mailto:pranawmishra73@gmail.com)
- **Kunal Aggarwal** - [aggarwalkunu263@gmail.com](mailto:aggarwalkunu263@gmail.com)

## Quick Start

### Basic Setup

```python
from sherlock_ai import sherlock_ai, get_logger, log_performance, hardcoded_value_detector
from sherlock_ai.monitoring import sherlock_error_handler
import time

# Initialize logging (call once at application startup)
sherlock_ai()

# Get a logger for your module
logger = get_logger(__name__)

@log_performance
@hardcoded_value_detector
@sherlock_error_handler
def my_function():
    # Your code here - hardcoded values will be automatically detected
    # Errors will be automatically analyzed and stored in MongoDB
    try:
        time.sleep(1)
        logger.info("Processing completed")
        return "result"
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

# This will log: PERFORMANCE | my_module.my_function | SUCCESS | 1.003s
# And automatically refactor any hardcoded values to constants
# And analyze any errors with AI-powered insights
result = my_function()
```

### Class-Based Setup (Advanced)

```python
from sherlock_ai import SherlockAI, get_logger, log_performance

# Initialize with class-based approach
logger_manager = SherlockAI()
logger_manager.setup()

# Get a logger for your module
logger = get_logger(__name__)

@log_performance
def my_function():
    logger.info("Processing with class-based setup")
    return "result"

# Later, reconfigure without restart
from sherlock_ai import LoggingPresets
logger_manager.reconfigure(LoggingPresets.development())

# Or use as context manager
with SherlockAI() as temp_logger:
    # Temporary logging configuration
    logger.info("This uses temporary configuration")
# Automatically cleaned up
```

### Auto-Instrumentation (Sentry-Style Setup)

Sherlock AI now supports automatic instrumentation for supported frameworks like FastAPI. This allows you to get comprehensive monitoring with a zero-code setup, without needing to add decorators to every route.

**How it Works:**
When enabled, Sherlock AI will "monkey-patch" the framework's routing methods. This means it automatically wraps your endpoint functions with the standard suite of monitoring decorators (`log_performance`, `monitor_memory`, `monitor_resources`, `sherlock_error_handler`) at runtime.

**Example Setup for FastAPI:**

```python
# main.py
from fastapi import FastAPI
from sherlock_ai import SherlockAI, LoggingConfig, get_logger

# 1. Initialize Sherlock AI with auto-instrumentation enabled
# This should be done BEFORE the FastAPI app is created.
config = LoggingConfig(
    auto_instrument=True, # default 
    log_format_type="json" # default
)
logging_manager = SherlockAI(config=config)
logging_manager.setup()

logger = get_logger(__name__)

# 2. Create your FastAPI app as usual
app = FastAPI()

# 3. Define your routes WITHOUT any manual decorators
@app.get("/health")
def health_check():
    # This endpoint is now automatically monitored for:
    # - Performance
    # - Memory Usage
    # - Resource Consumption
    # - Error Insights
    logger.info("Health check endpoint was called.")
    return {"status": "healthy"}

@app.get("/error")
def trigger_error():
    # Errors in this endpoint will also be captured automatically
    # and sent for AI analysis.
    result = 1 / 0
    return {"result": result}
```

With this setup, you no longer need to manually decorate each FastAPI route, simplifying your code while still getting the full benefits of Sherlock AI's monitoring capabilities.

### Using Logger Name Constants

```python
from sherlock_ai import sherlock_ai, get_logger, LoggerNames, list_available_loggers

# Initialize logging
sherlock_ai()

# Use predefined logger names with autocomplete support
api_logger = get_logger(LoggerNames.API)
db_logger = get_logger(LoggerNames.DATABASE)
service_logger = get_logger(LoggerNames.SERVICES)

# Discover available loggers programmatically
available_loggers = list_available_loggers()
print(f"Available loggers: {available_loggers}")

# Use the loggers
api_logger.info("API request received")        # → logs/api.log
db_logger.info("Database query executed")     # → logs/database.log
service_logger.info("Service operation done") # → logs/services.log
```

### Logging Introspection

```python
from sherlock_ai import sherlock_ai, get_logging_stats, get_current_config

# Initialize logging
sherlock_ai()

# Get current logging statistics
stats = get_logging_stats()
print(f"Logging configured: {stats['is_configured']}")
print(f"Active handlers: {stats['handlers']}")
print(f"Log directory: {stats['logs_dir']}")

# Get current configuration
config = get_current_config()
print(f"Console enabled: {config.console_enabled}")
print(f"Log files: {list(config.log_files.keys())}")
```

### Advanced Configuration

```python
@log_performance(min_duration=0.1, include_args=True, log_level="DEBUG")
def slow_database_query(user_id, limit=10):
    # Only logs if execution time >= 0.1 seconds
    # Includes function arguments in the log
    pass
```

### Context Manager for Code Blocks

```python
from sherlock_ai.performance import PerformanceTimer

with PerformanceTimer("database_operation"):
    # Your code block here
    result = database.query("SELECT * FROM users")
    
# Logs: PERFORMANCE | database_operation | SUCCESS | 0.234s
```

### Async Function Support

```python
@log_performance
async def async_api_call():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# Works automatically with async functions
result = await async_api_call()
```

### Manual Time Logging

```python
from sherlock_ai.performance import log_execution_time
import time

start_time = time.time()
try:
    # Your code here
    result = complex_operation()
    log_execution_time("complex_operation", start_time, success=True)
except Exception as e:
    log_execution_time("complex_operation", start_time, success=False, error=str(e))
```

## Memory and Resource Monitoring

### Memory Monitoring

Track Python memory usage with detailed heap analysis:

```python
from sherlock_ai import monitor_memory, MemoryTracker

# Basic memory monitoring
@monitor_memory
def memory_intensive_function():
    data = [i * i for i in range(1000000)]  # Allocate memory
    processed = sum(data)
    return processed

# Advanced memory monitoring with tracemalloc
@monitor_memory(trace_malloc=True, min_duration=0.1)
def critical_memory_function():
    # Only logs if execution time >= 0.1 seconds
    # Includes detailed Python memory tracking
    large_dict = {i: str(i) * 100 for i in range(10000)}
    return len(large_dict)

# Memory tracking context manager
with MemoryTracker("data_processing"):
    # Your memory-intensive code here
    data = load_large_dataset()
    processed = process_data(data)

# Output example:
# MEMORY | my_module.memory_intensive_function | SUCCESS | 0.245s | Current: 45.67MB | Change: +12.34MB | Traced: 38.92MB (Peak: 52.18MB)
```

### Resource Monitoring

Monitor comprehensive system resources:

```python
from sherlock_ai import monitor_resources, ResourceTracker

# Basic resource monitoring
@monitor_resources
def resource_intensive_function():
    # Monitors CPU, memory, and threads
    result = sum(i * i for i in range(1000000))
    return result

# Advanced resource monitoring with I/O and network
@monitor_resources(include_io=True, include_network=True)
def api_call_function():
    # Monitors CPU, memory, I/O, network, and threads
    response = requests.get("https://api.example.com")
    return response.json()

# Resource tracking context manager
with ResourceTracker("database_operation", include_io=True):
    # Your resource-intensive code here
    connection = database.connect()
    result = connection.execute("SELECT * FROM large_table")
    connection.close()

# Output example:
# RESOURCES | my_module.resource_intensive_function | SUCCESS | 0.156s | CPU: 25.4% | Memory: 128.45MB (+5.23MB) | Threads: 12 | I/O: R:2.34MB W:1.12MB
```

### Combined Monitoring

Use both performance and resource monitoring together:

```python
from sherlock_ai import log_performance, monitor_memory, monitor_resources

@log_performance
@monitor_memory(trace_malloc=True)
@monitor_resources(include_io=True)
def comprehensive_monitoring():
    # This function will be monitored for:
    # - Execution time (performance)
    # - Memory usage (memory)
    # - System resources (CPU, I/O, etc.)
    data = process_large_dataset()
    save_to_database(data)
    return len(data)
```

### Resource Monitor Utilities

Access low-level resource monitoring utilities:

```python
from sherlock_ai import ResourceMonitor

# Capture current resource snapshot
snapshot = ResourceMonitor.capture_resources()
if snapshot:
    print(f"CPU: {snapshot.cpu_percent}%")
    print(f"Memory: {ResourceMonitor.format_bytes(snapshot.memory_rss)}")
    print(f"Threads: {snapshot.num_threads}")

# Capture memory snapshot
memory_snapshot = ResourceMonitor.capture_memory()
print(f"Current memory: {ResourceMonitor.format_bytes(memory_snapshot.current_size)}")

# Format bytes in human-readable format
formatted = ResourceMonitor.format_bytes(1024 * 1024 * 512)  # "512.00MB"
```

## Error Analysis and Storage

### AI-Powered Error Insights

Automatically analyze errors with AI and store insights in MongoDB:

```python
from sherlock_ai.monitoring import sherlock_error_handler
import os

# Set up MongoDB connection (optional)
os.environ["MONGO_URI"] = "mongodb://localhost:27017"

@sherlock_error_handler
def risky_function():
    # Any errors will be automatically analyzed and stored
    result = 1 / 0  # This will trigger error analysis
    return result

# Error insights are automatically:
# 1. Analyzed by AI for probable cause
# 2. Stored in MongoDB (sherlock-meta.error-insights collection)
# 3. Logged with detailed information
```

### MongoDB Integration

Configure MongoDB storage for error insights:

```python
from sherlock_ai.storage import MongoManager

# Initialize MongoDB manager
mongo = MongoManager("mongodb://localhost:27017")

# Manual error insight storage
error_data = {
    "function_name": "my_function",
    "error_message": "Division by zero",
    "stack_trace": "...",
    "probable_cause": "AI analysis result"
}

mongo.save(error_data)
```

## Code Analysis and Refactoring

### Automatic Hardcoded Value Detection

Automatically detect and refactor hardcoded values in your functions:

```python
from sherlock_ai import hardcoded_value_detector

@hardcoded_value_detector
def api_handler():
    url = "https://api.example.com"
    timeout = 30
    message = "Processing request"
    return requests.get(url, timeout=timeout)

# Automatically creates constants.py with:
# API_URL = "https://api.example.com"
# TIMEOUT_SECONDS = 30
# PROCESSING_MESSAGE = "Processing request"
# And updates your function to use these constants
```

### Manual Code Analysis

Use the CodeAnalyzer class for custom analysis:

```python
from sherlock_ai.analysis import CodeAnalyzer

# Initialize with optional Groq API key for intelligent naming
analyzer = CodeAnalyzer()

# Detect hardcoded values in source code
with open('my_file.py', 'r') as f:
    source = f.read()

hardcoded_values = analyzer.detect_hardcoded_values(source)
for value, value_type, node in hardcoded_values:
    constant_name = analyzer.suggest_constant_name(value, value_type, "my_function")
    analyzer.append_to_constants_file(constant_name, value)
```

**Features:**
- **AST-based Detection**: Uses Python's AST parser for accurate analysis
- **Smart Naming**: LLM-powered constant naming with heuristic fallback
- **Automatic Refactoring**: Updates source code to use constants
- **Multiple Value Types**: Detects strings, numbers, and URLs
- **Constants Management**: Automatically manages constants.py file

## Advanced Configuration

### Configuration Presets

```python
from sherlock_ai import sherlock_ai, LoggingPresets

# Development environment - debug level logging
sherlock_ai(LoggingPresets.development())

# Production environment - optimized performance
sherlock_ai(LoggingPresets.production())

# Minimal setup - only basic app logs
sherlock_ai(LoggingPresets.minimal())

# Performance monitoring only
sherlock_ai(LoggingPresets.performance_only())
```

### Custom Configuration

```python
from sherlock_ai import sherlock_ai, LoggingConfig, LogFileConfig, LoggerConfig

# Create completely custom configuration with simplified file paths
config = LoggingConfig(
    logs_dir="my_app_logs",
    log_format_type="json",  # Will create .json files
    console_level="DEBUG",
    log_files={
        # Just specify base names - full paths auto-generated from logs_dir + log_format_type
        "application": LogFileConfig("app", max_bytes=50*1024*1024),
        "errors": LogFileConfig("errors", level="ERROR"),
        "performance": LogFileConfig("perf"),
        "custom": LogFileConfig("custom", backup_count=10)
    },
    loggers={
        "api": LoggerConfig("mycompany.api", log_files=["application", "custom"]),
        "database": LoggerConfig("mycompany.db", log_files=["application"]),
        "performance": LoggerConfig("PerformanceLogger", log_files=["performance"], propagate=False)
    }
)

sherlock_ai(config)
# Creates: my_app_logs/app.json, my_app_logs/errors.json, my_app_logs/perf.json, my_app_logs/custom.json
```

### Simplified vs Full Path Configuration

**Simplified Configuration (Recommended):**
```python
# Automatic path expansion - just specify base names
config = LoggingConfig(
    logs_dir="logs",
    log_format_type="json",  # or "log"
    log_files={
        "app": LogFileConfig("application"),      # → logs/application.json
        "errors": LogFileConfig("error_log"),    # → logs/error_log.json
        "api": LogFileConfig("api_requests"),    # → logs/api_requests.json
    }
)
```

**Real-World Example:**
```python
from sherlock_ai import LoggingConfig, LogFileConfig, SherlockAI

# Production setup with simplified configuration
config = LoggingConfig(
    logs_dir="production_logs",
    log_format_type="json",
    log_files={
        "app": LogFileConfig("application", max_bytes=100*1024*1024),  # 100MB files
        "errors": LogFileConfig("errors", level="ERROR", backup_count=20),
        "api": LogFileConfig("api_requests", backup_count=15),
        "performance": LogFileConfig("performance_metrics"),
    }
)

# This creates:
# production_logs/application.json
# production_logs/errors.json  
# production_logs/api_requests.json
# production_logs/performance_metrics.json

logging_manager = SherlockAI(config)
logging_manager.setup()
```

### JSON Format Logging

Choose between standard log format and structured JSON output:

```python
from sherlock_ai import sherlock_ai, SherlockAI

# Standard format (default) - creates .log files
sherlock_ai()

# JSON format - creates .json files with structured data
sherlock_ai(format_type="json")

# Class-based API with JSON format
logger_manager = SherlockAI()
logger_manager.setup("json")  # Creates app.json, errors.json, etc.
```

**Standard Format Output:**
```
2025-07-15 20:51:19 - aa580b62 - ApiLogger - INFO - Request started
```

**JSON Format Output:**
```json
{"timestamp": "2025-07-15 20:51:19", "level": "INFO", "logger": "ApiLogger", "message": "Request started", "request_id": "aa580b62", "module": "api", "function": "handle_request", "line": 42, "thread": 13672, "thread_name": "MainThread", "process": 22008}
```

**Loading JSON Logs:**
```python
import json

def load_json_logs(filename):
    logs = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line.strip()))
    return logs

# Usage
logs = load_json_logs('logs/api.json')
for log in logs:
    print(f"[{log['timestamp']}] {log['level']}: {log['message']}")
```

### Flexible Log Management

```python
from sherlock_ai import LoggingConfig, sherlock_ai

# Start with default configuration
config = LoggingConfig()

# Disable specific log files
config.log_files["api"].enabled = False
config.log_files["services"].enabled = False

# Change log levels
config.log_files["performance"].level = "DEBUG"
config.console_level = "WARNING"

# Modify file sizes and rotation
config.log_files["app"].max_bytes = 100 * 1024 * 1024  # 100MB
config.log_files["app"].backup_count = 15

# Apply the modified configuration
sherlock_ai(config)
```

### Custom File Names and Directories

```python
from sherlock_ai import LoggingPresets, sherlock_ai

# Use custom file names
config = LoggingPresets.custom_files({
    "app": "logs/application.log",
    "performance": "logs/metrics.log",
    "errors": "logs/error_tracking.log"
})

sherlock_ai(config)
```

### Environment-Specific Configuration

```python
import os
from sherlock_ai import sherlock_ai, LoggingPresets, LoggingConfig

# Configure based on environment
env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    sherlock_ai(LoggingPresets.production())
elif env == "development":
    sherlock_ai(LoggingPresets.development())
elif env == "testing":
    config = LoggingConfig(
        logs_dir="test_logs",
        console_enabled=False,  # No console output during tests
        log_files={"test_results": LogFileConfig("results")}  # → test_logs/results.log
    )
    sherlock_ai(config)
else:
    sherlock_ai()  # Default configuration
```

### Development with FastAPI

The package is optimized for FastAPI development with auto-reload enabled:

```python
# main.py
from sherlock_ai import sherlock_ai
import uvicorn

if __name__ == "__main__":
    # Set up logging once in the main entry point
    sherlock_ai()
    
    # FastAPI auto-reload won't cause duplicate log entries
    uvicorn.run(
        "myapp.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # ✅ Safe to use - no duplicate logs
    )
```

```python
# myapp/api.py
from fastapi import FastAPI, Request
from sherlock_ai import get_logger, LoggerNames, log_performance, monitor_memory

# Don't call sherlock_ai() here - it's already done in main.py
app = FastAPI()
logger = get_logger(LoggerNames.API)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}

# ⚠️ IMPORTANT: Decorator order matters for FastAPI middleware!
@app.middleware("http")  # ✅ Framework decorators must be outermost
@log_performance        # ✅ Then monitoring decorators
@monitor_memory         # ✅ Then other monitoring decorators
async def request_middleware(request: Request, call_next):
    # This will work correctly and log to performance.log
    response = await call_next(request)
    return response
```

### FastAPI Decorator Order ⚠️

**Critical**: Always put FastAPI decorators outermost:

```python
# ✅ CORRECT - Framework decorator first
@app.middleware("http")
@log_performance
@monitor_memory
async def middleware_function(request, call_next):
    pass

# ❌ WRONG - Monitoring decorators interfere with FastAPI
@log_performance
@monitor_memory
@app.middleware("http")  # FastAPI can't find this!
async def middleware_function(request, call_next):
    pass
```

This applies to all framework decorators (`@app.route`, `@app.middleware`, etc.).

## API Reference

### `@log_performance` Decorator

Parameters:
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `include_args` (bool): Whether to include function arguments in the log (default: False)
- `log_level` (str): Log level to use - INFO, DEBUG, WARNING, etc. (default: "INFO")

### `PerformanceTimer` Context Manager

Parameters:
- `name` (str): Name identifier for the operation
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)

### `log_execution_time` Function

Parameters:
- `name` (str): Name identifier for the operation
- `start_time` (float): Start time from `time.time()`
- `success` (bool): Whether the operation succeeded (default: True)
- `error` (str): Error message if operation failed (default: None)

### `@monitor_memory` Decorator

Monitor memory usage during function execution.

Parameters:
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `log_level` (str): Log level to use (default: "INFO")
- `trace_malloc` (bool): Use tracemalloc for detailed Python memory tracking (default: True)

### `@monitor_resources` Decorator

Monitor comprehensive system resources during function execution.

Parameters:
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `log_level` (str): Log level to use (default: "INFO")
- `include_io` (bool): Include I/O statistics (default: True)
- `include_network` (bool): Include network statistics (default: False)

### `MemoryTracker` Context Manager

Track memory usage in code blocks.

Parameters:
- `name` (str): Name identifier for the operation
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `trace_malloc` (bool): Use tracemalloc for detailed tracking (default: True)

### `ResourceTracker` Context Manager

Track comprehensive resource usage in code blocks.

Parameters:
- `name` (str): Name identifier for the operation
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `include_io` (bool): Include I/O statistics (default: True)
- `include_network` (bool): Include network statistics (default: False)

### `ResourceMonitor` Utility Class

Low-level resource monitoring utilities.

Static Methods:
- `capture_resources()`: Capture current system resource snapshot
- `capture_memory()`: Capture current memory usage snapshot
- `format_bytes(bytes_val)`: Format bytes in human-readable format
- `calculate_resource_diff(start, end)`: Calculate differences between snapshots

### Configuration Classes

#### `LoggingConfig`

Main configuration class for the logging system.

Parameters:
- `logs_dir` (str): Directory for log files (default: "logs")
- `log_format` (str): Log message format string
- `date_format` (str): Date format for timestamps
- `console_enabled` (bool): Enable console output (default: True)
- `console_level` (Union[str, int]): Console log level (default: INFO)
- `root_level` (Union[str, int]): Root logger level (default: INFO)
- `log_files` (Dict[str, LogFileConfig]): Log file configurations
- `loggers` (Dict[str, LoggerConfig]): Logger configurations
- `external_loggers` (Dict[str, Union[str, int]]): External library log levels

#### `LogFileConfig`

Configuration for individual log files.

Parameters:
- `filename` (str): **Base filename or full path**. If no directory separators are present, automatically expands to `{logs_dir}/{filename}{extension}` using the parent `LoggingConfig` settings.
- `level` (Union[str, int]): Log level for this file (default: INFO)
- `max_bytes` (int): Maximum file size before rotation (default: 10MB)
- `backup_count` (int): Number of backup files to keep (default: 5)
- `encoding` (str): File encoding (default: "utf-8")
- `enabled` (bool): Whether this log file is enabled (default: True)

**Filename Examples:**
- `"app"` → Expands to `logs/app.log` (or `logs/app.json` if JSON format)
- `"custom/path/file.log"` → Used as-is (no expansion)
- `"/absolute/path/file.log"` → Used as-is (no expansion)

#### `LoggerConfig`

Configuration for individual loggers.

Parameters:
- `name` (str): Logger name
- `level` (Union[str, int]): Logger level (default: INFO)
- `log_files` (List[str]): List of log file names this logger writes to
- `propagate` (bool): Whether to propagate to parent loggers (default: True)
- `enabled` (bool): Whether this logger is enabled (default: True)

### Configuration Presets

#### `LoggingPresets.minimal()`
Basic setup with only console and app log.

#### `LoggingPresets.development()`
Debug-level logging for development environment.

#### `LoggingPresets.production()`
Optimized configuration for production use.

#### `LoggingPresets.performance_only()`
Only performance monitoring logs.

#### `LoggingPresets.custom_files(file_configs)`
Custom file names for standard log types.

Parameters:
- `file_configs` (Dict[str, str]): Mapping of log type to custom filename

### Logger Constants and Discovery

#### `LoggerNames`
Class containing constants for available logger names.

Available constants:
- `LoggerNames.API` - API logger name
- `LoggerNames.DATABASE` - Database logger name  
- `LoggerNames.SERVICES` - Services logger name
- `LoggerNames.PERFORMANCE` - Performance logger name

#### `list_available_loggers()`
Function to discover all available logger names.

Returns:
- `List[str]`: List of all available logger names

Example:
```python
from sherlock_ai import LoggerNames, list_available_loggers

# Use constants with autocomplete
logger = get_logger(LoggerNames.API)

# Discover available loggers
loggers = list_available_loggers()
print(f"Available: {loggers}")
```

### Class-Based API

#### `SherlockAI` Class

Advanced logging management with instance-based configuration.

**Constructor Parameters:**
- `config` (Optional[LoggingConfig]): Configuration object. If None, uses default configuration.

**Methods:**
- `setup(format_type="log")`: Set up logging configuration. Pass "json" for JSON format logs. Returns applied LoggingConfig.
- `reconfigure(new_config)`: Change configuration without restart.
- `cleanup()`: Clean up handlers and resources.
- `get_stats()`: Get current logging statistics.
<!-- - `get_handler_info()`: Get information about current handlers. -->
<!-- - `get_logger_info()`: Get information about configured loggers. -->

**Class Methods:**
- `SherlockAI.get_instance()`: Get or create singleton instance.

**Context Manager Support:**
```python
with SherlockAI(config) as logger_manager:
    # Temporary logging configuration
    pass
# Automatically cleaned up
```

#### `get_logging_stats()`
Get current logging statistics from default instance.

Returns:
- `Dict[str, Any]`: Dictionary containing logging statistics

Example:
```python
from sherlock_ai import get_logging_stats

stats = get_logging_stats()
print(f"Configured: {stats['is_configured']}")
print(f"Handlers: {stats['handlers']}")
```

#### `get_current_config()`
Get current logging configuration from default instance.

Returns:
- `Optional[LoggingConfig]`: Current configuration if available

Example:
```python
from sherlock_ai import get_current_config

config = get_current_config()
if config:
    print(f"Console enabled: {config.console_enabled}")
```

### `@sherlock_error_handler` Decorator

Automatically analyze errors with AI and store insights in MongoDB.

Features:
- AI-powered error analysis using LLM
- Automatic MongoDB storage of error insights
- Support for both sync and async functions
- Detailed error logging with probable causes

### `@hardcoded_value_detector` Decorator

Automatically detect and refactor hardcoded values in functions.

Parameters:
- `analyzer` (CodeAnalyzer, optional): Custom CodeAnalyzer instance to use

### `CodeAnalyzer` Class

Analyze Python code and detect hardcoded values.

**Constructor Parameters:**
- `api_key` (str, optional): Groq API key for LLM-based naming
- `constants_file` (str, optional): Path to constants file (default: "constants.py")

**Methods:**
- `detect_hardcoded_values(source_code)`: Detect hardcoded strings, numbers, and URLs in source code
- `suggest_constant_name(value, value_type, context)`: Suggest appropriate constant names
- `append_to_constants_file(constant_name, value)`: Add constants to the constants file
- `modify_function_code(source_code, replacements, file_path)`: Refactor code to use constants

### `MongoManager` Class

Manage MongoDB connections and error insight storage.

**Constructor Parameters:**
- `mongo_uri` (str, optional): MongoDB connection string. If not provided, uses MONGO_URI environment variable.

**Methods:**
- `save(data)`: Save error insight data to MongoDB collection
- `enabled` (bool): Property indicating if MongoDB backend is configured and available

### `@sherlock_performance_insights` Decorator

Automatically analyze performance bottlenecks with AI and store insights in MongoDB.

Features:
- AI-powered performance analysis using LLM
- Automatic MongoDB storage of performance insights
- Support for both sync and async functions
- Intelligently extracts only user-defined function source code for analysis

**Storage Details:**
- Database: `sherlock-meta`
- Collection: `error-insights`, `performance-insights`
- Automatic connection management

## Configuration

### Basic Logging Setup

```python
from sherlock_ai import sherlock_ai, get_logger

# Initialize logging (call once at application startup)
sherlock_ai()  # Default: creates .log files

# Or use JSON format for structured logging
sherlock_ai(format_type="json")  # Creates .json files

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("Application started")
logger.error("Something went wrong")
```

**Default Log Files Created:**
When you call `sherlock_ai()` with no arguments, it automatically creates a `logs/` directory with these files:
- `app.log` - All INFO+ level logs from root logger
- `errors.log` - Only ERROR+ level logs from any logger
- `api.log` - Logs from `app.api` logger (empty unless you use this logger)
- `database.log` - Logs from `app.core.dbConnection` logger
- `services.log` - Logs from `app.services` logger  
- `performance.log` - Performance monitoring logs from your `@log_performance` decorators

### Using Specific Loggers

```python
import logging
from sherlock_ai import sherlock_ai

sherlock_ai()

# Use specific loggers to populate their respective log files
api_logger = logging.getLogger("app.api")
db_logger = logging.getLogger("app.core.dbConnection")
services_logger = logging.getLogger("app.services")

# These will go to their specific log files
api_logger.info("API request received")           # → api.log
db_logger.info("Database query executed")        # → database.log
services_logger.info("Service operation done")   # → services.log
```

### Request ID Tracking

```python
from sherlock_ai.utils.helper import get_request_id, set_request_id

# Set a request ID for the current context
request_id = set_request_id("req-12345")

# Get current request ID for distributed tracing
current_id = get_request_id()
```

### Complete Application Example

```python
from sherlock_ai import sherlock_ai, get_logger, log_performance, PerformanceTimer

# Initialize logging first
sherlock_ai()
logger = get_logger(__name__)

@log_performance
def main():
    logger.info("Application starting")
    
    with PerformanceTimer("initialization"):
        # Your initialization code
        pass
    
    logger.info("Application ready")

if __name__ == "__main__":
    main()
```

## Log Output Format

The package produces structured log messages with the following format:

```
{timestamp} - {request_id} - {logger_name} - {log_level} - {message_content}
```

Where:
- `{timestamp}`: Date and time of the log entry
- `{request_id}`: Request ID set by `set_request_id()` (shows `-` if not set)
- `{logger_name}`: Name of the logger (e.g., PerformanceLogger, MonitoringLogger)
- `{log_level}`: Log level (INFO, ERROR, DEBUG, etc.)
- `{message_content}`: The actual log message content

### Performance Logs
**Message Content Format:**
```
PERFORMANCE | {function_name} | {STATUS} | {execution_time}s | {additional_info}
```

**Examples:**
```
2025-07-05 19:19:11 - 07ca74ed - PerformanceLogger - INFO - PERFORMANCE | tests.test_fastapi.health_check | SUCCESS | 0.262s
2025-07-05 21:13:03 - 2c4774b0 - PerformanceLogger - INFO - PERFORMANCE | my_module.api_call | ERROR | 2.456s | Connection timeout
2025-07-05 19:20:15 - - - PerformanceLogger - INFO - PERFORMANCE | database_query | SUCCESS | 0.089s | Args: ('user123',) | Kwargs: {'limit': 10}
```

### Memory Monitoring Logs
**Message Content Format:**
```
MEMORY | {function_name} | {STATUS} | {execution_time}s | Current: {current_memory} | Change: {memory_change} | Traced: {traced_memory}
```

**Examples:**
```
2025-07-05 19:19:11 - 07ca74ed - MonitoringLogger - INFO - MEMORY | tests.test_fastapi.health_check | SUCCESS | 0.261s | Current: 57.66MB | Change: +1.64MB | Traced: 24.33KB (Peak: 30.33KB)
2025-07-05 21:15:22 - - - MonitoringLogger - INFO - MEMORY | data_processor | SUCCESS | 0.245s | Current: 45.67MB | Change: +12.34MB
```

### Resource Monitoring Logs
**Message Content Format:**
```
RESOURCES | {function_name} | {STATUS} | {execution_time}s | CPU: {cpu_percent}% | Memory: {memory_usage} | Threads: {thread_count} | I/O: R:{read_bytes} W:{write_bytes}
```

**Examples:**
```
2025-07-05 19:19:11 - 07ca74ed - MonitoringLogger - INFO - RESOURCES | tests.test_fastapi.health_check | SUCCESS | 0.144s | CPU: 59.3% | Memory: 57.66MB (+1.63MB) | Threads: 9 | I/O: R:0.00B W:414.00B
2025-07-05 21:13:03 - 2c4774b0 - MonitoringLogger - INFO - RESOURCES | api_handler | SUCCESS | 0.156s | CPU: 25.4% | Memory: 128.45MB (+5.23MB) | Threads: 12 | I/O: R:2.34MB W:1.12MB
2025-07-05 19:25:30 - - - MonitoringLogger - INFO - RESOURCES | database_query | SUCCESS | 0.089s | CPU: 15.2% | Memory: 95.67MB (+0.12MB) | Threads: 8
```

### Request ID Usage

To include request IDs in your logs, use the `set_request_id()` function:

```python
from sherlock_ai import set_request_id, get_request_id

# Set a request ID for the current context
request_id = set_request_id("req-12345")  # Custom ID
# or
request_id = set_request_id()  # Auto-generated ID (e.g., "07ca74ed")

# Now all logs will include this request ID
# When request ID is set: "2025-07-05 19:19:11 - 07ca74ed - ..."
# When request ID is not set: "2025-07-05 19:19:11 - - - ..."
```

## Use Cases

- **API Performance Monitoring**: Track response times for your web APIs with dedicated API logging
- **Memory Leak Detection**: Monitor memory usage patterns to identify potential memory leaks
- **Resource Optimization**: Analyze CPU, memory, and I/O usage to optimize application performance
- **Database Query Optimization**: Monitor slow database operations with separate database logs
- **Microservices Debugging**: Trace execution times across service boundaries with request ID tracking
- **Algorithm Benchmarking**: Compare performance of different implementations using custom configurations
- **Production Monitoring**: Get insights into your application's performance characteristics with production presets
- **Memory-Intensive Applications**: Monitor memory usage in data processing, ML model training, and large dataset operations
- **System Resource Analysis**: Track resource consumption patterns for capacity planning and scaling decisions
- **Environment-Specific Logging**: Use different configurations for development, testing, and production
- **Custom Log Management**: Create application-specific log files and directory structures
- **Compliance & Auditing**: Separate error logs and performance logs for security and compliance requirements
- **DevOps Integration**: Configure logging for containerized environments and CI/CD pipelines
- **FastAPI Development**: Optimized for FastAPI auto-reload with no duplicate log entries during development
- **Logger Organization**: Use predefined logger names with autocomplete support for better code maintainability
- **Performance Profiling**: Comprehensive monitoring for identifying bottlenecks in CPU, memory, and I/O operations
- **Code Quality Improvement**: Automatically detect and refactor hardcoded values to improve maintainability
- **Legacy Code Modernization**: Systematically identify and extract constants from existing codebases
- **Error Analysis & Debugging**: AI-powered error analysis with automatic storage for pattern recognition
- **Production Error Tracking**: MongoDB-based error insight storage for production monitoring and debugging

## Requirements

- Python >= 3.8
- **psutil** >= 5.8.0 (for memory and resource monitoring)
- **astor** >= 0.8.1 (for AST to source code conversion in code analysis)
- **groq** >= 0.30.0 (for LLM-based analysis and constant naming)
- **pymongo** >= 4.0.0 (for MongoDB error insight storage)
- Standard library for basic performance monitoring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Homepage**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Repository**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Issues**: [https://github.com/pranawmishra/sherlock-ai/issues](https://github.com/pranawmishra/sherlock-ai/issues)