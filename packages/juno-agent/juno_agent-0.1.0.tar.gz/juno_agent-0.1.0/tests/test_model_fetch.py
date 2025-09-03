#!/usr/bin/env python3
"""Test script to verify model fetching from backend."""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from juno_agent.ui import ChatInterface
from juno_agent.config import ConfigManager

def test_model_fetch():
    """Test fetching models from backend."""
    # Initialize config manager with current directory
    config_manager = ConfigManager(Path('.'))
    
    # Create chat interface
    chat_interface = ChatInterface(config_manager)
    
    # Test model fetching
    print("Testing model fetch from backend...")
    models = chat_interface._fetch_models_from_backend()
    
    if models:
        print(f"✅ Successfully fetched {len(models)} models:")
        for model in models[:5]:  # Show first 5
            print(f"  - {model.get('name', model['id'])} ({model['provider']})")
            print(f"    Model: {model['model_name']}")
            print(f"    Temp: {model.get('temperature', 'N/A')}")
            print(f"    Cost: {model.get('cost_tier', 'N/A')}")
        
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more models")
        return True
    else:
        print("❌ Failed to fetch models from backend (expected - testing fallback)")
        
        # Test the full model configuration function which includes fallback
        print("\nTesting model configuration with fallback...")
        
        # Import necessary modules for the test
        from unittest.mock import patch
        import io
        
        # Mock user input for testing
        with patch('builtins.input', return_value='1'):  # Select first option
            with patch('rich.prompt.Confirm.ask', return_value=False):  # Don't set API key
                try:
                    # Temporarily redirect stdout to capture output
                    old_stdout = sys.stdout
                    captured_output = io.StringIO()
                    sys.stdout = captured_output
                    
                    # This should use fallback models since backend failed
                    chat_interface._configure_model_and_provider()
                    
                    # Restore stdout
                    sys.stdout = old_stdout
                    output = captured_output.getvalue()
                    
                    if "Available AI Models" in output or "Backend unavailable" in output:
                        print("✅ Fallback model configuration works!")
                        return True
                    else:
                        print("❌ Fallback model configuration failed")
                        print(f"Output was: {output}")
                        return False
                        
                except Exception as e:
                    sys.stdout = old_stdout
                    print(f"❌ Error during fallback test: {e}")
                    return False

if __name__ == "__main__":
    success = test_model_fetch()
    sys.exit(0 if success else 1)