"""Test debug logging functionality."""

import pytest
from pathlib import Path
from juno_agent.config import DebugLogManager, ConfigManager


def test_debug_log_manager_creation(tmp_path):
    """Test that DebugLogManager creates proper log files."""
    config_dir = tmp_path / ".askbudi"
    config_dir.mkdir()
    
    debug_logger = DebugLogManager(config_dir)
    
    # Check that logs directory was created
    assert (config_dir / "logs").exists()
    
    # Check that log file was created
    log_file = debug_logger.get_log_file_path()
    assert log_file.exists()
    assert "debug_" in log_file.name
    assert log_file.suffix == ".log"


def test_debug_log_manager_logging(tmp_path):
    """Test that DebugLogManager logs messages properly."""
    config_dir = tmp_path / ".askbudi"
    config_dir.mkdir()
    
    debug_logger = DebugLogManager(config_dir)
    
    # Test different log levels
    debug_logger.debug("Debug message", test_param="debug_value")
    debug_logger.info("Info message", test_param="info_value")
    debug_logger.warning("Warning message", test_param="warning_value")
    debug_logger.error("Error message", test_param="error_value")
    
    # Check that log file contains the messages
    log_file = debug_logger.get_log_file_path()
    log_content = log_file.read_text()
    
    assert "Debug message" in log_content
    assert "Info message" in log_content
    assert "Warning message" in log_content
    assert "Error message" in log_content
    assert "test_param" in log_content


def test_config_manager_debug_logger_integration(tmp_path):
    """Test that ConfigManager can create debug loggers."""
    workdir = tmp_path / "project"
    workdir.mkdir()
    
    config_manager = ConfigManager(workdir)
    debug_logger = config_manager.create_debug_logger()
    
    assert isinstance(debug_logger, DebugLogManager)
    
    # Test that it logs
    debug_logger.info("Test message from config manager")
    
    log_file = debug_logger.get_log_file_path()
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Test message from config manager" in log_content