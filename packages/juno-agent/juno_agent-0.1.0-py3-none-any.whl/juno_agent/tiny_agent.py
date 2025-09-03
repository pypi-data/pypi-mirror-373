"""TinyCodeAgent integration for juno-agent."""

import asyncio
import json
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager
from .debug_logger import debug_logger


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary by examining its extension and content.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is likely binary, False otherwise
    """
    # Common binary file extensions
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',  # Images
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
        '.zip', '.tar', '.gz', '.rar', '.7z',  # Archives
        '.exe', '.dll', '.so', '.dylib',  # Executables/Libraries
        '.mp3', '.mp4', '.wav', '.avi', '.mov',  # Media
        '.bin', '.dat', '.sqlite', '.db'  # Data files
    }
    
    file_path = Path(file_path)
    
    # Check extension first
    if file_path.suffix.lower() in binary_extensions:
        return True
    
    # For small files, check if content appears to be binary
    try:
        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)  # Read first 512 bytes
                if b'\x00' in chunk:  # Null bytes typically indicate binary
                    return True
                # Check for high ratio of non-printable characters
                printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13))
                if len(chunk) > 0 and printable_chars / len(chunk) < 0.7:
                    return True
    except (IOError, OSError):
        pass
    
    return False


def get_file_info_for_binary(file_path: str) -> str:
    """
    Get informative description for binary files instead of their content.
    
    Args:
        file_path: Path to the binary file
        
    Returns:
        Description of the binary file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return f"File not found: {file_path}"
    
    try:
        stat = file_path.stat()
        size = stat.st_size
        
        # Format file size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        file_type = file_path.suffix.lower() or "unknown"
        
        return f"BINARY FILE: {file_path.name}\n" \
               f"Type: {file_type} file\n" \
               f"Size: {size_str}\n" \
               f"Path: {file_path}\n" \
               f"Note: Binary files cannot be displayed as text. Use appropriate tools for viewing this file type."
    
    except (IOError, OSError) as e:
        return f"ERROR reading file info for {file_path}: {e}"


class TinyCodeAgentChat:
    """Chat interface with TinyCodeAgent integration."""
    
    def __init__(self, config_manager: ConfigManager, debug: bool = False, console: Optional[Console] = None, ui_callback: Optional[Callable[[str, dict], None]] = None, storage_manager=None, enable_custom_instructions: bool = True):
        debug_logger.log_function_entry("TinyCodeAgentChat.__init__",
                                       debug=debug,
                                       ui_callback_available=ui_callback is not None,
                                       console_overridden=console is not None,
                                       storage_manager_available=storage_manager is not None)
        
        # DEBUG: Log storage manager details
        if storage_manager:
            print(f"[DEBUG] TinyCodeAgentChat.__init__: storage_manager provided: {type(storage_manager)}")
            print(f"[DEBUG] TinyCodeAgentChat.__init__: storage_manager session_id: {getattr(storage_manager, 'current_session_id', 'None')}")
        else:
            print(f"[DEBUG] TinyCodeAgentChat.__init__: NO storage_manager provided")
        
        self.config_manager = config_manager
        # Allow overriding the console (e.g., to suppress Rich output inside Textual)
        self.console = console or Console()
        self.conversation_history: List[Dict[str, Any]] = []
        self.agent = None  # Will be initialized when needed
        self.subagent = None  # Coding subagent for specialized tasks
        self.debug_logger = config_manager.create_debug_logger(debug=debug)  # Debug logging
        self.debug = debug  # Store debug flag
        self.ui_callback = ui_callback  # Optional UI update callback for tool tracking
        self.storage_manager = storage_manager  # Optional storage manager for conversation persistence
        self.enable_custom_instructions = enable_custom_instructions  # Whether to enable custom instructions
        
        # Debug: Log the ui_callback details
        if ui_callback:
            import asyncio
            debug_logger.log_event("tiny_code_agent_ui_callback_received",
                                 callback_id=hex(id(ui_callback)),
                                 callback_name=getattr(ui_callback, '__name__', 'unknown'),
                                 is_async=asyncio.iscoroutinefunction(ui_callback),
                                 is_method=hasattr(ui_callback, '__self__'))
        else:
            debug_logger.log_event("tiny_code_agent_no_ui_callback")
        self.log_manager = self.initialize_log_manager(config_manager.config_dir, debug)
        
        debug_logger.log_event("tiny_code_agent_chat_initialized",
                             agent_id=hex(id(self)),
                             ui_callback_id=hex(id(ui_callback)) if ui_callback else None)
    
    def _construct_model_name(self, agent_config) -> str:
        """Construct model name consistently across main agent and subagents.
        
        This method ensures that all agents (main and subagents) use the exact same
        model name construction logic to prevent model mismatches.
        
        Args:
            agent_config: Agent configuration object
            
        Returns:
            Properly formatted model name string
        """
        if agent_config.provider.lower() in agent_config.model_name.lower():
            return agent_config.model_name
        else:
            return agent_config.provider.lower() + "/" + agent_config.model_name.lower()

    def initialize_log_manager(self, config_dir: Path, debug: bool = False):
        """Initialize log manager with graceful fallback when tinyagent is not available."""
        import logging
        import sys
        import os
        
        self.config_dir = config_dir
        self.logs_dir = config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Use centralized app_run.log file in current working directory
        self.log_file = Path(os.getcwd()) / "app_run.log"
        
        try:
            # Try to use TinyAgent's LoggingManager if available
            from tinyagent.hooks.logging_manager import LoggingManager
            
            log_manager = LoggingManager(default_level=logging.INFO)
            log_manager.set_levels({
                'tinyagent.hooks.gradio_callback': logging.DEBUG,
                'tinyagent.tiny_agent': logging.DEBUG,
                'tinyagent.mcp_client': logging.INFO,
                'tinyagent.code_agent': logging.DEBUG,
            })

            # Console handler - only show DEBUG if debug flag is enabled
            console_handler = logging.StreamHandler(sys.stdout)
            # Without debug flag, suppress all logs on console (WARNING+ only)
            # With debug flag, show all DEBUG+ logs on console
            console_level = logging.DEBUG if debug else logging.WARNING
            log_manager.configure_handler(
                console_handler,
                format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=console_level
            )
            
            # File handler - append to centralized log file, always log DEBUG to file
            file_handler = logging.FileHandler(self.log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)

            log_manager.configure_handler(
                file_handler,
                format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.DEBUG
            )
            
            # Log initialization message to mark TinyAgent logging start
            logger = logging.getLogger('tinyagent.tiny_agent')
            logger.info(f"TinyAgent LogManager initialized - writing to {self.log_file}")

            return log_manager
            
        except ImportError:
            # Fallback to standard Python logging when tinyagent is not available
            log_manager = logging.getLogger('juno_agent.fallback')
            log_manager.setLevel(logging.DEBUG if debug else logging.INFO)
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_level = logging.DEBUG if debug else logging.WARNING
            console_handler.setLevel(console_level)
            
            # Create file handler
            file_handler = logging.FileHandler(self.log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # Add handlers to logger
            if not log_manager.handlers:  # Avoid duplicate handlers
                log_manager.addHandler(console_handler)
                log_manager.addHandler(file_handler)
            
            # Log fallback initialization message
            log_manager.info(f"Fallback LogManager initialized (tinyagent not available) - writing to {self.log_file}")
            
            return log_manager

    async def create_coding_subagent(self, force_new: bool = False):
        """Create a specialized coding subagent with shell tools only.
        
        Args:
            force_new: If True, always create a new subagent regardless of config
        """
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # CRITICAL FIX: Always create new subagent instances for proper session isolation
        # Each subagent call should get its own unique session and storage context
        # Disable reuse to ensure this behavior
        force_new = True  # Override to ensure unique instances
        print(f"[DEBUG] create_coding_subagent: Forcing new instance creation for proper session isolation")
            
        try:
            # Import TinyCodeAgent and callbacks
            from tinyagent import TinyCodeAgent
            from tinyagent.hooks import MessageCleanupHook
            from tinyagent.hooks import AnthropicPromptCacheCallback
            from tinyagent.hooks.token_tracker import create_token_tracker
            
            # Get API key for the configured model
            api_key = self.config_manager.get_model_api_key()
            if not api_key:
                expected_env_var = self._get_expected_env_var(agent_config.provider)
                raise ValueError(f"API key not found for subagent. Set {expected_env_var} environment variable")
            
            # Determine execution provider - same as main agent
            use_seatbelt = self._should_use_seatbelt()
            
            # CRITICAL FIX: Use consistent model name and prioritize parent's exact model
            parent_model = getattr(self.agent, 'model', None) if self.agent else None
            
            if parent_model:
                # Always use parent's exact model to ensure consistency
                model_name = parent_model
                print(f"[DEBUG] create_coding_subagent: Using parent's exact model: {model_name}")
            else:
                # Fallback to standardized construction if no parent agent
                model_name = self._construct_model_name(agent_config)
                print(f"[DEBUG] create_coding_subagent: No parent agent, using constructed model: {model_name}")
            
            subagent_params = {
                "model": model_name,
                "api_key": api_key,
                "system_prompt": self._get_subagent_system_prompt(),
                "enable_python_tool": False,  # Disabled as requested
                "enable_shell_tool": True,    # Enabled as requested
                "enable_file_tools": True,    # Enable file tools
                "enable_todo_write": True,    # Enable TodoWrite tool
                "local_execution": True,      # Same as main agent
                "temperature": agent_config.temperature,
                "default_workdir": str(self.config_manager.workdir)
            }
            
            # CRITICAL FIX: Add storage parameters if storage manager is available (each subagent gets unique session)
            if self.storage_manager:
                self.storage_manager._initialize_storage()
                if self.storage_manager.storage:
                    # Validate storage parameters before adding
                    if self.storage_manager.user_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.user_id is None when creating subagent!")
                    
                    if self.storage_manager.current_session_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.current_session_id is None when creating subagent!")
                    
                    # Create unique session ID for each subagent call (no reuse)
                    subagent_session_id = str(uuid.uuid4()) + "_subagent"
                    # Use main agent's user_id with _subagent postfix for proper isolation
                    subagent_user_id = self.storage_manager.user_id + "_subagent"
                    
                    storage_params = {
                        "storage": self.storage_manager.storage,
                        "session_id": subagent_session_id,
                        "user_id": subagent_user_id
                    }
                    
                    # Additional validation
                    assert storage_params["user_id"] is not None, "user_id must not be None"
                    assert storage_params["session_id"] is not None, "session_id must not be None"
                    
                    subagent_params.update(storage_params)
                    print(f"[DEBUG] create_coding_subagent: Added storage params - session_id: {subagent_session_id}, user_id: {subagent_user_id}")
            
            # Configure execution provider - same as main agent
            if use_seatbelt:
                subagent_params["provider"] = "seatbelt"
            else:
                subagent_params["provider"] = "modal"
                subagent_params["local_execution"] = True
            
            # Add max_tokens if specified
            if agent_config.max_tokens:
                subagent_params["max_tokens"] = agent_config.max_tokens
            
            # Add custom base URL if specified
            if agent_config.custom_base_url:
                subagent_params["base_url"] = agent_config.custom_base_url
            
            # Add custom parameters
            if agent_config.custom_params:
                subagent_params.update(agent_config.custom_params)
            
            # Add model_kwargs from configuration (inherit from main agent)
            if agent_config.model_kwargs:
                if "model_kwargs" not in subagent_params:
                    subagent_params["model_kwargs"] = {}
                subagent_params["model_kwargs"].update(agent_config.model_kwargs)
                print(f"[DEBUG] create_coding_subagent: Added model_kwargs from config: {agent_config.model_kwargs}")
            
            # Initialize coding subagent
            new_subagent = TinyCodeAgent(**subagent_params)
            
            # CRITICAL FIX: Validate model name propagation after creation
            parent_model = getattr(self.agent, 'model', None) if self.agent else None
            subagent_model = getattr(new_subagent, 'model', None)
            print(f"[DEBUG] create_coding_subagent: After creation - Parent: {parent_model}, Subagent: {subagent_model}")
            if parent_model and subagent_model != parent_model:
                print(f"[ERROR] create_coding_subagent: CRITICAL MODEL MISMATCH! Expected: {parent_model}, Got: {subagent_model}")
                print(f"[ERROR] create_coding_subagent: This indicates a regression in model propagation logic!")
                raise ValueError(f"Subagent model mismatch: expected {parent_model}, got {subagent_model}")
            else:
                print(f"[DEBUG] create_coding_subagent: Model propagation successful ✅")
            
            # CRITICAL FIX: Add all parent callbacks to subagent (properly propagated from parent)
            # Extract and propagate callbacks from parent agent if available
            message_cleanup_callback = None
            anthropic_cache_callback = None
            
            if self.agent and hasattr(self.agent, 'callbacks'):
                for callback in self.agent.callbacks:
                    callback_type = type(callback).__name__
                    
                    # Find MessageCleanupHook in parent callbacks
                    if callback_type == 'MessageCleanupHook':
                        message_cleanup_callback = callback
                        print(f"[DEBUG] create_coding_subagent: Found parent MessageCleanupHook callback")
                    
                    # Find AnthropicPromptCacheCallback in parent callbacks
                    elif callback_type == 'AnthropicPromptCacheCallback':
                        anthropic_cache_callback = callback
                        print(f"[DEBUG] create_coding_subagent: Found parent AnthropicPromptCacheCallback callback")
            
            # Add parent callbacks if found, otherwise create new ones
            if message_cleanup_callback:
                new_subagent.add_callback(message_cleanup_callback)
                print(f"[DEBUG] create_coding_subagent: Added parent MessageCleanupHook to subagent")
            else:
                new_subagent.add_callback(MessageCleanupHook())
                print(f"[DEBUG] create_coding_subagent: Added new MessageCleanupHook to subagent (parent not found)")
                
            if anthropic_cache_callback:
                new_subagent.add_callback(anthropic_cache_callback)
                print(f"[DEBUG] create_coding_subagent: Added parent AnthropicPromptCacheCallback to subagent")
            else:
                new_subagent.add_callback(AnthropicPromptCacheCallback())
                print(f"[DEBUG] create_coding_subagent: Added new AnthropicPromptCacheCallback to subagent (parent not found)")
            
            # CRITICAL FIX: Add UI callback for tool usage tracking if available (inherits from main agent)
            if self.ui_callback:
                try:
                    from .fancy_ui.callbacks.textual_tool_callback import create_textual_tool_callback
                    subagent_tool_callback = create_textual_tool_callback(
                        logger=self.debug_logger,
                        ui_update_callback=self.ui_callback,  # Same UI callback as main agent
                        max_events=100,
                        agent_level=1,  # Subagent is level 1 (main agent is level 0)
                        agent_id="direct_subagent",
                        parent_id="main_agent",
                        display_name="Direct Coding Subagent"
                    )
                    new_subagent.add_callback(subagent_tool_callback)
                    print(f"[DEBUG] create_coding_subagent: Added UI tool tracking callback to subagent")
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ Could not add UI callback to subagent: {e}[/yellow]")
                    print(f"[DEBUG] create_coding_subagent: Failed to add UI callback: {e}")
            
            # CRITICAL FIX: Add TokenTracker for cost monitoring (inherits from main agent)
            try:
                # Get parent tracker from main agent if available
                parent_tracker = None
                if self.agent and hasattr(self.agent, 'callbacks'):
                    for callback in self.agent.callbacks:
                        if hasattr(callback, 'get_total_usage'):  # TokenTracker has this method
                            parent_tracker = callback
                            break
                
                # Create child tracker for subagent
                if parent_tracker:
                    child_tracker = create_token_tracker(
                        name="direct_subagent",
                        parent_tracker=parent_tracker,
                        enable_detailed_logging=True
                    )
                    new_subagent.add_callback(child_tracker)
                    print(f"[DEBUG] create_coding_subagent: Added child token tracker to subagent (linked to parent)")
                else:
                    # Create standalone tracker if no parent available
                    standalone_tracker = create_token_tracker(
                        name="direct_subagent",
                        enable_detailed_logging=True
                    )
                    new_subagent.add_callback(standalone_tracker)
                    print(f"[DEBUG] create_coding_subagent: Added standalone token tracker to subagent")
                    
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not add token tracking to subagent: {e}[/yellow]")
                print(f"[DEBUG] create_coding_subagent: Failed to add token tracker: {e}")
            
            # CRITICAL FIX: Never store subagent for reuse - always create fresh instances
            # This ensures each subagent call gets unique session and storage context
            self.console.print(f"[dim]🔧 Fresh coding subagent created with unique session and storage isolation[/dim]")
                
            # Log completion of callback setup
            callback_count = len(new_subagent.callbacks) if hasattr(new_subagent, 'callbacks') else 0
            print(f"[DEBUG] create_coding_subagent: Subagent created with {callback_count} callbacks")
            print(f"[DEBUG] create_coding_subagent: MessageCleanupHook: {'✅ From parent' if message_cleanup_callback else '🆕 New instance'}")
            print(f"[DEBUG] create_coding_subagent: AnthropicPromptCacheCallback: {'✅ From parent' if anthropic_cache_callback else '🆕 New instance'}")
            self.console.print(f"[dim]💾 Subagent storage: {'✅ Enabled' if self.storage_manager else '❌ No storage'}[/dim]")
            self.console.print(f"[dim]🛠️ Subagent UI tracking: {'✅ Enabled' if self.ui_callback else '❌ No UI callback'}[/dim]")
            self.console.print(f"[dim]💰 Subagent cost tracking: {'✅ Enabled' if callback_count > 2 else '❌ Basic only'}[/dim]")
            self.console.print(f"[dim]🔗 Callback propagation: {'✅ MessageCleanup + AnthropicCache' if message_cleanup_callback and anthropic_cache_callback else '⚠️ Partial or missing'}[/dim]")
            
            return new_subagent
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not create coding subagent: {e}[/yellow]")
            print(f"[DEBUG] create_coding_subagent: Exception details: {e}")
            import traceback
            print(f"[DEBUG] create_coding_subagent: Traceback: {traceback.format_exc()}")
            return None
    
    def _get_subagent_system_prompt(self) -> str:
        """Get specialized system prompt for the coding subagent."""
        config = self.config_manager.load_config()
        
        # Build context about the project
        project_info = []
        if config.project_description:
            project_info.append(f"Project: {config.project_description}")
        
        if config.libraries:
            project_info.append(f"Dependencies: {', '.join(config.libraries[:10])}")
            if len(config.libraries) > 10:
                project_info.append(f"... and {len(config.libraries) - 10} more")
        
        if config.editor:
            project_info.append(f"Editor: {config.editor}")
        
        project_context = "\n".join(project_info) if project_info else "No project context available"
        
        return f"""You are a specialized coding assistant focused on development tasks and shell operations.

Current project context:
{project_context}

Working directory: {self.config_manager.workdir}

You are a subagent with access to the following tools:
- Shell commands for project management and system operations
- File tools: read_file, write_file, update_file, glob_tool, grep_tool for safe file operations
- TodoWrite tool for task management and tracking workflows

IMPORTANT: When working with files, be aware of binary files (images, executables, etc.):
- Binary files like PNG, JPG, PDF, etc. cannot be read as text and will cause UnicodeDecodeError
- Before reading files, consider if they might be binary based on their extension
- For binary files, use shell commands like 'file' to get information or 'ls -la' to check size
- Never try to read binary files with read_file tool - inform user about the file type instead

Your specialties include:
- File system operations (create, read, modify, organize files using file tools with proper binary handling)
- Git operations and version control
- Build and deployment scripts
- Package management (npm, pip, etc.)
- Process management and system monitoring
- Development environment setup
- Testing and validation through shell commands
- Task organization and workflow management

You can help with:
- Project structure analysis and organization
- Dependency management and installation
- Build processes and CI/CD tasks
- File operations and batch processing (with binary file awareness)
- Environment configuration
- Code linting and formatting via command-line tools
- Complex task planning and execution

Always be helpful, accurate, and safe with tool usage. Use the TodoWrite tool to break down complex tasks. Focus on development workflow improvements and project management tasks.
"""
    

    async def initialize_agent(self):
        """Initialize TinyCodeAgent if not already done."""
        if self.agent is not None:
            return
        
        # Validate model configuration before initializing
        if not self.config_manager.is_model_configured():
            status = self.config_manager.validate_model_setup()
            self.console.print("[bold yellow]⚠️ Model Configuration Required[/bold yellow]")
            self.console.print(f"Current model: {status['model_name']} ({status['provider']})")
            self.console.print(f"API key: {'Available' if status['has_api_key'] else 'Missing'}")
            self.console.print("\nUse '/model' command to configure your AI model and API key")
            return
            
        try:
            # Import TinyCodeAgent (this requires the tinyagent package)
            from tinyagent import TinyCodeAgent
            from tinyagent.hooks import MessageCleanupHook
            from tinyagent.hooks.token_tracker import TokenTracker, create_token_tracker
            from tinyagent.tools import create_coding_subagent
            from tinyagent import SubagentConfig
            from tinyagent.hooks import AnthropicPromptCacheCallback


            
            import tinyagent
            
            # Check tinyagent version for compatibility
            tinyagent_version = getattr(tinyagent, '__version__', 'unknown')
            if tinyagent_version != 'unknown':
                self.console.print(f"[dim]🔍 TinyAgent version: {tinyagent_version}[/dim]")
            
            # Get configuration
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            
            # Get API key for the configured model
            api_key = self.config_manager.get_model_api_key()
            if not api_key:
                expected_env_var = self._get_expected_env_var(agent_config.provider)
                raise ValueError(f"API key not found. Set {expected_env_var} environment variable or use /model command")
            
            # Determine execution provider based on system and user preference
            use_seatbelt = self._should_use_seatbelt()
            
            # Prepare TinyCodeAgent parameters
            model_name = self._construct_model_name(agent_config)
            tiny_agent_params = {
                "model": model_name,
                "api_key": api_key,
                # Pass the base system prompt - TinyCodeAgent will apply custom instructions to it
                "system_prompt": self._get_system_prompt(),
                "enable_python_tool": False,
                "enable_shell_tool": True,
                "enable_file_tools": True,  # Enable file tools (read_file, write_file, update_file, glob_tool, grep_tool)
                "enable_todo_write": True,  # Enable TodoWrite tool for task management
                "local_execution": True,  # Execute locally for safety
                "temperature": agent_config.temperature,
                "default_workdir": str(self.config_manager.workdir),  # Set working directory
                "log_manager": self.log_manager,
                # TinyCodeAgent has its own custom instruction handling
                # Pass configuration for TinyCodeAgent's custom instruction system  
                "enable_custom_instructions": self.enable_custom_instructions,  # TinyCodeAgent uses plural form
                # Pass absolute path to AGENTS.md if custom instructions are enabled
                "custom_instructions": str(self.config_manager.workdir / "AGENTS.md") if self.enable_custom_instructions else None,
                "custom_instruction_config": {
                    "auto_detect_agents_md": True,  # Enable auto-detection
                    "execution_directory": str(self.config_manager.workdir),  # Where to look for AGENTS.md
                    "custom_filename": "AGENTS.md"  # Filename to look for
                } if self.enable_custom_instructions else {}
            }
            
            # Add storage parameters if storage manager is available
            if self.storage_manager:
                self.storage_manager._initialize_storage()
                if self.storage_manager.storage:
                    # CRITICAL: Validate user_id before passing to TinyAgent
                    if self.storage_manager.user_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.user_id is None when initializing TinyAgent!")
                    
                    if self.storage_manager.current_session_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.current_session_id is None when initializing TinyAgent!")
                    
                    storage_params = {
                        "storage": self.storage_manager.storage,
                        "session_id": self.storage_manager.current_session_id,
                        "user_id": self.storage_manager.user_id
                    }
                    
                    # Additional validation
                    assert storage_params["user_id"] is not None, "user_id must not be None"
                    assert storage_params["session_id"] is not None, "session_id must not be None"
                    
                    tiny_agent_params.update(storage_params)
                    print(f"[DEBUG] initialize_agent: Added storage params - session_id: {self.storage_manager.current_session_id}, user_id: {self.storage_manager.user_id}")
                    print(f"[DEBUG] initialize_agent: Storage params validation passed!")
            
            # Configure execution provider
            if use_seatbelt:
                tiny_agent_params["provider"] = "seatbelt"
                self.console.print("[dim]🔒 Using macOS seatbelt sandbox for secure execution[/dim]")
            else:
                tiny_agent_params["provider"] = "modal"
                tiny_agent_params["local_execution"] = True
                self.console.print("[dim]💻 Using local execution mode[/dim]")
            
            # Add max_tokens if specified
            if agent_config.max_tokens:
                tiny_agent_params["max_tokens"] = agent_config.max_tokens
            
            # Add custom base URL if specified
            if agent_config.custom_base_url:
                tiny_agent_params["base_url"] = agent_config.custom_base_url
            
            # Add custom parameters
            if agent_config.custom_params:
                tiny_agent_params.update(agent_config.custom_params)
            
            # Add model_kwargs from configuration
            if agent_config.model_kwargs:
                if "model_kwargs" not in tiny_agent_params:
                    tiny_agent_params["model_kwargs"] = {}
                tiny_agent_params["model_kwargs"].update(agent_config.model_kwargs)
                print(f"[DEBUG] initialize_agent: Added model_kwargs from config: {agent_config.model_kwargs}")
            
            # Initialize TinyCodeAgent with configured model
            self.agent = TinyCodeAgent(**tiny_agent_params)
            
            # CRITICAL: Initialize the agent to load any existing session from storage
            # This is essential for loading previous conversations when session_id and user_id are provided
            await self.agent.init_async()
            
            # Debug logging for session initialization
            agent_session_id = getattr(self.agent, 'session_id', 'None')
            agent_user_id = getattr(self.agent, 'user_id', 'None')
            agent_messages = []
            
            # Try to get message count from the agent
            try:
                if hasattr(self.agent, 'messages') and self.agent.messages:
                    agent_messages = self.agent.messages
                elif hasattr(self.agent, 'conversation') and hasattr(self.agent.conversation, 'messages'):
                    agent_messages = self.agent.conversation.messages
                elif hasattr(self.agent, '_conversation') and hasattr(self.agent._conversation, 'messages'):
                    agent_messages = self.agent._conversation.messages
                
                message_count = len(agent_messages) if agent_messages else 0
            except Exception as e:
                message_count = -1  # Indicates error getting count
                print(f"[DEBUG] initialize_agent: Could not get message count: {e}")
            
            # Log comprehensive initialization details
            self.debug_logger.info("agent_initialized", 
                                 agent_session_id=agent_session_id,
                                 agent_user_id=agent_user_id, 
                                 message_count=message_count,
                                 storage_session_id=self.storage_manager.current_session_id if self.storage_manager else 'None',
                                 storage_user_id=self.storage_manager.user_id if self.storage_manager else 'None',
                                 agent_type=type(self.agent).__name__,
                                 agent_id=hex(id(self.agent)))
            
            print(f"[DEBUG] initialize_agent: Agent initialized - session_id={agent_session_id}, user_id={agent_user_id}, messages={message_count}")
            
            # Additional validation logging
            if self.storage_manager:
                session_match = agent_session_id == self.storage_manager.current_session_id
                user_match = agent_user_id == self.storage_manager.user_id
                self.debug_logger.info("agent_session_validation",
                                     session_id_match=session_match,
                                     user_id_match=user_match,
                                     expected_session_id=self.storage_manager.current_session_id,
                                     expected_user_id=self.storage_manager.user_id,
                                     actual_session_id=agent_session_id,
                                     actual_user_id=agent_user_id)
            
            self.agent.add_callback(MessageCleanupHook())
            parent_tracker = None
            # Add cache callback for Anthropic models, to cache prompts
            self.agent.add_callback(AnthropicPromptCacheCallback())
            
            # CRITICAL: Validate that TinyAgent received the user_id correctly
            if self.storage_manager:
                agent_user_id = getattr(self.agent, 'user_id', None)
                agent_session_id = getattr(self.agent, 'session_id', None)
                
                print(f"[DEBUG] initialize_agent: TinyAgent created - user_id: {agent_user_id}, session_id: {agent_session_id}")
                
                if agent_user_id != self.storage_manager.user_id:
                    print(f"[WARNING] initialize_agent: Agent user_id mismatch! Expected: {self.storage_manager.user_id}, Got: {agent_user_id}")
                
                if agent_user_id is None:
                    print(f"[ERROR] initialize_agent: CRITICAL - Agent user_id is None!")
                else:
                    print(f"[DEBUG] initialize_agent: Agent user_id validation passed: {agent_user_id}")
            
            # Check storage integration
            if self.storage_manager and hasattr(self.agent, 'storage') and self.agent.storage:
                print(f"[DEBUG] initialize_agent: Storage integrated successfully: {type(self.agent.storage)}")
                self.console.print("[dim]💾 Conversation storage enabled[/dim]")
            elif self.storage_manager:
                print(f"[DEBUG] initialize_agent: Storage manager available but not attached to agent")
                self.console.print("[yellow]⚠️ Storage not fully integrated[/yellow]")
            else:
                print(f"[DEBUG] initialize_agent: No storage manager available")
            
            # Add TextualToolCallback for UI tool usage tracking
            debug_logger.log_event("creating_textual_tool_callback",
                                 agent_id=hex(id(self.agent)),
                                 ui_callback_available=self.ui_callback is not None)
            main_tool_callback = None  # Store for subagent hierarchy
            try:
                from .fancy_ui.callbacks.textual_tool_callback import create_textual_tool_callback
                main_tool_callback = create_textual_tool_callback(
                    logger=self.debug_logger,
                    ui_update_callback=self.ui_callback,
                    max_events=100,
                    agent_level=0,  # Main agent is level 0
                    agent_id="main_agent",
                    display_name="Main Agent"
                )
                debug_logger.log_event("textual_tool_callback_created",
                                     callback_id=hex(id(main_tool_callback)),
                                     ui_callback_id=hex(id(self.ui_callback)) if self.ui_callback else None,
                                     agent_level=0,
                                     agent_id="main_agent")
                
                self.agent.add_callback(main_tool_callback)
                debug_logger.log_event("textual_tool_callback_added_to_agent",
                                     agent_id=hex(id(self.agent)),
                                     callback_id=hex(id(main_tool_callback)),
                                     total_callbacks=len(self.agent.callbacks))
                
                self.console.print("[dim]🛠️ Tool usage tracking enabled for main agent[/dim]")
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not enable tool usage tracking: {e}[/yellow]")
                self.debug_logger.error("Failed to create tool usage callback", error=str(e))
                debug_logger.log_error("textual_tool_callback_creation_failed", e,
                                     ui_callback_available=self.ui_callback is not None)
            # Add TokenTracker for cost monitoring
            self.debug_logger.info("Initializing parent token tracker for main agent")
            try:
                parent_tracker = create_token_tracker(
                    name="main_agent",
                    enable_detailed_logging=True
                )
                self.agent.add_callback(parent_tracker)
                self.console.print("[dim]💰 Cost tracking enabled with TokenTracker[/dim]")
                self.debug_logger.info("Parent token tracker successfully created and added to main agent", 
                                     tracker_type=type(parent_tracker).__name__, 
                                     tracker_id=id(parent_tracker))
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not enable cost tracking: {e}[/yellow]")
                self.debug_logger.error("Failed to create parent token tracker", error=str(e))
                parent_tracker = None
            # Create and add coding subagent tool using TinyCodeAgent.as_tool()
            
            try:
                from textwrap import dedent
                
                
                # Create child tracker (for subagent) - only if parent tracker was created successfully
                child_tracker = None
                self.debug_logger.info("Attempting to create child token tracker for subagent", 
                                     parent_available=parent_tracker is not None)
                if parent_tracker is not None:
                    try:
                        child_tracker = create_token_tracker(
                            name="subagent",
                            parent_tracker=parent_tracker,  # Link to parent
                            enable_detailed_logging=True
                        )
                        self.debug_logger.info("Child token tracker successfully created", 
                                             tracker_type=type(child_tracker).__name__, 
                                             tracker_id=id(child_tracker),
                                             parent_id=id(parent_tracker))
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Could not create child token tracker: {e}[/yellow]")
                        self.debug_logger.error("Failed to create child token tracker", error=str(e), parent_id=id(parent_tracker))
                        child_tracker = None
                else:
                    self.debug_logger.warning("Skipping child token tracker creation - no parent tracker available")
                
                coding_tool_description = dedent("""
                        Launch a new agent with empty history that has access to the following tools: Bash, Apply Patch.
                        
                        Agent doesn't know anything about the main agent, and anything it needs to know should be provided in the prompt.
                        Launch Agent to give it a sub-task with defined scope.
                        
                        Usage notes:
                            1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
                            2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
                            3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
                            4. The agents outputs should generally be trusted
                            5. Clearly tell the agent whether you expect it to perform. Research for implementation details, extract API Doc, write code using path tool, etc, since it is not aware of the user's intent
                        
                        Args:
                        - prompt: str: Detailed and concise prompt for the sub-agent task. It should include every details and requirement for the task.
                        - absolute_workdir: str: The absolute path to the workdir of the sub-agent.
                        - description: str: A clear, concise description of what this command does in 5-10 words. User will see the description on the UI, and help them understand what you want to achieve.
                        
                        Returns:
                        - str: The result of the task. The result is not visible to the user
                        """).strip()
                
                # Use from_parent_agent to inherit parent callbacks, then override specific settings
                parent_callbacks = list(self.agent.callbacks) if hasattr(self.agent.callbacks, '__iter__') and not isinstance(self.agent.callbacks, str) else []
                
                # IMPORTANT: Create hierarchy-aware tool callback for subagent
                subagent_tool_callback = None
                if main_tool_callback and self.ui_callback:
                    try:
                        debug_logger.log_event("creating_subagent_tool_callback",
                                             parent_callback_id=hex(id(main_tool_callback)))
                        subagent_tool_callback = create_textual_tool_callback(
                            logger=self.debug_logger,
                            ui_update_callback=self.ui_callback,  # Same UI callback
                            max_events=100,
                            agent_level=1,  # Subagent is level 1
                            agent_id="subagent_coding",
                            parent_id="main_agent",
                            display_name="Coding Subagent"
                        )
                        debug_logger.log_event("subagent_tool_callback_created",
                                             callback_id=hex(id(subagent_tool_callback)),
                                             parent_id="main_agent",
                                             agent_level=1)
                        self.console.print("[dim]🛠️ Tool usage tracking enabled for subagent (with hierarchy)[/dim]")
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Could not create subagent tool callback: {e}[/yellow]")
                        debug_logger.log_error("subagent_tool_callback_creation_failed", e)
                
                # Build subagent callbacks list - include essential parent callbacks
                subagent_callbacks = []
                
                # CRITICAL FIX: Add MessageCleanupHook and AnthropicPromptCacheCallback from parent
                message_cleanup_callback = None
                anthropic_cache_callback = None
                
                # Extract essential callbacks from parent
                for callback in parent_callbacks:
                    callback_type = type(callback).__name__
                    
                    # Include MessageCleanupHook from parent
                    if callback_type == 'MessageCleanupHook':
                        message_cleanup_callback = callback
                        subagent_callbacks.append(callback)
                        self.debug_logger.info("Added parent MessageCleanupHook to subagent tool callbacks")
                    
                    # Include AnthropicPromptCacheCallback from parent
                    elif callback_type == 'AnthropicPromptCacheCallback':
                        anthropic_cache_callback = callback
                        subagent_callbacks.append(callback)
                        self.debug_logger.info("Added parent AnthropicPromptCacheCallback to subagent tool callbacks")
                
                # Add new instances if parent callbacks not found
                if not message_cleanup_callback:
                    from tinyagent.hooks import MessageCleanupHook
                    subagent_callbacks.append(MessageCleanupHook())
                    self.debug_logger.info("Added new MessageCleanupHook to subagent tool callbacks (parent not found)")
                
                if not anthropic_cache_callback:
                    from tinyagent.hooks import AnthropicPromptCacheCallback
                    subagent_callbacks.append(AnthropicPromptCacheCallback())
                    self.debug_logger.info("Added new AnthropicPromptCacheCallback to subagent tool callbacks (parent not found)")
                
                # Add child-specific callbacks
                if child_tracker:
                    subagent_callbacks.append(child_tracker)
                if subagent_tool_callback:
                    subagent_callbacks.append(subagent_tool_callback)
                
                # CRITICAL FIX: Debug model propagation for SubagentConfig
                parent_model = getattr(self.agent, 'model', None) if self.agent else None
                # Use consistent model construction for fallback
                fallback_model = self._construct_model_name(agent_config)
                subagent_model = parent_model if parent_model else fallback_model
                print(f"[DEBUG] SubagentConfig: Parent model: {parent_model}, Subagent model: {subagent_model}")
                if parent_model and parent_model != subagent_model:
                    print(f"[WARNING] SubagentConfig: Model mismatch detected! Parent: {parent_model}, Subagent: {subagent_model}")
                else:
                    print(f"[DEBUG] SubagentConfig: Model consistency verified ✅")
                
                self.debug_logger.info("Creating SubagentConfig with callbacks", 
                                     parent_callbacks_count=len(parent_callbacks),
                                     child_tracker_available=child_tracker is not None,
                                     child_tracker_id=id(child_tracker) if child_tracker else None,
                                     subagent_tool_callback_available=subagent_tool_callback is not None,
                                     total_subagent_callbacks=len(subagent_callbacks),
                                     has_message_cleanup=message_cleanup_callback is not None,
                                     has_anthropic_cache=anthropic_cache_callback is not None,
                                     parent_model=parent_model,
                                     subagent_model=subagent_model)
                
                # CRITICAL FIX: Add storage parameters for SubagentConfig
                subagent_kwargs = {
                    "parent_agent": self.agent,
                    "model": subagent_model,
                    "api_key": api_key,
                    "system_prompt": self._get_subagent_system_prompt(),
                    "enable_python_tool": False,
                    "enable_shell_tool": True,
                    "enable_file_tools": True,  # Enable file tools for subagent
                    "enable_todo_write": True,  # Enable TodoWrite tool for subagent
                    "local_execution": tiny_agent_params["local_execution"],
                    "provider": tiny_agent_params["provider"],
                    "temperature": agent_config.temperature,
                    "default_workdir": str(self.config_manager.workdir),
                    "callbacks": subagent_callbacks,
                    "inherit_parent_hooks": False  # Don't inherit parent hooks to avoid duplication
                }
                
                # Add storage parameters to subagent_kwargs if available
                if self.storage_manager and self.storage_manager.storage:
                    # Create unique session ID for each SubagentConfig call
                    subagent_session_id = str(uuid.uuid4()) + "_subagent_tool"
                    subagent_user_id = self.storage_manager.user_id + "_subagent"
                    
                    subagent_kwargs.update({
                        "storage": self.storage_manager.storage,
                        "session_id": subagent_session_id,
                        "user_id": subagent_user_id
                    })
                    print(f"[DEBUG] SubagentConfig: Added storage - session_id: {subagent_session_id}, user_id: {subagent_user_id}")
                
                # Add model_kwargs from configuration (inherit from main agent)
                if agent_config.model_kwargs:
                    if "model_kwargs" not in subagent_kwargs:
                        subagent_kwargs["model_kwargs"] = {}
                    subagent_kwargs["model_kwargs"].update(agent_config.model_kwargs)
                    print(f"[DEBUG] SubagentConfig: Added model_kwargs from config: {agent_config.model_kwargs}")
                
                subagent_config = SubagentConfig.from_parent_agent(**subagent_kwargs)
                
                self.debug_logger.debug("SubagentConfig created successfully", 
                                      config_callbacks=len(subagent_config.callbacks) if hasattr(subagent_config, 'callbacks') else 'unknown')


                # Create the coding subagent tool
                self.debug_logger.info("Creating coding subagent tool with callbacks")
                
                # Log the config being passed to subagent
                agent_kwargs = subagent_config.to_agent_kwargs()
                self.debug_logger.debug("Subagent config kwargs", 
                                      kwargs_keys=list(agent_kwargs.keys()),
                                      has_callbacks=('callbacks' in agent_kwargs),
                                      callback_count=len(agent_kwargs.get('callbacks', [])))
                
                # DEBUG: Log each callback in detail
                if 'callbacks' in agent_kwargs:
                    for i, cb in enumerate(agent_kwargs['callbacks']):
                        cb_type = type(cb).__name__
                        cb_id = hex(id(cb))
                        self.debug_logger.debug(f"Callback[{i}]: {cb_type} @ {cb_id}")
                        debug_logger.log_event("subagent_callback_detail",
                                             index=i,
                                             callback_type=cb_type,
                                             callback_id=cb_id,
                                             is_textual_tool=cb_type == "TextualToolCallback",
                                             is_token_tracker=cb_type == "TokenTracker")
                
                # CRITICAL: Manually ensure callbacks are included if missing
                if 'callbacks' not in agent_kwargs:
                    self.debug_logger.warning("CRITICAL: callbacks missing from agent_kwargs, manually adding")
                    agent_kwargs['callbacks'] = subagent_callbacks
                    self.debug_logger.debug("Updated agent_kwargs", 
                                          has_callbacks_now=True,
                                          callback_count_now=len(agent_kwargs['callbacks']))
                
                # DEBUG: Log what we're passing to create_coding_subagent
                debug_logger.log_event("calling_create_coding_subagent",
                                     name='subAgent',
                                     has_callbacks='callbacks' in agent_kwargs,
                                     callback_count=len(agent_kwargs.get('callbacks', [])),
                                     kwargs_keys=list(agent_kwargs.keys()))
                
                coding_subagent_tool = create_coding_subagent(
                    name='subAgent',
                    description=coding_tool_description,
                    **agent_kwargs  # Clean, validated parameters
                )

                if coding_subagent_tool:
                    # Add the subagent tool to the main agent
                    self.agent.add_tool(coding_subagent_tool)
                    
                    # CRITICAL FIX: Validate SubagentConfig model propagation (debugging)
                    print(f"[DEBUG] SubagentConfig tool created: Model validation complete")
                    if hasattr(coding_subagent_tool, '_config') and hasattr(coding_subagent_tool._config, 'model'):
                        tool_model = coding_subagent_tool._config.model
                        print(f"[DEBUG] SubagentConfig tool model: {tool_model}")
                        if parent_model and tool_model != parent_model:
                            print(f"[ERROR] SubagentConfig tool: CRITICAL MODEL MISMATCH! Expected: {parent_model}, Got: {tool_model}")
                        else:
                            print(f"[DEBUG] SubagentConfig tool: Model consistency verified ✅")
                    
                    self.debug_logger.info("Coding subagent tool successfully added to main agent")
                    
                    # CRITICAL FIX: Always create fresh subagent tools for session isolation
                    self.console.print("[dim]🔧 Fresh coding subagent tool added to main agent (unique session per call)[/dim]")
                    
                    # Add debugging info about token tracking
                    if child_tracker:
                        self.console.print("[dim]💰 Subagent token tracking configured with dedicated child tracker[/dim]")
                        self.debug_logger.info("Token tracking fully configured with dedicated child tracker", 
                                             parent_tracker_id=id(parent_tracker), 
                                             child_tracker_id=id(child_tracker),
                                             child_tracker_linked_to_parent=True)
                    elif parent_tracker:
                        self.console.print("[dim]⚠️ Parent token tracker available but child tracker failed to initialize[/dim]")
                        self.debug_logger.warning("Partial token tracking - parent only", parent_tracker_id=id(parent_tracker))
                    else:
                        self.console.print("[dim]⚠️ Token tracking not available for subagent[/dim]")
                        self.debug_logger.warning("No token tracking available for subagent")
                else:
                    self.console.print("[yellow]⚠️ Failed to create coding subagent tool[/yellow]")
                    self.debug_logger.error("Failed to create coding subagent tool")
                    
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not add coding subagent tool: {e}[/yellow]")
                import traceback
                self.console.print(f"[dim]Debug: {traceback.format_exc()}[/dim]")
            

            
            self.console.print(f"[green]✅ TinyCodeAgent initialized with {agent_config.model_name} ({agent_config.provider})![/green]")
            
        except ImportError as e:
            self.console.print(f"[red]❌ TinyAgent package not available. Install with: pip install 'tinyagent-py[all]'[/red]")
            self.console.print(f"[red]Error: {e}[/red]")
            self.agent = None
        except Exception as e:
            self.console.print(f"[red]❌ Failed to initialize TinyCodeAgent: {e}[/red]")
            self.console.print("[yellow]💡 Try using /model command to configure your AI model and API key[/yellow]")
            self.agent = None
    
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
        else:
            return f"{provider.upper()}_API_KEY"
    
    def _should_use_seatbelt(self) -> bool:
        """Determine if seatbelt provider should be used."""
        # Only available on macOS
        if platform.system() != "Darwin":
            return False
        
        try:
            # Check if TinyCodeAgent supports seatbelt
            from tinyagent import TinyCodeAgent
            if hasattr(TinyCodeAgent, 'is_seatbelt_supported'):
                return TinyCodeAgent.is_seatbelt_supported()
            else:
                # Fallback: check for sandbox-exec command
                import shutil
                return shutil.which("sandbox-exec") is not None
        except ImportError:
            return False
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for TinyCodeAgent."""
        config = self.config_manager.load_config()
        
        # Build context about the project
        project_info = []
        if config.project_description:
            project_info.append(f"Project: {config.project_description}")
        
        if config.libraries:
            project_info.append(f"Dependencies: {', '.join(config.libraries[:10])}")
            if len(config.libraries) > 10:
                project_info.append(f"... and {len(config.libraries) - 10} more")
        
        if config.editor:
            project_info.append(f"Editor: {config.editor}")
        
        project_context = "\n".join(project_info) if project_info else "No project context available"
        
        return f"""You are a helpful AI coding assistant integrated into juno-agent.

Current project context:
{project_context}

Working directory: {self.config_manager.workdir}

You have access to the following tools:
- Shell commands for project management and system operations
- File tools: read_file, write_file, update_file, glob_tool, grep_tool for safe file operations
- TodoWrite tool for task management and tracking complex workflows

IMPORTANT: When working with files, be aware of binary files (images, executables, etc.):
- Binary files like PNG, JPG, PDF, etc. cannot be read as text and will cause UnicodeDecodeError
- Before reading files, consider if they might be binary based on their extension
- For binary files, use shell commands like 'file' to get information or 'ls -la' to check size
- Never try to read binary files with read_file tool - inform user about the file type instead

You can help the user with:
- Code analysis and debugging
- File operations and project management (with proper binary file handling)
- Dependency analysis
- Documentation generation
- Testing and validation
- Task planning and organization

Always be helpful, accurate, and safe with code execution. Use the TodoWrite tool to break down complex tasks into manageable steps. Ask for clarification if needed.
You are an autonomous agent, and you take care of the task yourself, instead of advising the user to do a task, you use your tools to perform the task and deliver the result.
"""
    
    async def process_chat_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a chat message using TinyCodeAgent."""
        # Initialize agent if needed
        await self.initialize_agent()
        
        # Preprocess message to detect potential binary file issues
        processed_message = self._preprocess_message_for_binary_files(message)
        
        print(f"[DEBUG] process_chat_message: Processing message: {message[:50]}...")
        print(f"[DEBUG] process_chat_message: Agent available: {self.agent is not None}")
        if self.agent and hasattr(self.agent, 'storage'):
            print(f"[DEBUG] process_chat_message: Agent has storage: {self.agent.storage is not None}")
            if self.agent.storage:
                print(f"[DEBUG] process_chat_message: Storage type: {type(self.agent.storage)}")
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": message,
            "context": context or {}
        })
        
        if self.agent is None:
            # Fallback to simple response if agent not available
            response = await self._fallback_response(processed_message, context)
        else:
            # Use TinyCodeAgent
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                progress.add_task("🤖 Processing with TinyCodeAgent...", total=None)
                
                try:
                    # Get max_turns from config
                    config = self.config_manager.load_config()
                    max_turns = config.agent_config.max_turns
                    
                    # Log agent state before running
                    self.debug_logger.info("Running agent with message", 
                                         callback_count=len(self.agent.callbacks) if hasattr(self.agent, 'callbacks') else 0,
                                         max_turns=max_turns)
                    
                    # Log callback details
                    if hasattr(self.agent, 'callbacks'):
                        for i, callback in enumerate(self.agent.callbacks):
                            callback_type = type(callback).__name__
                            self.debug_logger.debug(f"Callback {i}: {callback_type}", 
                                                  callback_id=id(callback),
                                                  has_get_total_usage=hasattr(callback, 'get_total_usage'))
                    
                    # Run the agent with the user's message and max_turns
                    print(f"[DEBUG] process_chat_message: About to run agent with message")
                    print(f"[DEBUG] process_chat_message: Agent storage check before run: {hasattr(self.agent, 'storage') and self.agent.storage is not None}")
                    
                    response = await self.agent.run(processed_message, max_turns=max_turns)
                    
                    print(f"[DEBUG] process_chat_message: Agent run completed")
                    print(f"[DEBUG] process_chat_message: Agent storage check after run: {hasattr(self.agent, 'storage') and self.agent.storage is not None}")
                    
                    # Log agent state after running
                    self.debug_logger.info("Agent run completed", 
                                         callback_count=len(self.agent.callbacks) if hasattr(self.agent, 'callbacks') else 0)
                except UnicodeDecodeError as e:
                    # Special handling for binary file read attempts
                    response = "❌ **Binary File Error**: It looks like you tried to read a binary file (like PNG, JPG, PDF, etc.) as text.\n\n"
                    response += "**Binary files cannot be read as text** - they contain non-text data that causes encoding errors.\n\n"
                    response += "**What you can do instead:**\n"
                    response += "• Use `file filename.png` to get file type information\n"
                    response += "• Use `ls -la filename.png` to see file size and permissions\n"
                    response += "• Use appropriate viewers/editors for that file type\n"
                    response += "• For images: use image viewers or editors\n"
                    response += "• For PDFs: use PDF readers\n\n"
                    response += f"**Technical details**: {str(e)}"
                except Exception as e:
                    response = f"❌ TinyCodeAgent error: {str(e)}\nFalling back to basic response..."
                    response += "\n\n" + await self._fallback_response(message, context)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant", 
            "content": response,
            "context": context or {}
        })
        
        print(f"[DEBUG] process_chat_message: Conversation history length: {len(self.conversation_history)}")
        if self.storage_manager:
            print(f"[DEBUG] process_chat_message: Storage manager available - sessions should be auto-saved by TinyAgent")
        
        return response
    
    def _preprocess_message_for_binary_files(self, message: str) -> str:
        """
        Preprocess message to detect potential binary file references and provide warnings.
        
        Args:
            message: The user's message
            
        Returns:
            Modified message with binary file warnings if needed
        """
        import re
        from pathlib import Path
        
        # Look for file paths in the message
        # Match patterns like: filename.png, ./path/file.jpg, /absolute/path/file.pdf, etc.
        file_patterns = [
            r'\b[\w\-./\\]+\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)\b',
            r'"[^"]*\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)"',
            r"'[^']*\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)'"
        ]
        
        found_binary_files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # Clean up quotes
                clean_match = match.strip('"\'')
                if is_binary_file(clean_match):
                    found_binary_files.append(clean_match)
        
        if found_binary_files:
            warning = "\n\n⚠️ **Binary File Warning**: I detected references to binary files in your message:\n"
            for binary_file in found_binary_files[:3]:  # Show max 3 files
                warning += f"• `{binary_file}` - {Path(binary_file).suffix.upper()} file\n"
            if len(found_binary_files) > 3:
                warning += f"• ... and {len(found_binary_files) - 3} more\n"
            
            warning += "\nRemember: Binary files cannot be read as text. Use shell commands like `file` or `ls -la` to inspect them.\n"
            message += warning
        
        return message
    
    async def resume(self, additional_turns: Optional[int] = None) -> str:
        """Resume TinyAgent session with additional turns."""
        # Initialize agent if needed
        await self.initialize_agent()
        
        if self.agent is None:
            return "❌ No TinyAgent session available to resume"
        
        config = self.config_manager.load_config()
        max_turns = additional_turns or config.agent_config.max_turns
        
        try:
            # Resume the agent with additional turns
            if hasattr(self.agent, 'resume'):
                response = await self.agent.resume(max_turns=max_turns)
            else:
                # If resume method doesn't exist, just continue with a generic message
                response = await self.agent.run("Please continue with the previous task.", max_turns=max_turns)
            
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": response,
                "context": {"resumed": True, "additional_turns": max_turns}
            })
            
            return response
        except Exception as e:
            error_msg = f"❌ Failed to resume TinyAgent: {str(e)}"
            self.console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    async def _fallback_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Fallback response when TinyCodeAgent is not available."""
        _ = context  # Not used in fallback response
        message_lower = message.lower()
        
        # Code-related queries
        if any(keyword in message_lower for keyword in ["code", "function", "class", "debug", "error", "bug"]):
            return """🔧 **Code Assistance**

I'd love to help with your coding needs! However, TinyCodeAgent requires:

• OPENAI_API_KEY environment variable set
• `tinyagent` package installed (`pip install tinyagent`)

With TinyCodeAgent, I can:
• Debug and analyze your code
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Generate and test code snippets

**To enable full functionality:**
```bash
export OPENAI_API_KEY="your-api-key-here"
pip install tinyagent
```

*In the meantime, I can still help with project analysis and configuration!*"""
        
        # File operations
        elif any(keyword in message_lower for keyword in ["file", "directory", "folder", "create", "delete", "move"]):
            return """📁 **File Operations**

TinyCodeAgent can help with file operations when properly configured:

• Create, read, modify, and organize files using safe file tools
• Directory structure analysis and cleanup with glob_tool and grep_tool
• Batch file operations and project management
• Git operations and version control
• Task management with TodoWrite tool

**Setup required:**
- OPENAI_API_KEY environment variable
- `tinyagent` package installation

*Use `/scan` to analyze your current project structure!*"""
        
        # Testing and validation
        elif any(keyword in message_lower for keyword in ["test", "pytest", "unittest", "validate", "check"]):
            return """🧪 **Testing & Validation**

TinyCodeAgent can assist with testing when available:

• Run existing tests and analyze results
• Generate new test cases for your code
• Validate code quality and style with file tools
• Check for potential issues and bugs
• Organize testing workflows with TodoWrite tool

**Current project info:**
""" + self._get_project_summary()
        
        # General coding help
        else:
            return f"""🤖 **TinyCodeAgent Integration**

I received: *"{message}"*

**Current Status:**
❌ TinyCodeAgent not available (requires setup)

**What TinyCodeAgent can do:**
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Analyze and debug your code interactively
• Generate and test code snippets
• Perform automated project tasks

**Setup Instructions:**
1. Set OPENAI_API_KEY environment variable
2. Install: `pip install tinyagent`
3. Use `/tiny` command for code assistance

**Available now:**
• Project configuration via `/setup`
• Dependency analysis via `/scan`
• Editor integration via `/editor`

*What specific coding task can I help you prepare for?*"""
    
    def _get_project_summary(self) -> str:
        """Get a summary of the current project."""
        config = self.config_manager.load_config()
        
        summary_parts = []
        if config.project_description:
            summary_parts.append(f"• Project: {config.project_description}")
        
        if config.libraries:
            dep_count = len(config.libraries)
            summary_parts.append(f"• Dependencies: {dep_count} libraries detected")
        
        if config.editor:
            summary_parts.append(f"• Editor: {config.editor}")
        else:
            summary_parts.append("• Editor: Not configured")
        
        return "\n".join(summary_parts) if summary_parts else "• No project data available (run `/scan`)"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation for context."""
        return {
            "total_exchanges": len([h for h in self.conversation_history if h["role"] == "user"]),
            "last_user_message": next(
                (h["content"] for h in reversed(self.conversation_history) if h["role"] == "user"), 
                None
            ),
            "conversation_topics": self._extract_topics(),
            "session_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "agent_available": self.agent is not None
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from conversation history."""
        topics = set()
        keywords_map = {
            "coding": ["code", "function", "class", "debug", "python", "javascript"],
            "files": ["file", "directory", "folder", "create", "delete"],
            "testing": ["test", "pytest", "unittest", "validate"],
            "project": ["project", "dependencies", "scan", "analyze"],
            "setup": ["setup", "configure", "install"],
            "git": ["git", "commit", "branch", "repository"]
        }
        
        for message in self.conversation_history:
            if message["role"] == "user":
                content_lower = message["content"].lower()
                for topic, keywords in keywords_map.items():
                    if any(keyword in content_lower for keyword in keywords):
                        topics.add(topic)
        
        return list(topics)
    
    def save_conversation(self) -> None:
        """Save conversation history to file."""
        if not self.conversation_history:
            return
            
        conversation_file = self.config_manager.config_dir / "tiny_agent_conversations.json"
        
        # Load existing conversations
        conversations = []
        if conversation_file.exists():
            try:
                with open(conversation_file, 'r') as f:
                    conversations = json.load(f)
            except:
                conversations = []
        
        # Add current conversation
        conversation_data = {
            "session_id": datetime.now().isoformat(),
            "messages": self.conversation_history,
            "summary": self.get_conversation_summary()
        }
        conversations.append(conversation_data)
        
        # Keep only last 10 conversations
        conversations = conversations[-10:]
        
        # Save updated conversations (create directory if needed)
        conversation_file.parent.mkdir(parents=True, exist_ok=True)
        with open(conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def reset_conversation(self) -> None:
        """Reset/clear the conversation history."""
        self.conversation_history.clear()
        
        # Also clear agent's internal messages if agent exists
        if self.agent and hasattr(self.agent, 'messages'):
            self.agent.messages = []
        
        # Clear any cached conversation state
        if hasattr(self.agent, 'clear_conversation'):
            self.agent.clear_conversation()
    
    async def start_new_session(self) -> str:
        """Start a new conversation session with storage and properly reinitialize agent."""
        if self.storage_manager:
            # Create new session in storage
            new_session_id = self.storage_manager.new_session()
            
            # Clear current conversation
            self.reset_conversation()
            
            # CRITICAL FIX: Recreate agent with new session to ensure system prompt is preserved
            # Simply clearing messages loses the system prompt, so we need to reinitialize
            if self.agent:
                print(f"[DEBUG] start_new_session: Recreating agent with new session_id {new_session_id}")
                
                # Log debugging information about agent initialization
                self.debug_logger.info("start_new_session_initiated", 
                                     new_session_id=new_session_id,
                                     old_session_id=getattr(self.agent, 'session_id', 'None'),
                                     agent_messages_before=len(getattr(self.agent, 'messages', [])))
                
                # Use recreate_with_session_context to properly reinitialize with new session
                # This ensures the system prompt is preserved and the agent starts fresh
                success = await self.recreate_with_session_context(new_session_id, self.storage_manager.user_id)
                
                if success:
                    print(f"[DEBUG] start_new_session: Agent successfully recreated with new session")
                    
                    # Log final state
                    final_messages = len(getattr(self.agent, 'messages', []))
                    self.debug_logger.info("start_new_session_completed_success",
                                         new_session_id=new_session_id,
                                         agent_messages_after=final_messages,
                                         system_prompt_preserved=final_messages > 0)
                else:
                    print(f"[WARNING] start_new_session: Failed to recreate agent, falling back to session_id update")
                    
                    self.debug_logger.warning("start_new_session_fallback",
                                            new_session_id=new_session_id,
                                            reason="agent_recreation_failed")
                    
                    # Fallback: just update session_id if recreation fails
                    if hasattr(self.agent, 'session_id'):
                        self.agent.session_id = new_session_id
                    if hasattr(self.agent, 'messages'):
                        self.agent.messages = []
            
            # Save session metadata
            self.storage_manager.save_session_metadata({
                "started_at": datetime.now().isoformat(),
                "project_dir": str(self.config_manager.workdir)
            })
            
            return new_session_id
        else:
            # Just reset conversation if no storage
            self.reset_conversation()
            
            # For no storage case, we still need to preserve system prompt
            # The best approach is to reinitialize the agent if possible
            if self.agent:
                print(f"[DEBUG] start_new_session: Reinitializing agent (no storage)")
                try:
                    # Close and recreate agent to ensure system prompt is preserved
                    await self.agent.close()
                    self.agent = None
                    await self.initialize_agent()
                    print(f"[DEBUG] start_new_session: Agent reinitialized successfully")
                except Exception as e:
                    print(f"[ERROR] start_new_session: Failed to reinitialize agent: {e}")
                    # Fallback: just clear messages (old behavior)
                    if hasattr(self.agent, 'messages'):
                        self.agent.messages = []
            
            return "no_storage"
    
    async def load_session(self, session_id: str) -> bool:
        """Load a session using TinyAgent's native loading.
        
        Simple approach: Update session_id and call init_async().
        """
        try:
            if not self.agent:
                return False
            
            # Update session_id
            self.agent.session_id = session_id
            
            # Let TinyAgent load the session
            await self.agent.init_async()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load session: {e}")
            return False
    
    async def recreate_with_session_context(self, session_id: str, user_id: str) -> bool:
        """Recreate TinyAgent with specific session and user context.
        
        This ensures the agent loads the existing conversation from the database
        with the proper session_id and user_id combination.
        """
        try:
            print(f"[DEBUG] recreate_with_session_context: Starting recreation with session_id={session_id}, user_id={user_id}")
            
            # Log session recreation start
            self.debug_logger.info("session_recreation_started",
                                 target_session_id=session_id,
                                 target_user_id=user_id,
                                 current_agent_exists=(self.agent is not None))
            
            # Close existing agent to ensure clean state
            if self.agent:
                old_agent_session = getattr(self.agent, 'session_id', 'None')
                old_agent_user = getattr(self.agent, 'user_id', 'None')
                print(f"[DEBUG] recreate_with_session_context: Closing existing agent (session_id={old_agent_session}, user_id={old_agent_user})")
                
                self.debug_logger.info("closing_existing_agent",
                                     old_agent_session_id=old_agent_session,
                                     old_agent_user_id=old_agent_user,
                                     agent_id=hex(id(self.agent)))
                
                await self.agent.close()
                self.agent = None
            
            # Update storage manager context BEFORE creating new agent
            if self.storage_manager:
                old_session = self.storage_manager.current_session_id
                old_user = self.storage_manager.user_id
                
                # Use switch_to_session to properly update both IDs
                self.storage_manager.switch_to_session(session_id, user_id)
                
                print(f"[DEBUG] recreate_with_session_context: Storage context switched from ({old_session}, {old_user}) to ({session_id}, {user_id})")
                
                self.debug_logger.info("storage_context_switched",
                                     old_session_id=old_session,
                                     old_user_id=old_user,
                                     new_session_id=session_id,
                                     new_user_id=user_id,
                                     storage_manager_id=hex(id(self.storage_manager)))
            else:
                print(f"[ERROR] recreate_with_session_context: No storage manager available")
                self.debug_logger.error("no_storage_manager_available")
                return False
            
            # Create new agent with the updated storage context
            # initialize_agent will:
            # 1. Use storage_manager's current session_id and user_id
            # 2. Create TinyCodeAgent with storage parameters
            # 3. Call init_async() to load the session from database
            await self.initialize_agent()
            
            if not self.agent:
                print(f"[ERROR] recreate_with_session_context: Failed to initialize agent")
                return False
            
            # The agent is now fully initialized with the session loaded from the database
            print(f"[DEBUG] recreate_with_session_context: Agent successfully recreated with session loaded")
            
            # Verify the agent has the correct session context and get message count
            final_agent_session_id = getattr(self.agent, 'session_id', 'None')
            final_agent_user_id = getattr(self.agent, 'user_id', 'None')
            
            # Try to get final message count
            try:
                final_messages = []
                if hasattr(self.agent, 'messages') and self.agent.messages:
                    final_messages = self.agent.messages
                elif hasattr(self.agent, 'conversation') and hasattr(self.agent.conversation, 'messages'):
                    final_messages = self.agent.conversation.messages
                elif hasattr(self.agent, '_conversation') and hasattr(self.agent._conversation, 'messages'):
                    final_messages = self.agent._conversation.messages
                    
                final_message_count = len(final_messages) if final_messages else 0
            except Exception as e:
                final_message_count = -1
                print(f"[DEBUG] recreate_with_session_context: Could not get final message count: {e}")
            
            print(f"[DEBUG] recreate_with_session_context: Agent context verified - session_id={final_agent_session_id}, user_id={final_agent_user_id}, messages={final_message_count}")
            
            # Log successful recreation
            self.debug_logger.info("session_recreation_completed",
                                 success=True,
                                 final_agent_session_id=final_agent_session_id,
                                 final_agent_user_id=final_agent_user_id,
                                 final_message_count=final_message_count,
                                 target_session_id=session_id,
                                 target_user_id=user_id,
                                 session_id_match=(final_agent_session_id == session_id),
                                 user_id_match=(final_agent_user_id == user_id),
                                 agent_id=hex(id(self.agent)))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] recreate_with_session_context: Failed to recreate agent: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            
            # Log failed recreation
            self.debug_logger.error("session_recreation_failed",
                                  error=str(e),
                                  traceback=traceback.format_exc(),
                                  target_session_id=session_id,
                                  target_user_id=user_id)
            
            return False
    
    async def close(self):
        """Clean up resources."""
        try:
            # Close subagent instances created with as_tool()
            if hasattr(self, '_subagent_instances'):
                for subagent in self._subagent_instances:
                    try:
                        await subagent.close()
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Error closing subagent instance: {e}[/yellow]")
                self._subagent_instances = []
            
            # Close subagent first (legacy)
            if self.subagent:
                try:
                    await self.subagent.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing subagent: {e}[/yellow]")
                self.subagent = None
            
            # Close main agent
            if self.agent:
                try:
                    await self.agent.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing main agent: {e}[/yellow]")
                self.agent = None
            
            # Close storage manager
            if self.storage_manager:
                try:
                    self.storage_manager.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing storage manager: {e}[/yellow]")
                self.storage_manager = None
            
            # Clear conversation history
            self.conversation_history.clear()
            
        except Exception as e:
            self.console.print(f"[red]Error during cleanup: {e}[/red]")


class TinyCodeAgentManager:
    """Manager for TinyCodeAgent operations."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
    
    def check_requirements(self) -> Dict[str, Any]:
        """Check if TinyCodeAgent requirements are met."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Get expected API key for current model
        model_api_key = self.config_manager.get_model_api_key()
        expected_env_var = self._get_expected_env_var(agent_config.provider)
        
        status = {
            "model_api_key": bool(model_api_key),
            "tinyagent_available": False,
            "can_initialize": False,
            "missing_requirements": [],
            "current_model": agent_config.provider + "/" + agent_config.model_name,
            "current_provider": agent_config.provider,
            "expected_env_var": expected_env_var
        }
        
        # Check if tinyagent package is available
        try:
            import tinyagent  # noqa: F401
            status["tinyagent_available"] = True
        except ImportError:
            status["missing_requirements"].append("tinyagent package (pip install tinyagent)")
        
        # Check API key for current model
        if not status["model_api_key"]:
            status["missing_requirements"].append(f"{expected_env_var} environment variable or use /model command")
        
        status["can_initialize"] = status["model_api_key"] and status["tinyagent_available"]
        
        return status
    
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
        else:
            return f"{provider.upper()}_API_KEY"
    
    def display_setup_instructions(self) -> None:
        """Display setup instructions for TinyCodeAgent."""
        status = self.check_requirements()
        
        if status["can_initialize"]:
            setup_content = f"""[bold green]✅ TinyCodeAgent Ready![/bold green]

All requirements are satisfied:
• ✅ {status["expected_env_var"]} environment variable set
• ✅ tinyagent package available

**Current Configuration:**
• Model: [bold]{status["current_model"]}[/bold]
• Provider: [bold]{status["current_provider"]}[/bold]
• Temperature: {self.config_manager.load_config().agent_config.temperature}

You can now use the `/tiny` command for advanced code assistance!

**What you can do:**
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Debug and analyze code interactively
• Generate and test code snippets
• Perform automated project tasks

**Need to change models?** Use `/model` command to configure different AI providers."""
        else:
            missing_items = "\n".join(f"• ❌ {item}" for item in status["missing_requirements"])
            
            setup_content = f"""[bold yellow]🚧 TinyCodeAgent Setup Required[/bold yellow]

**Current Configuration:**
• Model: [bold]{status["current_model"]}[/bold]
• Provider: [bold]{status["current_provider"]}[/bold]

Missing requirements:
{missing_items}

**Setup Instructions:**

1. **Install TinyAgent:**
   ```bash
   pip install tinyagent
   ```

2. **Configure Model & API Key:**
   Use the `/model` command for easy setup, or set manually:
   ```bash
   export {status["expected_env_var"]}="your-api-key"
   ```

3. **Get API Keys:**
   • OpenAI: https://platform.openai.com/api-keys
   • Anthropic: https://console.anthropic.com/
   • Google: https://makersuite.google.com/app/apikey
   • Others: Check provider documentation

**Recommended for cost-effective usage:**
• OpenAI: gpt-5-mini
• Anthropic: claude-4-haiku
• Google: gemini-2.5-flash

**After setup:**
• Use `/model` command to configure your preferred AI model
• Use `/tiny` command for advanced AI coding assistance!"""
        
        setup_panel = Panel(
            setup_content,
            title="[bold]🤖 TinyCodeAgent Setup[/bold]",
            border_style="bright_blue" if status["can_initialize"] else "bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(setup_panel)
    
    def get_status_info(self) -> Dict[str, str]:
        """Get status information for display."""
        status = self.check_requirements()
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        return {
            "status": "✅ Ready" if status["can_initialize"] else "❌ Setup Required",
            "openai_key": "✅ Set" if status["model_api_key"] else "❌ Missing", 
            "tinyagent": "✅ Available" if status["tinyagent_available"] else "❌ Not installed",
            "model": f"{agent_config.model_name} ({agent_config.provider})",
            "provider": f"Local Execution (temp: {agent_config.temperature})"
        }