"""Comprehensive debug logging system for tool usage display debugging."""

import logging
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class DebugLogger:
    """Centralized debug logger for tool usage display debugging."""
    
    def __init__(self, log_file_path: str = "app_run.log"):
        self.log_file_path = Path(log_file_path)
        self._manage_log_file()
        self.logger = self._setup_logger()
    
    def _manage_log_file(self):
        """Manage log file size and add session separator."""
        # Add session separator if file exists and has content
        if self.log_file_path.exists() and self.log_file_path.stat().st_size > 0:
            with open(self.log_file_path, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"NEW SESSION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
        
        # If log file is too large (>10MB), truncate it but keep last 5MB
        max_size = 10 * 1024 * 1024  # 10MB
        keep_size = 5 * 1024 * 1024   # 5MB
        
        if self.log_file_path.exists() and self.log_file_path.stat().st_size > max_size:
            try:
                # Try to read the file and keep only the last part
                with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read all content first
                    full_content = f.read()
                
                # Keep only the last keep_size bytes worth of content
                # Convert to bytes to measure accurately, then back to string
                content_bytes = full_content.encode('utf-8', errors='ignore')
                if len(content_bytes) > keep_size:
                    # Keep the last keep_size bytes
                    truncated_bytes = content_bytes[-keep_size:]
                    # Decode back to string, ignoring any incomplete characters at the start
                    content = truncated_bytes.decode('utf-8', errors='ignore')
                else:
                    content = full_content
                
                # Find first complete line to avoid partial lines at the beginning
                first_newline = content.find('\n')
                if first_newline != -1:
                    content = content[first_newline + 1:]
                
                # Write the truncated content back
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"[LOG TRUNCATED - Previous content was too large]\n")
                    f.write(f"[Keeping last ~{keep_size//1024//1024}MB of logs]\n\n")
                    f.write(content)
                    
            except Exception as e:
                # If truncation fails, just create a new log file
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"[LOG TRUNCATION FAILED - Starting fresh log]\n")
                    f.write(f"[Error: {str(e)}]\n\n")
        
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger with file output."""
        # Create logger
        logger = logging.getLogger("ToolDisplayDebug")
        logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create file handler - append to file to integrate with TinyAgent logs
        file_handler = logging.FileHandler(self.log_file_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%H:%M:%S.%f'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Log initialization message to mark DebugLogger start
        logger.info(f"DebugLogger initialized - writing to {self.log_file_path}")
        
        return logger
    
    def log_function_entry(self, func_name: str, **kwargs):
        """Log function entry with parameters."""
        params = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        self.logger.debug(f"ENTRY: {func_name} | params={json.dumps(params, indent=2)}")
    
    def log_function_exit(self, func_name: str, result: Any = None):
        """Log function exit with result."""
        safe_result = self._safe_serialize(result)
        self.logger.debug(f"EXIT: {func_name} | result={json.dumps(safe_result, indent=2)}")
    
    def log_event(self, event_name: str, **kwargs):
        """Log a general event with data."""
        data = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        self.logger.info(f"EVENT: {event_name} | data={json.dumps(data, indent=2)}")
    
    def log_tool_event(self, event_type: str, tool_name: str, **kwargs):
        """Log tool-specific events."""
        data = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        # Add special handling for subagent tools
        if tool_name in ['subAgent', 'subagent', 'coding_subagent']:
            self.logger.info(f"SUBAGENT_TOOL_{event_type.upper()}: {tool_name} | data={json.dumps(data, indent=2)}")
        self.logger.info(f"TOOL_{event_type.upper()}: {tool_name} | data={json.dumps(data, indent=2)}")
    
    def log_ui_update(self, component: str, action: str, **kwargs):
        """Log UI update events."""
        data = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        self.logger.info(f"UI_UPDATE: {component}.{action} | data={json.dumps(data, indent=2)}")
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None, **kwargs):
        """Log errors with stack trace."""
        data = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        error_info = {
            "message": error_msg,
            "context": data
        }
        
        if exception:
            error_info["exception_type"] = type(exception).__name__
            error_info["exception_msg"] = str(exception)
            error_info["traceback"] = traceback.format_exc()
        
        self.logger.error(f"ERROR: {json.dumps(error_info, indent=2)}")
    
    def log_state_change(self, component: str, field: str, old_value: Any, new_value: Any):
        """Log state changes."""
        self.logger.debug(f"STATE_CHANGE: {component}.{field} | {self._safe_serialize(old_value)} -> {self._safe_serialize(new_value)}")
    
    def log_callback_invocation(self, callback_name: str, event_name: str, **kwargs):
        """Log callback invocations."""
        data = {k: self._safe_serialize(v) for k, v in kwargs.items()}
        # Add extra info for subagent-related callbacks
        if 'is_subagent' in kwargs or 'agent_level' in kwargs:
            self.logger.info(f"SUBAGENT_CALLBACK: {callback_name}.{event_name} | data={json.dumps(data, indent=2)}")
        self.logger.info(f"CALLBACK: {callback_name}.{event_name} | data={json.dumps(data, indent=2)}")
    
    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize objects for JSON logging."""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._safe_serialize(item) for item in obj[:5]]  # Limit list size
        elif isinstance(obj, dict):
            # Limit dict size and avoid recursive serialization
            limited_dict = {}
            for i, (k, v) in enumerate(obj.items()):
                if i >= 10:  # Limit number of keys
                    limited_dict["..."] = f"({len(obj) - 10} more items)"
                    break
                limited_dict[str(k)] = self._safe_serialize(v)
            return limited_dict
        elif hasattr(obj, '__class__'):
            return f"<{obj.__class__.__name__} at {hex(id(obj))}>"
        else:
            return str(obj)[:200]  # Truncate long strings


# Global debug logger instance
debug_logger = DebugLogger()