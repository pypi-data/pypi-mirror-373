"""Model handler for managing all model configuration and management functionality."""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from ...debug_logger import debug_logger


class ModelHandler:
    """Handler for all model-related operations."""
    
    def __init__(self, app, config_manager, chat_area, model_selection_menu, 
                 api_key_prompt, global_default_menu, yes_no_menu, chat_input):
        """Initialize ModelHandler with dependencies."""
        self.app = app
        self.config_manager = config_manager
        self.chat_area = chat_area
        self.model_selection_menu = model_selection_menu
        self.api_key_prompt = api_key_prompt
        self.global_default_menu = global_default_menu
        self.yes_no_menu = yes_no_menu
        self.chat_input = chat_input
        self.debug_log = config_manager.create_debug_logger(debug=True)
        
    async def handle_model_command(self) -> None:
        """Handle /model command for configuring AI models."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Display model_kwargs information
        model_kwargs_info = ""
        if agent_config.model_kwargs:
            kwargs_list = [f"{k}: {v}" for k, v in agent_config.model_kwargs.items()]
            model_kwargs_info = f"• **Model Options**: {', '.join(kwargs_list)}\n"
        
        # Use slug for display if available, otherwise fallback to model_name
        display_model = agent_config.model_slug or agent_config.model_name
        
        # Display current configuration
        current_config_content = f"""**🤖 AI Model Configuration**

**🔧 Current Configuration**
• **Model**: {display_model}
• **Provider**: {agent_config.provider}
• **Temperature**: {agent_config.temperature}
• **Max Tokens**: {agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}
• **Base URL**: {agent_config.custom_base_url or 'Default'}
{model_kwargs_info}
📋 **Select a new model from the menu below, or press Escape to cancel.**"""

        self.chat_area.add_message(current_config_content, is_user=False)
        
        # Show the model selection menu
        if self.model_selection_menu:
            self.model_selection_menu.show()
    
    def start_model_config_mode(self) -> None:
        """Start model configuration mode for text input handling."""
        self.app.setup_active = True
        self.app.setup_data = {'mode': 'model_config', 'sub_step': 'menu'}
    
    async def handle_model_config_input(self, user_input: str) -> None:
        """Handle user input during model configuration."""
        if user_input.lower() in ['/cancel', '/quit', '/exit', 'q']:
            self.app.setup_active = False
            self.chat_area.add_message("Model configuration cancelled.", is_user=False)
            return
        
        mode_data = self.app.setup_data
        sub_step = mode_data.get('sub_step', 'menu')
        
        if sub_step == 'menu':
            await self._handle_model_menu_choice(user_input)
        elif sub_step == 'change_model':
            await self._handle_change_model_input(user_input)
        elif sub_step == 'api_key':
            await self._handle_model_api_key_input(user_input)
        elif sub_step == 'temperature':
            await self._handle_temperature_input(user_input)
        elif sub_step == 'max_tokens':
            await self._handle_max_tokens_input(user_input)
        elif sub_step == 'base_url':
            await self._handle_base_url_input(user_input)
        elif sub_step == 'select_openai_model':
            await self._handle_openai_model_selection(user_input)
        elif sub_step == 'select_anthropic_model':
            await self._handle_anthropic_model_selection(user_input)
        elif sub_step == 'select_google_model':
            await self._handle_google_model_selection(user_input)
        elif sub_step == 'select_groq_model':
            await self._handle_groq_model_selection(user_input)
        elif sub_step == 'custom_model_name':
            await self._handle_custom_model_name(user_input)
        elif sub_step == 'custom_provider':
            await self._handle_custom_provider(user_input)
        elif sub_step == 'ask_api_key':
            await self._handle_ask_api_key(user_input)
    
    async def _handle_model_menu_choice(self, choice: str) -> None:
        """Handle the main model configuration menu choice."""
        choice = choice.strip()
        
        if choice == "1":
            # Change model/provider
            self.chat_area.add_message("**🎯 Change Model & Provider**\n\nAvailable options:\n1. **OpenAI** - gpt-5-mini (recommended), gpt-5, o3, o4-mini\n2. **Anthropic** - claude-4-sonnet-20250514 (recommended), claude-4-haiku\n3. **Google** - gemini-2.5-pro (recommended), gemini-2.5-flash\n4. **Groq** - moonshotai/kimi-k2-instruct (recommended), qwen-coder\n5. **Custom** - Enter custom model details\n\nEnter your choice (1-5):", is_user=False)
            self.app.setup_data['sub_step'] = 'change_model'
            
        elif choice == "2":
            # Set API key
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            self.chat_area.add_message(f"**🔑 API Key Configuration**\n\nFor **{agent_config.model_name}** ({agent_config.provider})\nExpected environment variable: **{expected_env_var}**\n\nPlease enter your API key (it will be saved securely):", is_user=False)
            self.app.setup_data['sub_step'] = 'api_key'
            
        elif choice == "3":
            # Adjust parameters
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            self.chat_area.add_message(f"**⚙️ Model Parameters Configuration**\n\nCurrent temperature: **{agent_config.temperature}**\n\nEnter new temperature (0.0-2.0), or press Enter to keep current:", is_user=False)
            self.app.setup_data['sub_step'] = 'temperature'
            
        elif choice == "4":
            # Set custom base URL
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            current_url = agent_config.custom_base_url or "Default"
            self.chat_area.add_message(f"**🌐 Custom Base URL Configuration**\n\nCurrent base URL: **{current_url}**\n\nEnter new base URL, or press Enter to use default:", is_user=False)
            self.app.setup_data['sub_step'] = 'base_url'
            
        elif choice == "5":
            # Reset to defaults
            from ...config import AgentConfig
            default_config = AgentConfig()
            
            try:
                # Use global scope by default for model configurations to persist across projects
                scope = "global"
                
                self.config_manager.update_agent_config_with_scope(
                    scope=scope,
                    model_name=default_config.model_name,
                    provider=default_config.provider,
                    temperature=default_config.temperature,
                    custom_base_url=default_config.custom_base_url,
                    api_key_env_var=default_config.api_key_env_var
                )
                
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Model configuration reset to defaults** {scope_text}\n\nModel: **{default_config.model_name}** ({default_config.provider})", is_user=False)
                self.app.setup_active = False
                
            except Exception as e:
                self.chat_area.add_message(f"❌ Error resetting model config: {str(e)}", is_user=False)
                self.app.setup_active = False
            
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-5 or 'q' to quit.", is_user=False)
    
    async def _handle_change_model_input(self, choice: str) -> None:
        """Handle model/provider change input."""
        choice = choice.strip()
        
        if choice == "1":
            # OpenAI
            self.chat_area.add_message("**OpenAI Models**\n\n1. **gpt-5** (latest flagship model)\n2. **gpt-5-mini** (recommended - fast, cost-effective)\n3. **o3** (advanced reasoning model)\n4. **o4-mini** (lightweight reasoning model)\n\nSelect model (1-4):", is_user=False)
            self.app.setup_data['provider'] = 'openai'
            self.app.setup_data['sub_step'] = 'select_openai_model'
            
        elif choice == "2":
            # Anthropic 
            self.chat_area.add_message("**Anthropic Models**\n\n1. **claude-4-sonnet-20250514** (recommended - latest v4)\n2. **claude-4-haiku** (fast, efficient v4)\n\nSelect model (1-2):", is_user=False)
            self.app.setup_data['provider'] = 'anthropic'
            self.app.setup_data['sub_step'] = 'select_anthropic_model'
            
        elif choice == "3":
            # Google
            self.chat_area.add_message("**Google Models**\n\n1. **gemini-2.5-pro** (recommended - most capable)\n2. **gemini-2.5-flash** (fast, efficient)\n\nSelect model (1-2):", is_user=False)
            self.app.setup_data['provider'] = 'google'
            self.app.setup_data['sub_step'] = 'select_google_model'
            
        elif choice == "4":
            # Groq
            self.chat_area.add_message("**Groq Models**\n\n1. **moonshotai/kimi-k2-instruct** (recommended - high performance)\n2. **qwen-coder** (specialized for coding)\n\nSelect model (1-2):", is_user=False)
            self.app.setup_data['provider'] = 'groq'
            self.app.setup_data['sub_step'] = 'select_groq_model'
            
        elif choice == "5":
            # Custom
            self.chat_area.add_message("**Custom Model Configuration**\n\nEnter the model name (LiteLLM format, e.g., 'gpt-5' or 'claude-4-sonnet-20250514'):", is_user=False)
            self.app.setup_data['provider'] = 'custom'
            self.app.setup_data['sub_step'] = 'custom_model_name'
            
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-5.", is_user=False)
    
    async def _handle_model_api_key_input(self, api_key: str) -> None:
        """Handle API key input."""
        if not api_key.strip():
            self.chat_area.add_message("❌ **Please enter a valid API key**.", is_user=False)
            return
        
        try:
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            # Use global scope by default for API keys to persist across projects
            scope = "global"
            self.config_manager.set_model_api_key_with_scope(api_key.strip(), scope=scope, key_name=expected_env_var)
            
            scope_text = "globally" if scope == "global" else "locally"
            self.chat_area.add_message(f"✅ **API key saved** {scope_text} as **{expected_env_var}**\n\n🔒 Key is securely stored and will not be logged", is_user=False)
            self.app.setup_active = False
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error saving API key**: {str(e)}", is_user=False)
            self.app.setup_active = False
    
    async def _handle_temperature_input(self, temp_str: str) -> None:
        """Handle temperature input."""
        if not temp_str.strip():
            # Keep current temperature
            self.chat_area.add_message("✅ **Temperature unchanged**", is_user=False)
            # Continue to max_tokens configuration
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            self.chat_area.add_message(f"**Max Tokens Configuration**\n\nCurrent max tokens: **{agent_config.max_tokens or 'Auto'}**\n\nEnter new max tokens value, or press Enter to keep current:", is_user=False)
            self.app.setup_data['sub_step'] = 'max_tokens'
            return
        
        try:
            temperature = float(temp_str)
            if 0.0 <= temperature <= 2.0:
                scope = "global"  # Default to global for model configurations
                self.config_manager.update_agent_config_with_scope(scope=scope, temperature=temperature)
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Temperature set to {temperature}** {scope_text}", is_user=False)
                
                # Continue to max_tokens configuration
                config = self.config_manager.load_config()
                agent_config = config.agent_config
                self.chat_area.add_message(f"**Max Tokens Configuration**\n\nCurrent max tokens: **{agent_config.max_tokens or 'Auto'}**\n\nEnter new max tokens value, or press Enter to keep current:", is_user=False)
                self.app.setup_data['sub_step'] = 'max_tokens'
            else:
                self.chat_area.add_message("❌ **Temperature must be between 0.0 and 2.0**. Please try again:", is_user=False)
        except ValueError:
            self.chat_area.add_message("❌ **Invalid temperature value**. Please enter a number between 0.0 and 2.0:", is_user=False)
    
    async def _handle_max_tokens_input(self, tokens_str: str) -> None:
        """Handle max tokens input."""
        if not tokens_str.strip():
            # Set to auto (None)
            scope = "global"  # Default to global for model configurations
            self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Max tokens set to auto** {scope_text}", is_user=False)
            self.app.setup_active = False
            return
        
        try:
            max_tokens = int(tokens_str)
            if max_tokens > 0:
                scope = "global"  # Default to global for model configurations
                self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=max_tokens)
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Max tokens set to {max_tokens}** {scope_text}", is_user=False)
                self.app.setup_active = False
            else:
                self.chat_area.add_message("❌ **Max tokens must be positive**. Please try again:", is_user=False)
        except ValueError:
            self.chat_area.add_message("❌ **Invalid max tokens value**. Please enter a positive integer:", is_user=False)
    
    async def _handle_base_url_input(self, url_str: str) -> None:
        """Handle base URL input."""
        scope = "global"  # Default to global for model configurations
        
        if not url_str.strip():
            # Reset to default
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Base URL reset to default** {scope_text}", is_user=False)
        else:
            # Set custom URL
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=url_str.strip())
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Base URL set to {url_str.strip()}** {scope_text}", is_user=False)
        
        self.app.setup_active = False
    
    async def _handle_openai_model_selection(self, choice: str) -> None:
        """Handle OpenAI model selection."""
        models = {
            "1": ("gpt-5", "GPT-5"),
            "2": ("gpt-5-mini", "GPT-5 Mini"),
            "3": ("o3", "O3"),
            "4": ("o4-mini", "O4 Mini")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "openai", 1.0, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-4.", is_user=False)
    
    async def _handle_anthropic_model_selection(self, choice: str) -> None:
        """Handle Anthropic model selection."""
        models = {
            "1": ("claude-4-sonnet-20250514", "Claude 4 Sonnet"),
            "2": ("claude-4-haiku", "Claude 4 Haiku")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "anthropic", 0.2, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_google_model_selection(self, choice: str) -> None:
        """Handle Google model selection."""
        models = {
            "1": ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            "2": ("gemini-2.5-flash", "Gemini 2.5 Flash")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "google", 0.7, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_groq_model_selection(self, choice: str) -> None:
        """Handle Groq model selection."""
        models = {
            "1": ("moonshotai/kimi-k2-instruct", "Moonshot K2 Instruct"),
            "2": ("qwen-coder", "Qwen Coder")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "groq", 0.7, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_custom_model_name(self, model_name: str) -> None:
        """Handle custom model name input."""
        if not model_name.strip():
            self.chat_area.add_message("❌ **Please enter a valid model name**.", is_user=False)
            return
        
        self.app.setup_data['custom_model'] = model_name.strip()
        self.chat_area.add_message("**Provider Configuration**\n\nEnter the provider name (e.g., 'openai', 'anthropic', 'custom'):", is_user=False)
        self.app.setup_data['sub_step'] = 'custom_provider'
    
    async def _handle_custom_provider(self, provider: str) -> None:
        """Handle custom provider input."""
        if not provider.strip():
            self.chat_area.add_message("❌ **Please enter a valid provider name**.", is_user=False)
            return
        
        model_name = self.app.setup_data.get('custom_model')
        await self._save_model_config(model_name, provider.strip(), 0.7, f"Custom: {model_name}")
    
    async def _save_model_config(self, model_name: str, provider: str, temperature: float, display_name: str) -> None:
        """Save model configuration and exit model config mode."""
        try:
            # Use global scope by default for model configurations to persist across projects
            scope = "global"
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=model_name,
                provider=provider,
                temperature=temperature,
                api_key_env_var=api_key_env_var
            )
            
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Model updated to {display_name}** {scope_text}\n\nProvider: **{provider}**\nTemperature: **{temperature}**", is_user=False)
            
            # Reinitialize agent with new model configuration
            try:
                await self.app.initialize_agent()
                self.debug_log.info("Agent reinitialized successfully after model config save")
            except Exception as agent_error:
                self.debug_log.error(f"Agent reinitialization failed after model config save: {agent_error}")
                self.chat_area.add_message(f"⚠️ **Model saved but agent initialization failed**: {str(agent_error)}", is_user=False)
            
            # Ask about API key
            expected_env_var = self._get_expected_env_var(provider)
            current_key = self.config_manager.get_model_api_key()
            
            if not current_key:
                self.chat_area.add_message(f"**🔑 API Key Setup**\n\nWould you like to set up the API key for **{provider}** now?\nExpected environment variable: **{expected_env_var}**\n\nReply with **'yes'** to enter API key, or **'no'** to skip:", is_user=False)
                self.app.setup_data['sub_step'] = 'ask_api_key'
            else:
                self.chat_area.add_message("**✅ Configuration Complete!**\n\nModel configuration updated successfully. API key is already configured.", is_user=False)
                self.app.setup_active = False
                
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error saving model config**: {str(e)}", is_user=False)
            self.app.setup_active = False
    
    async def _handle_ask_api_key(self, response: str) -> None:
        """Handle API key setup question response."""
        if response.lower().strip() in ['yes', 'y', '1', 'true']:
            # Switch to API key input mode
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            self.chat_area.add_message(f"**🔑 API Key Configuration**\n\nFor **{agent_config.model_name}** ({agent_config.provider})\nExpected environment variable: **{expected_env_var}**\n\nPlease enter your API key (it will be saved securely):", is_user=False)
            self.app.setup_data['sub_step'] = 'api_key'
        else:
            # Skip API key setup
            self.chat_area.add_message("**✅ Configuration Complete!**\n\nModel configuration updated successfully. You can set up the API key later using `/model` command option 2.", is_user=False)
            self.app.setup_active = False
    
    def _extract_first_two_paragraphs(self, summary: str) -> str:
        """Extract the first 2 paragraphs from a summary for preview display.
        
        Args:
            summary: The full summary text
            
        Returns:
            A formatted string containing the first 2 paragraphs, or a fallback message
        """
        if not summary or not summary.strip():
            return "No summary content available."
        
        # Clean up the summary text
        cleaned_summary = summary.strip()
        
        # Split by double newlines (common paragraph separator)
        paragraphs = [p.strip() for p in cleaned_summary.split('\n\n') if p.strip()]
        
        # If no double newlines, try single newlines but be more conservative
        if len(paragraphs) <= 1:
            lines = [line.strip() for line in cleaned_summary.split('\n') if line.strip()]
            # Group lines into paragraphs (assume every 2-3 lines is a paragraph)
            if len(lines) > 3:
                # Try to detect paragraph breaks by finding empty lines or significant content changes
                paragraphs = []
                current_paragraph = []
                
                for line in lines:
                    if len(line) < 20 and len(current_paragraph) > 0:  # Short line might be end of paragraph
                        current_paragraph.append(line)
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                    else:
                        current_paragraph.append(line)
                
                # Add remaining lines as final paragraph
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
            else:
                # Very short summary, treat as single paragraph
                paragraphs = [' '.join(lines)]
        
        # Take first 2 paragraphs
        selected_paragraphs = paragraphs[:2]
        
        # Handle very long paragraphs by truncating if needed
        max_paragraph_length = 300  # Reasonable length for display
        truncated_paragraphs = []
        
        for para in selected_paragraphs:
            if len(para) > max_paragraph_length:
                # Find a good break point (preferably at sentence end)
                truncate_point = max_paragraph_length
                # Look for sentence endings within reasonable range
                for i in range(max_paragraph_length - 50, min(len(para), max_paragraph_length + 50)):
                    if para[i] in '.!?':
                        truncate_point = i + 1
                        break
                
                truncated_para = para[:truncate_point].strip()
                if not truncated_para.endswith(('.', '!', '?')):
                    truncated_para += "..."
                truncated_paragraphs.append(truncated_para)
            else:
                truncated_paragraphs.append(para)
        
        # Join paragraphs with double newlines
        result = '\n\n'.join(truncated_paragraphs)
        
        # Fallback for very short content
        if len(result.strip()) < 10:
            return "Brief summary generated - content preserved in context."
        
        return result

    def _get_expected_env_var(self, provider: str) -> str:
        """Get expected environment variable name for a provider."""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return "OPENAI_API_KEY"
        elif provider_lower == "anthropic":
            return "ANTHROPIC_API_KEY"
        elif provider_lower == "google":
            return "GOOGLE_API_KEY"
        elif provider_lower == "azure":
            return "AZURE_OPENAI_API_KEY"
        elif provider_lower == "cohere":
            return "COHERE_API_KEY"
        elif provider_lower == "huggingface":
            return "HUGGINGFACE_API_KEY"
        elif provider_lower == "groq":
            return "GROQ_API_KEY"
        elif provider_lower == "xai":
            return "XAI_API_KEY"
        elif provider_lower == "openrouter":
            return "OPENROUTER_API_KEY"
        elif provider_lower == "ollama":
            return "OLLAMA_API_KEY"
        elif provider_lower in ["together_ai", "togetherai"]:
            return "TOGETHER_API_KEY"
        else:
            return f"{provider.upper()}_API_KEY"
    
    async def handle_model_selected(self, model: Dict[str, Any], provider: str) -> None:
        """Handle when a model is selected from the menu."""
        try:
            model_id = model.get('id', 'unknown')
            model_slug = model.get('slug', model_id)  # Get slug, fallback to id if not present
            display_name = model.get('display_name', model_id)
            model_kwargs = model.get('model_kwargs', {})  # Extract model_kwargs from model definition
            
            # Load models config to get provider info
            models_config_path = Path(__file__).parent.parent / "models.json"
            if models_config_path.exists():
                with open(models_config_path, 'r') as f:
                    models_config = json.load(f)
                
                provider_data = models_config.get("providers", {}).get(provider, {})
                api_key_env = provider_data.get("api_key_env", f"{provider.upper()}_API_KEY")
            else:
                api_key_env = self._get_expected_env_var(provider)
            
            # Store selected model info including model_kwargs and slug for use during configuration
            self.app._selected_model_info = {
                'model_id': model_id,
                'model_slug': model_slug,
                'provider': provider, 
                'display_name': display_name, 
                'api_key_env': api_key_env,
                'model_kwargs': model_kwargs
            }
            
            # Always use the unified model configuration flow
            # This will handle API key checking and user prompts consistently
            await self._configure_selected_model(model, provider)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error selecting model**: {str(e)}", is_user=False)
    
    async def handle_manual_model_entry(self) -> None:
        """Handle manual model entry request."""
        self.chat_area.add_message("""**🔧 Manual Model Entry**

Please enter the model details in the format: `provider/model-name`

**Examples:**
• `openai/gpt-4`
• `anthropic/claude-3-sonnet`
• `google/gemini-pro`
• `groq/llama2-70b-chat`
• `ollama/codellama`

Enter your custom model:""", is_user=False)
        
        # Start manual entry mode
        self.app.setup_active = True
        self.app.setup_step = 0
        self.app.setup_data = {'mode': 'manual_model_entry'}
    
    async def handle_api_key_entered(self, api_key: str, provider: str) -> None:
        """Handle when API key is entered."""
        try:
            # Add comprehensive debugging
            debug_log = self.debug_log
            debug_log.debug(f"API key entered", provider=provider, has_key=bool(api_key), key_length=len(api_key) if api_key else 0)
            
            # Get the environment variable name for this provider
            # Check if we have a stored API key env from pending model selection (for manual entries)
            if hasattr(self.app, '_pending_model_selection') and 'api_key_env' in self.app._pending_model_selection:
                env_var = self.app._pending_model_selection['api_key_env']
            else:
                # Use standard provider mapping
                env_var = self._get_expected_env_var(provider)
            
            debug_log.debug(f"Determined env var", provider=provider, env_var=env_var)
            
            # Save API key to config with global scope for consistency and cross-project persistence
            scope = "global"
            debug_log.debug(f"Calling set_model_api_key_with_scope", api_key_provided=bool(api_key), key_name=env_var, scope=scope)
            self.config_manager.set_model_api_key_with_scope(api_key, scope=scope, key_name=env_var)
            
            debug_log.info(f"API key saved successfully", provider=provider, env_var=env_var, scope=scope)
            scope_text = "globally" if scope == "global" else "locally"
            self.chat_area.add_message(f"🔑 **API Key Saved** {scope_text} for {provider.title()} (as {env_var})\n⏳ **Configuring model...**", is_user=False)
            
            # Hide the API key prompt 
            if self.api_key_prompt:
                self.api_key_prompt.hide()
            
            # Check for different types of pending operations
            if hasattr(self.app, '_pending_model_selection'):
                debug_log.debug(f"Processing pending model selection")
                pending = self.app._pending_model_selection
                await self._configure_selected_model(pending["model"], pending["provider"])
                delattr(self.app, '_pending_model_selection')
                debug_log.debug(f"Completed pending model selection")
            
            # Check for model setup context from API key prompt
            elif hasattr(self.api_key_prompt, 'context') and self.api_key_prompt.context.get('model_setup'):
                debug_log.debug(f"Processing model setup after API key entry")
                context = self.api_key_prompt.context
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                display_name = context.get('display_name', model_id)
                
                # Get model_kwargs from stored model selection info
                model_kwargs = getattr(self.app, '_selected_model_info', {}).get('model_kwargs', {})
                
                # Save model configuration and continue with global default flow
                await self._save_model_with_new_api_key(model_id, provider, display_name, model_kwargs)
                debug_log.debug(f"Completed model setup after API key entry")
            
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error saving API key: {str(e)}", provider=provider)
            self.chat_area.add_message(f"❌ **Error saving API key**: {str(e)}", is_user=False)
    
    def handle_api_key_entered_direct(self, api_key: str, provider: str) -> None:
        """Handle API key entered via direct callback (non-async wrapper)."""
        # Schedule the async handler to run
        self.app.call_after_refresh(self._schedule_api_key_handler, api_key, provider)
    
    async def _schedule_api_key_handler(self, api_key: str, provider: str) -> None:
        """Schedule the async API key handler."""
        await self.handle_api_key_entered(api_key, provider)
    
    async def _configure_selected_model(self, model: Dict[str, Any], provider: str) -> None:
        """Configure the selected model in the config."""
        try:
            debug_log = self.debug_log
            model_id = model.get('id', 'unknown')
            display_name = model.get('display_name', model_id)
            
            debug_log.debug(f"Configuring selected model", model_id=model_id, provider=provider, display_name=display_name)
            
            # First, always save to local config for this project
            debug_log.debug(f"Saving to local config first", model_id=model_id, provider=provider)
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            debug_log.debug(f"Using API key env var", api_key_env_var=api_key_env_var, provider=provider)
            
            # Check if API key already exists for this provider
            existing_api_key = self.config_manager.has_api_key_for_provider(provider)
            debug_log.debug(f"Existing API key for provider {provider}", has_key=existing_api_key)
            
            if existing_api_key:
                # API key exists - ask user if they want to update it
                debug_log.debug(f"API key exists for {provider}, asking user if they want to update")
                
                self.yes_no_menu.show(
                    title="🔑 Update API Key?",
                    message=f"You already have an API key configured for {provider.title()}.\n\nWould you like to update it with a new value?",
                    yes_label="🔄 Yes, update API key",
                    no_label="✅ No, use existing key",
                    context={
                        'type': 'api_key_update',
                        'model_id': model_id,
                        'provider': provider,
                        'display_name': display_name,
                        'api_key_env_var': api_key_env_var
                    }
                )
                
                # Blur chat input and focus yes/no menu
                if self.chat_input:
                    self.chat_input.blur()
                self.app.call_after_refresh(self._ensure_yes_no_menu_focus)
                
            else:
                # No API key exists - show API key prompt directly
                debug_log.debug(f"No API key for {provider}, showing API key prompt")
                
                self.api_key_prompt.show(
                    title=f"Set {provider.title()} API Key",
                    provider=provider,
                    context={'model_setup': True, 'model_id': model_id, 'provider': provider, 'display_name': display_name}
                )
                # Blur chat input and focus API key prompt
                if self.chat_input:
                    self.chat_input.blur()
                self.app.call_after_refresh(self._ensure_api_key_prompt_focus)
            
            # Hide the model selection menu
            if self.model_selection_menu:
                self.model_selection_menu.hide()
                
        except Exception as e:
            debug_log.error(f"Error configuring model: {str(e)}", model_id=model.get('id', 'unknown'), provider=provider)
            if self.chat_area:
                self.chat_area.add_message(f"❌ **Error configuring model**: {str(e)}", is_user=False)
    
    def _show_global_default_prompt(self, display_name: str, provider: str) -> None:
        """Show prompt asking if user wants to set model as global default."""
        # Remove focus from chat input first
        if self.chat_input:
            self.chat_input.blur()
        
        # Show the global default menu widget
        if self.global_default_menu:
            self.global_default_menu.show(display_name, provider)
            # Ensure menu gets focus after a brief delay
            self.app.call_after_refresh(self._ensure_global_menu_focus)
    
    def _ensure_global_menu_focus(self) -> None:
        """Ensure the global default menu has focus."""
        if self.global_default_menu and self.global_default_menu.is_visible:
            self.global_default_menu.focus()
    
    def _ensure_yes_no_menu_focus(self) -> None:
        """Ensure the yes/no menu has focus."""
        if self.yes_no_menu and self.yes_no_menu.is_visible:
            self.yes_no_menu.focus()
    
    def _ensure_api_key_prompt_focus(self) -> None:
        """Ensure the API key prompt has focus."""
        if self.api_key_prompt and self.api_key_prompt.is_visible:
            self.api_key_prompt.focus()
    
    async def handle_global_default_selection(self, set_global: bool) -> None:
        """Handle the selection from global default menu."""
        try:
            debug_log = self.debug_log
            
            if set_global and hasattr(self.app, '_pending_global_model'):
                pending = self.app._pending_global_model
                debug_log.debug(f"Saving model to global config", model_id=pending['model_id'], provider=pending['provider'])
                
                # Save to global config with correct API key env var
                self.config_manager.update_agent_config_with_scope(
                    scope="global",
                    model_name=pending['model_id'],
                    provider=pending['provider'],
                    api_key_env_var=pending['api_key_env_var']
                )
                
                debug_log.info(f"Model saved to global config", model=pending['model_id'], provider=pending['provider'])
                
                # Check agent status
                agent_status = "✅ Reinitialized and ready" if pending.get('agent_reinitialized', True) else f"❌ Failed: {pending.get('agent_error', 'Unknown error')}"
                
                success_message = f"""✅ **Model Configuration Complete**

📋 **Configuration Summary:**
• **Model**: {pending['display_name']}
• **Provider**: {pending['provider'].title()}
• **Local Config**: ✅ Saved (for this project)
• **Global Config**: ✅ Saved (default for all projects)
• **Agent**: {agent_status}

🎉 **Ready to chat!** Your new model is active."""
            else:
                if hasattr(self.app, '_pending_global_model'):
                    pending = self.app._pending_global_model
                    # Check agent status
                    agent_status = "✅ Reinitialized and ready" if pending.get('agent_reinitialized', True) else f"❌ Failed: {pending.get('agent_error', 'Unknown error')}"
                    
                    success_message = f"""✅ **Model Configuration Complete**

📋 **Configuration Summary:**
• **Model**: {pending['display_name']}
• **Provider**: {pending['provider'].title()}
• **Local Config**: ✅ Saved (for this project only)
• **Global Config**: Not changed
• **Agent**: {agent_status}

🎉 **Ready to chat!** Your new model is active for this project."""
                else:
                    success_message = "✅ **Model configuration complete**"
            
            self.chat_area.add_message(success_message, is_user=False)
            
            # Clean up pending model
            if hasattr(self.app, '_pending_global_model'):
                delattr(self.app, '_pending_global_model')
            
            # Refresh welcome screen to show updated model information
            self.update_welcome_message_and_footer()
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error handling global default response: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
            self.app.setup_active = False
            self.app.setup_data = {}
    
    async def handle_yes_no_selection(self, selected_yes: bool, context: dict) -> None:
        """Handle Yes/No selection from the reusable YesNoMenu."""
        try:
            debug_log = self.debug_log
            debug_log.debug(f"Handling yes/no selection", selected_yes=selected_yes, context=context)
            
            # Route to specific handlers based on context
            context_type = context.get('type', 'unknown')
            
            if context_type == 'api_key_update':
                await self._handle_api_key_update_selection(selected_yes, context)
            else:
                debug_log.warning(f"Unknown yes/no context type", context_type=context_type)
                self.chat_area.add_message(f"❌ **Error**: Unknown selection context: {context_type}", is_user=False)
            
            # Always focus input after selection
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error handling yes/no selection: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _handle_api_key_update_selection(self, update_api_key: bool, context: dict) -> None:
        """Handle API key update selection."""
        try:
            debug_log = self.debug_log
            
            if update_api_key:
                # User wants to update API key - show API key prompt
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                
                debug_log.debug(f"User chose to update API key", model_id=model_id, provider=provider)
                
                # Show API key prompt
                self.api_key_prompt.show(
                    title=f"Update {provider.title()} API Key",
                    provider=provider,
                    context={'model_setup': True, 'model_id': model_id, 'provider': provider}
                )
                # Blur chat input and focus API key prompt
                if self.chat_input:
                    self.chat_input.blur()
                self.app.call_after_refresh(self._ensure_api_key_prompt_focus)
                
            else:
                # User doesn't want to update API key - proceed with existing key
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                display_name = context.get('display_name', model_id)
                
                debug_log.debug(f"User chose to keep existing API key", model_id=model_id, provider=provider)
                
                # Get model_kwargs from stored model selection info
                model_kwargs = getattr(self.app, '_selected_model_info', {}).get('model_kwargs', {})
                
                # Save model config without updating API key
                await self._save_model_without_api_key_update(model_id, provider, display_name, model_kwargs)
                
        except Exception as e:
            debug_log.error(f"Error handling API key update selection: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _save_model_without_api_key_update(self, model_id: str, provider: str, display_name: str, model_kwargs: Optional[Dict[str, Any]] = None) -> None:
        """Save model configuration without updating API key."""
        try:
            debug_log = self.debug_log
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            # Get slug from stored model info
            model_slug = getattr(self.app, '_selected_model_info', {}).get('model_slug', model_id)
            
            debug_log.debug(f"Saving model without API key update", model_id=model_id, provider=provider, api_key_env_var=api_key_env_var, model_kwargs=model_kwargs, model_slug=model_slug)
            
            # Prepare update parameters
            update_params = {
                "model_name": model_id,
                "model_slug": model_slug,
                "provider": provider.lower(),
                "api_key_env_var": api_key_env_var
            }
            
            # Add model_kwargs if provided
            if model_kwargs:
                update_params["model_kwargs"] = model_kwargs
                debug_log.debug(f"Including model_kwargs in config", model_kwargs=model_kwargs)
            
            # Save to local config
            self.config_manager.update_agent_config_with_scope(
                scope="local",
                **update_params
            )
            
            # Reinitialize agent
            await self.app.initialize_agent()
            
            # Store pending model info for global default prompt
            self.app._pending_global_model = {
                'model_id': model_id,
                'provider': provider,
                'display_name': display_name,
                'api_key_env_var': api_key_env_var,
                'agent_reinitialized': True
            }
            
            # Show global default selection menu
            self.global_default_menu.show(display_name, provider)
            # Blur chat input and focus global default menu
            if self.chat_input:
                self.chat_input.blur()
            self.app.call_after_refresh(self._ensure_global_menu_focus)
            
        except Exception as e:
            debug_log.error(f"Error saving model without API key update: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _save_model_with_new_api_key(self, model_id: str, provider: str, display_name: str, model_kwargs: Optional[Dict[str, Any]] = None) -> None:
        """Save model configuration after new API key has been set."""
        try:
            debug_log = self.debug_log
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            # Get slug from stored model info
            model_slug = getattr(self.app, '_selected_model_info', {}).get('model_slug', model_id)
            
            debug_log.debug(f"Saving model with new API key", model_id=model_id, provider=provider, api_key_env_var=api_key_env_var, model_kwargs=model_kwargs, model_slug=model_slug)
            
            # Prepare update parameters
            update_params = {
                "model_name": model_id,
                "model_slug": model_slug,
                "provider": provider.lower(),
                "api_key_env_var": api_key_env_var
            }
            
            # Add model_kwargs if provided
            if model_kwargs:
                update_params["model_kwargs"] = model_kwargs
                debug_log.debug(f"Including model_kwargs in config", model_kwargs=model_kwargs)
            
            # Save to local config
            self.config_manager.update_agent_config_with_scope(
                scope="local",
                **update_params
            )
            
            # Reinitialize agent
            await self.app.initialize_agent()
            
            # Store pending model info for global default prompt
            self.app._pending_global_model = {
                'model_id': model_id,
                'provider': provider,
                'display_name': display_name,
                'api_key_env_var': api_key_env_var,
                'agent_reinitialized': True
            }
            
            # Show global default selection menu
            self.global_default_menu.show(display_name, provider)
            # Blur chat input and focus global default menu
            if self.chat_input:
                self.chat_input.blur()
            self.app.call_after_refresh(self._ensure_global_menu_focus)
            
        except Exception as e:
            debug_log.error(f"Error saving model with new API key: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def handle_manual_model_input(self, user_input: str) -> None:
        """Handle manual model input."""
        try:
            debug_log = self.debug_log
            model_input = user_input.strip()
            
            debug_log.debug(f"Processing manual model input", input=model_input)
            
            if not model_input:
                self.chat_area.add_message("❌ **Please enter a valid model name**", is_user=False)
                return
            
            # Parse provider/model format
            if '/' in model_input:
                provider, model_name = model_input.split('/', 1)
            else:
                # Assume it's an OpenAI model if no provider specified
                provider = "openai"
                model_name = model_input
            
            provider = provider.strip()
            model_name = model_name.strip()
            
            debug_log.debug(f"Parsed manual model", provider=provider, model_name=model_name)
            
            # Create a model dict for the manual entry
            manual_model = {
                'id': model_input,  # Use full input as ID (e.g., "together_ai/codellama-34b")
                'display_name': model_name,
                'max_tokens': 0,  # Unknown for manual entries
                'supports_vision': False,  # Unknown for manual entries
                'supports_function_calling': True  # Assume true for manual entries
            }
            
            debug_log.debug(f"Created manual model dict", model=manual_model)
            
            # Determine API key environment variable for this provider
            provider_lower = provider.lower()
            known_providers = ["openai", "anthropic", "google", "groq", "xai", "openrouter", "ollama", "together_ai", "togetherai"]
            
            if provider_lower in known_providers:
                api_key_env = self._get_expected_env_var(provider)
            else:
                # Use MANUAL_LLM_API_KEY for unknown providers
                api_key_env = "MANUAL_LLM_API_KEY"
            
            debug_log.debug(f"Determined API key env for manual model", provider=provider, api_key_env=api_key_env)
            
            # Check if API key is available
            if not os.getenv(api_key_env) and provider_lower != "ollama":
                # Show API key prompt
                self.chat_area.add_message(f"🔑 **API Key Required** for {provider} (will be saved as {api_key_env})", is_user=False)
                if self.api_key_prompt:
                    self.api_key_prompt.show(provider, api_key_env, self.handle_api_key_entered_direct)
                # Store manual model for after API key is entered
                self.app._pending_model_selection = {"model": manual_model, "provider": provider, "api_key_env": api_key_env}
                debug_log.debug(f"Showing API key prompt for manual model", api_key_env=api_key_env)
            else:
                # Configure the model directly
                await self._configure_selected_model(manual_model, provider)
                debug_log.info(f"Manual model configuration completed", provider=provider, model_name=model_name)
            
            # Exit manual entry mode
            self.app.setup_active = False
            self.app.setup_data = {}
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error with manual model entry**: {str(e)}", is_user=False)
    
    async def handle_setup_input_routing(self, user_input: str) -> bool:
        """
        Handle setup input routing for model-related modes.
        
        This method should be called by the main app's _handle_setup_input method
        to route model-related setup inputs properly.
        
        Returns:
            bool: True if input was handled by model handler, False if not applicable
        """
        if not self.app.setup_active or not hasattr(self.app, 'setup_data'):
            return False
            
        mode_data = self.app.setup_data
        mode = mode_data.get('mode')
        
        if mode == 'manual_model_entry':
            # Handle manual model entry input
            await self.handle_manual_model_input(user_input)
            return True
        elif mode == 'model_config':
            # Handle model configuration input
            await self.handle_model_config_input(user_input)
            return True
        
        return False
    
    def update_welcome_message_and_footer(self) -> None:
        """Update welcome message and footer after model changes."""
        # Refresh welcome screen to show updated model information
        if hasattr(self.app, 'app_lifecycle_handler') and self.app.app_lifecycle_handler:
            self.app.app_lifecycle_handler._refresh_welcome_message()
            # Update footer and focus input
            self.app.app_lifecycle_handler._update_footer_stats()
        elif hasattr(self.app, '_refresh_welcome_message'):
            # Fallback for direct app methods
            self.app._refresh_welcome_message()
            if hasattr(self.app, '_update_footer_stats'):
                self.app._update_footer_stats()