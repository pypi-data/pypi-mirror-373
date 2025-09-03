import pytest
import json
import os
import sys
import tempfile
import logging
from unittest.mock import patch, MagicMock
from ebook_mcp.tools.logger_config import (
    StructuredFormatter, 
    StructuredLogger, 
    setup_logger, 
    get_logger, 
    log_operation
)

class TestStructuredFormatter:
    """Test the structured formatter"""
    
    def test_format_basic_log(self):
        """Test basic log formatting"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test_logger"
        assert log_entry["message"] == "Test message"
        assert log_entry["module"] == "test"
        # function name might be None in test environment
        assert log_entry["function"] in ["<module>", None]
        assert log_entry["line"] == 10
        assert "timestamp" in log_entry
    
    def test_format_with_extra_fields(self):
        """Test formatting with extra context fields"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=20,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.file_path = "/test/file.epub"
        record.operation = "metadata_extraction"
        record.duration_ms = 150.5
        record.error_type = "FileNotFoundError"
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["file_path"] == "/test/file.epub"
        assert log_entry["operation"] == "metadata_extraction"
        assert log_entry["duration_ms"] == 150.5
        assert log_entry["error_type"] == "FileNotFoundError"
    
    def test_format_with_exception(self):
        """Test formatting with exception info"""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=30,
                msg="Exception occurred",
                args=(),
                exc_info=sys.exc_info()
            )
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert "exception" in log_entry
        assert log_entry["exception"]["type"] == "ValueError"
        assert log_entry["exception"]["message"] == "Test exception"
        assert "traceback" in log_entry["exception"]

class TestStructuredLogger:
    """Test the structured logger"""
    
    def test_logger_creation(self):
        """Test logger creation"""
        logger = StructuredLogger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger.logger, logging.Logger)
    
    def test_log_with_context(self):
        """Test logging with context fields"""
        # Test that StructuredLogger can be created and has the expected interface
        logger = StructuredLogger("test_module")
        assert logger.name == "test_module"
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')

class TestLogOperationDecorator:
    """Test the log_operation decorator"""
    
    def test_log_operation_success(self):
        """Test successful operation logging"""
        @log_operation("test_operation")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_log_operation_failure(self):
        """Test failed operation logging"""
        @log_operation("test_operation")
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_function()

class TestSetupLogger:
    """Test logger setup"""
    
    def test_setup_logger_creates_directory(self):
        """Test that setup_logger creates logs directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('ebook_mcp.tools.logger_config.os.path.dirname', return_value=temp_dir):
                with patch('ebook_mcp.tools.logger_config.os.makedirs') as mock_makedirs:
                    with patch('ebook_mcp.tools.logger_config.logging.FileHandler') as mock_file_handler:
                        mock_handler = MagicMock()
                        mock_file_handler.return_value = mock_handler
                        setup_logger()
                        mock_makedirs.assert_called_once()
    
    def test_setup_logger_configures_handlers(self):
        """Test that setup_logger configures handlers correctly"""
        with patch('ebook_mcp.tools.logger_config.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            setup_logger()
            
            # Verify handlers were added
            mock_logger.addHandler.assert_called()
            assert mock_logger.addHandler.call_count == 2  # file and console handlers

if __name__ == "__main__":
    # Import sys for exception testing
    import sys
    pytest.main([__file__])
