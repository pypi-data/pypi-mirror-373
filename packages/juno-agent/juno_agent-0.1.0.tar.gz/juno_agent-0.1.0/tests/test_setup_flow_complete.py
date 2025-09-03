"""Test complete setup flow with IDE selection."""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, Mock
from juno_agent.config import ConfigManager
from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.fancy_ui.setup.api_key_manager import APIKeyManager


@pytest.mark.asyncio
async def test_complete_setup_flow_with_ide_selection():
    """Test the complete setup flow including IDE selection."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            config_manager = ConfigManager(project_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start the setup command
                await app._handle_setup_command()
                await pilot.pause(0.3)
                
                # Should be in project description step
                assert app.setup_active
                assert app.setup_step == 0
                
                # Skip project description by submitting empty message
                # Get the text area by ID and submit empty message  
                input_widget = app.query_one("#chat-input")
                input_widget.focus()
                await pilot.pause(0.1)
                await pilot.press("enter")  # Submit empty message
                await pilot.pause(0.3)
                
                # Should now be in IDE selection step
                assert app.setup_step == 1
                assert app.ide_selection_menu.is_visible
                
                # Navigate to Cursor (second option)
                await pilot.press("down")
                await pilot.pause(0.1)
                assert app.ide_selection_menu.selected_index == 1
                
                # Select Cursor
                await pilot.press("enter")
                await pilot.pause(0.3)
                
                # Should have saved to setup data
                assert app.setup_data['selected_editor'] == 'Cursor'
                
                # Should have moved to next step
                assert app.setup_step == 2
                
                # Menu should be hidden
                assert not app.ide_selection_menu.is_visible
                
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']


@pytest.mark.asyncio 
async def test_ide_selection_keyboard_navigation_in_setup():
    """Test keyboard navigation during setup."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            config_manager = ConfigManager(project_dir)
            app = PyWizardTUIApp(config_manager)
            
            async with app.run_test() as pilot:
                # Start setup and get to IDE selection
                await app._handle_setup_command()
                await pilot.pause(0.2)
                await pilot.press("enter")  # Skip project description
                await pilot.pause(0.2)
                
                # Should be in IDE selection
                assert app.setup_step == 1
                ide_menu = app.ide_selection_menu
                assert ide_menu.is_visible
                
                # Test navigation
                assert ide_menu.selected_index == 0
                
                # Navigate down twice
                await pilot.press("down")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 1
                
                await pilot.press("down")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 2
                
                # Navigate up once
                await pilot.press("up")
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 1
                
                # Test wraparound - from first to last
                await pilot.press("up")  # Back to 0
                await pilot.pause(0.1)
                assert ide_menu.selected_index == 0
                
                await pilot.press("up")  # Should wrap to last
                await pilot.pause(0.1)
                assert ide_menu.selected_index == len(ide_menu.options) - 1
                
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']


@pytest.mark.asyncio
async def test_setup_flow_with_api_key_collection():
    """Test setup flow with API key collection step."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        original_api_key = os.environ.get('ASKBUDI_API_KEY')
        
        # Remove API key from environment to force collection
        if 'ASKBUDI_API_KEY' in os.environ:
            del os.environ['ASKBUDI_API_KEY']
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        askbudi_dir = os.path.join(home_dir, ".ASKBUDI")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(askbudi_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate:
                # Mock API key validation to return True
                mock_validate.return_value = True
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Select IDE (Cursor)
                    await pilot.press("down")
                    await pilot.press("enter")
                    await pilot.pause(0.3)
                    
                    # Should now be asking for API key
                    assert app.setup_step == 2  # API key collection step
                    
                    # Enter a test API key
                    input_widget = app.query_one("#chat-input")
                    input_widget.value = "test_api_key_valid_123"
                    await pilot.press("enter")
                    await pilot.pause(0.5)
                    
                    # Should have saved API key and proceeded
                    api_manager = APIKeyManager()
                    assert api_manager.has_valid_api_key()
                    
                    # Check that .env file was created
                    env_file = os.path.join(askbudi_dir, ".env")
                    assert os.path.exists(env_file)
                    
                    with open(env_file, 'r') as f:
                        content = f.read()
                        assert "ASKBUDI_API_KEY=test_api_key_valid_123" in content
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if original_api_key:
                os.environ['ASKBUDI_API_KEY'] = original_api_key


@pytest.mark.asyncio
async def test_setup_flow_with_existing_valid_api_key():
    """Test setup flow when valid API key already exists."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        askbudi_dir = os.path.join(home_dir, ".ASKBUDI")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(askbudi_dir, exist_ok=True)
        
        # Create existing .env file with valid API key
        env_file = os.path.join(askbudi_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("ASKBUDI_API_KEY=existing_valid_key_123\n")
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate:
                # Mock API key validation to return True for existing key
                mock_validate.return_value = True
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Select IDE (Cursor)
                    await pilot.press("down")
                    await pilot.press("enter")
                    await pilot.pause(0.5)
                    
                    # Should skip API key collection since valid key exists
                    # Should proceed directly to TinyAgent setup
                    assert app.setup_step >= 3  # Should be past API key step
                    
                    # Verify API key manager found the existing key
                    api_manager = APIKeyManager()
                    assert api_manager.has_valid_api_key()
                    assert api_manager.get_askbudi_api_key() == "existing_valid_key_123"
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']


@pytest.mark.asyncio
async def test_setup_flow_with_invalid_api_key_retry():
    """Test setup flow with invalid API key requiring retry."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        original_api_key = os.environ.get('ASKBUDI_API_KEY')
        
        # Remove API key from environment
        if 'ASKBUDI_API_KEY' in os.environ:
            del os.environ['ASKBUDI_API_KEY']
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        askbudi_dir = os.path.join(home_dir, ".ASKBUDI")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(askbudi_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate:
                # First call returns False (invalid), second returns True (valid)
                mock_validate.side_effect = [False, True]
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Select IDE
                    await pilot.press("down")
                    await pilot.press("enter")
                    await pilot.pause(0.3)
                    
                    # Enter invalid API key first
                    input_widget = app.query_one("#chat-input")
                    input_widget.value = "invalid_key"
                    await pilot.press("enter")
                    await pilot.pause(0.5)
                    
                    # Should still be in API key collection step due to invalid key
                    assert app.setup_step == 2
                    
                    # Enter valid API key
                    input_widget.value = "valid_key_123"
                    await pilot.press("enter")
                    await pilot.pause(0.5)
                    
                    # Should now proceed past API key step
                    assert app.setup_step >= 3
                    
                    # Verify both validation calls were made
                    assert mock_validate.call_count == 2
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if original_api_key:
                os.environ['ASKBUDI_API_KEY'] = original_api_key


@pytest.mark.asyncio
async def test_setup_flow_with_mcp_installation():
    """Test complete setup flow with MCP server installation."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        original_api_key = os.environ.get('ASKBUDI_API_KEY')
        
        # Remove API key from environment
        if 'ASKBUDI_API_KEY' in os.environ:
            del os.environ['ASKBUDI_API_KEY']
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        askbudi_dir = os.path.join(home_dir, ".ASKBUDI")
        cursor_dir = os.path.join(project_dir, ".cursor")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(askbudi_dir, exist_ok=True)
        os.makedirs(cursor_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate, \
                 patch('juno_agent.fancy_ui.setup.mcp_installer.MCPInstaller._test_mcp_connection') as mock_test:
                # Mock API key validation and MCP connection test
                mock_validate.return_value = True
                mock_test.return_value = True
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Select Cursor IDE
                    await pilot.press("down")
                    await pilot.press("enter")
                    await pilot.pause(0.3)
                    
                    # Enter API key
                    input_widget = app.query_one("#chat-input")
                    input_widget.value = "test_valid_api_key"
                    await pilot.press("enter")
                    await pilot.pause(1.0)  # Give more time for MCP installation
                    
                    # Verify MCP configuration was created
                    mcp_config_path = os.path.join(cursor_dir, "mcp.json")
                    assert os.path.exists(mcp_config_path), f"MCP config not found at {mcp_config_path}"
                    
                    # Verify MCP configuration content
                    with open(mcp_config_path, 'r') as f:
                        mcp_config = json.load(f)
                        assert "mcp" in mcp_config
                        assert "servers" in mcp_config["mcp"]
                        assert "vibe-context" in mcp_config["mcp"]["servers"]
                        
                        server_config = mcp_config["mcp"]["servers"]["vibe-context"]
                        assert "env" in server_config
                        assert "ASKBUDI_API_KEY" in server_config["env"]
                        assert server_config["env"]["ASKBUDI_API_KEY"] == "test_valid_api_key"
                    
                    # Verify AGENTS.md was created
                    agents_md_path = os.path.join(project_dir, "AGENTS.md")
                    assert os.path.exists(agents_md_path), "AGENTS.md not created"
                    
                    with open(agents_md_path, 'r') as f:
                        content = f.read()
                        assert "MCP Server Integration" in content
                        assert "vibe-context" in content
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if original_api_key:
                os.environ['ASKBUDI_API_KEY'] = original_api_key


@pytest.mark.asyncio
async def test_setup_flow_mcp_not_installed_without_api_key():
    """Test that MCP server is not installed when API key is invalid."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        original_api_key = os.environ.get('ASKBUDI_API_KEY')
        
        # Remove API key from environment
        if 'ASKBUDI_API_KEY' in os.environ:
            del os.environ['ASKBUDI_API_KEY']
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        cursor_dir = os.path.join(project_dir, ".cursor")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(cursor_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate:
                # Mock API key validation to always return False
                mock_validate.return_value = False
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                # Test that MCP installer correctly identifies no valid API key
                from juno_agent.fancy_ui.setup.mcp_installer import MCPInstaller
                installer = MCPInstaller()
                
                # Should not install MCP without valid API key
                assert not installer.should_install_mcp()
                
                # Verify MCP config is not created
                mcp_config_path = os.path.join(cursor_dir, "mcp.json")
                assert not os.path.exists(mcp_config_path)
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if original_api_key:
                os.environ['ASKBUDI_API_KEY'] = original_api_key


@pytest.mark.asyncio  
async def test_setup_flow_multiple_ide_mcp_configurations():
    """Test MCP installation for different IDE configurations."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate, \
                 patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.has_valid_api_key') as mock_has_key:
                mock_validate.return_value = True
                mock_has_key.return_value = True
                
                from juno_agent.fancy_ui.setup.mcp_installer import MCPInstaller
                
                # Test Claude Code MCP configuration
                installer = MCPInstaller()
                claude_code_config_path = os.path.join(home_dir, ".claude_code_config.json")
                
                installer.install_claude_code_mcp("test_api_key")
                assert os.path.exists(claude_code_config_path)
                
                with open(claude_code_config_path, 'r') as f:
                    config = json.load(f)
                    assert "mcpServers" in config
                    assert "vibe-context" in config["mcpServers"]
                    assert config["mcpServers"]["vibe-context"]["env"]["ASKBUDI_API_KEY"] == "test_api_key"
                
                # Test Cursor MCP configuration
                cursor_dir = os.path.join(project_dir, ".cursor")
                os.makedirs(cursor_dir, exist_ok=True)
                cursor_config_path = os.path.join(cursor_dir, "mcp.json")
                
                installer.install_cursor_mcp("test_api_key")
                assert os.path.exists(cursor_config_path)
                
                with open(cursor_config_path, 'r') as f:
                    config = json.load(f)
                    assert "mcp" in config
                    assert "servers" in config["mcp"]
                    assert "vibe-context" in config["mcp"]["servers"]
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']


@pytest.mark.asyncio
async def test_setup_flow_with_verification_step():
    """Test complete setup flow including verification step."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        askbudi_dir = os.path.join(home_dir, ".ASKBUDI")
        cursor_dir = os.path.join(project_dir, ".cursor")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(askbudi_dir, exist_ok=True)
        os.makedirs(cursor_dir, exist_ok=True)
        
        # Set environment and API key
        os.environ['HOME'] = home_dir
        os.environ['ASKBUDI_API_KEY'] = 'test_verification_key'
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.fancy_ui.setup.api_key_manager.APIKeyManager.validate_api_key') as mock_validate, \
                 patch('juno_agent.fancy_ui.setup.mcp_installer.MCPInstaller._test_mcp_connection') as mock_test, \
                 patch('juno_agent.tiny_agent.TinyCodeAgentChat') as MockTinyAgent:
                
                # Mock API key validation and MCP connection test
                mock_validate.return_value = True
                mock_test.return_value = True
                
                # Mock TinyAgent to avoid actual agent execution
                mock_agent_instance = Mock()
                mock_agent_instance.process_chat_message.return_value = "Verification completed successfully."
                MockTinyAgent.return_value = mock_agent_instance
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Start setup
                    await app._handle_setup_command()
                    await pilot.pause(0.2)
                    
                    # Skip project description
                    await pilot.press("enter")
                    await pilot.pause(0.2)
                    
                    # Select Cursor IDE
                    await pilot.press("down")
                    await pilot.press("enter")
                    await pilot.pause(1.0)  # Give time for full setup including verification
                    
                    # Should have completed full setup including verification
                    # Verify MCP was installed
                    mcp_config_path = os.path.join(cursor_dir, "mcp.json")
                    assert os.path.exists(mcp_config_path)
                    
                    # Verify IDE instructions were created  
                    agents_md_path = os.path.join(project_dir, "AGENTS.md")
                    assert os.path.exists(agents_md_path)
                    
                    # Verify setup completed (should be at final step or completed)
                    assert app.setup_step >= 8  # Should have reached verification step
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if 'ASKBUDI_API_KEY' in os.environ:
                del os.environ['ASKBUDI_API_KEY']


@pytest.mark.asyncio
async def test_setup_verification_without_threading_issues():
    """Test that verification runs without threading/UI blocking issues."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.environ['ASKBUDI_API_KEY'] = 'test_key'
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.tiny_agent.TinyCodeAgentChat') as MockTinyAgent:
                # Mock TinyAgent to simulate verification
                mock_agent_instance = Mock()
                mock_agent_instance.process_chat_message.return_value = "✅ PASS: MCP Server Configuration\\n✅ PASS: IDE Configuration Files\\n"
                MockTinyAgent.return_value = mock_agent_instance
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Test that verification method can be called without threading issues
                    await app._perform_setup_verification()
                    await pilot.pause(0.5)
                    
                    # Should complete without hanging or throwing threading errors
                    # This test mainly ensures no RuntimeError: call_from_thread issues
                    assert True  # If we get here, no threading issues occurred
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if 'ASKBUDI_API_KEY' in os.environ:
                del os.environ['ASKBUDI_API_KEY']


@pytest.mark.asyncio
async def test_setup_flow_handles_verification_failures():
    """Test that setup handles verification failures gracefully."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        original_home = os.environ.get('HOME')
        
        # Create directory structure
        home_dir = os.path.join(temp_dir, "home")
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(project_dir, exist_ok=True)
        
        # Set environment
        os.environ['HOME'] = home_dir
        os.environ['ASKBUDI_API_KEY'] = 'test_key'
        os.chdir(project_dir)
        
        try:
            with patch('juno_agent.tiny_agent.TinyCodeAgentChat') as MockTinyAgent:
                # Mock TinyAgent to simulate verification failures
                mock_agent_instance = Mock()
                mock_agent_instance.process_chat_message.return_value = "❌ FAIL: MCP Server Configuration (server not responding)\\n⚠️ WARN: External Context Setup"
                MockTinyAgent.return_value = mock_agent_instance
                
                config_manager = ConfigManager(project_dir)
                app = PyWizardTUIApp(config_manager)
                
                async with app.run_test() as pilot:
                    # Run verification that will report failures
                    await app._perform_setup_verification()
                    await pilot.pause(0.5)
                    
                    # Should handle failures gracefully without crashing
                    # The verification agent should report the failures but setup should complete
                    assert True  # If we get here, failures were handled gracefully
                        
        finally:
            os.chdir(original_cwd)
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
            if 'ASKBUDI_API_KEY' in os.environ:
                del os.environ['ASKBUDI_API_KEY']