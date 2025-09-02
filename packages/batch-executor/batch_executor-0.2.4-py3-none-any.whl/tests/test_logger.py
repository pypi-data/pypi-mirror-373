import pytest
import logging
import os
import tempfile
from batch_executor import setup_logger  # 导入你的logger模块

class TestLogger:
    @pytest.fixture
    def temp_log_file(self):
        """Fixture to create a temporary log file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as tmp:
            yield tmp.name
        # Cleanup after test
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

    def test_logger_creation(self):
        """Test basic logger creation"""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_console_output(self, capsys):
        """Test console output"""
        logger = setup_logger("test_console", console=True, colored=False)
        test_message = "Test console message"
        logger.info(test_message)
        
        captured = capsys.readouterr()
        assert test_message in captured.err or test_message in captured.out

    def test_file_output(self, temp_log_file):
        """Test file output"""
        logger = setup_logger("test_file", log_file=temp_log_file)
        test_message = "Test file message"
        logger.info(test_message)
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        assert test_message in content

    def test_log_levels(self, temp_log_file):
        """Test different log levels"""
        logger = setup_logger(
            "test_levels",
            log_file=temp_log_file,
            log_level="DEBUG"
        )
        
        messages = {
            "debug": "Debug message",
            "info": "Info message",
            "warning": "Warning message",
            "error": "Error message",
            "critical": "Critical message"
        }
        
        # Log messages at different levels
        logger.debug(messages["debug"])
        logger.info(messages["info"])
        logger.warning(messages["warning"])
        logger.error(messages["error"])
        logger.critical(messages["critical"])
        
        # Check file contents
        with open(temp_log_file, 'r') as f:
            content = f.read()
            for message in messages.values():
                assert message in content

    def test_format_types(self, temp_log_file):
        """Test different format types"""
        # Test simple format
        logger_simple = setup_logger(
            "test_simple",
            log_file=temp_log_file,
            format_type="simple"
        )
        logger_simple.info("Simple format test")
        
        with open(temp_log_file, 'r') as f:
            simple_content = f.read()
        assert "Simple format test" in simple_content.strip()
        
        # Test detailed format
        logger_detailed = setup_logger(
            "test_detailed",
            log_file=temp_log_file,
            format_type="detailed",
            file_mode="w"  # Override previous content
        )
        logger_detailed.info("Detailed format test")
        
        with open(temp_log_file, 'r') as f:
            detailed_content = f.read()
        assert "[test_logger.py:" in detailed_content

    def test_colored_output(self, capsys):
        """Test colored output"""
        logger = setup_logger("test_color", colored=True)
        logger.info("Colored message")
        
        captured = capsys.readouterr()
        output = captured.err or captured.out
        # Check for ANSI color codes
        assert "\x1b[" in output

    def test_file_modes(self, temp_log_file):
        """Test different file modes (append vs write)"""
        # Write mode
        logger1 = setup_logger("test_write", log_file=temp_log_file, file_mode="w")
        logger1.info("First message")
        
        # Append mode
        logger2 = setup_logger("test_append", log_file=temp_log_file, file_mode="a")
        logger2.info("Second message")
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
            assert "First message" in content
            assert "Second message" in content

    def test_custom_log_levels(self, temp_log_file):
        """Test custom log levels for console and file"""
        logger = setup_logger(
            "test_custom_levels",
            log_file=temp_log_file,
            console_log_level="ERROR",
            file_log_level="DEBUG"
        )
        
        # This should only go to file
        logger.info("Info message")
        
        # This should go to both console and file
        logger.error("Error message")
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
            assert "Info message" in content
            assert "Error message" in content
