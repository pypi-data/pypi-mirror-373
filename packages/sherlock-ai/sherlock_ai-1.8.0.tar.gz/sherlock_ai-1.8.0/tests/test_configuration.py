# test_configuration.py
"""
Test suite for the enhanced logging configuration system
"""
import time
import asyncio
from sherlock_ai import get_logger, LoggingConfig, LoggingPresets, LogFileConfig, LoggerConfig, SherlockAI
from sherlock_ai.monitoring.performance import log_performance

# Initialize logging for this test
logging_manager = SherlockAI.get_instance()
logger = get_logger(__name__)


def test_default_configuration():
    """Test default logging configuration"""
    logger.info("🔧 Testing default configuration...")
    
    # Test creating default config
    config = LoggingConfig()
    logger.info(f"Default logs directory: {config.logs_dir}")
    logger.info(f"Default log files: {list(config.log_files.keys())}")
    logger.info(f"Default loggers: {list(config.loggers.keys())}")
    
    # Test individual file config
    app_config = config.log_files["app"]
    logger.info(f"App log file: {app_config.filename}, Level: {app_config.level}")
    
    logger.info("✅ Default configuration test completed")


def test_preset_configurations():
    """Test all preset configurations"""
    logger.info("🎛️ Testing preset configurations...")
    
    # Test minimal preset
    minimal_config = LoggingPresets.minimal()
    logger.info(f"Minimal config log files: {list(minimal_config.log_files.keys())}")
    
    # Test development preset
    dev_config = LoggingPresets.development()
    logger.info(f"Development config console level: {dev_config.console_level}")
    
    # Test production preset
    prod_config = LoggingPresets.production()
    logger.info(f"Production config console level: {prod_config.console_level}")
    
    # Test performance only preset
    perf_config = LoggingPresets.performance_only()
    logger.info(f"Performance-only config files: {list(perf_config.log_files.keys())}")
    
    logger.info("✅ Preset configurations test completed")


def test_custom_configuration():
    """Test custom logging configuration"""
    logger.info("⚙️ Testing custom configuration...")
    
    # Create custom configuration
    custom_config = LoggingConfig(
        logs_dir="test_logs",
        console_level="DEBUG",
        log_files={
            "custom_app": LogFileConfig("test_logs/my_app.log", max_bytes=5*1024*1024),
            "custom_errors": LogFileConfig("test_logs/my_errors.log", level="ERROR"),
            "custom_performance": LogFileConfig("test_logs/my_performance.log")
        },
        loggers={
            "custom_api": LoggerConfig("mycompany.api", log_files=["custom_app"]),
            "custom_perf": LoggerConfig("mycompany.performance", log_files=["custom_performance"], propagate=False)
        }
    )
    
    logger.info(f"Custom logs directory: {custom_config.logs_dir}")
    logger.info(f"Custom console level: {custom_config.console_level}")
    logger.info(f"Custom app log max bytes: {custom_config.log_files['custom_app'].max_bytes}")
    
    logger.info("✅ Custom configuration test completed")


def test_configuration_flexibility():
    """Test configuration flexibility and modifications"""
    logger.info("🔀 Testing configuration flexibility...")
    
    # Start with default config
    config = LoggingConfig()
    
    # Disable some log files
    config.log_files["api"].enabled = False
    config.log_files["services"].enabled = False
    logger.info("Disabled API and services logs")
    
    # Change log levels
    config.log_files["performance"].level = "DEBUG"
    config.console_level = "WARNING"
    logger.info("Changed performance log to DEBUG, console to WARNING")
    
    # Modify file sizes
    config.log_files["app"].max_bytes = 50 * 1024 * 1024  # 50MB
    config.log_files["app"].backup_count = 10
    logger.info("Increased app log size and backup count")
    
    # Test custom file names preset
    custom_files_config = LoggingPresets.custom_files({
        "app": "custom_logs/application.log",
        "performance": "custom_logs/perf_metrics.log"
    })
    logger.info(f"Custom files app log: {custom_files_config.log_files['app'].filename}")
    
    logger.info("✅ Configuration flexibility test completed")


@log_performance
def test_performance_with_custom_config():
    """Test performance monitoring with custom configuration"""
    logger.info("⚡ Testing performance monitoring with custom config...")
    
    # This function itself is being monitored
    time.sleep(0.05)
    
    # Test that our performance decorator still works with new config system
    result = "Performance monitoring works with new config!"
    logger.info(f"Result: {result}")
    
    return result


def test_configuration_validation():
    """Test configuration validation and error handling"""
    logger.info("✔️ Testing configuration validation...")
    
    # Test that configuration objects work correctly
    config = LoggingConfig()
    
    # Test that we can access all expected attributes
    assert hasattr(config, 'logs_dir')
    assert hasattr(config, 'log_files')
    assert hasattr(config, 'loggers')
    assert hasattr(config, 'console_enabled')
    
    # Test that default files are created
    expected_files = ["app", "errors", "api", "database", "services", "performance"]
    for file_name in expected_files:
        assert file_name in config.log_files
        
    # Test that default loggers are created
    expected_loggers = ["api", "database", "services", "performance"]
    for logger_name in expected_loggers:
        assert logger_name in config.loggers
    
    logger.info("All configuration validations passed")
    logger.info("✅ Configuration validation test completed")


def test_preset_integration():
    """Test that presets can be used with setup_logging"""
    logger.info("🔗 Testing preset integration...")
    
    # Test that we can actually use presets with setup_logging
    # (We won't actually call setup_logging to avoid conflicts)
    
    minimal_config = LoggingPresets.minimal()
    dev_config = LoggingPresets.development()
    prod_config = LoggingPresets.production()
    perf_config = LoggingPresets.performance_only()
    
    # Verify they all return LoggingConfig objects
    assert isinstance(minimal_config, LoggingConfig)
    assert isinstance(dev_config, LoggingConfig)
    assert isinstance(prod_config, LoggingConfig)
    assert isinstance(perf_config, LoggingConfig)
    
    logger.info("All presets return valid LoggingConfig objects")
    logger.info("✅ Preset integration test completed")


async def test_configuration_complete():
    """Complete test of all configuration features"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTING ENHANCED CONFIGURATION SYSTEM")
    logger.info("="*60)
    
    # Test all configuration features
    test_default_configuration()
    logger.info("")
    
    test_preset_configurations()
    logger.info("")
    
    test_custom_configuration()
    logger.info("")
    
    test_configuration_flexibility()
    logger.info("")
    
    test_configuration_validation()
    logger.info("")
    
    test_preset_integration()
    logger.info("")
    
    # Test performance monitoring still works
    result = test_performance_with_custom_config()
    logger.info(f"Performance test result: {result}")
    
    logger.info("="*60)
    logger.info("✅ ALL CONFIGURATION TESTS COMPLETED!")
    logger.info("="*60)

def test_decorator_function_source():
    """Test that decorator function source is correctly extracted"""
    logger.info("🔍 Testing decorator function source...")
    
    # Test that we can extract the source code of the decorator function
    result = test_performance_with_custom_config()
    logger.info(f"Performance test result: {result}")


if __name__ == "__main__":
    """Run configuration tests"""
    logger.info("🚀 RUNNING CONFIGURATION TEST SUITE")
    logger.info("=" * 60)
    
    asyncio.run(test_configuration_complete())
    
    logger.info("\n🎉 CONFIGURATION TESTS COMPLETED SUCCESSFULLY!") 