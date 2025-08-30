from dataclasses import dataclass, field
from typing import Union, List, Dict
import logging
import os
@dataclass
class LogFileConfig:
    """Configuration for individual log files"""
    filename: str
    level: Union[str, int] = logging.INFO
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    encoding: str = "utf-8"
    enabled: bool = True

@dataclass
class LoggerConfig:
    """Configuration for individual loggers"""
    name: str
    level: Union[str, int] = logging.INFO
    log_files: List[str] = field(default_factory=list)  # Which log files this logger writes to
    propagate: bool = True
    enabled: bool = True

@dataclass
class LoggingConfig:
    """Complete logging configuration"""

    auto_instrument: bool = True
    auto_trace_functions: bool = False
    auto_frameworks: List[str] = field(default_factory=lambda: ["fastapi"])
    auto_exclude_modules: List[str] = field(default_factory=lambda: ["sys", "os", "logging"])
    auto_min_duration: float = 0.0  # Only auto-log functions taking longer than this
    
    # Directory settings
    logs_dir: str = "logs"
    
    # Format settings
    log_format: str = "%(asctime)s - %(request_id)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    log_format_type: str = "json"
    
    # Console settings
    console_enabled: bool = True
    console_level: Union[str, int] = logging.INFO
    
    # Root logger settings
    root_level: Union[str, int] = logging.INFO
    
    # Log files configuration
    log_files: Dict[str, LogFileConfig] = field(default_factory=dict)
    
    # Logger configuration
    loggers: Dict[str, LoggerConfig] = field(default_factory=dict)
    
    # External library log levels
    external_loggers: Dict[str, Union[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        """Set up default configuration if not provided"""
        # Auto-expand log file paths for user convenience
        self._expand_log_file_paths()

        if not self.log_files:
            self.log_files = self._get_default_log_files()
        
        if not self.loggers:
            self.loggers = self._get_default_loggers()
            
        if not self.external_loggers:
            self.external_loggers = self._get_default_external_loggers()

    def _expand_log_file_paths(self):
        """Automatically expand base filenames to full paths using logs_dir and log_format_type"""
        file_extension = ".json" if self.log_format_type == "json" else ".log"
        
        for config in self.log_files.values():
            # Check if filename is just a base name (no directory separators)
            if not any(sep in config.filename for sep in ['/', '\\', os.path.sep]):
                # Expand to full path with proper extension if not already present
                # if not config.filename.endswith(('.log', '.json')):
                config.filename = f"{self.logs_dir}/{config.filename}{file_extension}"
                # else:
                    # config.filename = f"{self.logs_dir}/{config.filename}"

    def _get_default_log_files(self) -> Dict[str, LogFileConfig]:
        """Default log files configuration"""

        # Choose file extension based on format type
        file_extension = ".json" if self.log_format_type == "json" else ".log"
        return {
            "app": LogFileConfig(f"{self.logs_dir}/app{file_extension}"),
            "errors": LogFileConfig(f"{self.logs_dir}/errors{file_extension}", level=logging.ERROR),
            "api": LogFileConfig(f"{self.logs_dir}/api{file_extension}"),
            "database": LogFileConfig(f"{self.logs_dir}/database{file_extension}"),
            "services": LogFileConfig(f"{self.logs_dir}/services{file_extension}"),
            "performance": LogFileConfig(f"{self.logs_dir}/performance{file_extension}"),
            "monitoring": LogFileConfig(f"{self.logs_dir}/monitoring{file_extension}"),
            "error_insights": LogFileConfig(f"{self.logs_dir}/error_insights{file_extension}"),
            "auto_instrumentation": LogFileConfig(f"{self.logs_dir}/auto_instrumentation{file_extension}"),
        }

    def _get_default_loggers(self) -> Dict[str, LoggerConfig]:
        """Default loggers configuration"""
        return {
            "api": LoggerConfig("ApiLogger", log_files=["api"]),
            "database": LoggerConfig("DatabaseLogger", log_files=["database"]),
            "services": LoggerConfig("ServiceLogger", log_files=["services"]),
            "performance": LoggerConfig("PerformanceLogger", log_files=["performance"], propagate=False),
            "monitoring": LoggerConfig("MonitoringLogger", log_files=["monitoring"], propagate=False),
            "error_insights": LoggerConfig("ErrorInsightsLogger", log_files=["error_insights"], propagate=False),
            "auto_instrumentation": LoggerConfig("AutoInstrumentationLogger", log_files=["auto_instrumentation"], propagate=False),
        }

    def _get_default_external_loggers(self) -> Dict[str, Union[str, int]]:
        """Default external library log levels"""
        return {
            "uvicorn": logging.INFO,
            "fastapi": logging.INFO,
        }

# Factory methods for common configurations
class LoggingPresets:
    """Pre-configured logging setups for common use cases"""
    
    @staticmethod
    def minimal() -> LoggingConfig:
        """Minimal logging - console + basic app log only"""
        config = LoggingConfig()
        config.log_files = {
            "app": LogFileConfig("logs/app.log"),
        }
        config.loggers = {}
        return config
    
    @staticmethod
    def development() -> LoggingConfig:
        """Development preset - all logs with debug level"""
        config = LoggingConfig()
        config.console_level = logging.DEBUG
        config.root_level = logging.DEBUG
        
        # Enable debug level for all files
        for file_config in config.log_files.values():
            file_config.level = logging.DEBUG
            
        return config
    
    @staticmethod
    def production() -> LoggingConfig:
        """Production preset - optimized for performance"""
        config = LoggingConfig()
        config.console_level = logging.WARNING
        
        # Disable some less critical logs in production
        config.log_files["api"].enabled = False
        config.log_files["services"].enabled = False
        
        return config
    
    @staticmethod
    def performance_only() -> LoggingConfig:
        """Only performance monitoring"""
        config = LoggingConfig()
        config.log_files = {
            "performance": LogFileConfig("logs/performance.log"),
        }
        config.loggers = {
            "performance": LoggerConfig("PerformanceLogger", log_files=["performance"], propagate=False),
        }
        return config

    @staticmethod
    def custom_files(file_configs: Dict[str, str]) -> LoggingConfig:
        """Create config with custom file names"""
        config = LoggingConfig()
        
        # Update file paths
        for key, filename in file_configs.items():
            if key in config.log_files:
                config.log_files[key].filename = filename
                
        return config
    
    @staticmethod
    def auto_instrument_all() -> LoggingConfig:
        """Full auto-instrumentation - frameworks + function tracing"""
        config = LoggingConfig()
        config.auto_instrument = True
        config.auto_trace_functions = True
        config.auto_min_duration = 0.001  # 1ms threshold
        return config
        
    @staticmethod
    def auto_frameworks_only() -> LoggingConfig:
        """Auto-instrument frameworks only (recommended)"""
        config = LoggingConfig()
        config.auto_instrument = True
        config.auto_trace_functions = False
        return config