"""
Logger Singleton Module.

This module provides a singleton logger instance for consistent logging across the application.
"""

import os
import sys
from logging.handlers import RotatingFileHandler
import logging
from pythonjsonlogger import jsonlogger
from typing import Any, Dict

class RequestAwareJsonFormatter(jsonlogger.JsonFormatter):
    """
    JSON formatter that includes request ID in all log messages.
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Add custom fields to the log record.
        
        Args:
            log_record: The log record being built
            record: The original log record
            message_dict: Additional message dictionary
        """
        super().add_fields(log_record, record, message_dict)
        
        # Include request_id if available in extra
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        elif not log_record.get('request_id'):
            # If no request_id in extra, try to get it from context
            try:
                from app.middleware.context import get_request_id
                request_id = get_request_id()
                if request_id:
                    log_record['request_id'] = request_id
            except ImportError:
                pass

class LoggerSingleton:
    """
    A Singleton Logger class to maintain a single logger instance throughout the application.
    
    Attributes:
        _instance (LoggerSingleton): The singleton instance of the logger
        logger (logging.Logger): The logger object
    """
    _instance = None
    logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """Initialize the logger with JSON formatting and both file and console handlers."""
        self.logger = logging.getLogger('neo4j_driver')
        
        # Get log level from environment with fallback to INFO
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        try:
            # Convert string log level to logging module constant
            self.logger.setLevel(getattr(logging, log_level))
        except AttributeError:
            # If invalid log level, default to INFO
            self.logger.setLevel(logging.INFO)
            self.logger.warning(
                f"Invalid LOG_LEVEL '{log_level}' in .env. Using INFO instead. "
                f"Valid levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )

        # Create logs directory if it doesn't exist
        log_dir = 'app/logs'
        os.makedirs(log_dir, exist_ok=True)

        # File Handler
        file_handler = RotatingFileHandler(
            f'{log_dir}/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Custom JSON Formatter with request ID support
        formatter = RequestAwareJsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """
        Get the logger instance.
        
        Returns:
            logging.Logger: The configured logger instance
        """
        return self.logger

# Create a convenience function to get the logger
def get_logger():
    """
    Convenience function to get the logger instance.
    
    Returns:
        logging.Logger: The configured logger instance
    """
    return LoggerSingleton().get_logger() 