"""Tests for IDESelectionMenu widget."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from juno_agent.fancy_ui.widgets.ide_selection_menu import IDESelectionMenu
from juno_agent.fancy_ui.widgets.base_selection_menu import BaseSelectionMenu


class TestIDESelectionMenuApp(App):
    """Test app for IDESelectionMenu widget."""
    
    def __init__(self):
        super().__init__()
        self.selected_ide = None
        self.selection_cancelled = False
    
    def compose(self) -> ComposeResult:
        yield Static("Test app for IDE Selection Menu")
        self.ide_menu = IDESelectionMenu()
        yield self.ide_menu
    
    def on_base_selection_menu_option_selected(self, message: BaseSelectionMenu.OptionSelected) -> None:
        """Handle IDE selection."""
        self.selected_ide = message.value
    
    def on_base_selection_menu_selection_cancelled(self, message: BaseSelectionMenu.SelectionCancelled) -> None:
        """Handle IDE selection cancellation."""
        self.selection_cancelled = True


@pytest.mark.asyncio
async def test_ide_selection_menu_shows():
    """Test that IDE selection menu appears when shown."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        # Initially menu should not be visible
        ide_menu = app.ide_menu
        assert not ide_menu.is_visible
        assert "visible" not in ide_menu.classes
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        
        # Menu should now be visible
        assert ide_menu.is_visible
        assert "visible" in ide_menu.classes


@pytest.mark.asyncio
async def test_ide_selection_menu_options():
    """Test that all expected IDE options are available."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Get default options (priority IDEs)
        options = ide_menu.get_default_options()
        
        # Should have priority IDEs plus "show_all" and "other"
        expected_priority_ides = ["claude_code", "cursor", "windsurf", "vscode", "claude_desktop", "cline", "jetbrains_ai"]
        actual_ide_values = [option["value"] for option in options]
        
        # Check that priority IDEs are present
        for expected_ide in expected_priority_ides:
            assert expected_ide in actual_ide_values, f"Expected IDE {expected_ide} not found in options"
        
        # Check that "show_all" and "other" options are present
        assert "show_all" in actual_ide_values, "show_all option should be present in priority view"
        assert "other" in actual_ide_values, "other option should always be present"
        
        # Should have 9 options total (7 priority + show_all + other)
        assert len(options) == 9


@pytest.mark.asyncio
async def test_ide_selection_keyboard_navigation():
    """Test keyboard navigation in IDE selection menu."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        
        # Wait for the display to update
        await pilot.pause(0.1)
        
        # Initial selection should be 0
        assert ide_menu.selected_index == 0
        
        # Navigate down
        await pilot.press("down")
        assert ide_menu.selected_index == 1
        
        # Navigate down again
        await pilot.press("down")
        assert ide_menu.selected_index == 2
        
        # Navigate up
        await pilot.press("up")
        assert ide_menu.selected_index == 1
        
        # Navigate up from index 1 should go to 0
        await pilot.press("up")
        assert ide_menu.selected_index == 0
        
        # Navigate up from index 0 should wrap to last option
        await pilot.press("up")
        assert ide_menu.selected_index == len(ide_menu.options) - 1


@pytest.mark.asyncio
async def test_ide_selection_enter_key():
    """Test selecting an IDE with Enter key."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        
        # Wait for the display to update
        await pilot.pause(0.1)
        
        # Navigate to second option (cursor)
        await pilot.press("down")
        assert ide_menu.selected_index == 1
        
        # Select with Enter
        await pilot.press("enter")
        
        # Wait for message processing
        await pilot.pause(0.1)
        
        # Should have selected the IDE (cursor is the second option)
        assert app.selected_ide == "cursor"
        
        # Menu should be hidden after selection
        assert not ide_menu.is_visible


@pytest.mark.asyncio
async def test_ide_selection_escape_key():
    """Test cancelling IDE selection with Escape key."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        
        # Wait for the display to update
        await pilot.pause(0.1)
        
        # Cancel with Escape
        await pilot.press("escape")
        
        # Wait for message processing
        await pilot.pause(0.1)
        
        # Should have cancelled selection
        assert app.selection_cancelled
        assert app.selected_ide is None
        
        # Menu should be hidden after cancellation
        assert not ide_menu.is_visible


@pytest.mark.asyncio
async def test_ide_selection_all_options():
    """Test that all IDE options can be selected."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        await pilot.pause(0.1)
        
        # Test selecting a few key IDEs
        test_ide_values = ["claude_code", "cursor", "other"]  # Skip "show_all" as it has special behavior
        
        for ide_value in test_ide_values:
            # Reset menu for each test
            ide_menu.hide()
            ide_menu.show("Test IDE Selection", "Choose your IDE:")
            await pilot.pause(0.1)
            
            # Find the index of the expected IDE
            target_index = None
            for i, option in enumerate(ide_menu.options):
                if option["value"] == ide_value:
                    target_index = i
                    break
            
            assert target_index is not None, f"IDE {ide_value} not found in options"
            
            # Navigate to the target IDE
            current_index = ide_menu.selected_index
            while current_index != target_index:
                if current_index < target_index:
                    await pilot.press("down")
                    current_index = (current_index + 1) % len(ide_menu.options)
                else:
                    await pilot.press("up")
                    current_index = (current_index - 1) % len(ide_menu.options)
                await pilot.pause(0.05)
            
            # Reset app state
            app.selected_ide = None
            
            # Select the IDE
            await pilot.press("enter")
            await pilot.pause(0.1)
            
            # Verify the correct IDE was selected
            assert app.selected_ide == ide_value, f"Expected {ide_value}, got {app.selected_ide}"


@pytest.mark.asyncio
async def test_ide_selection_display_content():
    """Test that the menu displays the correct content."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu with custom title and message
        title = "Custom IDE Selection"
        message = "Pick your favorite IDE"
        ide_menu.show(title, message)
        
        await pilot.pause(0.1)
        
        # Check that title and message are reflected in header text
        header_text = ide_menu.get_header_text()
        assert title in header_text
        assert message in header_text
        
        # Check that footer has instructions
        footer_text = ide_menu.get_footer_text()
        assert "↑↓" in footer_text
        assert "Enter" in footer_text
        assert "Escape" in footer_text


@pytest.mark.asyncio
async def test_ide_selection_focus_behavior():
    """Test that the menu properly handles focus."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Initially can't focus when not visible
        assert not ide_menu.can_focus
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        await pilot.pause(0.1)
        
        # Should be able to focus when visible
        assert ide_menu.can_focus
        
        # Hide the menu
        ide_menu.hide()
        
        # Should not be able to focus when hidden
        assert not ide_menu.can_focus


@pytest.mark.asyncio
async def test_ide_selection_show_all_options():
    """Test the show_all_ides functionality."""
    # Test priority view (show_all_ides=False)
    priority_menu = IDESelectionMenu(show_all_ides=False)
    priority_options = priority_menu.get_default_options()
    
    # Priority view should have "show_all" option
    show_all_present = any(opt["value"] == "show_all" for opt in priority_options)
    assert show_all_present, "Priority view should contain 'show_all' option"
    
    # Should have limited number of options (priority IDEs + show_all + other)
    assert len(priority_options) == 9
    
    # Test all view (show_all_ides=True)  
    all_menu = IDESelectionMenu(show_all_ides=True)
    all_options = all_menu.get_default_options()
    
    # All view should NOT have "show_all" option
    show_all_present_all = any(opt["value"] == "show_all" for opt in all_options)
    assert not show_all_present_all, "All view should NOT contain 'show_all' option"
    
    # Should have many more options (all supported IDEs + other)
    assert len(all_options) > 20, f"Expected >20 options in all view, got {len(all_options)}"
    
    # Should still have "other" option
    other_present = any(opt["value"] == "other" for opt in all_options)
    assert other_present, "All view should still contain 'other' option"


@pytest.mark.asyncio
async def test_ide_selection_show_all_behavior():
    """Test that selecting 'show_all' is handled correctly."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show priority menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        await pilot.pause(0.1)
        
        # Find and select "show_all" option
        show_all_index = None
        for i, option in enumerate(ide_menu.options):
            if option["value"] == "show_all":
                show_all_index = i
                break
        
        assert show_all_index is not None, "show_all option not found"
        
        # Navigate to show_all option
        while ide_menu.selected_index != show_all_index:
            await pilot.press("down")
            await pilot.pause(0.05)
        
        # Select show_all
        await pilot.press("enter")
        await pilot.pause(0.1)
        
        # Should have triggered selection with "show_all" value
        assert app.selected_ide == "show_all", f"Expected 'show_all', got {app.selected_ide}"


@pytest.mark.asyncio
async def test_ide_selection_hide_behavior():
    """Test that hiding the menu works correctly."""
    app = TestIDESelectionMenuApp()
    
    async with app.run_test() as pilot:
        ide_menu = app.ide_menu
        
        # Show the menu
        ide_menu.show("Test IDE Selection", "Choose your IDE:")
        await pilot.pause(0.1)
        
        assert ide_menu.is_visible
        assert "visible" in ide_menu.classes
        
        # Hide the menu
        ide_menu.hide()
        
        assert not ide_menu.is_visible
        assert "visible" not in ide_menu.classes
        assert ide_menu.selected_index == 0  # Should reset to 0