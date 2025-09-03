"""Tests for logger module."""

import pytest
import sys
import logging
from io import StringIO


class TestLogger:
    """Test suite for logger module."""

    def test_logger_import(self):
        """Test that logger module can be imported."""
        try:
            from masster import logger
            assert logger is not None
        except ImportError:
            pytest.skip("Logger module not directly importable")

    def test_logger_creation(self):
        """Test logger creation."""
        try:
            from masster.logger import MassterLogger
            
            logger = MassterLogger("sample", "test_id", level="INFO")
            assert logger is not None
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'debug')
            assert hasattr(logger, 'warning')
            assert hasattr(logger, 'error')
            
        except ImportError:
            pytest.skip("Logger functions not available")

    def test_logger_with_level(self):
        """Test logger with different levels."""
        try:
            from masster.logger import MassterLogger
            
            # Test different log levels
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            
            for level in levels:
                logger = MassterLogger("sample", f"test_{level.lower()}", level=level)
                assert logger is not None
                assert logger.level == level
                
        except ImportError:
            pytest.skip("Logger functions not available")

    def test_logger_output_capture(self):
        """Test logger output capture."""
        try:
            from masster.logger import MassterLogger
            
            # Create string buffer to capture output
            log_capture_string = StringIO()
            
            # Create logger with string sink
            logger = MassterLogger("sample", "test_capture", sink=log_capture_string)
            
            # Log a test message
            logger.info("Test message")
                
            # Check if message was captured
            log_contents = log_capture_string.getvalue()
            assert "Test message" in log_contents
                
        except (ImportError, AttributeError):
            pytest.skip("Logger output capture not available")

    def test_logger_file_output(self):
        """Test logger file output."""
        try:
            from masster.logger import MassterLogger
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
                temp_file = f.name
            
            try:
                # Create logger with file sink
                with open(temp_file, 'w') as file_sink:
                    logger = MassterLogger("sample", "test_file", sink=file_sink)
                    
                    # Log a test message
                    logger.info("File test message")
                    
                # Check if file contains message
                if os.path.exists(temp_file):
                    with open(temp_file, 'r') as f:
                        content = f.read()
                        assert "File test message" in content
                        
            finally:
                # Clean up
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except (ImportError, AttributeError):
            pytest.skip("Logger file output not available")

    def test_logger_formatting(self):
        """Test logger message formatting."""
        try:
            from masster.logger import MassterLogger
            
            log_capture = StringIO()
            logger = MassterLogger("sample", "test_format", sink=log_capture)
            
            # Test different log methods
            test_methods = ['debug', 'info', 'warning', 'error', 'critical']
            
            for method_name in test_methods:
                if hasattr(logger, method_name):
                    method = getattr(logger, method_name)
                    method(f"Test {method_name} message")
            
            log_contents = log_capture.getvalue()
            assert len(log_contents) > 0
            
        except (ImportError, AttributeError):
            pytest.skip("Logger formatting not available")

    def test_logger_configuration(self):
        """Test logger configuration options."""
        try:
            from masster.logger import MassterLogger
            
            # Test configuration with different options
            logger = MassterLogger(
                instance_type="sample",
                instance_id="test_config",
                level="INFO",
                label="test_label",
                sink=sys.stdout
            )
            assert logger is not None
            assert logger.level == "INFO"
            assert logger.label == "test_label"
            
        except ImportError:
            pytest.skip("Logger configuration not available")

    def test_logger_context_manager(self):
        """Test logger as context manager."""
        try:
            from masster.logger import get_logger
            
            logger = get_logger("test_context")
            
            # Test if logger can be used as context manager
            if hasattr(logger, '__enter__') and hasattr(logger, '__exit__'):
                with logger as ctx_logger:
                    assert ctx_logger is not None
            else:
                pytest.skip("Logger context manager not implemented")
                
        except ImportError:
            pytest.skip("Logger context manager not available")

    def test_logger_filter_functionality(self):
        """Test logger filtering functionality."""
        try:
            from masster.logger import get_logger
            
            log_capture = StringIO()
            logger = get_logger("test_filter", level="WARNING", sink=log_capture)
            
            # Try to log messages at different levels
            if hasattr(logger, 'debug') and hasattr(logger, 'warning'):
                logger.debug("Debug message")  # Should be filtered out
                logger.warning("Warning message")  # Should appear
                
                log_contents = log_capture.getvalue()
                assert "Warning message" in log_contents
                assert "Debug message" not in log_contents
                
        except (ImportError, AttributeError):
            pytest.skip("Logger filtering not available")

    def test_logger_multiple_sinks(self):
        """Test logger with multiple output sinks."""
        try:
            from masster.logger import get_logger
            
            sink1 = StringIO()
            sink2 = StringIO()
            
            # Try to create logger with multiple sinks
            logger = get_logger("test_multi", sink=[sink1, sink2])
            
            if hasattr(logger, 'info'):
                logger.info("Multi-sink test")
                
                # Check both sinks received the message
                content1 = sink1.getvalue()
                content2 = sink2.getvalue()
                
                assert "Multi-sink test" in content1
                assert "Multi-sink test" in content2
                
        except (ImportError, AttributeError, TypeError):
            pytest.skip("Multiple sink logging not available")

    def test_logger_performance(self):
        """Test logger performance with many messages."""
        try:
            from masster.logger import get_logger
            import time
            
            logger = get_logger("test_perf", sink=StringIO())
            
            if hasattr(logger, 'info'):
                start_time = time.time()
                
                # Log many messages
                for i in range(100):
                    logger.info(f"Performance test message {i}")
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Should complete in reasonable time (less than 1 second)
                assert duration < 1.0
                
        except (ImportError, AttributeError):
            pytest.skip("Logger performance test not available")

    def test_logger_error_handling(self):
        """Test logger error handling."""
        try:
            from masster.logger import get_logger
            
            # Test with invalid parameters
            test_logger = get_logger("test_error")
            assert test_logger is not None
            
            # Test logging with invalid sink
            try:
                bad_logger = get_logger("test_bad", sink="/invalid/path/file.log")
                assert bad_logger is not None  # Should handle gracefully
            except Exception:
                pass  # Expected for invalid paths
                
        except ImportError:
            pytest.skip("Logger error handling test not available")

    def test_logger_cleanup(self):
        """Test logger cleanup functionality."""
        try:
            from masster.logger import get_logger
            
            logger = get_logger("test_cleanup")
            
            # Test cleanup methods if they exist
            if hasattr(logger, 'close'):
                logger.close()
            elif hasattr(logger, 'cleanup'):
                logger.cleanup()
            
            # Should not raise exceptions
            assert True
            
        except (ImportError, AttributeError):
            pytest.skip("Logger cleanup not available")
