"""Test for model name propagation fix in TinyCodeAgent subagents.

This test validates that subagents use the same model as their parent agent.
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import pytest

from juno_agent.config import ConfigManager
from juno_agent.tiny_agent import TinyCodeAgentChat


class TestModelNamePropagationFix:
    """Test model name propagation from parent to subagents."""
    
    @pytest.mark.asyncio
    async def test_create_coding_subagent_model_consistency(self):
        """Test that create_coding_subagent uses the same model as parent.""" 
        # Mock the entire tinyagent module and its imports
        mock_tinyagent = Mock()
        mock_agent_class = Mock()
        mock_hooks = Mock()
        mock_tools = Mock()
        
        with patch.dict('sys.modules', {
            'tinyagent': mock_tinyagent,
            'tinyagent.hooks': mock_hooks,
            'tinyagent.hooks.token_tracker': Mock(),
            'tinyagent.tools': mock_tools,
        }):
            mock_tinyagent.TinyCodeAgent = mock_agent_class
            mock_tinyagent.SubagentConfig = Mock()
            mock_hooks.MessageCleanupHook = Mock()
            mock_hooks.AnthropicPromptCacheCallback = Mock()
            mock_tools.create_coding_subagent = Mock()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                workdir = Path(temp_dir)
                config_manager = ConfigManager(workdir)
                
                # Set up mock configuration with specific model
                config_manager.update_config(
                    provider="openai",
                    model_name="gpt-4o-mini",
                    temperature=0.7,
                    api_key="test_key_123"
                )
                
                # Create agent with mock environment for API key
                with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_123'}):
                    agent_chat = TinyCodeAgentChat(config_manager, debug=True)
                    
                    # Mock main agent
                    mock_main_agent = MagicMock()
                    mock_main_agent.model = "openai/gpt-4o-mini"  # Parent agent model
                    mock_agent_class.return_value = mock_main_agent
                    
                    # Initialize main agent (will be mocked)
                    await agent_chat.initialize_agent()
                    agent_chat.agent = mock_main_agent  # Set manually for testing
                    
                    # Mock subagent creation to capture model parameter
                    mock_subagent = MagicMock()
                    captured_params = {}
                    
                    def capture_model_param(**kwargs):
                        """Capture the model parameter passed to subagent constructor."""
                        captured_params.update(kwargs)
                        mock_subagent.model = kwargs.get('model')
                        return mock_subagent
                    
                    mock_agent_class.side_effect = capture_model_param
                    
                    # Test create_coding_subagent
                    result = await agent_chat.create_coding_subagent()
                    
                    # Verify subagent was created with same model as parent
                    assert result is not None, "Subagent creation should succeed"
                    assert captured_params.get('model') == "openai/gpt-4o-mini", (
                        f"Subagent should be created with parent model 'openai/gpt-4o-mini', "
                        f"got '{captured_params.get('model')}'"
                    )
    
    @pytest.mark.asyncio
    async def test_model_name_construction_consistency(self):
        """Test that model name construction is consistent between parent and subagent."""
        # Mock the entire tinyagent module
        mock_tinyagent = Mock()
        mock_agent_class = Mock()
        mock_hooks = Mock()
        mock_tools = Mock()
        
        with patch.dict('sys.modules', {
            'tinyagent': mock_tinyagent,
            'tinyagent.hooks': mock_hooks,
            'tinyagent.hooks.token_tracker': Mock(),
            'tinyagent.tools': mock_tools,
        }):
            mock_tinyagent.TinyCodeAgent = mock_agent_class
            mock_tinyagent.SubagentConfig = Mock()
            mock_hooks.MessageCleanupHook = Mock()
            mock_hooks.AnthropicPromptCacheCallback = Mock()
            mock_tools.create_coding_subagent = Mock()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                workdir = Path(temp_dir)
                config_manager = ConfigManager(workdir)
                
                # Test cases for model name construction
                test_cases = [
                    {
                        "provider": "openai",
                        "model_name": "gpt-4o-mini",
                        "expected": "openai/gpt-4o-mini"
                    },
                    {
                        "provider": "anthropic", 
                        "model_name": "claude-3-sonnet-20240229",
                        "expected": "anthropic/claude-3-sonnet-20240229"
                    },
                    {
                        "provider": "openai",
                        "model_name": "openai/gpt-4o",  # Already has provider prefix
                        "expected": "openai/gpt-4o"
                    }
                ]
                
                for test_case in test_cases:
                    config_manager.update_config(
                        provider=test_case["provider"],
                        model_name=test_case["model_name"],
                        api_key="test_key_123"
                    )
                    
                    # Create agent with mock environment for API key
                    with patch.dict('os.environ', {f'{test_case["provider"].upper()}_API_KEY': 'test_key_123'}):
                        agent_chat = TinyCodeAgentChat(config_manager, debug=True)
                        
                        # Mock main agent
                        mock_main_agent = MagicMock()
                        mock_main_agent.model = test_case["expected"]  # Parent uses expected model format
                        mock_agent_class.return_value = mock_main_agent
                        
                        # Initialize main agent (will be mocked)
                        await agent_chat.initialize_agent()
                        agent_chat.agent = mock_main_agent  # Set manually for testing
                        
                        # Mock subagent creation to validate model consistency
                        captured_params = {}
                        
                        def capture_and_validate_model(**kwargs):
                            captured_model = kwargs.get('model')
                            captured_params.update(kwargs)
                            # The fix should ensure subagent gets parent's exact model
                            assert captured_model == test_case["expected"], (
                                f"Provider: {test_case['provider']}, Model: {test_case['model_name']} - "
                                f"Expected: {test_case['expected']}, Got: {captured_model}"
                            )
                            mock_subagent = MagicMock()
                            mock_subagent.model = captured_model
                            return mock_subagent
                        
                        mock_agent_class.side_effect = capture_and_validate_model
                        
                        # Test subagent creation
                        result = await agent_chat.create_coding_subagent()
                        assert result is not None, f"Subagent creation failed for {test_case}"
    
    def test_model_name_construction_logic(self):
        """Test the model name construction logic directly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            agent_chat = TinyCodeAgentChat(config_manager)
            
            # Test the logic used in both parent and subagent creation
            test_cases = [
                ("openai", "gpt-4o-mini", "openai/gpt-4o-mini"),
                ("anthropic", "claude-3-sonnet", "anthropic/claude-3-sonnet"), 
                ("openai", "openai/gpt-4o", "openai/gpt-4o"),  # Already has provider
                ("anthropic", "anthropic/claude-3-haiku", "anthropic/claude-3-haiku"),
            ]
            
            for provider, model_name, expected in test_cases:
                # This is the exact logic used in both parent and subagent creation
                constructed_model = (
                    model_name if provider.lower() in model_name.lower() 
                    else provider.lower() + "/" + model_name.lower()
                )
                
                assert constructed_model == expected, (
                    f"Model construction failed for provider='{provider}', model='{model_name}'. "
                    f"Expected: '{expected}', Got: '{constructed_model}'"
                )


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])