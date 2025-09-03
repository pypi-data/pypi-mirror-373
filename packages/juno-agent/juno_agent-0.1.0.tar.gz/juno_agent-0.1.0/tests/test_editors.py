"""Tests for editor management and MCP server installation."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from juno_agent.editors import EditorConfig, MCPServerInstaller
from juno_agent.scanner import ProjectInfo


class TestEditorConfig:
    """Test EditorConfig model."""
    
    def test_editor_config_creation(self):
        """Test creating EditorConfig instance."""
        config = EditorConfig(
            name="Test Editor",
            config_file_name="config.json",
            supported=True,
        )
        assert config.name == "Test Editor"
        assert config.config_file_name == "config.json"
        assert config.supported is True
        assert config.config_dir is None
        assert config.rules_file is None


class TestMCPServerInstaller:
    """Test MCPServerInstaller class."""
    
    def test_init(self):
        """Test MCPServerInstaller initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            assert installer.workdir == workdir
            assert isinstance(installer.editors, dict)
    
    def test_get_supported_editors(self):
        """Test getting supported editors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            supported = installer.get_supported_editor_names()
            assert "claude-code" in supported
            assert "cursor" in supported  
            assert "windsurf" in supported
            assert "vscode" in supported  # Now supported
            assert "zed" in supported
            # Check for completeness - should have all editors from README
            assert len(supported) >= 20  # At least 20 supported editors
    
    def test_is_editor_supported(self):
        """Test checking if editor is supported."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            assert installer.is_editor_supported("claude-code")
            assert installer.is_editor_supported("cursor")
            assert installer.is_editor_supported("windsurf")
            assert installer.is_editor_supported("vscode")
            assert installer.is_editor_supported("zed")
            assert not installer.is_editor_supported("unknown-editor")
    
    def test_install_claude_code_mcp_new_config(self):
        """Test installing MCP server for Claude Code with new config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("claude-code", "test-api-key")
            
            assert success
            assert "installed successfully" in message
            
            # Check that config file was created in project directory
            config_file = workdir / ".claude_code_config.json"
            assert config_file.exists()
            
            with open(config_file) as f:
                config = json.load(f)
            
            assert "mcpServers" in config
            assert "askbudi-vibe-context" in config["mcpServers"]
            assert config["mcpServers"]["askbudi-vibe-context"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            assert config["mcpServers"]["askbudi-vibe-context"]["env"]["PLATFORM"] == "claude"
    
    def test_install_claude_code_mcp_existing_config(self):
        """Test installing MCP server for Claude Code with existing config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_file = workdir / ".claude_code_config.json"
            
            # Create existing config
            existing_config = {
                "mcpServers": {
                    "existing-server": {
                        "command": "existing",
                        "args": []
                    }
                }
            }
            with open(config_file, "w") as f:
                json.dump(existing_config, f)
            
            installer = MCPServerInstaller(workdir)
            success, message = installer.install_mcp_server("Claude Code", "test-api-key")
            
            # Debug output
            if not success:
                print(f"Installation failed: {message}")
            
            assert success, f"Installation failed: {message}"
            
            # Check that existing config is preserved
            with open(config_file) as f:
                config = json.load(f)
            
            assert "existing-server" in config["mcpServers"]
            assert "askbudi-vibe-context" in config["mcpServers"]
    
    def test_install_cursor_mcp(self):
        """Test installing MCP server for Cursor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("cursor", "test-api-key")
            
            assert success
            assert ".cursor/mcp.json" in message
            assert ".cursor/rules/vibe_context_mcp.mdc" in message
            
            # Check that .cursor/mcp.json file was created
            mcp_config_file = workdir / ".cursor" / "mcp.json" 
            assert mcp_config_file.exists()
            
            with open(mcp_config_file) as f:
                config = json.load(f)
            
            assert "mcpServers" in config
            assert "vibe_context" in config["mcpServers"]
            assert config["mcpServers"]["vibe_context"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            
            # Check that proper Cursor rules file was created
            rules_file = workdir / ".cursor" / "rules" / "vibe_context_mcp.mdc"
            assert rules_file.exists()
            
            content = rules_file.read_text()
            assert "VibeContext MCP Server" in content
            assert "description: VibeContext MCP Server integration" in content
            assert "alwaysApply: true" in content
    
    def test_install_windsurf_mcp(self):
        """Test installing MCP server for Windsurf."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("Windsurf", "test-api-key")
            
            assert success
            assert ".windsurfrules" in message
            
            # Check that .windsurfrules file was created
            rules_file = workdir / ".windsurfrules"
            assert rules_file.exists()
            
            content = rules_file.read_text()
            assert "VibeContext MCP Server" in content
            assert "test-api-key" in content
    
    def test_install_unsupported_editor(self):
        """Test installing MCP server for unsupported editor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("Unknown Editor", "test-api-key")
            
            assert not success
            assert "not supported" in message
    
    def test_create_rules_file(self):
        """Test creating rules file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            # Create mock project info
            project_info = ProjectInfo(
                languages=["Python"],
                frameworks=["FastAPI"],
                dependencies=["fastapi", "pytest"],
                package_managers=["pip"],
            )
            
            success, message = installer.create_rules_file(
                "claude-code", project_info, ["fastapi", "pytest"]
            )
            
            assert success
            assert "CLAUDE.md" in message
            
            # Check that rules file was created
            rules_file = workdir / "CLAUDE.md"
            assert rules_file.exists()
            
            content = rules_file.read_text()
            assert "Python" in content
            assert "FastAPI" in content
            assert "fastapi" in content
            assert "pytest" in content
            assert "MCP Server Integration" in content
    
    def test_create_rules_file_unsupported_editor(self):
        """Test creating rules file for unsupported editor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            project_info = ProjectInfo()
            
            success, message = installer.create_rules_file(
                "Unknown Editor", project_info, []
            )
            
            assert not success
            assert "not supported" in message
    
    def test_cursor_mcp_migrate_legacy_rules(self):
        """Test installing Cursor MCP when .cursorrules already exists - should migrate to backup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            legacy_rules_file = workdir / ".cursorrules"
            
            # Create existing legacy rules file
            existing_content = "# Existing rules\nSome existing content"
            legacy_rules_file.write_text(existing_content)
            
            installer = MCPServerInstaller(workdir)
            success, message = installer.install_mcp_server("cursor", "test-api-key")
            
            assert success
            
            # Legacy file should be migrated to backup
            backup_file = workdir / ".cursorrules.backup"
            assert backup_file.exists()
            backup_content = backup_file.read_text()
            assert "Existing rules" in backup_content
            assert "Some existing content" in backup_content
            
            # Legacy file should not exist anymore
            assert not legacy_rules_file.exists()
            
            # New rules file should exist
            new_rules_file = workdir / ".cursor" / "rules" / "vibe_context_mcp.mdc"
            assert new_rules_file.exists()
            new_content = new_rules_file.read_text()
            assert "VibeContext MCP Server" in new_content
    
    def test_windsurf_mcp_append_to_existing(self):
        """Test installing Windsurf MCP when .windsurfrules already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            rules_file = workdir / ".windsurfrules"
            
            # Create existing rules file
            existing_content = "# Existing windsurf rules\nExisting configuration"
            rules_file.write_text(existing_content)
            
            installer = MCPServerInstaller(workdir)
            success, message = installer.install_mcp_server("Windsurf", "test-api-key")
            
            assert success
            
            content = rules_file.read_text()
            assert "Existing windsurf rules" in content
            assert "Existing configuration" in content
            assert "VibeContext MCP Server" in content
    
    def test_generate_rules_content_with_frameworks(self):
        """Test generating rules content with framework-specific guidelines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            project_info = ProjectInfo(
                languages=["Python", "JavaScript"],
                frameworks=["FastAPI", "React", "Django"],
                package_managers=["pip", "npm"],
            )
            
            content = installer._generate_rules_content(
                "claude-code", project_info, ["fastapi", "react", "django"]
            )
            
            assert "FastAPI Guidelines" in content
            assert "React Guidelines" in content
            assert "Django Guidelines" in content
            assert "type hints" in content  # FastAPI specific
            assert "functional components" in content  # React specific
            assert "Django conventions" in content  # Django specific
    
    def test_install_vscode_mcp(self):
        """Test installing MCP server for VS Code."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("vscode", "test-api-key")
            
            assert success
            assert "VS Code" in message
            
            # Check that .vscode/settings.json file was created
            settings_file = workdir / ".vscode" / "settings.json"
            assert settings_file.exists()
            
            with open(settings_file) as f:
                settings = json.load(f)
            
            assert "mcp.servers" in settings
            assert "askbudi" in settings["mcp.servers"]
            assert settings["mcp.servers"]["askbudi"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            assert settings["mcp.servers"]["askbudi"]["env"]["PLATFORM"] == "vscode"
    
    def test_install_zed_mcp(self):
        """Test installing MCP server for Zed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("zed", "test-api-key")
            
            assert success
            assert "Zed" in message
            
            # Check that .zed/settings.json file was created
            settings_file = workdir / ".zed" / "settings.json"
            assert settings_file.exists()
            
            with open(settings_file) as f:
                settings = json.load(f)
            
            assert "assistant" in settings
            assert "mcp_servers" in settings["assistant"]
            assert "askbudi" in settings["assistant"]["mcp_servers"]
            assert settings["assistant"]["mcp_servers"]["askbudi"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            assert settings["assistant"]["mcp_servers"]["askbudi"]["env"]["PLATFORM"] == "zed"
    
    def test_install_cline_mcp(self):
        """Test installing MCP server for Cline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer.install_mcp_server("cline", "test-api-key")
            
            assert success
            assert "Cline" in message
            
            # Check that .vscode/settings.json file was created for Cline
            settings_file = workdir / ".vscode" / "settings.json"
            assert settings_file.exists()
            
            with open(settings_file) as f:
                settings = json.load(f)
            
            assert "cline.mcp.servers" in settings
            assert "askbudi" in settings["cline.mcp.servers"]
            assert settings["cline.mcp.servers"]["askbudi"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            assert settings["cline.mcp.servers"]["askbudi"]["env"]["PLATFORM"] == "cline"
    
    def test_create_mcp_placeholder(self):
        """Test creating MCP configuration placeholder for unsupported editors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            installer = MCPServerInstaller(workdir)
            
            success, message = installer._create_mcp_placeholder("custom-editor", "test-api-key")
            
            assert success
            assert "configuration created" in message
            
            # Check that config file was created
            config_file = workdir / ".custom-editor_mcp_config.json"
            assert config_file.exists()
            
            with open(config_file) as f:
                config = json.load(f)
            
            assert "mcp" in config
            assert "servers" in config["mcp"]
            assert "askbudi" in config["mcp"]["servers"]
            assert config["mcp"]["servers"]["askbudi"]["env"]["ASKBUDI_API_KEY"] == "test-api-key"
            assert config["mcp"]["servers"]["askbudi"]["env"]["PLATFORM"] == "custom-editor"
            
            # Check that instructions file was created
            instructions_file = workdir / "CUSTOM-EDITOR_MCP_SETUP.md"
            assert instructions_file.exists()
            
            content = instructions_file.read_text()
            assert "MCP Server Setup for custom-editor" in content
            assert "test-api-key" in content