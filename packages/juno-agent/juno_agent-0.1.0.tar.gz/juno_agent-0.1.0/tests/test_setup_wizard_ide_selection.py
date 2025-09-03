"""Tests for IDE selection in the setup wizard."""

import pytest
import tempfile
import os
from pathlib import Path
from textual.app import App

from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.config import ConfigManager


@pytest.mark.asyncio
async def test_setup_wizard_ide_selection_step():
    """Test that IDE selection menu appears during setup wizard step 2."""
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory for test isolation
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config_manager = ConfigManager(temp_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start the setup command
                await app._handle_setup_command()
                
                # Wait for initialization
                await pilot.pause(0.2)
                
                # Should be in step 1 (project description)
                assert app.setup_active
                assert app.setup_step == 0
                assert app.setup_steps[0] == 'collect_project_description'
                
                # Simulate providing project description (press Enter to skip)
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Should now be in step 2 (editor selection)
                assert app.setup_step == 1
                assert app.setup_steps[1] == 'editor_selection'
                
                # IDE selection menu should be visible
                assert hasattr(app, 'ide_selection_menu')
                ide_menu = app.ide_selection_menu
                
                # Wait a bit more for the menu to appear
                await pilot.pause(0.3)
                
                # Menu should be visible and focused
                assert ide_menu.is_visible
                assert "visible" in ide_menu.classes
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_setup_wizard_ide_selection_saves_to_config():
    """Test that IDE selection is properly saved to config."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config_manager = ConfigManager(temp_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start setup
                await app._handle_setup_command()
                await pilot.pause(0.2)
                
                # Skip project description
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Should be in IDE selection step
                assert app.setup_step == 1
                ide_menu = app.ide_selection_menu
                await pilot.pause(0.3)
                
                # Navigate to Cursor (second option)
                await pilot.press("down")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 1
                
                # Select Cursor
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Should have saved to setup data
                assert app.setup_data['selected_editor'] == 'Cursor'
                
                # Should have saved to config file
                config = app.config_manager.load_config()
                assert config.editor == 'Cursor'
                
        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_setup_wizard_ide_selection_cancellation():
    """Test that IDE selection cancellation continues setup."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config_manager = ConfigManager(temp_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start setup
                await app._handle_setup_command()
                await pilot.pause(0.2)
                
                # Skip project description
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Should be in IDE selection step
                assert app.setup_step == 1
                ide_menu = app.ide_selection_menu
                await pilot.pause(0.3)
                
                # Cancel IDE selection
                await pilot.press("escape")
                await pilot.pause(0.2)
                
                # Should have moved to next step (dependency detection)
                assert app.setup_step == 2
                assert app.setup_steps[2] == 'detect_dependencies'
                
                # Menu should be hidden
                assert not ide_menu.is_visible
                
        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_setup_wizard_ide_selection_all_options():
    """Test selecting each IDE option in the setup wizard."""
    
    ide_options = ["Claude Code", "Cursor", "Windsurf", "VS Code", "GitHub Copilot", "Other"]
    
    for expected_ide in ide_options:
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                config_manager = ConfigManager(temp_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Navigate to target IDE
                    ide_menu = app.ide_selection_menu
                    await pilot.pause(0.3)
                    
                    # Find target index
                    target_index = None
                    for i, option in enumerate(ide_menu.options):
                        if option["value"] == expected_ide:
                            target_index = i
                            break
                    
                    assert target_index is not None
                    
                    # Navigate to target
                    while ide_menu.selected_index != target_index:
                        await pilot.press("down")
                        await pilot.pause(0.05)
                    
                    # Select the IDE
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Verify selection
                    assert app.setup_data['selected_editor'] == expected_ide
                    
                    # Verify config save
                    config = app.config_manager.load_config()
                    assert config.editor == expected_ide
                    
            finally:
                os.chdir(original_cwd)


@pytest.mark.asyncio 
async def test_setup_wizard_ide_selection_keyboard_navigation():
    """Test keyboard navigation works in setup wizard context."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config_manager = ConfigManager(temp_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start setup
                await app._handle_setup_command()
                await pilot.pause(0.2)
                
                # Skip project description
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Should be in IDE selection
                ide_menu = app.ide_selection_menu
                await pilot.pause(0.3)
                
                # Test navigation
                assert ide_menu.selected_index == 0
                
                # Down arrow should move to next option
                await pilot.press("down")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 1
                
                # Up arrow should move back
                await pilot.press("up")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 0
                
                # Up from first should wrap to last
                await pilot.press("up")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == len(ide_menu.options) - 1
                
                # Down from last should wrap to first
                await pilot.press("down")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 0
                
        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_setup_wizard_fallback_when_menu_fails():
    """Test fallback behavior when IDE selection menu fails."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config_manager = ConfigManager(temp_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start setup
                await app._handle_setup_command()
                await pilot.pause(0.2)
                
                # Skip project description
                await pilot.press("enter")
                await pilot.pause(0.2)
                
                # Simulate menu failure by removing the menu widget
                app.ide_selection_menu.remove()
                
                # Wait for the fallback message
                await pilot.pause(0.3)
                
                # Should show fallback message in chat
                messages = app.chat_area.get_all_messages()
                fallback_found = any("failed to load" in msg.lower() for msg in messages)
                assert fallback_found, "Fallback message not found in chat"
                
        finally:
            os.chdir(original_cwd)