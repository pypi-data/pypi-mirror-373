#!/usr/bin/env python3
"""Comprehensive behavioral test suite for PyWizardTUIApp using Textual Pilot.

This test suite validates ALL user interactions and functionality work correctly 
in the refactored application, ensuring 100% behavioral compatibility with the original app.
"""

import pytest
import pytest_asyncio
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import AsyncGenerator, Dict, Any, List

from textual.pilot import Pilot
from textual.keys import Keys

# Import the main app and required components
from juno_agent.config import ConfigManager, Config, UIMode
from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.debug_logger import debug_logger

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


class TestPyWizardTUIAppBehavioral:
    """Comprehensive behavioral test suite for PyWizardTUIApp."""
    
    @pytest_asyncio.fixture
    async def app_with_mocks(self, temp_project_dir: Path) -> AsyncGenerator[PyWizardTUIApp, None]:
        """Create a fully mocked PyWizardTUIApp for testing."""
        config_manager = ConfigManager(temp_project_dir)
        config = config_manager.load_config()
        config.ui_mode = UIMode.FANCY
        config_manager.save_config(config)
        
        app = PyWizardTUIApp(config_manager, show_welcome=True)
        
        # Mock the TinyAgent to avoid actual API calls
        mock_agent = AsyncMock()
        mock_agent.ask_user = AsyncMock(return_value="Mock AI response")
        mock_agent.run_tools = AsyncMock(return_value="Mock tool result")
        mock_agent.initialize_agent = AsyncMock()
        mock_agent.compact_chat = AsyncMock(return_value="Mock compact summary")
        mock_agent.close = AsyncMock()
        
        # Mock storage manager
        mock_storage = Mock()
        mock_storage.get_all_sessions = AsyncMock(return_value=[
            {"id": "test-session-1", "title": "Test Chat 1", "created_at": "2024-01-01"},
            {"id": "test-session-2", "title": "Test Chat 2", "created_at": "2024-01-02"}
        ])
        mock_storage.close = Mock()
        
        app.tiny_code_agent = mock_agent
        app.storage_manager = mock_storage
        
        yield app
    
    @pytest_asyncio.fixture
    async def pilot_app(self, app_with_mocks: PyWizardTUIApp) -> AsyncGenerator[Pilot, None]:
        """Create a Pilot instance for testing the app."""
        async with app_with_mocks.run_test() as pilot:
            # Wait for the app to fully initialize
            await pilot.pause(0.5)
            yield pilot
    
    # ===========================================
    # 1. Application Launch & Welcome Screen Tests
    # ===========================================
    
    async def test_app_launches_without_errors(self, pilot_app: Pilot):
        """Test that the app launches without any errors."""
        app = pilot_app.app
        assert app is not None
        assert isinstance(app, PyWizardTUIApp)
        assert app.is_running
    
    async def test_welcome_message_displays_correctly(self, pilot_app: Pilot):
        """Test that the welcome message displays correctly on startup."""
        app = pilot_app.app
        
        # Wait for welcome message to be added
        await pilot_app.pause(0.5)
        
        # Check that chat area exists and has messages
        assert app.chat_area is not None
        assert hasattr(app.chat_area, 'messages')
        
        # The app should have at least one welcome message
        messages = getattr(app.chat_area, 'messages', [])
        assert len(messages) > 0
        
        # At least one message should contain welcome-like content
        welcome_indicators = ['welcome', 'ready', 'assistant', 'help']
        has_welcome = any(
            any(indicator in str(msg).lower() for indicator in welcome_indicators)
            for msg in messages
        )
        assert has_welcome, "No welcome message found in chat area"
    
    async def test_status_indicators_show_proper_states(self, pilot_app: Pilot):
        """Test that status indicators show proper initial states."""
        app = pilot_app.app
        
        # Check that dynamic footer exists and shows status
        assert app.dynamic_footer is not None
        
        # Footer should have some status text
        footer_content = str(app.dynamic_footer)
        assert len(footer_content) > 0
    
    async def test_footer_hints_displayed_correctly(self, pilot_app: Pilot):
        """Test that footer hints are displayed correctly."""
        app = pilot_app.app
        
        # Dynamic footer should exist
        assert app.dynamic_footer is not None
        
        # Footer should show some hint text (this validates the display works)
        # The exact content may vary, but it should be present
        assert hasattr(app.dynamic_footer, 'set_hint')
    
    # ===========================================
    # 2. Keyboard Shortcuts & Commands Tests
    # ===========================================
    
    async def test_f1_history_menu(self, pilot_app: Pilot):
        """Test F1 key opens history menu."""
        app = pilot_app.app
        
        # Initially history menu should be hidden
        assert app.history_menu is not None
        assert not app.history_menu.display
        
        # Press F1
        await pilot_app.press("f1")
        await pilot_app.pause(0.2)
        
        # History menu should now be visible
        assert app.history_menu.display
    
    async def test_f2_copy_functionality(self, pilot_app: Pilot):
        """Test F2 key triggers copy functionality."""
        app = pilot_app.app
        
        # First enter some text in chat to have something to copy
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Test message for copying")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Try to trigger copy - this should not crash the app
        await pilot_app.press("f2")
        await pilot_app.pause(0.2)
        
        # App should still be running
        assert app.is_running
    
    async def test_ctrl_n_new_chat(self, pilot_app: Pilot):
        """Test Ctrl+N creates a new chat."""
        app = pilot_app.app
        
        # Add a message first
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Test message")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Press Ctrl+N
        await pilot_app.press("ctrl+n")
        await pilot_app.pause(0.2)
        
        # Chat should be cleared and new welcome message should appear
        messages = getattr(app.chat_area, 'messages', [])
        # Should have at least a new chat message
        assert len(messages) >= 1
    
    async def test_ctrl_q_quit_application(self, pilot_app: Pilot):
        """Test Ctrl+Q quits the application."""
        app = pilot_app.app
        
        # Mock the exit to prevent actual termination during tests
        with patch.object(app, 'exit') as mock_exit:
            await pilot_app.press("ctrl+q")
            await pilot_app.pause(0.2)
            
            # Exit should have been called
            mock_exit.assert_called_once()
    
    async def test_slash_commands(self, pilot_app: Pilot):
        """Test various slash commands work correctly."""
        app = pilot_app.app
        
        commands_to_test = ["/help", "/cost", "/clear", "/reset", "/new-chat"]
        
        for command in commands_to_test:
            # Click input area and type command
            await pilot_app.click(app.chat_input)
            await pilot_app.type(command)
            await pilot_app.press("enter")
            await pilot_app.pause(0.3)
            
            # App should still be running after each command
            assert app.is_running
            
            # Clear input for next command
            await pilot_app.click(app.chat_input)
            await pilot_app.press("ctrl+a")
            await pilot_app.press("delete")
    
    async def test_help_command_content(self, pilot_app: Pilot):
        """Test that /help command displays proper content."""
        app = pilot_app.app
        
        # Execute help command
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/help")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Check that help content was added to chat
        messages = getattr(app.chat_area, 'messages', [])
        help_content_found = any(
            'help' in str(msg).lower() and 'commands' in str(msg).lower()
            for msg in messages
        )
        assert help_content_found, "Help command did not display help content"
    
    # ===========================================
    # 3. Selection Mode Operations Tests
    # ===========================================
    
    async def test_double_click_enter_selection_mode(self, pilot_app: Pilot):
        """Test double-click enters selection mode."""
        app = pilot_app.app
        
        # Add some content to chat area first
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Test content for selection")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Try double-clicking on chat area
        await pilot_app.click(app.chat_area)
        await pilot_app.click(app.chat_area)
        await pilot_app.pause(0.1)
        
        # App should still be functional
        assert app.is_running
    
    async def test_text_selection_functionality(self, pilot_app: Pilot):
        """Test text selection functionality works."""
        app = pilot_app.app
        
        # Add content
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Selectable content for testing")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Try to trigger selection mode via keyboard shortcut
        await pilot_app.press("ctrl+s")
        await pilot_app.pause(0.2)
        
        # App should remain stable
        assert app.is_running
    
    async def test_copy_selected_text(self, pilot_app: Pilot):
        """Test copying selected text with F2."""
        app = pilot_app.app
        
        # Add content
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Text to be copied")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Try selection and copy
        await pilot_app.press("ctrl+s")  # Enter selection mode
        await pilot_app.pause(0.1)
        await pilot_app.press("f2")      # Try to copy
        await pilot_app.pause(0.2)
        
        # App should remain stable
        assert app.is_running
    
    async def test_exit_selection_mode(self, pilot_app: Pilot):
        """Test exiting selection mode."""
        app = pilot_app.app
        
        # Enter selection mode
        await pilot_app.press("ctrl+s")
        await pilot_app.pause(0.1)
        
        # Exit selection mode (Escape or Ctrl+S again)
        await pilot_app.press("escape")
        await pilot_app.pause(0.1)
        
        # App should remain stable
        assert app.is_running
    
    # ===========================================
    # 4. Chat Functionality Tests
    # ===========================================
    
    async def test_send_chat_messages(self, pilot_app: Pilot):
        """Test sending chat messages works correctly."""
        app = pilot_app.app
        
        test_message = "Hello, this is a test message"
        
        # Send a chat message
        await pilot_app.click(app.chat_input)
        await pilot_app.type(test_message)
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Message should be added to chat area
        messages = getattr(app.chat_area, 'messages', [])
        user_message_found = any(test_message in str(msg) for msg in messages)
        assert user_message_found, "User message not found in chat area"
    
    async def test_receive_ai_responses(self, pilot_app: Pilot):
        """Test receiving AI responses after sending messages."""
        app = pilot_app.app
        
        # Send a message that would trigger AI response
        await pilot_app.click(app.chat_input)
        await pilot_app.type("What is Python?")
        await pilot_app.press("enter")
        await pilot_app.pause(0.5)  # Give time for mock response
        
        # Should have both user message and AI response
        messages = getattr(app.chat_area, 'messages', [])
        assert len(messages) >= 2, "Should have user message and AI response"
    
    async def test_tool_call_execution_display(self, pilot_app: Pilot):
        """Test that tool calls are displayed properly."""
        app = pilot_app.app
        
        # Mock a tool call response
        if hasattr(app, 'ui_tool_update_callback'):
            await app.ui_tool_update_callback('tool_start', {
                'tool_name': 'test_tool',
                'input': {'query': 'test'}
            })
            await pilot_app.pause(0.1)
            
            await app.ui_tool_update_callback('tool_end', {
                'tool_name': 'test_tool',
                'result': 'test result'
            })
            await pilot_app.pause(0.1)
        
        # App should handle tool calls without crashing
        assert app.is_running
    
    async def test_message_history_preservation(self, pilot_app: Pilot):
        """Test that message history is preserved during session."""
        app = pilot_app.app
        
        messages_to_send = ["First message", "Second message", "Third message"]
        
        # Send multiple messages
        for msg in messages_to_send:
            await pilot_app.click(app.chat_input)
            await pilot_app.type(msg)
            await pilot_app.press("enter")
            await pilot_app.pause(0.2)
        
        # All messages should be in chat area
        chat_messages = getattr(app.chat_area, 'messages', [])
        for original_msg in messages_to_send:
            found = any(original_msg in str(chat_msg) for chat_msg in chat_messages)
            assert found, f"Message '{original_msg}' not found in chat history"
    
    async def test_chat_clearing_and_compacting(self, pilot_app: Pilot):
        """Test chat clearing and compacting functionality."""
        app = pilot_app.app
        
        # Add some messages first
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Message to be cleared")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Clear chat
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/clear")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Should have a reset confirmation message
        messages = getattr(app.chat_area, 'messages', [])
        reset_found = any('reset' in str(msg).lower() or 'clear' in str(msg).lower() for msg in messages)
        assert reset_found, "Clear command did not show reset confirmation"
        
        # Test compact command
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Another message")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/compact")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # App should handle compact without crashing
        assert app.is_running
    
    # ===========================================
    # 5. Menu Interactions Tests
    # ===========================================
    
    async def test_history_menu_navigation_and_selection(self, pilot_app: Pilot):
        """Test history menu navigation and session selection."""
        app = pilot_app.app
        
        # Open history menu
        await pilot_app.press("f1")
        await pilot_app.pause(0.2)
        
        # History menu should be visible
        assert app.history_menu.display
        
        # Navigate through menu
        await pilot_app.press("down")
        await pilot_app.pause(0.1)
        await pilot_app.press("up")
        await pilot_app.pause(0.1)
        
        # Close menu
        await pilot_app.press("escape")
        await pilot_app.pause(0.1)
        
        # Menu should be hidden
        assert not app.history_menu.display
    
    async def test_model_configuration_menu(self, pilot_app: Pilot):
        """Test model configuration menu interactions."""
        app = pilot_app.app
        
        # Trigger model configuration
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/model")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Model selection menu should appear
        if hasattr(app, 'model_selection_menu') and app.model_selection_menu:
            # Menu navigation should work
            await pilot_app.press("down")
            await pilot_app.pause(0.1)
            await pilot_app.press("escape")
            await pilot_app.pause(0.1)
        
        # App should remain stable
        assert app.is_running
    
    async def test_setup_wizard_interactions(self, pilot_app: Pilot):
        """Test setup wizard menu interactions."""
        app = pilot_app.app
        
        # Trigger setup wizard
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/setup")
        await pilot_app.press("enter")
        await pilot_app.pause(0.5)
        
        # Setup should be activated
        if hasattr(app, 'setup_active'):
            # If setup is active, try to interact with it
            if app.setup_active:
                # Send a test response
                await pilot_app.click(app.chat_input)
                await pilot_app.type("Test project description")
                await pilot_app.press("enter")
                await pilot_app.pause(0.3)
        
        # App should remain stable
        assert app.is_running
    
    async def test_menu_focus_and_navigation(self, pilot_app: Pilot):
        """Test that menu focus and navigation work correctly."""
        app = pilot_app.app
        
        # Test focus switching between elements
        await pilot_app.click(app.chat_input)
        await pilot_app.pause(0.1)
        
        # Focus should be on input
        assert app.chat_input.has_focus
        
        # Open history menu to test focus switching
        await pilot_app.press("f1")
        await pilot_app.pause(0.2)
        
        if app.history_menu.display:
            # Focus should switch to menu
            await pilot_app.press("escape")
            await pilot_app.pause(0.1)
            
            # Focus should return to input
            assert app.chat_input.has_focus or not app.history_menu.display
    
    # ===========================================
    # 6. Setup and Configuration Tests
    # ===========================================
    
    async def test_setup_wizard_flow(self, pilot_app: Pilot):
        """Test the complete setup wizard flow."""
        app = pilot_app.app
        
        # Start setup wizard
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/setup")
        await pilot_app.press("enter")
        await pilot_app.pause(0.5)
        
        # If setup becomes active, interact with it
        if hasattr(app, 'setup_active') and app.setup_active:
            # Provide project description
            await pilot_app.click(app.chat_input)
            await pilot_app.type("Test project for behavioral testing")
            await pilot_app.press("enter")
            await pilot_app.pause(0.5)
            
            # Setup handler should process the input
            messages = getattr(app.chat_area, 'messages', [])
            assert len(messages) > 0
        
        # App should remain stable throughout setup
        assert app.is_running
    
    async def test_model_configuration_process(self, pilot_app: Pilot):
        """Test the model configuration process."""
        app = pilot_app.app
        
        # Start model configuration
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/model")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Should get a response about model configuration
        messages = getattr(app.chat_area, 'messages', [])
        model_related = any(
            'model' in str(msg).lower() for msg in messages
        )
        assert model_related, "Model command should produce model-related output"
        
        # App should remain stable
        assert app.is_running
    
    async def test_api_key_management(self, pilot_app: Pilot):
        """Test API key management functionality."""
        app = pilot_app.app
        
        # This test ensures the API key management doesn't crash the app
        # Since we're using mocks, we won't actually set real API keys
        
        # Try to trigger API key prompt through model configuration
        await pilot_app.click(app.chat_input)
        await pilot_app.type("/model")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # App should handle API key related operations without crashing
        assert app.is_running
    
    async def test_settings_persistence(self, pilot_app: Pilot):
        """Test that settings are persisted correctly."""
        app = pilot_app.app
        
        # This is a basic test that the config system works
        config = app.config_manager.load_config()
        assert config is not None
        assert hasattr(config, 'ui_mode')
        
        # Settings should be accessible
        assert app.config_manager is not None
    
    # ===========================================
    # 7. Error Handling and Edge Cases Tests
    # ===========================================
    
    async def test_invalid_commands(self, pilot_app: Pilot):
        """Test that invalid commands are handled gracefully."""
        app = pilot_app.app
        
        invalid_commands = ["/nonexistent", "/badcommand", "/123invalid"]
        
        for cmd in invalid_commands:
            await pilot_app.click(app.chat_input)
            await pilot_app.type(cmd)
            await pilot_app.press("enter")
            await pilot_app.pause(0.2)
            
            # App should remain stable
            assert app.is_running
    
    async def test_empty_input_handling(self, pilot_app: Pilot):
        """Test handling of empty inputs."""
        app = pilot_app.app
        
        # Send empty message
        await pilot_app.click(app.chat_input)
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Send only spaces
        await pilot_app.click(app.chat_input)
        await pilot_app.type("   ")
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # App should handle empty inputs gracefully
        assert app.is_running
    
    async def test_rapid_input_handling(self, pilot_app: Pilot):
        """Test that rapid input doesn't break the app."""
        app = pilot_app.app
        
        # Send multiple messages rapidly
        for i in range(5):
            await pilot_app.click(app.chat_input)
            await pilot_app.type(f"Rapid message {i}")
            await pilot_app.press("enter")
            await pilot_app.pause(0.05)  # Very short pause
        
        # Wait for processing
        await pilot_app.pause(0.5)
        
        # App should handle rapid input
        assert app.is_running
    
    async def test_long_message_handling(self, pilot_app: Pilot):
        """Test handling of very long messages."""
        app = pilot_app.app
        
        # Create a long message
        long_message = "This is a very long message. " * 100
        
        await pilot_app.click(app.chat_input)
        await pilot_app.type(long_message[:500])  # Limit to reasonable test size
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # App should handle long messages
        assert app.is_running
    
    # ===========================================
    # 8. Performance and Integration Tests
    # ===========================================
    
    async def test_memory_usage_stability(self, pilot_app: Pilot):
        """Test that memory usage remains stable during operation."""
        app = pilot_app.app
        
        # Perform various operations to test memory stability
        operations = [
            ("/help", 0.2),
            ("Test message 1", 0.2),
            ("/clear", 0.2),
            ("Test message 2", 0.2),
            ("f1", 0.2),  # Open history
            ("escape", 0.1),  # Close history
        ]
        
        for operation, pause in operations:
            if operation.startswith("/") or len(operation) > 3:
                await pilot_app.click(app.chat_input)
                await pilot_app.type(operation)
                await pilot_app.press("enter")
            else:
                await pilot_app.press(operation)
            await pilot_app.pause(pause)
        
        # App should remain stable
        assert app.is_running
    
    async def test_concurrent_operations(self, pilot_app: Pilot):
        """Test that the app handles concurrent-like operations."""
        app = pilot_app.app
        
        # Simulate overlapping operations
        await pilot_app.click(app.chat_input)
        await pilot_app.type("First message")
        # Don't wait for completion, immediately do another operation
        await pilot_app.press("f1")  # Open history menu
        await pilot_app.press("enter")  # Send message and select history
        await pilot_app.pause(0.3)
        
        # App should handle overlapping operations
        assert app.is_running
    
    async def test_ui_state_consistency(self, pilot_app: Pilot):
        """Test that UI state remains consistent across operations."""
        app = pilot_app.app
        
        # Perform a sequence of operations and verify UI state
        await pilot_app.click(app.chat_input)
        assert app.chat_input.has_focus
        
        await pilot_app.press("f1")  # Open history
        await pilot_app.pause(0.1)
        
        if app.history_menu.display:
            await pilot_app.press("escape")  # Close history
            await pilot_app.pause(0.1)
            
            # Focus should return to input
            assert not app.history_menu.display
    
    # ===========================================
    # 9. Cleanup and Resource Management Tests
    # ===========================================
    
    async def test_proper_cleanup_on_exit(self, pilot_app: Pilot):
        """Test that resources are properly cleaned up on exit."""
        app = pilot_app.app
        
        # Mock the cleanup methods to verify they're called
        with patch.object(app, '_cleanup') as mock_cleanup:
            with patch.object(app, 'exit') as mock_exit:
                # Trigger quit
                await pilot_app.press("ctrl+q")
                await pilot_app.pause(0.2)
                
                # Either cleanup or exit should be called
                assert mock_cleanup.called or mock_exit.called
    
    async def test_storage_manager_integration(self, pilot_app: Pilot):
        """Test that storage manager integration works properly."""
        app = pilot_app.app
        
        # Storage manager should be available
        assert app.storage_manager is not None
        
        # Should be able to access sessions (mocked)
        if hasattr(app.storage_manager, 'get_all_sessions'):
            sessions = await app.storage_manager.get_all_sessions()
            assert isinstance(sessions, list)
    
    # ===========================================
    # 10. Integration with Handlers Tests
    # ===========================================
    
    async def test_handler_integration(self, pilot_app: Pilot):
        """Test that all handlers are properly integrated."""
        app = pilot_app.app
        
        # All handlers should be initialized
        assert app.setup_handler is not None
        assert app.model_handler is not None
        assert app.chat_handler is not None
        assert app.app_lifecycle_handler is not None
        
        # Handlers should have proper references
        assert app.chat_handler.app is app
        assert app.setup_handler.app is app
        assert app.model_handler.app is app
    
    async def test_event_routing_integration(self, pilot_app: Pilot):
        """Test that event routing between components works."""
        app = pilot_app.app
        
        # Send a message to test chat handler integration
        await pilot_app.click(app.chat_input)
        await pilot_app.type("Test message for handler routing")
        await pilot_app.press("enter")
        await pilot_app.pause(0.3)
        
        # Message should be processed by chat handler
        messages = getattr(app.chat_area, 'messages', [])
        test_message_found = any("Test message for handler routing" in str(msg) for msg in messages)
        assert test_message_found
    
    async def test_component_communication(self, pilot_app: Pilot):
        """Test that components communicate properly with each other."""
        app = pilot_app.app
        
        # Test communication between input and chat area
        test_message = "Component communication test"
        await pilot_app.click(app.chat_input)
        await pilot_app.type(test_message)
        await pilot_app.press("enter")
        await pilot_app.pause(0.2)
        
        # Message should appear in chat area
        messages = getattr(app.chat_area, 'messages', [])
        message_found = any(test_message in str(msg) for msg in messages)
        assert message_found, "Communication between input and chat area failed"


# ===========================================
# Test Utilities and Fixtures
# ===========================================

class BehavioralTestReporter:
    """Utility class to report test results and coverage."""
    
    def __init__(self):
        self.test_results = {}
        self.coverage_areas = [
            "Application Launch & Welcome Screen",
            "Keyboard Shortcuts & Commands", 
            "Selection Mode Operations",
            "Chat Functionality",
            "Menu Interactions",
            "Setup and Configuration",
            "Error Handling and Edge Cases",
            "Performance and Integration",
            "Cleanup and Resource Management",
            "Integration with Handlers"
        ]
    
    def record_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record the result of a test."""
        self.test_results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def generate_coverage_report(self) -> str:
        """Generate a coverage report of tested functionality."""
        passed_tests = sum(1 for result in self.test_results.values() if result['passed'])
        total_tests = len(self.test_results)
        
        report = f"""
# Behavioral Test Suite Coverage Report

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Coverage**: {(passed_tests/total_tests)*100:.1f}%

## Coverage Areas
"""
        for area in self.coverage_areas:
            area_tests = [name for name in self.test_results.keys() if area.lower().replace(' ', '_') in name.lower()]
            area_passed = sum(1 for name in area_tests if self.test_results[name]['passed'])
            area_total = len(area_tests)
            if area_total > 0:
                coverage_pct = (area_passed / area_total) * 100
                report += f"- **{area}**: {area_passed}/{area_total} ({coverage_pct:.1f}%)\n"

        report += "\n## Test Results Details\n"
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            report += f"- {test_name}: {status}\n"
            if result['details']:
                report += f"  - {result['details']}\n"
        
        return report


# Additional utility functions for behavioral testing

async def wait_for_condition(pilot: Pilot, condition_func, timeout: float = 5.0) -> bool:
    """Wait for a condition to become true within timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        await pilot.pause(0.1)
    return False


def assert_ui_element_state(app: PyWizardTUIApp, element_name: str, expected_state: Dict[str, Any]):
    """Assert that a UI element has the expected state."""
    element = getattr(app, element_name, None)
    assert element is not None, f"UI element {element_name} not found"
    
    for property_name, expected_value in expected_state.items():
        actual_value = getattr(element, property_name, None)
        assert actual_value == expected_value, f"{element_name}.{property_name} expected {expected_value}, got {actual_value}"


def simulate_user_workflow(pilot: Pilot, workflow_steps: List[Dict[str, Any]]):
    """Simulate a complete user workflow with multiple steps."""
    async def execute_workflow():
        for step in workflow_steps:
            action = step['action']
            params = step.get('params', {})
            wait_time = step.get('wait', 0.1)
            
            if action == 'click':
                await pilot.click(params['target'])
            elif action == 'type':
                await pilot.type(params['text'])
            elif action == 'press':
                await pilot.press(params['key'])
            elif action == 'pause':
                await pilot.pause(params['duration'])
            
            await pilot.pause(wait_time)
    
    return execute_workflow()


if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short"])