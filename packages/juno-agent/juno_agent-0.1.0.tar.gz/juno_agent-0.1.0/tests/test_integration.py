#!/usr/bin/env python3
"""Test the complete integration with local dev server."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_backend_integration():
    """Test that the backend integration works with local dev server."""
    from juno_agent.ui import ChatInterface
    from juno_agent.config import ConfigManager
    
    print("🧪 Testing backend integration with local dev server...")
    
    # Initialize components
    config_manager = ConfigManager(Path('.'))
    chat_interface = ChatInterface(config_manager)
    
    # Test model fetching
    models = chat_interface._fetch_models_from_backend()
    
    if not models:
        print("❌ Failed to fetch models from backend")
        return False
    
    print(f"✅ Successfully fetched {len(models)} models from backend!")
    
    # Verify specific requested models are present
    expected_models = [
        "claude-sonnet-4",
        "o3", 
        "gpt-5-mini",
        "gpt-5",
        "kimi-k2-instruct"
    ]
    
    found_models = {model["id"]: model for model in models}
    
    print("\n📋 Checking for specific requested models:")
    all_found = True
    for expected_id in expected_models:
        if expected_id in found_models:
            model = found_models[expected_id]
            print(f"  ✅ {model['name']} ({model['provider']})")
            print(f"      Model: {model['model_name']}")
            print(f"      Temp: {model['temperature']}")
            print(f"      Cost: {model.get('cost_tier', 'N/A')}")
        else:
            print(f"  ❌ Missing: {expected_id}")
            all_found = False
    
    if not all_found:
        print("\n❌ Some expected models were missing")
        return False
    
    # Test provider-specific temperature defaults
    print("\n🌡️  Checking temperature defaults:")
    temp_checks = [
        ("claude-sonnet-4", 0.2, "Anthropic"),
        ("o3", 1.0, "OpenAI O-family"),
        ("gpt-5-mini", 1.0, "OpenAI"), 
        ("kimi-k2-instruct", 0.0, "Groq")
    ]
    
    temp_correct = True
    for model_id, expected_temp, provider_note in temp_checks:
        if model_id in found_models:
            actual_temp = found_models[model_id]["temperature"]
            if actual_temp == expected_temp:
                print(f"  ✅ {model_id}: {actual_temp} ({provider_note})")
            else:
                print(f"  ❌ {model_id}: expected {expected_temp}, got {actual_temp}")
                temp_correct = False
        else:
            print(f"  ❌ {model_id}: model not found")
            temp_correct = False
    
    if not temp_correct:
        print("\n❌ Temperature defaults are incorrect")
        return False
    
    # Test LiteLLM format compliance
    print("\n🔧 Checking LiteLLM format compliance:")
    litellm_checks = [
        ("claude-sonnet-4", "anthropic/claude-sonnet-4-20250514"),
        ("o3", "o3"),
        ("gpt-5-mini", "gpt-5-mini"),
        ("kimi-k2-instruct", "groq/moonshotai/kimi-k2-instruct")
    ]
    
    litellm_correct = True
    for model_id, expected_model_name in litellm_checks:
        if model_id in found_models:
            actual_model_name = found_models[model_id]["model_name"]
            if actual_model_name == expected_model_name:
                print(f"  ✅ {model_id}: {actual_model_name}")
            else:
                print(f"  ❌ {model_id}: expected '{expected_model_name}', got '{actual_model_name}'")
                litellm_correct = False
        else:
            print(f"  ❌ {model_id}: model not found")
            litellm_correct = False
    
    if not litellm_correct:
        print("\n❌ LiteLLM format compliance failed")
        return False
    
    print("\n🎉 All integration tests passed!")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🔗 COMPLETE BACKEND INTEGRATION TEST")
    print("=" * 70)
    
    success = test_backend_integration()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED - Integration is working perfectly!")
        print("🚀 The juno-agent can now fetch models from the backend!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please check the implementation")
        sys.exit(1)