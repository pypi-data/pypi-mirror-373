"""Tests for AI agent functionality."""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from juno_agent.config import ConfigManager
from juno_agent.agent import TinyAgentChat, ProjectAnalysisAgent


class TestTinyAgentChat:
    """Test TinyAgentChat functionality."""
    
    def test_initialization(self):
        """Test TinyAgentChat initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            assert agent.config_manager == config_manager
            assert agent.conversation_history == []
    
    @pytest.mark.asyncio
    async def test_process_chat_message(self):
        """Test processing chat messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("Hello, how are you?")
            
            assert isinstance(response, str)
            assert len(response) > 0
            assert len(agent.conversation_history) == 2  # user + assistant
    
    @pytest.mark.asyncio
    async def test_project_related_queries(self):
        """Test project-related query responses."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(libraries=["fastapi", "requests", "pytest"])
            
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("Tell me about my project dependencies")
            
            assert "fastapi" in response.lower() or "dependencies" in response.lower()
            assert "project" in response.lower() or "analysis" in response.lower()
    
    @pytest.mark.asyncio
    async def test_setup_related_queries(self):
        """Test setup-related query responses."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("How do I set up my development environment?")
            
            assert "setup" in response.lower() or "configure" in response.lower()
            assert "api" in response.lower() or "editor" in response.lower()
    
    @pytest.mark.asyncio
    async def test_api_key_queries(self):
        """Test API key related query responses."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("I need help with my API key")
            
            assert "api" in response.lower() and "key" in response.lower()
            assert "askbudi" in response.lower() or "configuration" in response.lower()
    
    @pytest.mark.asyncio
    async def test_help_queries(self):
        """Test help-related query responses."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("What can you help me with?")
            
            assert "help" in response.lower() or "assist" in response.lower()
            assert "setup" in response.lower() or "project" in response.lower()
    
    @pytest.mark.asyncio
    async def test_context_awareness(self):
        """Test that agent uses provided context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            context = {
                "workdir": str(workdir),
                "has_api_key": True,
                "editor": "Claude Code",
                "libraries": ["django", "celery"]
            }
            
            response = await agent.process_chat_message("What's my current setup?", context)
            
            # Should reference context elements
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_get_conversation_summary(self):
        """Test conversation summary generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            # Add mock conversation
            agent.conversation_history = [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                {"role": "assistant", "content": "Hi!", "timestamp": "2024-01-01T00:00:01"},
                {"role": "user", "content": "Help with setup", "timestamp": "2024-01-01T00:01:00"},
                {"role": "assistant", "content": "Sure!", "timestamp": "2024-01-01T00:01:01"}
            ]
            
            summary = agent.get_conversation_summary()
            
            assert summary["total_exchanges"] == 2
            assert summary["last_user_message"] == "Help with setup"
            assert summary["session_start"] == "2024-01-01T00:00:00"
    
    def test_extract_topics(self):
        """Test topic extraction from conversation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            # Add conversation with various topics
            agent.conversation_history = [
                {"role": "user", "content": "help me setup my project"},
                {"role": "user", "content": "what about my API key?"},
                {"role": "user", "content": "scan my dependencies"}
            ]
            
            topics = agent._extract_topics()
            
            assert "setup" in topics
            assert "api" in topics
            assert "project" in topics
    
    def test_save_conversation(self):
        """Test conversation persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            # Add conversation
            agent.conversation_history = [
                {
                    "timestamp": "2024-01-01T00:00:00",
                    "role": "user",
                    "content": "Test message",
                    "context": {}
                }
            ]
            
            agent.save_conversation()
            
            # Verify file was created
            conversation_file = config_manager.config_dir / "conversation_history.json"
            assert conversation_file.exists()
            
            # Verify content
            with open(conversation_file, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 1
            assert data[0]["messages"] == agent.conversation_history
    
    def test_conversation_history_limit(self):
        """Test that conversation history is limited to 10 sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Create 15 conversations
            for i in range(15):
                agent = TinyAgentChat(config_manager)
                agent.conversation_history = [
                    {
                        "timestamp": f"2024-01-{i+1:02d}T00:00:00",
                        "role": "user",
                        "content": f"Message {i}",
                        "context": {}
                    }
                ]
                agent.save_conversation()
            
            # Check that only 10 are kept
            conversation_file = config_manager.config_dir / "conversation_history.json"
            with open(conversation_file, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 10


class TestProjectAnalysisAgent:
    """Test ProjectAnalysisAgent functionality."""
    
    def test_initialization(self):
        """Test ProjectAnalysisAgent initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = ProjectAnalysisAgent(config_manager)
            
            assert agent.config_manager == config_manager
    
    @pytest.mark.asyncio
    async def test_analyze_project_context(self):
        """Test project context analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(libraries=["flask", "sqlalchemy"])
            
            agent = ProjectAnalysisAgent(config_manager)
            
            context = await agent.analyze_project_context(workdir)
            
            assert "analysis_timestamp" in context
            assert "project_path" in context
            assert context["project_path"] == str(workdir)
            assert "detected_patterns" in context
            assert "optimization_suggestions" in context
            assert "security_recommendations" in context
            assert "documentation_gaps" in context
    
    @pytest.mark.asyncio
    async def test_analysis_with_dependencies(self):
        """Test analysis with project dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(libraries=["django", "redis", "celery"])
            
            agent = ProjectAnalysisAgent(config_manager)
            
            context = await agent.analyze_project_context(workdir)
            
            # Should have patterns detected
            assert len(context["detected_patterns"]) > 0
            assert any("dependencies" in pattern.lower() for pattern in context["detected_patterns"])
    
    @pytest.mark.asyncio
    async def test_analysis_without_mcp_server(self):
        """Test analysis suggests MCP server when not installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(editor="Claude Code", mcp_server_installed=False)
            
            agent = ProjectAnalysisAgent(config_manager)
            
            context = await agent.analyze_project_context(workdir)
            
            # Should suggest MCP server installation
            mcp_suggestion = any(
                "mcp server" in suggestion.lower() 
                for suggestion in context["optimization_suggestions"]
            )
            assert mcp_suggestion
    
    def test_generate_insights_report(self):
        """Test insights report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = ProjectAnalysisAgent(config_manager)
            
            analysis = {
                "detected_patterns": [
                    "Modern Python project structure",
                    "Uses virtual environment"
                ],
                "optimization_suggestions": [
                    "Add type hints for better code quality",
                    "Consider using pre-commit hooks"
                ],
                "security_recommendations": [
                    "Update dependencies to latest versions"
                ]
            }
            
            report = agent.generate_insights_report(analysis)
            
            assert "Detected Patterns" in report
            assert "Optimization Suggestions" in report
            assert "Security Recommendations" in report
            assert "Modern Python project structure" in report
    
    def test_generate_empty_insights_report(self):
        """Test insights report with empty analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = ProjectAnalysisAgent(config_manager)
            
            analysis = {}
            
            report = agent.generate_insights_report(analysis)
            
            assert "Project Analysis" in report
            assert "/scan" in report


class TestAgentErrorHandling:
    """Test error handling in agent functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_handles_empty_message(self):
        """Test agent handles empty messages gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            response = await agent.process_chat_message("")
            
            assert isinstance(response, str)
            assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_agent_handles_invalid_context(self):
        """Test agent handles invalid context gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            # Should not raise exception with invalid context
            response = await agent.process_chat_message("test", {"invalid": None})
            
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_save_conversation_creates_directory(self):
        """Test that save_conversation creates config directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Remove config directory to test creation (if it exists)
            import shutil
            if config_manager.config_dir.exists():
                shutil.rmtree(config_manager.config_dir)
            
            agent = TinyAgentChat(config_manager)
            agent.conversation_history = [
                {"timestamp": "2024-01-01T00:00:00", "role": "user", "content": "test", "context": {}}
            ]
            
            # Should create directory and save file
            agent.save_conversation()
            
            conversation_file = config_manager.config_dir / "conversation_history.json"
            assert conversation_file.exists()
    
    def test_save_conversation_handles_json_errors(self):
        """Test that save_conversation handles JSON errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent = TinyAgentChat(config_manager)
            
            # Create invalid JSON file
            conversation_file = config_manager.config_dir / "conversation_history.json"
            conversation_file.parent.mkdir(parents=True, exist_ok=True)
            with open(conversation_file, 'w') as f:
                f.write("invalid json")
            
            agent.conversation_history = [
                {"timestamp": "2024-01-01T00:00:00", "role": "user", "content": "test", "context": {}}
            ]
            
            # Should handle error and create new file
            agent.save_conversation()
            
            # Verify file was overwritten with valid JSON
            with open(conversation_file, 'r') as f:
                data = json.load(f)
                assert len(data) == 1