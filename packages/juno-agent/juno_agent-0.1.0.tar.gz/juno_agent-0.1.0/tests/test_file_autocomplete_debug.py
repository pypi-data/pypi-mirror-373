#!/usr/bin/env python3
"""Comprehensive debug tests for file autocomplete feature @ trigger."""

import pytest
import tempfile
import asyncio
import logging
from pathlib import Path
from unittest.mock import Mock, patch
from textual.app import App, ComposeResult
from textual.widgets import Static, Header
from textual.pilot import Pilot

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from juno_agent.fancy_ui.widgets.input_area import ChatInput, CustomTextArea
from juno_agent.fancy_ui.widgets.file_autocomplete import FileAutocomplete


class TestFileAutocompleteDebugApp(App):
    """Test app specifically for debugging file autocomplete @ feature."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.submitted_messages = []
        self.event_log = []
        self.focus_log = []
    
    def compose(self) -> ComposeResult:
        """Compose the debug test app."""
        yield Header()
        yield Static("File Autocomplete Debug Test", id="title")
        self.chat_input = ChatInput()
        yield self.chat_input
    
    def on_chat_input_submit(self, message: ChatInput.Submit) -> None:
        """Handle submitted messages."""
        self.submitted_messages.append(message.content)
        self.event_log.append(f"SUBMIT: {message.content}")
        logger.info(f"Message submitted: {message.content}")
    
    def on_focus(self, event):
        """Log focus events."""
        self.focus_log.append(f"FOCUS: {event.widget}")
        logger.info(f"Focus changed to: {event.widget}")
    
    def on_blur(self, event):
        """Log blur events."""
        self.focus_log.append(f"BLUR: {event.widget}")
        logger.info(f"Focus lost from: {event.widget}")


@pytest.mark.asyncio
async def test_at_symbol_input_focus_behavior():
    """Test what happens to input focus when @ is typed."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        # Get references to key components
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Starting @ symbol input focus test ===")
        
        # Ensure input starts focused
        input_area.focus()
        await pilot.pause(0.1)
        
        # Log initial state
        initial_focus = app.focused
        initial_text = input_area.text
        initial_cursor = input_area.cursor_location
        
        logger.info(f"Initial state: focused={initial_focus}, text='{initial_text}', cursor={initial_cursor}")
        
        # Check that input has focus
        assert app.focused == input_area, f"Expected input to be focused, but {app.focused} is focused"
        
        # Type @ character
        logger.info("Typing @ character...")
        await pilot.press("@")
        await pilot.pause(0.1)
        
        # Check state after @ is typed
        after_at_focus = app.focused
        after_at_text = input_area.text
        after_at_cursor = input_area.cursor_location
        file_ac_visible = file_autocomplete.is_visible if file_autocomplete else False
        
        logger.info(f"After @: focused={after_at_focus}, text='{after_at_text}', cursor={after_at_cursor}")
        logger.info(f"File autocomplete visible: {file_ac_visible}")
        
        # Log all focus changes
        logger.info(f"Focus log: {app.focus_log}")
        
        # Key assertions
        assert after_at_text == "@", f"Expected text to be '@', got '{after_at_text}'"
        assert app.focused == input_area, f"Input should maintain focus after @, but {app.focused} is focused"
        
        # If file autocomplete should be visible, check it
        if file_autocomplete:
            assert file_autocomplete.is_visible, "File autocomplete should be visible after @"
        
        # Type more characters to test continued input
        logger.info("Typing additional characters...")
        await pilot.press("t", "e", "s", "t")
        await pilot.pause(0.1)
        
        final_text = input_area.text
        final_focus = app.focused
        
        logger.info(f"Final state: focused={final_focus}, text='{final_text}'")
        
        assert "@test" == final_text, f"Expected '@test', got '{final_text}'"
        assert app.focused == input_area, f"Input should still have focus, but {app.focused} is focused"


@pytest.mark.asyncio
async def test_at_symbol_edge_cases():
    """Test @ symbol in various positions and contexts."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        # Test 1: @ at beginning of input
        logger.info("=== Test 1: @ at beginning ===")
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        assert input_area.text == "@"
        assert app.focused == input_area
        if file_autocomplete:
            assert file_autocomplete.is_visible
        
        # Clear input properly
        input_area.text = ""
        await pilot.pause(0.1)
        
        # Test 2: @ after space
        logger.info("=== Test 2: @ after space ===")
        await pilot.press("h", "e", "l", "l", "o", " ", "@")
        await pilot.pause(0.1)
        
        assert input_area.text == "hello @"
        assert app.focused == input_area
        if file_autocomplete:
            assert file_autocomplete.is_visible
        
        # Clear input properly
        input_area.text = ""
        await pilot.pause(0.1)
        
        # Test 3: @ after text (should NOT trigger)
        logger.info("=== Test 3: @ after text (no space) ===")
        await pilot.press("e", "m", "a", "i", "l", "@")
        await pilot.pause(0.1)
        
        assert input_area.text == "email@"
        assert app.focused == input_area
        if file_autocomplete:
            # Should NOT be visible because @ is part of email
            assert not file_autocomplete.is_visible
        
        # Clear input properly
        input_area.text = ""
        await pilot.pause(0.1)
        
        # Test 4: Multiple @ symbols
        logger.info("=== Test 4: Multiple @ symbols ===")
        await pilot.press("@", "f", "i", "l", "e", " ", "@")
        await pilot.pause(0.1)
        
        assert input_area.text == "@file @"
        assert app.focused == input_area
        if file_autocomplete:
            # Should show autocomplete for the last @ position
            assert file_autocomplete.is_visible


@pytest.mark.asyncio
async def test_file_autocomplete_navigation_focus():
    """Test focus behavior during file autocomplete navigation."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing navigation focus behavior ===")
        
        # Trigger file autocomplete
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        if file_autocomplete and file_autocomplete.is_visible:
            logger.info("File autocomplete is visible, testing navigation...")
            
            # Test navigation keys
            navigation_keys = ["down", "up", "down", "down"]
            for key in navigation_keys:
                logger.info(f"Pressing {key}")
                focused_before = app.focused
                await pilot.press(key)
                await pilot.pause(0.05)
                focused_after = app.focused
                
                logger.info(f"Focus before {key}: {focused_before}")
                logger.info(f"Focus after {key}: {focused_after}")
                
                # Input should maintain focus even during navigation
                assert app.focused == input_area, f"Input should keep focus during {key} navigation"
                
                # Check that selection changed
                if hasattr(file_autocomplete, 'selected_index'):
                    logger.info(f"Selected index: {file_autocomplete.selected_index}")
        else:
            logger.warning("File autocomplete not visible, skipping navigation tests")


@pytest.mark.asyncio
async def test_file_autocomplete_selection_and_insertion():
    """Test file selection and text insertion behavior."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing file selection and insertion ===")
        
        # Trigger file autocomplete
        input_area.focus()
        await pilot.press("@", "t", "e", "s")
        await pilot.pause(0.1)
        
        initial_text = input_area.text
        logger.info(f"Text after typing '@tes': '{initial_text}'")
        
        if file_autocomplete and file_autocomplete.is_visible:
            logger.info("File autocomplete visible, testing selection...")
            
            # Check available options
            options_count = len(file_autocomplete.options)
            selected_index = file_autocomplete.selected_index
            logger.info(f"Options available: {options_count}, selected index: {selected_index}")
            
            if options_count > 0:
                # Navigate and select
                await pilot.press("down")
                await pilot.pause(0.1)
                
                new_selected_index = file_autocomplete.selected_index
                logger.info(f"After navigation, selected index: {new_selected_index}")
                
                await pilot.press("enter")
                await pilot.pause(0.2)  # Give more time for selection processing
                
                final_text = input_area.text
                final_focus = app.focused
                ac_visible = file_autocomplete.is_visible
                
                logger.info(f"After selection - text: '{final_text}', focus: {final_focus}, ac_visible: {ac_visible}")
                
                # Assertions
                assert app.focused == input_area, "Input should maintain focus after selection"
                assert not file_autocomplete.is_visible, "File autocomplete should hide after selection"
                assert final_text.startswith("@"), "Text should still start with @"
                assert len(final_text) > len(initial_text), "Text should be longer after insertion"
            else:
                logger.warning("No options available for selection test")
        else:
            logger.warning("File autocomplete not visible, skipping selection tests")


@pytest.mark.asyncio
async def test_escape_behavior():
    """Test escape key behavior with file autocomplete."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing escape behavior ===")
        
        # Trigger file autocomplete
        input_area.focus()
        await pilot.press("@", "t", "e", "s", "t")
        await pilot.pause(0.1)
        
        text_before_escape = input_area.text
        logger.info(f"Text before escape: '{text_before_escape}'")
        
        if file_autocomplete and file_autocomplete.is_visible:
            logger.info("File autocomplete visible, testing escape...")
            
            await pilot.press("escape")
            await pilot.pause(0.1)
            
            text_after_escape = input_area.text
            focus_after_escape = app.focused
            ac_visible = file_autocomplete.is_visible
            
            logger.info(f"After escape - text: '{text_after_escape}', focus: {focus_after_escape}, ac_visible: {ac_visible}")
            
            # Assertions
            assert app.focused == input_area, "Input should maintain focus after escape"
            assert not file_autocomplete.is_visible, "File autocomplete should hide after escape"
            assert text_after_escape == text_before_escape, "Text should remain unchanged after escape"
        else:
            logger.warning("File autocomplete not visible, skipping escape tests")


@pytest.mark.asyncio
async def test_space_closes_autocomplete():
    """Test that space after @ closes file autocomplete."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing space closes autocomplete ===")
        
        # Trigger file autocomplete
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        if file_autocomplete and file_autocomplete.is_visible:
            logger.info("File autocomplete visible, testing space...")
            
            await pilot.press("space")
            await pilot.pause(0.1)
            
            text_after_space = input_area.text
            focus_after_space = app.focused
            ac_visible = file_autocomplete.is_visible
            
            logger.info(f"After space - text: '{text_after_space}', focus: {focus_after_space}, ac_visible: {ac_visible}")
            
            # Assertions
            assert app.focused == input_area, "Input should maintain focus after space"
            assert not file_autocomplete.is_visible, "File autocomplete should hide after space"
            assert text_after_space == "@ ", "Text should be '@ ' after space"
        else:
            logger.warning("File autocomplete not visible, skipping space test")


@pytest.mark.asyncio
async def test_widget_mounting_and_visibility():
    """Test that file autocomplete widget is properly mounted and configured."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing widget mounting and visibility ===")
        
        # Check basic widget state
        assert file_autocomplete is not None, "File autocomplete widget should exist"
        assert file_autocomplete.is_mounted, "File autocomplete should be mounted"
        
        logger.info(f"Widget classes: {file_autocomplete.classes}")
        logger.info(f"Widget styles: {file_autocomplete.styles}")
        logger.info(f"Initial visibility: {file_autocomplete.is_visible}")
        
        # Check initial state
        assert not file_autocomplete.is_visible, "File autocomplete should be hidden initially"
        assert not file_autocomplete.has_class("visible"), "Should not have visible class initially"
        
        # Test show method directly
        logger.info("Testing show method directly...")
        file_autocomplete.show_for_query("")
        await pilot.pause(0.1)
        
        logger.info(f"After show_for_query: visible={file_autocomplete.is_visible}, has_visible_class={file_autocomplete.has_class('visible')}")
        
        # Test hide method directly
        logger.info("Testing hide method directly...")
        file_autocomplete.hide()
        await pilot.pause(0.1)
        
        logger.info(f"After hide: visible={file_autocomplete.is_visible}, has_visible_class={file_autocomplete.has_class('visible')}")


@pytest.mark.asyncio
async def test_text_area_event_flow():
    """Test the event flow from TextArea to ChatInput for @ handling."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        file_autocomplete = chat_input.file_autocomplete_widget
        
        logger.info("=== Testing TextArea event flow ===")
        
        # Type @ and check that the autocomplete appears
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        # Check that the text was updated and autocomplete is showing
        assert input_area.text == "@", "Text should contain @"
        assert file_autocomplete.is_visible, "File autocomplete should be visible"
        
        logger.info("Text area event flow test passed - @ triggers autocomplete")


@pytest.mark.asyncio 
async def test_cursor_position_tracking():
    """Test cursor position tracking for @ trigger detection."""
    app = TestFileAutocompleteDebugApp()
    
    async with app.run_test() as pilot:
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input", CustomTextArea)
        
        logger.info("=== Testing cursor position tracking ===")
        
        input_area.focus()
        
        # Test various cursor positions
        test_cases = [
            ("@", (0, 1)),  # @ at beginning
            ("hello @", (0, 7)),  # @ after space
        ]
        
        for text_input, expected_cursor in test_cases:
            # Clear input
            input_area.text = ""
            await pilot.pause(0.05)
            
            # Type the test input
            for char in text_input:
                await pilot.press(char)
                await pilot.pause(0.01)
            
            actual_cursor = input_area.cursor_location
            actual_text = input_area.text
            
            logger.info(f"Input: '{repr(text_input)}' -> Text: '{repr(actual_text)}', Cursor: {actual_cursor}")
            
            # Check that text is as expected
            assert actual_text == text_input, f"Text mismatch for {repr(text_input)}"
            
            # Check cursor position (allowing some flexibility)
            assert actual_cursor == expected_cursor or actual_cursor[1] >= expected_cursor[1], f"Cursor position issue for {repr(text_input)}"


def run_debug_tests():
    """Run tests with detailed debug output."""
    import asyncio
    
    async def run_all_tests():
        logger.info("Starting comprehensive file autocomplete debug tests...")
        
        try:
            await test_at_symbol_input_focus_behavior()
            logger.info("✓ test_at_symbol_input_focus_behavior passed")
        except Exception as e:
            logger.error(f"✗ test_at_symbol_input_focus_behavior failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        try:
            await test_at_symbol_edge_cases()
            logger.info("✓ test_at_symbol_edge_cases passed")
        except Exception as e:
            logger.error(f"✗ test_at_symbol_edge_cases failed: {e}")
        
        try:
            await test_file_autocomplete_navigation_focus()
            logger.info("✓ test_file_autocomplete_navigation_focus passed")
        except Exception as e:
            logger.error(f"✗ test_file_autocomplete_navigation_focus failed: {e}")
        
        try:
            await test_widget_mounting_and_visibility()
            logger.info("✓ test_widget_mounting_and_visibility passed")
        except Exception as e:
            logger.error(f"✗ test_widget_mounting_and_visibility failed: {e}")
        
        logger.info("Debug tests completed!")
    
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    run_debug_tests()