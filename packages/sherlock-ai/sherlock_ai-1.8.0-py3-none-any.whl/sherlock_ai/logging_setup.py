# app > core > logging_config.py
from dotenv import load_dotenv
load_dotenv()

from typing import Optional, Dict, Any
import logging
import logging.handlers
import json
import traceback
from pathlib import Path
from sherlock_ai.config.logging import LoggingConfig
from sherlock_ai.utils import request_id_var

# Add module-level variable to store current config
_current_config: Optional[LoggingConfig] = None

class RequestIdFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""

    def format(self, record):
        """Add request ID to log message"""
        # get current request ID from context
        record.request_id = request_id_var.get("") or "-"
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""

    def format(self, record):
        """Add request ID to log message"""
        request_id = request_id_var.get("") or "-"
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id
        }

        # Add exception details if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": "".join(traceback.format_exception(*record.exc_info))
            }

        # Add extra fields if available
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))

class SherlockAI:
    """
    Simple logging framework for local development
    """
    
    # Single instance for the application
    _instance: Optional['SherlockAI'] = None
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        """
        Initialize SherlockAI logging manager
        
        Args:
            config: LoggingConfig object. If None, uses default configuration.
        """
        self.config = config or LoggingConfig()
        self.is_configured = False
        self.handlers: Dict[str, logging.Handler] = {}
        self.formatter: Optional[RequestIdFormatter] = None
        
    def setup(self) -> LoggingConfig:
        """
        Set up logging configuration

        Args:
            format_type: "log" for standard format, "json" for JSON format
        
        Returns:
            The configuration that was applied
        """

        # Create logs directory if it doesn't exist
        logs_dir = Path(self.config.logs_dir)
        logs_dir.mkdir(exist_ok=True)

        # Create custom formatter based on format type
        if self.config.log_format_type == "json":
            self.formatter = JSONFormatter(datefmt=self.config.date_format)
        else:
            self.formatter = RequestIdFormatter(self.config.log_format, datefmt=self.config.date_format)

        # Clear existing handlers to avoid duplicates
        self._clear_existing_handlers()

        # Setup console handler
        if self.config.console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config.console_level)
            # Console always uses standard format for readability
            console_formatter = RequestIdFormatter(self.config.log_format, datefmt=self.config.date_format)
            console_handler.setFormatter(console_formatter)
            logging.root.addHandler(console_handler)
            self.handlers['console'] = console_handler

        # Create file handlers
        self._create_file_handlers()

        # Configure root logger
        logging.root.setLevel(self.config.root_level)

        # Add main app and error handlers to root by default
        if "app" in self.handlers:
            logging.root.addHandler(self.handlers["app"])
        if "errors" in self.handlers:
            logging.root.addHandler(self.handlers["errors"])
        
        # Configure specific loggers
        self._configure_loggers()
        
        # Configure external library loggers
        self._configure_external_loggers()

        # 🆕 NEW: Enable auto-instrumentation
        if self.config.auto_instrument:
            from .auto import enable_auto_instrumentation
            enable_auto_instrumentation(self.config)

        self.is_configured = True
        return self.config
    
    def _clear_existing_handlers(self):
        """Clear existing handlers to avoid duplicates"""
        logging.root.handlers.clear()
        for logger_name in list(logging.Logger.manager.loggerDict.keys()):
            logger = logging.getLogger(logger_name)
            if hasattr(logger, 'handlers'):
                logger.handlers.clear()
    
    def _create_file_handlers(self):
        """Create file handlers based on configuration"""
        for name, file_config in self.config.log_files.items():
            if file_config.enabled:
                handler = logging.handlers.RotatingFileHandler(
                    file_config.filename,
                    maxBytes=file_config.max_bytes,
                    backupCount=file_config.backup_count,
                    encoding=file_config.encoding
                )
                handler.setLevel(file_config.level)
                handler.setFormatter(self.formatter)
                self.handlers[name] = handler
    
    def _configure_loggers(self):
        """Configure specific loggers based on configuration"""
        for name, logger_config in self.config.loggers.items():
            if logger_config.enabled:
                logger = logging.getLogger(logger_config.name)
                logger.setLevel(logger_config.level)
                logger.propagate = logger_config.propagate

                # Add specified file handlers to this logger
                for file_name in logger_config.log_files:
                    if file_name in self.handlers:
                        logger.addHandler(self.handlers[file_name])
    
    def _configure_external_loggers(self):
        """Configure external library loggers"""
        for logger_name, level in self.config.external_loggers.items():
            logging.getLogger(logger_name).setLevel(level)
    
    def reconfigure(self, new_config: LoggingConfig):
        """
        Reconfigure logging with new settings
        
        Args:
            new_config: New LoggingConfig to apply
        """
        self.cleanup()
        self.config = new_config
        self.setup()
    
    def cleanup(self):
        """Clean up handlers and resources"""
        for handler in self.handlers.values():
            handler.close()
        self.handlers.clear()
        logging.root.handlers.clear()
        self.is_configured = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current logging statistics"""
        return {
            'is_configured': self.is_configured,
            'handlers': list(self.handlers.keys()),
            'log_files': list(self.config.log_files.keys()),
            'logs_dir': self.config.logs_dir,
            'console_enabled': self.config.console_enabled,
            "format_type": self.config.log_format_type
        }
    
    @classmethod
    def get_instance(cls) -> 'SherlockAI':
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def sherlock_ai(config: Optional[LoggingConfig] = None, format_type: str = "log", auto_instrument: bool = True):
    """
    Set up logging configuration with full customization support

    Args:
        config: LoggingConfig object. If None, uses default configuration.
    
    Returns:
        The configuation that was applied (useful for introspection)
    """
    global _current_config # Access the global variable
    
    if config is None:
        config = LoggingConfig(log_format_type=format_type, auto_instrument=auto_instrument)

    # Create logs directory if it doesn't exist
    logs_dir = Path(config.logs_dir)
    logs_dir.mkdir(exist_ok=True)

    # Create custom formatter based on format type
    if config.log_format_type == "json":
        formatter = JSONFormatter(datefmt=config.date_format)
    else:
        formatter = RequestIdFormatter(config.log_format, datefmt=config.date_format)

    # Clear existing handlers to avoid duplicates
    logging.root.handlers.clear()

    # Clear handlers from all existing loggers
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        if hasattr(logger, 'handlers'):
            logger.handlers.clear()

    # 1. Console Handler - prints to terminal
    if config.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.console_level)
        # Console always uses standard format for readability
        console_formatter = RequestIdFormatter(config.log_format, datefmt=config.date_format)
        console_handler.setFormatter(console_formatter)
        logging.root.addHandler(console_handler)

    # Create file handlers
    file_handlers = {}
    for name, file_config in config.log_files.items():
        if file_config.enabled:
            handler = logging.handlers.RotatingFileHandler(
                file_config.filename,
                maxBytes=file_config.max_bytes,
                backupCount=file_config.backup_count,
                encoding=file_config.encoding
            )
            handler.setLevel(file_config.level)
            handler.setFormatter(formatter)
            file_handlers[name] = handler

    # Configure root logger
    logging.root.setLevel(config.root_level)

    # Add main app and error handlers to root by default
    if "app" in file_handlers:
        logging.root.addHandler(file_handlers["app"])
    if "errors" in file_handlers:
        logging.root.addHandler(file_handlers["errors"])
    
    # Configure specific loggers
    for name, logger_config in config.loggers.items():
        if logger_config.enabled:
            logger = logging.getLogger(logger_config.name)
            logger.setLevel(logger_config.level)
            logger.propagate = logger_config.propagate

            # Add specified file handlers to this logger
            for file_name in logger_config.log_files:
                if file_name in file_handlers:
                    logger.addHandler(file_handlers[file_name])
    
    # Configure external library loggers
    for logger_name, level in config.external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

    # 🆕 NEW: Enable auto-instrumentation
    if config.auto_instrument:
        from .auto import enable_auto_instrumentation
        enable_auto_instrumentation(config)

    # Store the config in the module-level variable
    _current_config = config

    return config

# Helper function to get logger (optional, but clean)
def get_logger(name: str = None):
    """Get a logger. If no name provided, uses the caller's __name__."""
    return logging.getLogger(name) if name else logging.getLogger(__name__)

def get_current_config() -> Optional[LoggingConfig]:
    """Get the current logging configuration"""
    instance = SherlockAI.get_instance()
    return instance.config if instance.is_configured else None

def get_logging_stats() -> Dict[str, Any]:
    """Get current logging statistics"""
    instance = SherlockAI.get_instance()
    return instance.get_stats()