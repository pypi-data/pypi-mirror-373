"""
Simple and deterministic tool error detection for UI status reporting.

This module only detects ACTUAL tool execution failures, not content that mentions errors.
"""

import json
import re
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass

from ...debug_logger import debug_logger


@dataclass
class ErrorDetectionResult:
    """Result of tool error detection analysis."""
    has_error: bool
    error_type: str
    error_message: str


def detect_tool_error(result: Any, tool_name: str = "unknown", tool_data: Optional[Dict] = None) -> ErrorDetectionResult:
    """
    Detect if a tool call result indicates an ACTUAL execution error.
    
    Only returns has_error=True for 100% certain error scenarios:
    1. Tool returns dict/JSON with stderr field that is not empty
    2. Tool returns dict/JSON with success=false or error field
    3. LiteLLM API errors (litellm.BadRequestError, etc.)
    4. TinyAgent file tool errors with specific error response format
    
    Args:
        result: The tool execution result (string or dict)
        tool_name: Name of the tool that was executed
        tool_data: Additional tool metadata (exit codes, etc.)
        
    Returns:
        ErrorDetectionResult with has_error=True only for actual errors
    """
    
    # Handle None or empty results
    if result is None:
        return ErrorDetectionResult(has_error=False, error_type="no_error", error_message="")
    
    # Convert result to string for analysis
    result_str = str(result) if not isinstance(result, str) else result
    
    # 1. Check structured response data (highest priority)
    if tool_data and isinstance(tool_data, dict):
        # Check for non-empty stderr
        stderr = tool_data.get("stderr", "")
        if stderr and stderr.strip():
            return ErrorDetectionResult(
                has_error=True,
                error_type="stderr_output",
                error_message=f"Tool produced stderr output: {stderr[:100]}"
            )
        
        # Check for non-zero exit code (except grep which uses 1 for "no matches")
        exit_code = tool_data.get("exit_code") or tool_data.get("returncode")
        if exit_code is not None and exit_code != 0:
            # Special case: grep returns 1 for "no matches" which is not an error
            if tool_name == "grep" and exit_code == 1:
                pass  # Not an error
            else:
                return ErrorDetectionResult(
                    has_error=True,
                    error_type="non_zero_exit",
                    error_message=f"Tool exited with code {exit_code}"
                )
        
        # Check success flag
        if "success" in tool_data and tool_data["success"] is False:
            return ErrorDetectionResult(
                has_error=True,
                error_type="success_false",
                error_message="Tool returned success=false"
            )
        
        # Check for error field
        if "error" in tool_data and tool_data["error"]:
            return ErrorDetectionResult(
                has_error=True,
                error_type="error_field",
                error_message=f"Tool returned error: {tool_data['error'][:100]}"
            )
    
    # 2. Try to parse JSON from string result
    try:
        # Look for JSON in the result string
        if "{" in result_str and "}" in result_str:
            # Try to extract JSON
            json_match = re.search(r'\{[^{}]*\}', result_str)
            if json_match:
                json_data = json.loads(json_match.group())
                
                # Check success field
                if json_data.get("success") is False:
                    return ErrorDetectionResult(
                        has_error=True,
                        error_type="success_false",
                        error_message="Tool returned success=false in response"
                    )
                
                # Check error field
                if json_data.get("error") and json_data["error"]:
                    return ErrorDetectionResult(
                        has_error=True,
                        error_type="error_field",
                        error_message=f"Tool returned error: {json_data['error'][:100]}"
                    )
                
                # Check stderr field
                stderr = json_data.get("stderr", "")
                if stderr and stderr.strip():
                    return ErrorDetectionResult(
                        has_error=True,
                        error_type="stderr_output",
                        error_message=f"Tool produced stderr: {stderr[:100]}"
                    )
    except (json.JSONDecodeError, KeyError, TypeError):
        pass  # Not JSON or malformed, continue checking
    
    # 3. Check for LiteLLM API errors (these are actual API failures)
    if "litellm." in result_str and any(err in result_str for err in [
        "BadRequestError", "AuthenticationError", "RateLimitError", 
        "APIError", "APIConnectionError", "APITimeoutError"
    ]):
        return ErrorDetectionResult(
            has_error=True,
            error_type="litellm_error",
            error_message="LiteLLM API error occurred"
        )
    
    # 4. Check for TinyAgent file tool specific error responses
    # These tools return specific error formats when they fail
    if tool_name in ["read_file", "write_file", "update_file", "glob_tool", "grep_tool"]:
        # TinyAgent file tools use specific error format
        if result_str.startswith("Error:") or result_str.startswith("ERROR:"):
            # But exclude informational messages like "ERROR: ... exceeds token limit"
            # This is informational, not a tool failure
            if "exceeds" in result_str and "token limit" in result_str:
                return ErrorDetectionResult(has_error=False, error_type="no_error", error_message="")
            
            # Check for actual file operation errors
            if any(err in result_str for err in [
                "Code provider not available",
                "Permission denied",
                "No such file or directory", 
                "Directory does not exist",
                "not found",
                "File not found"
            ]):
                return ErrorDetectionResult(
                    has_error=True,
                    error_type="file_tool_error",
                    error_message="File tool execution failed"
                )
    
    # No errors detected - tool executed successfully
    return ErrorDetectionResult(has_error=False, error_type="no_error", error_message="")


# For backward compatibility, provide a class-based interface
class ToolErrorDetector:
    """Simple tool error detector class for backward compatibility."""
    
    def detect_tool_error(self, result: Any, tool_name: str = "unknown") -> ErrorDetectionResult:
        """Detect tool errors using the simple detection function."""
        return detect_tool_error(result, tool_name)