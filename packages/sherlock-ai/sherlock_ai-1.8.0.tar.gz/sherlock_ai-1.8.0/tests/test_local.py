# test_local.py
import time
import asyncio
from sherlock_ai.monitoring.performance import log_performance, PerformanceTimer, log_execution_time
from sherlock_ai import sherlock_ai, get_logger

sherlock_ai()

logger = get_logger(__name__)

# Test 1: Basic decorator
@log_performance
def test_sync_function():
    """Test synchronous function"""
    time.sleep(0.1)
    return "sync result"


# Test 2: Decorator with options
@log_performance(min_duration=0.05, include_args=True, log_level="DEBUG")
def test_function_with_args(name, count=5):
    """Test function with arguments"""
    time.sleep(0.1)
    return f"Processed {count} items for {name}"


# Test 3: Async function
@log_performance
async def test_async_function():
    """Test asynchronous function"""
    await asyncio.sleep(0.1)
    return "async result"


# Test 4: Context manager
def test_context_manager():
    """Test PerformanceTimer context manager"""
    with PerformanceTimer("test_operation"):
        time.sleep(0.1)
        print("Operation completed")


# Test 5: Manual logging
def test_manual_logging():
    """Test manual execution time logging"""
    start_time = time.time()
    try:
        time.sleep(0.1)
        log_execution_time("manual_test", start_time, success=True)
    except Exception as e:
        log_execution_time("manual_test", start_time, success=False, error=str(e))


async def test_main():
    """Run all tests"""
    logger.info("🧪 Testing sherlock-ai package locally...")
    logger.info("=" * 50)
    
    # Test imports
    logger.info("✅ Import test passed")
    
    # Test sync function
    logger.info("\n🔄 Testing sync function...")
    result1 = test_sync_function()
    logger.info(f"Result: {result1}")
    
    # Test function with args
    logger.info("\n🔄 Testing function with arguments...")
    result2 = test_function_with_args("Alice", count=10)
    logger.info(f"Result: {result2}")
    
    # Test async function
    logger.info("\n🔄 Testing async function...")
    result3 = await test_async_function()
    logger.info(f"Result: {result3}")
    
    # Test context manager
    # logger.info("\n🔄 Testing context manager...")
    # test_context_manager()
    
    # Test manual logging
    # logger.info("\n🔄 Testing manual logging...")
    # test_manual_logging()
    
    logger.info("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_main())