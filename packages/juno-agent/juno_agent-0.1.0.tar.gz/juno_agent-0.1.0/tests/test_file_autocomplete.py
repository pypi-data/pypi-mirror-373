"""Tests for file autocomplete functionality."""

import pytest
from pathlib import Path
from textual.pilot import Pilot
from textual.app import App, ComposeResult
from textual.widgets import Header
from juno_agent.fancy_ui.widgets.input_area import ChatInput
from juno_agent.fancy_ui.widgets.file_autocomplete import FileAutocomplete


class TestFileAutocompleteApp(App):
    """Test app for file autocomplete."""
    
    def compose(self) -> ComposeResult:
        """Compose the test app."""
        yield Header()
        yield ChatInput()


@pytest.mark.asyncio
async def test_file_autocomplete_trigger():
    """Test that @ triggers file autocomplete."""
    app = TestFileAutocompleteApp()
    
    async with app.run_test() as pilot:
        # Get the chat input
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input")
        
        # Focus the input
        input_area.focus()
        
        # Type @ to trigger file autocomplete
        await pilot.press("@")
        await pilot.pause(0.1)
        
        # Check that file autocomplete is visible
        file_autocomplete = chat_input.file_autocomplete_widget
        assert file_autocomplete is not None
        assert file_autocomplete.is_visible
        
        # Type a search query
        await pilot.press("t", "e", "s", "t")
        await pilot.pause(0.1)
        
        # File autocomplete should still be visible
        assert file_autocomplete.is_visible


@pytest.mark.asyncio
async def test_file_autocomplete_navigation():
    """Test navigation in file autocomplete."""
    app = TestFileAutocompleteApp()
    
    async with app.run_test() as pilot:
        # Get the chat input
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input")
        
        # Focus and trigger file autocomplete
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        file_autocomplete = chat_input.file_autocomplete_widget
        
        # Navigate down
        await pilot.press("down")
        await pilot.pause(0.1)
        assert file_autocomplete.selected_index == 1
        
        # Navigate up
        await pilot.press("up")
        await pilot.pause(0.1)
        assert file_autocomplete.selected_index == 0


@pytest.mark.asyncio
async def test_file_autocomplete_escape():
    """Test escaping file autocomplete."""
    app = TestFileAutocompleteApp()
    
    async with app.run_test() as pilot:
        # Get the chat input
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input")
        
        # Focus and trigger file autocomplete
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        file_autocomplete = chat_input.file_autocomplete_widget
        assert file_autocomplete.is_visible
        
        # Press escape to close
        await pilot.press("escape")
        await pilot.pause(0.1)
        
        # File autocomplete should be hidden
        assert not file_autocomplete.is_visible


@pytest.mark.asyncio
async def test_file_autocomplete_space_closes():
    """Test that space after @ closes file autocomplete."""
    app = TestFileAutocompleteApp()
    
    async with app.run_test() as pilot:
        # Get the chat input
        chat_input = app.query_one(ChatInput)
        input_area = chat_input.query_one("#chat-input")
        
        # Focus and trigger file autocomplete
        input_area.focus()
        await pilot.press("@")
        await pilot.pause(0.1)
        
        file_autocomplete = chat_input.file_autocomplete_widget
        assert file_autocomplete.is_visible
        
        # Type space
        await pilot.press("space")
        await pilot.pause(0.1)
        
        # File autocomplete should be hidden
        assert not file_autocomplete.is_visible


@pytest.mark.asyncio
async def test_file_path_patterns():
    """Test the file path discovery patterns."""
    # Create a FileAutocomplete instance
    file_ac = FileAutocomplete()
    
    # Test getting files and folders
    files = file_ac._get_files_and_folders("")
    assert isinstance(files, list)
    
    # Test with search query
    files = file_ac._get_files_and_folders("test")
    assert isinstance(files, list)
    
    # Test file icon mapping
    assert file_ac._get_file_icon(".py") == "🐍"
    assert file_ac._get_file_icon(".js") == "📜"
    assert file_ac._get_file_icon(".md") == "📝"
    assert file_ac._get_file_icon(".unknown") == "📄"


@pytest.mark.asyncio
async def test_gitignore_patterns():
    """Test gitignore pattern handling."""
    file_ac = FileAutocomplete()
    
    # Test common ignore patterns
    assert file_ac._should_ignore(Path(".git"))
    assert file_ac._should_ignore(Path("__pycache__"))
    assert file_ac._should_ignore(Path("node_modules"))
    assert file_ac._should_ignore(Path("test.pyc"))
    
    # Test that normal files are not ignored
    assert not file_ac._should_ignore(Path("main.py"))
    assert not file_ac._should_ignore(Path("README.md"))