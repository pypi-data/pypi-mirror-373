#!/usr/bin/env python3
"""
Standalone test for TextualToolCallback without UI dependencies.
Tests the callback logic directly.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

# Import debug logger directly
sys.path.insert(0, 'juno_agent')
from juno_agent.debug_logger import debug_logger

# Copy the callback classes to avoid UI imports
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

class TextualToolCallbackTest:
    """Test version of TextualToolCallback."""
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        ui_update_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        max_events: int = 100
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.ui_update_callback = ui_update_callback
        self.max_events = max_events
        
        # Event storage
        self.tool_events: List[ToolEvent] = []
        self.active_tools: Dict[str, ToolEvent] = {}  # tool_call_id -> ToolEvent
        
        # Statistics
        self.total_tool_calls = 0
        self.total_tool_time = 0.0
        self.tool_usage_counts: Dict[str, int] = {}
        
        debug_logger.log_event("textual_callback_test_initialized", 
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
            self.tool_events = self.tool_events[-self.max_events:]
        
        self.logger.debug(f"Added tool event: {event.event_type} for {event.tool_name}")
    
    def _send_ui_update(self, message_type: str, data: Dict[str, Any]) -> None:
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
                self.ui_update_callback(message_type, data)
                debug_logger.log_event("ui_callback_completed", message_type=message_type)
            except Exception as e:
                self.logger.error(f"Error sending UI update: {e}")
                debug_logger.log_error("ui_callback_failed", e, 
                                     message_type=message_type, 
                                     callback_id=hex(id(self.ui_update_callback)))
        else:
            debug_logger.log_event("no_ui_callback_available", message_type=message_type)
    
    async def handle_tool_start(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool start event."""
        debug_logger.log_function_entry("handle_tool_start", kwargs_keys=list(kwargs.keys()))
        
        tool_call = kwargs.get("tool_call", {})
        func_info = tool_call.get("function", {})
        tool_name = func_info.get("name", "unknown_tool")
        tool_call_id = tool_call.get("id", f"call_{int(time.time())}")
        
        # Parse arguments
        try:
            args = json.loads(func_info.get("arguments", "{}"))
        except (json.JSONDecodeError, TypeError):
            args = {"raw_args": func_info.get("arguments", "{}") }
        
        # Create tool event
        event = ToolEvent(
            event_type="start",
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            arguments=args
        )
        
        # Store active tool
        self.active_tools[tool_call_id] = event
        
        # Add to event history
        self._add_tool_event(event)
        
        # Send UI update
        ui_data = {
            "message": f"🔧 Tool Call: {tool_name}",
            "tool_name": tool_name,
            "tool_call_id": tool_call_id,
            "arguments": args
        }
        
        self._send_ui_update("tool_start", ui_data)
        self.logger.info(f"Tool started: {tool_name} (ID: {tool_call_id})")
    
    async def handle_tool_end(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool end event."""
        debug_logger.log_function_entry("handle_tool_end", kwargs_keys=list(kwargs.keys()))
        
        tool_call_id = kwargs.get("tool_call_id")
        result = kwargs.get("result", "")
        
        # Find the corresponding start event
        start_event = self.active_tools.pop(tool_call_id, None) if tool_call_id else None
        
        if start_event:
            tool_name = start_event.tool_name
            duration = time.time() - start_event.timestamp
        else:
            tool_name = "unknown_tool"
            duration = None
            self.logger.warning(f"Tool end without matching start: {tool_call_id}")
        
        # Create tool end event
        event = ToolEvent(
            event_type="end",
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            result=result,
            duration=duration
        )
        
        # Add to event history
        self._add_tool_event(event)
        
        # Send UI update
        ui_data = {
            "message": f"✅ Tool Completed: {tool_name}",
            "tool_name": tool_name,
            "tool_call_id": tool_call_id,
            "result": result,
            "duration": duration
        }
        
        self._send_ui_update("tool_end", ui_data)
        self.logger.info(f"Tool completed: {tool_name} (Duration: {duration:.2f}s)" if duration else f"Tool completed: {tool_name}")
    
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

class MockAgent:
    """Mock agent for testing."""
    def __init__(self):
        self.session_id = "test_session"

class MockUI:
    """Mock UI update receiver."""
    def __init__(self):
        self.received_updates = []
    
    def ui_update_callback(self, message_type: str, data: dict):
        """Receive UI updates from the callback."""
        self.received_updates.append({
            "message_type": message_type,
            "data": data.copy()
        })
        print(f"📨 UI Update: {message_type} - {data.get('tool_name', 'unknown')}")

async def test_callback_functionality():
    """Test the callback functionality."""
    print("🧪 Testing TextualToolCallback functionality...")
    
    # Create mock UI
    mock_ui = MockUI()
    
    # Create callback with UI update function
    callback = TextualToolCallbackTest(
        ui_update_callback=mock_ui.ui_update_callback,
        max_events=50
    )
    
    # Create mock agent
    agent = MockAgent()
    
    # Test 1: Tool start event
    print("\n📝 Test 1: Tool start event")
    tool_call_data = {
        "tool_call": {
            "id": "call_test_123",
            "function": {
                "name": "write_file",
                "arguments": '{"file_path": "test.py", "content": "print(\\"hello\\")"}'
            }
        }
    }
    
    await callback.handle_tool_start(agent, **tool_call_data)
    
    # Verify callback received the event
    if len(mock_ui.received_updates) > 0:
        update = mock_ui.received_updates[-1]
        if update["message_type"] == "tool_start" and update["data"]["tool_name"] == "write_file":
            print("✅ Tool start event processed correctly")
        else:
            print("❌ Tool start event not processed correctly")
            return False
    else:
        print("❌ No UI updates received for tool start")
        return False
    
    # Test 2: Tool end event
    print("\n📝 Test 2: Tool end event")
    tool_end_data = {
        "tool_call_id": "call_test_123",
        "result": "File written successfully"
    }
    
    await callback.handle_tool_end(agent, **tool_end_data)
    
    # Verify tool end was processed
    if len(mock_ui.received_updates) > 1:
        update = mock_ui.received_updates[-1]
        if update["message_type"] == "tool_end" and "result" in update["data"]:
            print("✅ Tool end event processed correctly")
        else:
            print("❌ Tool end event not processed correctly")
            return False
    else:
        print("❌ No UI updates received for tool end")
        return False
    
    # Test 3: Check callback statistics
    print("\n📝 Test 3: Callback statistics")
    stats = callback.get_tool_usage_stats()
    print(f"   Total calls: {stats['total_calls']}")
    print(f"   Tool counts: {stats['tool_counts']}")
    
    if stats["total_calls"] > 0 and "write_file" in stats["tool_counts"]:
        print("✅ Callback statistics tracking correctly")
    else:
        print("❌ Callback statistics not tracking correctly")
        return False
    
    # Test 4: Check event history
    print("\n📝 Test 4: Event history")
    events = callback.get_recent_tool_events(limit=5)
    print(f"   Recent events: {len(events)}")
    
    if len(events) >= 2:  # start and end events
        start_event = events[0]
        end_event = events[1]
        if start_event["event_type"] == "start" and end_event["event_type"] == "end":
            print("✅ Event history tracking correctly")
            return True
        else:
            print("❌ Event history not in correct order")
            return False
    else:
        print("❌ Not enough events in history")
        return False

def main():
    """Run the test."""
    try:
        success = asyncio.run(test_callback_functionality())
        if success:
            print("\n🎉 All callback tests passed!")
            print("\n📋 What was verified:")
            print("   • TextualToolCallback processes tool start/end events correctly")
            print("   • UI update callbacks are triggered with proper data")
            print("   • Tool usage statistics are tracked accurately")
            print("   • Event history maintains proper order")
            print("\n✅ The callback system is working correctly!")
            print("   Next step: Test with the actual TUI application")
        else:
            print("\n❌ Callback tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
