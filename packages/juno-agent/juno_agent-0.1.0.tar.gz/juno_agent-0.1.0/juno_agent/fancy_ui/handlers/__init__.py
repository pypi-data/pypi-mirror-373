"""Handler modules for PyWizardTUIApp functionality.

This package contains modular handlers extracted from the main app.py file
to improve maintainability and readability.

Handlers:
- setup_handler: Setup wizard and verification functionality
- model_handler: Model configuration and API key management
- chat_handler: Chat message processing and command handling
- app_lifecycle: Application lifecycle and action methods
- ui_state: UI state management and utility methods
"""

from .setup_handler import SetupHandler
from .model_handler import ModelHandler
from .chat_handler import ChatHandler
from .app_lifecycle import AppLifecycleHandler

__all__ = [
    'SetupHandler',
    'ModelHandler',
    'ChatHandler',
    'AppLifecycleHandler',
]