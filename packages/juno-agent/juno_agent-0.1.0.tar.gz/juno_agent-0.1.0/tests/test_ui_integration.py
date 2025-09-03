#!/usr/bin/env python3
"""Test the actual UI integration with model selection."""

import sys
import os
from pathlib import Path
from unittest.mock import patch
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_model_selection_ui():
    """Test the model selection UI with backend integration."""
    from juno_agent.ui import ChatInterface
    from juno_agent.config import ConfigManager
    
    print("🖥️  Testing model selection UI with backend integration...")
    
    # Initialize components
    config_manager = ConfigManager(Path('.'))
    chat_interface = ChatInterface(config_manager)
    
    # Capture the output to verify the UI shows backend models
    old_stdout = sys.stdout
    captured_output = io.StringIO()
    
    try:
        # Mock user input: select first model (claude-sonnet-4), don't set API key
        with patch('rich.prompt.Prompt.ask', side_effect=['1']):  # Select first model
            with patch('rich.prompt.Confirm.ask', return_value=False):  # Don't set API key
                # Temporarily redirect stdout
                sys.stdout = captured_output
                
                # This should fetch models from backend and show selection UI
                chat_interface._configure_model_and_provider() 
                
                # Restore stdout
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                # Check if the output contains expected elements
                checks = [
                    ("Backend models loaded", "✅ Loaded 10 models from backend" in output),
                    ("Available AI Models header", "📋 Available AI Models" in output),
                    ("Claude Sonnet 4 listed", "Claude Sonnet 4" in output),
                    ("Anthropic provider shown", "(anthropic)" in output),
                    ("Model name shown", "anthropic/claude-sonnet-4-20250514" in output),
                    ("Temperature shown", "Temp: 0.2" in output),
                    ("Premium cost tier", "💎" in output),
                    ("Model updated confirmation", "✅ Model updated" in output)
                ]
                
                print("\n🔍 Checking UI elements:")
                all_passed = True
                for check_name, check_result in checks:
                    if check_result:
                        print(f"  ✅ {check_name}")
                    else:
                        print(f"  ❌ {check_name}")
                        all_passed = False
                
                if not all_passed:
                    print(f"\n📄 Captured output:\n{output}")
                    return False
                
                # Verify the model was actually configured
                config = config_manager.load_config()
                agent_config = config.agent_config
                
                print(f"\n⚙️  Configuration verification:")
                print(f"  Model: {agent_config.model_name}")
                print(f"  Provider: {agent_config.provider}")
                print(f"  Temperature: {agent_config.temperature}")
                
                if (agent_config.model_name == "anthropic/claude-sonnet-4-20250514" and
                    agent_config.provider == "anthropic" and
                    agent_config.temperature == 0.2):
                    print("  ✅ Configuration correctly updated!")
                    return True
                else:
                    print("  ❌ Configuration not updated correctly")
                    return False
                    
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ Error during UI test: {e}")
        return False
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    print("=" * 70)
    print("🖥️  UI INTEGRATION TEST")
    print("=" * 70)
    
    success = test_model_selection_ui()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ UI INTEGRATION TEST PASSED!")
        print("🎯 The model selection UI successfully integrates with the backend!")
        sys.exit(0)
    else:
        print("❌ UI integration test failed")
        sys.exit(1)