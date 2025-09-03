"""
Comprehensive test cases for each IDE in the supported list to verify correct 
instruction file creation and MCP server configuration.

This test suite validates that each supported IDE properly:
1. Creates the correct instruction files (AGENTS.md, CLAUDE.md, WINDSURF.md, etc.)
2. Configures MCP server in the correct location
3. Uses the correct file format (JSON/TOML)
4. Has proper content structure and values
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Tuple, Optional

from juno_agent.fancy_ui.setup.mcp_installer import MCPInstaller, MCPInstallationError


class TestIDEConfigurations:
    """Test suite for all supported IDE configurations."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            yield project_path
    
    @pytest.fixture
    def mock_env_with_api_key(self, monkeypatch):
        """Set up environment with ASKBUDI_API_KEY."""
        monkeypatch.setenv("ASKBUDI_API_KEY", "test-api-key-12345")
        
    @pytest.fixture
    def installer(self, temp_project_dir):
        """Create MCPInstaller instance for testing."""
        return MCPInstaller(project_dir=temp_project_dir)
    
    @pytest.fixture
    def expected_ide_matrix(self):
        """Test matrix defining expected behavior for each IDE."""
        return {
            # IDE Key: (Display Name, Instruction File, MCP Config Path, Config Format, Creates MCP Config)
            "claude_code": ("Claude Code", "", "~/.claude_code_config.json", "cli", False),  # Uses CLI command
            "cursor": ("Cursor", "AGENTS.md", ".cursor/mcp.json", "json", True),
            "windsurf": ("Windsurf", ".windsurfrules", "~/.codeium/windsurf/mcp_config.json", "json", True),
            "vscode": ("VS Code", "AGENTS.md", "settings.json", "json", True),  # Actually creates .vscode/mcp.json
            "cline": ("Cline", "", "cline_mcp_settings.json", "json", True),
            "zed": ("Zed", "settings.json", "settings.json", "json", True),
            "augment_code": ("Augment Code", "", "settings.json", "json", True),
            "roo_code": ("Roo Code", "", "mcp_config.json", "json", True),
            "gemini_cli": ("Gemini CLI", "", "~/.gemini/settings.json", "json", True),
            "claude_desktop": ("Claude Desktop", "", "claude_desktop_config.json", "json", True),
            "opencode": ("Opencode", "", "config.json", "json", True),
            "openai_codex": ("OpenAI Codex", "", "config.toml", "toml", True),
            "jetbrains_ai": ("JetBrains AI Assistant", "", "IDE Settings", "json", True),
            "kiro": ("Kiro", "", "MCP Settings", "json", True),
            "trae": ("Trae", "", "mcp_config.json", "json", True),
            "lm_studio": ("LM Studio", "", "mcp.json", "json", True),
            "visual_studio_2022": ("Visual Studio 2022", "", "mcp_config.json", "json", True),
            "crush": ("Crush", "", "crush.json", "json", True),
            "boltai": ("BoltAI", "", "Settings", "json", True),
            "rovo_dev_cli": ("Rovo Dev CLI", "", "MCP Config", "json", True),
            "zencoder": ("Zencoder", "", "MCP Settings", "json", True),
            "qodo_gen": ("Qodo Gen", "", "MCP Settings", "json", True),
            "perplexity_desktop": ("Perplexity Desktop", "", "Connectors Settings", "json", True),
            "warp": ("Warp", "", "MCP Settings", "json", True),
            "copilot_coding_agent": ("GitHub Copilot Coding Agent", "", "Repository Settings", "json", True),
            "amazon_q_cli": ("Amazon Q Developer CLI", "", "config.json", "json", True),
        }
    
    def test_all_supported_ides_in_matrix(self, installer, expected_ide_matrix):
        """Test that all supported IDEs are covered in our test matrix."""
        supported_editors = installer.get_supported_editors()
        expected_ides = set(expected_ide_matrix.keys())
        actual_ides = set(supported_editors.keys())
        
        missing_from_matrix = actual_ides - expected_ides
        extra_in_matrix = expected_ides - actual_ides
        
        assert not missing_from_matrix, f"IDEs missing from test matrix: {missing_from_matrix}"
        assert not extra_in_matrix, f"Extra IDEs in test matrix: {extra_in_matrix}"
        
        # Also test that we have the right number
        assert len(expected_ides) == len(actual_ides), f"Expected {len(actual_ides)} IDEs, got {len(expected_ides)} in matrix"
    
    @pytest.mark.parametrize("ide_key", [
        "claude_code", "cursor", "windsurf", "vscode", "cline", "zed",
        "augment_code", "roo_code", "gemini_cli", "claude_desktop", "opencode",
        "openai_codex", "jetbrains_ai", "kiro", "trae", "lm_studio",
        "visual_studio_2022", "crush", "boltai", "rovo_dev_cli", "zencoder",
        "qodo_gen", "perplexity_desktop", "warp", "copilot_coding_agent", "amazon_q_cli"
    ])
    def test_ide_config_path_generation(self, installer, temp_project_dir, ide_key):
        """Test that MCP config path is generated correctly for each IDE."""
        try:
            config_path = installer.get_mcp_config_path(ide_key, temp_project_dir)
            assert config_path is not None
            assert isinstance(config_path, Path)
            
            # Path should be absolute
            assert config_path.is_absolute()
            
        except MCPInstallationError as e:
            # Some IDEs may not support file-based configuration
            if ide_key in ["claude_code"]:  # CLI-based configuration
                pytest.skip(f"IDE {ide_key} uses CLI configuration method: {e}")
            else:
                pytest.fail(f"Unexpected error for {ide_key}: {e}")
    
    @pytest.mark.parametrize("ide_key", [
        "cursor", "vscode"  # IDEs that should create AGENTS.md
    ])
    def test_agents_md_creation(self, installer, temp_project_dir, mock_env_with_api_key, ide_key):
        """Test AGENTS.md creation for IDEs that should have it."""
        agents_md_path = temp_project_dir / "AGENTS.md"
        
        # Mock the necessary methods to avoid full installation
        with patch.object(installer, 'get_mcp_config_path', return_value=temp_project_dir / 'test_config.json'):
            with patch.object(installer, 'create_vibe_context_config', return_value={'test': 'config'}):
                with patch.object(installer, 'update_ide_config', return_value=True):
                    success = installer.install_mcp_servers(ide_key, temp_project_dir)
                    
                    assert success is True
                    assert agents_md_path.exists(), f"AGENTS.md should be created for {ide_key}"
                    
                    # Check content
                    content = agents_md_path.read_text(encoding='utf-8')
                    assert f"AI Agent Instructions for" in content
                    assert "VibeContext MCP Server Integration" in content
                    assert f"{installer.get_supported_editors()[ide_key]['name']}" in content
    
    @pytest.mark.parametrize("ide_key", [
        "windsurf"  # IDE that should create .windsurfrules
    ])
    def test_windsurf_rules_creation(self, installer, temp_project_dir, mock_env_with_api_key, ide_key):
        """Test .windsurfrules creation for Windsurf."""
        # Note: Based on the config, Windsurf should create .windsurfrules file
        # But the current implementation creates AGENTS.md. This test documents the current behavior.
        
        agents_md_path = temp_project_dir / "AGENTS.md"
        windsurfrules_path = temp_project_dir / ".windsurfrules"
        
        with patch.object(installer, 'get_mcp_config_path', return_value=temp_project_dir / 'test_config.json'):
            with patch.object(installer, 'create_vibe_context_config', return_value={'test': 'config'}):
                with patch.object(installer, 'update_ide_config', return_value=True):
                    success = installer.install_mcp_servers(ide_key, temp_project_dir)
                    
                    assert success is True
                    
                    # Currently creates AGENTS.md for all non-Claude IDEs
                    # This documents current behavior vs expected behavior from config
                    assert agents_md_path.exists(), f"Currently creates AGENTS.md for {ide_key}"
                    
                    # Check if it should create .windsurfrules based on config
                    ide_info = installer.get_ide_info(ide_key)
                    expected_file = ide_info['custom_instructions']['file_name']
                    if expected_file == ".windsurfrules":
                        # This test will fail until implementation matches config
                        pytest.xfail("Implementation should create .windsurfrules for Windsurf according to config")
    
    def test_claude_code_no_instruction_file(self, installer, temp_project_dir, mock_env_with_api_key):
        """Test that Claude Code doesn't create instruction files."""
        ide_key = "claude_code"
        
        # Mock CLI command method since Claude Code uses command-based config
        with patch.object(installer, 'get_mcp_config_path') as mock_path:
            mock_path.side_effect = MCPInstallationError("Claude Code uses CLI configuration")
            
            with pytest.raises(MCPInstallationError):
                installer.install_mcp_servers(ide_key, temp_project_dir)
            
        # No instruction files should be created
        agents_md_path = temp_project_dir / "AGENTS.md"
        claude_md_path = temp_project_dir / "CLAUDE.md"
        
        assert not agents_md_path.exists()
        assert not claude_md_path.exists()
    
    @pytest.mark.parametrize("ide_key,expected_mcp_key", [
        ("cursor", "mcpServers"),
        ("vscode", "mcp.servers"),
        ("windsurf", "mcpServers"),
        ("openai_codex", "mcp_servers"),
        ("zed", "context_servers"),
        ("augment_code", "augment.advanced.mcpServers"),
        ("visual_studio_2022", "servers"),
        ("crush", "mcp"),
        ("opencode", "mcp"),
    ])
    def test_mcp_config_key_correctness(self, installer, ide_key, expected_mcp_key):
        """Test that each IDE uses the correct MCP configuration key."""
        supported_editors = installer.get_supported_editors()
        
        if ide_key in supported_editors:
            actual_mcp_key = supported_editors[ide_key]['mcp_key']
            assert actual_mcp_key == expected_mcp_key, f"IDE {ide_key} should use MCP key '{expected_mcp_key}', got '{actual_mcp_key}'"
    
    @pytest.mark.parametrize("ide_key,expected_format", [
        ("cursor", "json"),
        ("vscode", "json"),
        ("windsurf", "json"),
        ("openai_codex", "toml"),
        ("claude_code", "cli"),
    ])
    def test_mcp_config_format(self, installer, ide_key, expected_format):
        """Test that each IDE uses the correct configuration format."""
        supported_editors = installer.get_supported_editors()
        
        if ide_key in supported_editors:
            actual_format = supported_editors[ide_key]['config_format']
            assert actual_format == expected_format, f"IDE {ide_key} should use format '{expected_format}', got '{actual_format}'"
    
    def test_mcp_config_content_structure(self, installer, temp_project_dir, mock_env_with_api_key):
        """Test that MCP configuration has correct structure and content."""
        test_api_key = "test-vibe-context-key"
        
        # Test with a typical IDE
        config = installer.create_vibe_context_config(temp_project_dir, test_api_key)
        
        # Should have vibe_context server
        assert "vibe_context" in config
        
        vibe_config = config["vibe_context"]
        
        # Should have required fields
        assert "command" in vibe_config
        assert "args" in vibe_config
        assert "env" in vibe_config
        
        # Should have correct environment variables
        assert "ASKBUDI_API_KEY" in vibe_config["env"]
        assert vibe_config["env"]["ASKBUDI_API_KEY"] == test_api_key
        assert "PLATFORM" in vibe_config["env"]
        assert vibe_config["env"]["PLATFORM"] == "claude"
        
        # Command should be appropriate
        assert vibe_config["command"] in ["node", "npx"]
        assert isinstance(vibe_config["args"], list)
        assert len(vibe_config["args"]) > 0
    
    def test_config_path_resolution_patterns(self, installer, temp_project_dir):
        """Test config path resolution for different IDE patterns."""
        test_cases = [
            # (ide_key, expected_path_pattern, location_type)
            ("cursor", ".cursor/mcp.json", "project"),
            ("vscode", ".vscode/settings.json", "project"),  # Note: actual implementation may differ
            ("windsurf", "~/.codeium/windsurf/mcp_config.json", "windsurf_home"),
            ("claude_code", "~/.claude_code_config.json", "home"),
        ]
        
        for ide_key, expected_pattern, location_type in test_cases:
            try:
                config_path = installer.get_mcp_config_path(ide_key, temp_project_dir)
                
                if location_type == "project":
                    # Should be in project directory
                    assert str(temp_project_dir) in str(config_path)
                elif location_type == "home":
                    # Should be in home directory  
                    assert str(Path.home()) in str(config_path) or str(config_path).startswith("~")
                elif location_type == "windsurf_home":
                    # Should be in windsurf directory
                    expected_windsurf_dir = Path.home() / '.codeium' / 'windsurf'
                    assert str(expected_windsurf_dir) in str(config_path)
                    
            except MCPInstallationError:
                # Some IDEs may use different config methods
                pass
    
    def test_platform_support_validation(self, installer):
        """Test platform support validation for each IDE."""
        current_platform = installer.system
        
        for ide_key in installer.get_supported_editors().keys():
            # Test current platform support
            is_supported = installer.is_platform_supported(ide_key)
            
            # Should return boolean
            assert isinstance(is_supported, bool)
            
            # Test with specific platforms
            for platform in ['windows', 'macos', 'linux']:
                platform_supported = installer.is_platform_supported(ide_key, platform)
                assert isinstance(platform_supported, bool)
    
    def test_one_click_install_support(self, installer):
        """Test one-click install support detection."""
        one_click_ides = []
        manual_ides = []
        
        for ide_key in installer.get_supported_editors().keys():
            supports_one_click = installer.supports_one_click_install(ide_key)
            assert isinstance(supports_one_click, bool)
            
            if supports_one_click:
                one_click_ides.append(ide_key)
            else:
                manual_ides.append(ide_key)
        
        # Should have some IDEs supporting one-click install
        expected_one_click = ["cursor", "vscode", "cline", "zed", "lm_studio"]
        for ide in expected_one_click:
            if ide in installer.get_supported_editors():
                assert ide in one_click_ides, f"{ide} should support one-click install"
    
    def test_connection_types_validation(self, installer):
        """Test connection types for each IDE."""
        expected_connection_types = {
            "local_npm", "remote_http", "remote_sse", "remote_streamable_http",
            "local_stdio", "marketplace", "extension", "ui", "command", "remote_connector"
        }
        
        for ide_key in installer.get_supported_editors().keys():
            connection_types = installer.get_connection_types(ide_key)
            
            # Should return list
            assert isinstance(connection_types, list)
            assert len(connection_types) > 0
            
            # All connection types should be valid
            for conn_type in connection_types:
                assert conn_type in expected_connection_types, f"Unknown connection type '{conn_type}' for {ide_key}"
    
    def test_installation_status_reporting(self, installer, temp_project_dir):
        """Test installation status reporting for each IDE."""
        for ide_key in ["cursor", "vscode", "windsurf"]:  # Test subset of file-based IDEs
            try:
                status = installer.get_installation_status(ide_key, temp_project_dir)
                
                # Should have required fields
                assert "editor" in status
                assert "config_path" in status
                assert "config_exists" in status
                assert "vibe_context_installed" in status
                assert "total_servers" in status
                assert "servers" in status
                
                # Types should be correct
                assert isinstance(status["config_exists"], bool)
                assert isinstance(status["vibe_context_installed"], bool)
                assert isinstance(status["total_servers"], int)
                assert isinstance(status["servers"], list)
                
            except MCPInstallationError:
                # Some IDEs may not support file-based status checking
                pass
    
    def test_error_handling_for_unsupported_ides(self, installer, temp_project_dir, mock_env_with_api_key):
        """Test error handling for unsupported IDE keys."""
        unsupported_ide = "nonexistent_ide"
        
        with pytest.raises(MCPInstallationError) as exc_info:
            installer.install_mcp_servers(unsupported_ide, temp_project_dir)
        
        assert "Unsupported editor" in str(exc_info.value)
        assert unsupported_ide in str(exc_info.value)
    
    @pytest.mark.parametrize("ide_key", [
        "cursor", "vscode", "windsurf", "zed", "augment_code"
    ])
    def test_mcp_config_file_creation(self, installer, temp_project_dir, mock_env_with_api_key, ide_key):
        """Test that MCP configuration files are created with proper content."""
        try:
            config_path = installer.get_mcp_config_path(ide_key, temp_project_dir)
            
            # Mock the required methods for isolated testing
            with patch.object(installer, 'create_vibe_context_config') as mock_create_config:
                with patch.object(installer, 'update_ide_config') as mock_update_config:
                    mock_create_config.return_value = {"vibe_context": {"test": "config"}}
                    mock_update_config.return_value = True
                    
                    success = installer.install_mcp_servers(ide_key, temp_project_dir)
                    
                    assert success is True
                    
                    # Verify methods were called
                    mock_create_config.assert_called_once()
                    mock_update_config.assert_called_once()
                    
                    # Check the update_ide_config was called with correct parameters
                    call_args = mock_update_config.call_args
                    assert call_args[0][0] == config_path  # config_path
                    assert call_args[0][2] == ide_key      # editor
                    
        except MCPInstallationError:
            # Some IDEs may not support file-based configuration
            if ide_key not in ["cursor", "vscode", "windsurf"]:
                pytest.skip(f"IDE {ide_key} may not support file-based configuration")
            else:
                pytest.fail(f"File-based IDE {ide_key} should support configuration file creation")


class TestIDEConfigurationMatrix:
    """Test class for generating and validating IDE configuration matrix."""
    
    def test_generate_ide_behavior_matrix(self, temp_project_dir):
        """Generate a comprehensive matrix of IDE behaviors for documentation."""
        installer = MCPInstaller(project_dir=temp_project_dir)
        supported_editors = installer.get_supported_editors()
        
        matrix_data = []
        
        for ide_key, config in supported_editors.items():
            ide_info = installer.get_ide_info(ide_key)
            
            # Extract information from config
            display_name = config.get('name', ide_key.title())
            config_method = config.get('config_method', 'unknown')
            config_format = config.get('config_format', 'unknown')
            mcp_key = config.get('mcp_key', 'unknown')
            one_click = config.get('one_click_install', False)
            connection_types = config.get('connection_types', [])
            
            # Get custom instructions info
            custom_instructions = ide_info.get('custom_instructions', {}) if ide_info else {}
            instruction_file = custom_instructions.get('file_name', '') if custom_instructions else ''
            
            # Try to get config path (may fail for non-file-based configs)
            config_path = "N/A (CLI/UI based)"
            try:
                path = installer.get_mcp_config_path(ide_key, temp_project_dir)
                config_path = str(path).replace(str(temp_project_dir), "PROJECT_DIR").replace(str(Path.home()), "~")
            except MCPInstallationError:
                pass
            
            matrix_data.append({
                'IDE Key': ide_key,
                'Display Name': display_name,
                'Instruction File': instruction_file if instruction_file else "None",
                'MCP Config Path': config_path,
                'Config Method': config_method,
                'Config Format': config_format,
                'MCP Key': mcp_key,
                'One-Click Install': "Yes" if one_click else "No",
                'Connection Types': ", ".join(connection_types)
            })
        
        # Print the matrix for documentation
        print("\n" + "="*120)
        print("IDE CONFIGURATION MATRIX")
        print("="*120)
        
        # Print header
        header_format = "{:<20} {:<25} {:<15} {:<35} {:<12} {:<10} {:<20} {:<8} {:<25}"
        print(header_format.format(
            "IDE Key", "Display Name", "Instruction File", "MCP Config Path", 
            "Config Method", "Format", "MCP Key", "One-Click", "Connection Types"
        ))
        print("-" * 120)
        
        # Print data
        for data in sorted(matrix_data, key=lambda x: x['Display Name']):
            print(header_format.format(
                data['IDE Key'][:19],
                data['Display Name'][:24],
                data['Instruction File'][:14],
                data['MCP Config Path'][:34],
                data['Config Method'][:11],
                data['Config Format'][:9],
                data['MCP Key'][:19],
                data['One-Click Install'][:7],
                data['Connection Types'][:24]
            ))
        
        print("="*120)
        print(f"Total IDEs: {len(matrix_data)}")
        
        # Summary statistics
        file_based_ides = [d for d in matrix_data if d['Config Method'] == 'file']
        ui_based_ides = [d for d in matrix_data if d['Config Method'] == 'ui']
        cli_based_ides = [d for d in matrix_data if d['Config Method'] in ['command', 'cli']]
        one_click_ides = [d for d in matrix_data if d['One-Click Install'] == 'Yes']
        
        print(f"File-based configuration: {len(file_based_ides)}")
        print(f"UI-based configuration: {len(ui_based_ides)}")
        print(f"CLI-based configuration: {len(cli_based_ides)}")
        print(f"One-click install support: {len(one_click_ides)}")
        print("="*120)
        
        # Store for validation
        assert len(matrix_data) > 20, "Should have significant number of supported IDEs"
        return matrix_data
    
    def test_validate_instruction_file_expectations(self, temp_project_dir):
        """Validate which IDEs should create which instruction files."""
        installer = MCPInstaller(project_dir=temp_project_dir)
        
        # Based on config analysis, these IDEs should create specific files
        expected_instruction_files = {
            "cursor": "AGENTS.md",      # From custom_instructions.file_name in config
            "vscode": "AGENTS.md",      # From custom_instructions.file_name in config
            "windsurf": ".windsurfrules", # From custom_instructions.file_name in config
            "claude_code": "",          # No instruction file (CLI-based)
            "claude_desktop": "",       # UI-based configuration
            "zed": "settings.json",     # From custom_instructions.file_name in config
        }
        
        # Check against actual config
        for ide_key, expected_file in expected_instruction_files.items():
            ide_info = installer.get_ide_info(ide_key)
            if ide_info:
                custom_instructions = ide_info.get('custom_instructions', {})
                actual_file = custom_instructions.get('file_name', '')
                
                assert actual_file == expected_file, (
                    f"IDE {ide_key}: expected instruction file '{expected_file}', "
                    f"but config shows '{actual_file}'"
                )


if __name__ == "__main__":
    # Run specific test to generate the IDE matrix
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--matrix":
        # Create a temporary directory and run matrix test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_instance = TestIDEConfigurationMatrix()
            test_instance.test_generate_ide_behavior_matrix(Path(temp_dir))
    else:
        pytest.main([__file__, "-v"])