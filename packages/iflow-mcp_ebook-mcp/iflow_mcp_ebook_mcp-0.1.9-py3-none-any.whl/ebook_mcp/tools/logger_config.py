import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'file_path'):
            log_entry['file_path'] = record.file_path
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if hasattr(record, 'file_size'):
            log_entry['file_size'] = record.file_size
        if hasattr(record, 'page_count'):
            log_entry['page_count'] = record.page_count
        if hasattr(record, 'chapter_count'):
            log_entry['chapter_count'] = record.chapter_count
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'error_details'):
            log_entry['error_details'] = record.error_details
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class StructuredLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _log_with_context(self, level: int, message: str, **context):
        """Log with additional context fields"""
        # Check if we're in a test environment
        import sys
        if 'pytest' in sys.modules or 'test' in self.name:
            # Skip logging in test environment
            return
            
        extra = {}
        for key, value in context.items():
            if value is not None:
                extra[key] = value
        
        self.logger.log(level, message, extra=extra)
    
    def info(self, message: str, **context):
        """Log info message with context"""
        self._log_with_context(logging.INFO, message, **context)
    
    def debug(self, message: str, **context):
        """Log debug message with context"""
        self._log_with_context(logging.DEBUG, message, **context)
    
    def warning(self, message: str, **context):
        """Log warning message with context"""
        self._log_with_context(logging.WARNING, message, **context)
    
    def error(self, message: str, **context):
        """Log error message with context"""
        self._log_with_context(logging.ERROR, message, **context)
    
    def critical(self, message: str, **context):
        """Log critical message with context"""
        self._log_with_context(logging.CRITICAL, message, **context)

def setup_logger(level: str = "INFO", log_file: str = "ebook_mcp.log"):
    """Configure structured logging system"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_dir, log_file)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    structured_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with structured JSON logging
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(structured_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with human-readable format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)

def log_operation(operation_name: str):
    """Decorator to log operation start/end with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if we're in a test environment by looking for pytest
            import sys
            if 'pytest' in sys.modules or 'test' in func.__module__:
                # Skip logging in test environment
                return func(*args, **kwargs)
            
            logger = get_logger(func.__module__)
            start_time = time.time()
            
            # Log operation start
            logger.info(
                f"Starting {operation_name}",
                operation=operation_name,
                function=func.__name__
            )
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log operation success
                logger.info(
                    f"Completed {operation_name} successfully",
                    operation=operation_name,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2)
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log operation failure
                logger.error(
                    f"Failed to complete {operation_name}",
                    operation=operation_name,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    error_type=type(e).__name__,
                    error_details=str(e)
                )
                raise
                
        return wrapper
    return decorator

# Configure logger when module is imported
setup_logger() 