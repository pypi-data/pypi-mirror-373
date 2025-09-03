"""Textual callback for tool usage tracking in TinyAgent."""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

# Import debug logger
from ...debug_logger import debug_logger
# Import error detection module
from ..utils.tool_error_detector import detect_tool_error, ErrorDetectionResult


@dataclass
class ToolEvent:
    """Represents a tool usage event."""
    event_type: str  # 'start', 'end', 'error'
    tool_name: str
    timestamp: float
    tool_call_id: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    # Hierarchy information
    agent_level: int = 0
    is_subagent: bool = False
    agent_id: Optional[str] = None
    parent_id: Optional[str] = None
    display_name: Optional[str] = None


class TextualToolCallback:
    """
    A callback for TinyAgent that tracks tool usage for Textual UI applications.
    
    This callback follows the same event handling pattern as the Jupyter callback
    but is designed to integrate with Textual's async architecture.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        ui_update_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        max_events: int = 100,
        agent_level: int = 0,
        agent_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        display_name: Optional[str] = None
    ):
        """
        Initialize the Textual tool callback.
        
        Args:
            logger: Optional logger instance
            ui_update_callback: Optional callback to send UI updates
            max_events: Maximum number of events to store in memory
            agent_level: Hierarchy level (0 = main agent, 1+ = subagent)
            agent_id: Unique identifier for the agent
            parent_id: ID of the parent agent (if subagent)
            display_name: Human-readable name for the agent
        """
        debug_logger.log_function_entry("TextualToolCallback.__init__", 
                                       ui_callback_available=ui_update_callback is not None,
                                       max_events=max_events)
        
        self.logger = logger or logging.getLogger(__name__)
        self.ui_update_callback = ui_update_callback
        self.max_events = max_events
        
        # Hierarchy information
        self.agent_level = agent_level
        self.agent_id = agent_id or "main_agent"
        self.parent_id = parent_id
        self.display_name = display_name or ("Main Agent" if agent_level == 0 else f"Subagent-{agent_level}")
        self.is_subagent = agent_level > 0
        
        # Event storage
        self.tool_events: List[ToolEvent] = []
        self.active_tools: Dict[str, ToolEvent] = {}  # tool_call_id -> ToolEvent
        
        # Statistics
        self.total_tool_calls = 0
        self.total_tool_time = 0.0
        self.tool_usage_counts: Dict[str, int] = {}
        
        self.logger.debug("TextualToolCallback initialized")
        debug_logger.log_event("textual_callback_initialized", 
                              callback_id=hex(id(self)),
                              ui_callback_id=hex(id(ui_update_callback)) if ui_update_callback else None)
    
    def _add_tool_event(self, event: ToolEvent) -> None:
        """Add a tool event to storage with size management."""
        self.tool_events.append(event)
        
        # Update statistics
        if event.event_type == "start":
            self.total_tool_calls += 1
            self.tool_usage_counts[event.tool_name] = self.tool_usage_counts.get(event.tool_name, 0) + 1
        elif event.event_type == "end" and event.duration:
            self.total_tool_time += event.duration
        
        # Trim events if we exceed max size
        if len(self.tool_events) > self.max_events:
            # Remove oldest events (keep recent ones)
            self.tool_events = self.tool_events[-self.max_events:]
        
        self.logger.debug(f"Added tool event: {event.event_type} for {event.tool_name}")
    
    async def _send_ui_update(self, message_type: str, data: Dict[str, Any]) -> None:
        """Send an update to the UI if callback is available."""
        debug_logger.log_function_entry("_send_ui_update", 
                                       message_type=message_type, 
                                       data_keys=list(data.keys()),
                                       ui_callback_available=self.ui_update_callback is not None)
        
        if self.ui_update_callback:
            try:
                debug_logger.log_event("calling_ui_callback", 
                                     message_type=message_type, 
                                     callback_id=hex(id(self.ui_update_callback)))
                
                # Check if the callback is async and await it accordingly
                import asyncio
                import inspect
                if asyncio.iscoroutinefunction(self.ui_update_callback):
                    debug_logger.log_event("ui_callback_is_async", message_type=message_type)
                    await self.ui_update_callback(message_type, data)
                else:
                    debug_logger.log_event("ui_callback_is_sync", message_type=message_type)
                    self.ui_update_callback(message_type, data)
                
                debug_logger.log_event("ui_callback_completed", message_type=message_type)
            except Exception as e:
                self.logger.error(f"Error sending UI update: {e}")
                debug_logger.log_error("ui_callback_failed", e, 
                                     message_type=message_type, 
                                     callback_id=hex(id(self.ui_update_callback)))
        else:
            debug_logger.log_event("no_ui_callback_available", message_type=message_type)
    
    def _format_tool_message(self, tool_name: str, event_type: str) -> str:
        """Format a simple tool usage message."""
        if event_type == "start":
            return f"🛠️ Tool Call: {tool_name}"
        elif event_type == "end":
            return f"✅ Tool Completed: {tool_name}"
        elif event_type == "error":
            return f"❌ Tool Error: {tool_name}"
        else:
            return f"🔧 Tool {event_type}: {tool_name}"
    
    async def __call__(self, event_name: str, agent: Any, *args, **kwargs: Any) -> None:
        """
        Main callback entry point.
        
        This method handles both the new interface (kwargs_dict as positional arg)
        and the legacy interface (**kwargs) for backward compatibility.
        """
        debug_logger.log_callback_invocation("TextualToolCallback", event_name,
                                            agent_id=hex(id(agent)),
                                            args_count=len(args),
                                            kwargs_keys=list(kwargs.keys()),
                                            callback_agent_level=self.agent_level,
                                            callback_agent_id=self.agent_id,
                                            callback_is_subagent=self.is_subagent,
                                            callback_display_name=self.display_name)
        
        # Extract kwargs from either interface
        if args and isinstance(args[0], dict):
            # New interface: kwargs_dict passed as positional argument
            event_kwargs = args[0]
        else:
            # Legacy interface: use **kwargs
            event_kwargs = kwargs
        
        debug_logger.log_event("callback_event_routing", 
                             event_name_param=event_name,
                             event_kwargs_keys=list(event_kwargs.keys()),
                             agent_hierarchy=f"Level {self.agent_level}: {self.display_name}",
                             is_subagent_callback=self.is_subagent)
        
        # Route to appropriate handler
        handler = getattr(self, f"_handle_{event_name}", None)
        if handler:
            debug_logger.log_event("calling_event_handler", 
                                 event_name_param=event_name, 
                                 handler_name=handler.__name__)
            await handler(agent, **event_kwargs)
        else:
            self.logger.debug(f"No handler for event: {event_name}")
            debug_logger.log_event("no_handler_found", event_name_param=event_name)
    
    async def _handle_tool_start(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool start event."""
        debug_logger.log_function_entry("_handle_tool_start", 
                                       kwargs_keys=list(kwargs.keys()),
                                       agent_level=self.agent_level,
                                       agent_id=self.agent_id,
                                       is_subagent=self.is_subagent,
                                       display_name=self.display_name)
        
        # TinyAgent sends: tool_call=tool_call_object (Pydantic model)
        tool_call = kwargs.get("tool_call")
        if not tool_call:
            self.logger.warning("No tool_call in tool_start event")
            return
            
        # Handle Pydantic model attributes
        if hasattr(tool_call, 'function'):
            # It's a Pydantic ChatCompletionMessageToolCall object
            func_info = tool_call.function
            tool_name = func_info.name if hasattr(func_info, 'name') else "unknown_tool"
            tool_call_id = tool_call.id if hasattr(tool_call, 'id') else f"call_{int(time.time())}"
            arguments_str = func_info.arguments if hasattr(func_info, 'arguments') else "{}"
        else:
            # Fallback for dict-like objects
            func_info = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
            tool_name = func_info.get("name", "unknown_tool") if isinstance(func_info, dict) else "unknown_tool"
            tool_call_id = tool_call.get("id", f"call_{int(time.time())}") if isinstance(tool_call, dict) else f"call_{int(time.time())}"
            arguments_str = func_info.get("arguments", "{}") if isinstance(func_info, dict) else "{}"
        
        debug_logger.log_event("tool_start_parameter_extraction",
                             tool_call_available=tool_call is not None,
                             tool_call_id=tool_call_id,
                             tool_name=tool_name)
        
        debug_logger.log_tool_event("start", tool_name, 
                                  tool_call_id=tool_call_id,
                                  agent_level=self.agent_level,
                                  is_subagent=self.is_subagent,
                                  agent_display_name=self.display_name)
        
        # Parse arguments with robust error handling
        try:
            args = json.loads(arguments_str)
        except (json.JSONDecodeError, TypeError) as e:
            args = {"raw_args": arguments_str, "parse_error": str(e)}
            debug_logger.log_error("tool_start_args_parse_failed", e, tool_call_id=tool_call_id)
        
        # Create tool event with hierarchy information
        event = ToolEvent(
            event_type="start",
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            arguments=args,
            agent_level=self.agent_level,
            is_subagent=self.is_subagent,
            agent_id=self.agent_id,
            parent_id=self.parent_id,
            display_name=self.display_name
        )
        
        # Store active tool
        self.active_tools[tool_call_id] = event
        
        # Add to event history
        self._add_tool_event(event)
        
        # Send simple UI update with error handling
        try:
            message = self._format_tool_message(tool_name, "start")
            ui_data = {
                "message": message,
                "tool_name": tool_name,
                "tool_call_id": tool_call_id,
                "arguments": args,
                "agent_level": self.agent_level,
                "is_subagent": self.is_subagent,
                "agent_id": self.agent_id,
                "parent_id": self.parent_id,
                "display_name": self.display_name
            }
            
            debug_logger.log_event("sending_tool_start_ui_update", 
                                 tool_name=tool_name, 
                                 tool_call_id=tool_call_id,
                                 ui_data_keys=list(ui_data.keys()))
            
            await self._send_ui_update("tool_start", ui_data)
        except Exception as e:
            self.logger.error(f"Error sending tool_start UI update: {e}")
            debug_logger.log_error("tool_start_ui_update_failed", e, tool_call_id=tool_call_id)
        
        prefix = f"[Subagent-L{self.agent_level}] " if self.is_subagent else ""
        self.logger.info(f"{prefix}Tool started: {tool_name} (ID: {tool_call_id})")
        debug_logger.log_function_exit("_handle_tool_start")
    
    async def _handle_tool_end(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool end event."""
        debug_logger.log_function_entry("_handle_tool_end", 
                                       kwargs_keys=list(kwargs.keys()),
                                       agent_level=self.agent_level,
                                       agent_id=self.agent_id,
                                       is_subagent=self.is_subagent,
                                       display_name=self.display_name)
        
        # TinyAgent sends: tool_call=tool_call_object, result=result_content
        tool_call = kwargs.get("tool_call")
        result = kwargs.get("result", "")
        
        # Extract tool_call_id from the tool_call object (handle Pydantic model)
        if hasattr(tool_call, 'id'):
            # Pydantic model
            tool_call_id = tool_call.id
        elif isinstance(tool_call, dict):
            # Dictionary
            tool_call_id = tool_call.get("id")
        else:
            tool_call_id = None
        
        debug_logger.log_event("tool_end_parameter_extraction", 
                             tool_call_available=tool_call is not None,
                             tool_call_id=tool_call_id,
                             result_length=len(str(result)) if result else 0)
        
        # Find the corresponding start event
        start_event = self.active_tools.pop(tool_call_id, None) if tool_call_id else None
        
        if start_event:
            tool_name = start_event.tool_name
            duration = time.time() - start_event.timestamp
            debug_logger.log_event("tool_end_matched_start", tool_name=tool_name, tool_call_id=tool_call_id)
        else:
            # Fallback: extract tool name from tool_call if available
            if hasattr(tool_call, 'function'):
                # Pydantic model
                func_info = tool_call.function
                tool_name = func_info.name if hasattr(func_info, 'name') else "unknown_tool"
            elif isinstance(tool_call, dict):
                # Dictionary
                func_info = tool_call.get("function", {})
                tool_name = func_info.get("name", "unknown_tool") if isinstance(func_info, dict) else "unknown_tool"
            else:
                tool_name = "unknown_tool"
            duration = None
            self.logger.warning(f"Tool end without matching start: {tool_call_id}")
            debug_logger.log_event("tool_end_orphaned", 
                                 tool_call_id=tool_call_id,
                                 fallback_tool_name=tool_name)
        
        debug_logger.log_tool_event("end", tool_name, 
                                  tool_call_id=tool_call_id,
                                  duration=duration,
                                  result_length=len(str(result)) if result else 0,
                                  agent_level=self.agent_level,
                                  is_subagent=self.is_subagent,
                                  agent_display_name=self.display_name)
        
        # Detect tool execution errors (only actual failures, not content mentioning errors)
        error_detection: ErrorDetectionResult = detect_tool_error(result, tool_name)
        
        debug_logger.log_event("tool_error_analysis_completed",
                             tool_name=tool_name,
                             tool_call_id=tool_call_id,
                             has_error=error_detection.has_error,
                             error_type=error_detection.error_type)
        
        # Log error detection details if error found
        if error_detection.has_error:
            self.logger.warning(f"Tool error detected for {tool_name}: {error_detection.error_message}")
            debug_logger.log_event("tool_error_detected_details",
                                 tool_name=tool_name,
                                 error_type=error_detection.error_type,
                                 error_message=error_detection.error_message)
        
        # Determine the event type based on error detection
        event_type = "error" if error_detection.has_error else "end"
        error_message = error_detection.error_message if error_detection.has_error else None
        
        # Create tool end event with hierarchy information and error status
        event = ToolEvent(
            event_type=event_type,
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            result=result,
            error=error_message,
            duration=duration,
            agent_level=self.agent_level,
            is_subagent=self.is_subagent,
            agent_id=self.agent_id,
            parent_id=self.parent_id,
            display_name=self.display_name
        )
        
        # Add to event history
        self._add_tool_event(event)
        
        # Send enhanced UI update with error status and handling
        try:
            # Use error-aware message formatting
            message_event_type = "error" if error_detection.has_error else "end"
            message = self._format_tool_message(tool_name, message_event_type)
            
            # Create UI data including error information
            ui_data = {
                "message": message,
                "tool_name": tool_name,
                "tool_call_id": tool_call_id,
                "result": result,
                "duration": duration,
                "agent_level": self.agent_level,
                "is_subagent": self.is_subagent,
                "agent_id": self.agent_id,
                "parent_id": self.parent_id,
                "display_name": self.display_name,
                # Error detection information
                "has_error": error_detection.has_error,
                "error_type": error_detection.error_type,
                "error_message": error_detection.error_message
            }
            
            debug_logger.log_event("sending_enhanced_tool_end_ui_update", 
                                 tool_name=tool_name, 
                                 tool_call_id=tool_call_id,
                                 has_error=error_detection.has_error,
                                 error_type=error_detection.error_type,
                                 ui_data_keys=list(ui_data.keys()))
            
            # Send appropriate UI update based on error status
            ui_message_type = "tool_error" if error_detection.has_error else "tool_end"
            await self._send_ui_update(ui_message_type, ui_data)
        except Exception as e:
            self.logger.error(f"Error sending tool_end UI update: {e}")
            debug_logger.log_error("tool_end_ui_update_failed", e, tool_call_id=tool_call_id)
        
        prefix = f"[Subagent-L{self.agent_level}] " if self.is_subagent else ""
        
        # Enhanced logging with error status
        if error_detection.has_error:
            duration_str = f" (Duration: {duration:.2f}s)" if duration else ""
            self.logger.info(f"{prefix}Tool completed with error: {tool_name}{duration_str} - {error_detection.error_message}")
        else:
            duration_str = f" (Duration: {duration:.2f}s)" if duration else ""
            self.logger.info(f"{prefix}Tool completed successfully: {tool_name}{duration_str}")
        
        debug_logger.log_function_exit("_handle_tool_end")
    
    # NOTE: TinyAgent doesn't have a separate tool_error event.
    # Errors are handled as regular tool_end events with error messages in the result.
    # The _handle_tool_error method has been removed as it's not called by TinyAgent.
    #
    # MIGRATION NOTE: If upgrading from a version that had _handle_tool_error,
    # error handling logic should be moved to _handle_tool_end and check if
    # the result contains error information.
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        return {
            "total_calls": self.total_tool_calls,
            "total_time": self.total_tool_time,
            "average_time": self.total_tool_time / max(self.total_tool_calls, 1),
            "tool_counts": self.tool_usage_counts.copy(),
            "recent_events": len(self.tool_events),
            "active_tools": len(self.active_tools)
        }
    
    def get_recent_tool_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tool events as dictionaries."""
        recent_events = self.tool_events[-limit:] if limit > 0 else self.tool_events
        return [
            {
                "event_type": event.event_type,
                "tool_name": event.tool_name,
                "timestamp": event.timestamp,
                "tool_call_id": event.tool_call_id,
                "duration": event.duration,
                "error": event.error
            }
            for event in recent_events
        ]
    
    def clear_events(self) -> None:
        """Clear all stored events and reset statistics."""
        self.tool_events.clear()
        self.active_tools.clear()
        self.total_tool_calls = 0
        self.total_tool_time = 0.0
        self.tool_usage_counts.clear()
        self.logger.info("Tool usage tracking cleared")
    
    async def close(self) -> None:
        """Clean up resources."""
        self.clear_events()
        self.logger.debug("TextualToolCallback closed")


def create_textual_tool_callback(
    logger: Optional[logging.Logger] = None,
    ui_update_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    max_events: int = 100,
    agent_level: int = 0,
    agent_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    display_name: Optional[str] = None
) -> TextualToolCallback:
    """
    Factory function to create a TextualToolCallback instance.
    
    Args:
        logger: Optional logger instance
        ui_update_callback: Optional callback to send UI updates
        max_events: Maximum number of events to store in memory
        agent_level: Hierarchy level (0 = main agent, 1+ = subagent)
        agent_id: Unique identifier for the agent
        parent_id: ID of the parent agent (if subagent)
        display_name: Human-readable name for the agent
        
    Returns:
        TextualToolCallback instance
    """
    return TextualToolCallback(
        logger=logger,
        ui_update_callback=ui_update_callback,
        max_events=max_events,
        agent_level=agent_level,
        agent_id=agent_id,
        parent_id=parent_id,
        display_name=display_name
    )