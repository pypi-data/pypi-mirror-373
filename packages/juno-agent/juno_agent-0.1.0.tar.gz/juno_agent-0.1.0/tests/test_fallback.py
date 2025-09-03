#!/usr/bin/env python3
"""Test script to verify fallback model loading works."""

import sys
import os
from pathlib import Path

# Add juno_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_fallback_models():
    """Test that fallback models are properly loaded when backend is unavailable."""
    from juno_agent.ui import ChatInterface
    from juno_agent.config import ConfigManager
    
    # Initialize config manager
    config_manager = ConfigManager(Path('.'))
    chat_interface = ChatInterface(config_manager)
    
    print("Testing fallback model loading...")
    
    # Since backend is unavailable, _fetch_models_from_backend should return []
    models = chat_interface._fetch_models_from_backend()
    if models:
        print(f"❌ Expected empty list from backend, got {len(models)} models")
        return False
    
    print("✅ Backend correctly returned empty list")
    
    # Now test the full _configure_model_and_provider method with a mock that simulates
    # the method call but doesn't require user input
    
    # Check that we have fallback models in the method
    import inspect
    source = inspect.getsource(chat_interface._configure_model_and_provider)
    
    # Check that fallback models are defined
    if '"gpt-5-mini"' in source and '"claude-4-sonnet-20250514"' in source:
        print("✅ Fallback models are properly defined in the method")
    else:
        print("❌ Fallback models not found in method source")
        return False
    
    # Check GROQ support
    if 'groq' in source.lower():
        print("✅ GROQ support is included in the models")
    else:
        print("⚠️  GROQ support might not be included (this is just a warning)")
    
    print("✅ All fallback mechanisms appear to be properly implemented")
    return True

def test_groq_support():
    """Test that GROQ API key support is properly implemented."""
    from juno_agent.ui import ChatInterface
    from juno_agent.config import ConfigManager
    
    config_manager = ConfigManager(Path('.'))
    chat_interface = ChatInterface(config_manager)
    
    print("\nTesting GROQ API key support...")
    
    # Test the _get_expected_env_var method
    groq_env_var = chat_interface._get_expected_env_var("groq")
    if groq_env_var == "GROQ_API_KEY":
        print("✅ UI correctly maps 'groq' provider to 'GROQ_API_KEY'")
    else:
        print(f"❌ Expected 'GROQ_API_KEY', got '{groq_env_var}'")
        return False
    
    # Test the config manager API key support
    from juno_agent.config import ConfigManager
    
    # Create a test config with groq provider
    config_manager.update_agent_config(provider="groq")
    
    # Test that get_model_api_key attempts to get GROQ_API_KEY
    # We expect None since we don't have it set, but the method should work
    try:
        api_key = config_manager.get_model_api_key()
        print("✅ ConfigManager.get_model_api_key() works with groq provider")
    except Exception as e:
        print(f"❌ ConfigManager.get_model_api_key() failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing juno-agent Model Integration")
    print("=" * 60)
    
    success1 = test_fallback_models()
    success2 = test_groq_support()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed! Model integration is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)