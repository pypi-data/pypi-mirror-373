from sherlock_ai import monitor_memory, monitor_resources, MemoryTracker, ResourceTracker, setup_logging, log_performance
import time

# Setup logging
setup_logging()

# logger = get_logger("MonitoringLogger")

# Basic memory monitoring
@log_performance
@monitor_memory
@monitor_resources
def combined_monitoring_function():
    """Test function with both memory and resource monitoring"""
    # logger.info("Combined monitoring test...")
    
    # Memory allocation
    data = list(range(50000))
    
    # CPU work
    result = sum(x * x for x in data)
    
    time.sleep(0.1)
    return result

# Advanced resource monitoring
@monitor_resources(include_io=True, include_network=True)
def api_call():
    print("Calling API...")

# Context managers
# with MemoryTracker("data_processing"):
#     print("Processing data...")

# with ResourceTracker("api_processing", include_io=True):
#     print("Calling API...")

if __name__ == "__main__":
    combined_monitoring_function()