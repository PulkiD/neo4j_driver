"""
Logger Singleton Module.

This module provides a singleton logger instance for consistent logging across the application.
"""

import os
import sys
from logging.handlers import RotatingFileHandler
import logging
from pythonjsonlogger import jsonlogger

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
        self.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

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

        # JSON Formatter
        formatter = jsonlogger.JsonFormatter(
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