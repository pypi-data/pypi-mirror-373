"""Command history manager for persistent command storage."""

import json
import os
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class CommandHistoryManager:
    """Manages command history with persistent storage."""
    
    def __init__(self, max_history: int = 500):
        """Initialize command history manager.
        
        Args:
            max_history: Maximum number of commands to store
        """
        self.max_history = max_history
        self.history: List[str] = []
        self.current_index = -1
        self.original_command = ""
        self.history_file = self._get_history_file_path()
        self.load_history()
    
    def _get_history_file_path(self) -> Path:
        """Get the path to the history file based on current working directory."""
        # Store in user's home directory under .juno-agent
        home_dir = Path.home()
        config_dir = home_dir / ".juno-agent"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current working directory
        current_dir = os.getcwd()
        
        # Create a safe filename based on the directory path
        safe_filename = self._sanitize_directory_path(current_dir)
        
        return config_dir / f"command_history_{safe_filename}.json"
    
    def load_history(self) -> None:
        """Load command history from disk."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('commands', [])
                    # Ensure we don't exceed max_history
                    if len(self.history) > self.max_history:
                        self.history = self.history[-self.max_history:]
        except Exception as e:
            # If loading fails, start with empty history
            self.history = []
            print(f"Warning: Could not load command history: {e}")
    
    def save_history(self) -> None:
        """Save command history to disk."""
        try:
            data = {
                'commands': self.history,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save command history: {e}")
    
    def add_command(self, command: str) -> None:
        """Add a command to history.
        
        Args:
            command: The command to add
        """
        if not command or not command.strip():
            return
        
        command = command.strip()
        
        # Remove duplicate if it exists
        if command in self.history:
            self.history.remove(command)
        
        # Add to end of history
        self.history.append(command)
        
        # Trim history if it exceeds max size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Reset navigation state
        self.current_index = -1
        self.original_command = ""
        
        # Save to disk
        self.save_history()
    
    def _sanitize_directory_path(self, directory_path: str) -> str:
        """Convert a directory path to a safe filename.
        
        Args:
            directory_path: The directory path to sanitize
            
        Returns:
            A safe filename string
        """
        # Normalize the path (resolve . and .. components, remove extra separators)
        normalized_path = os.path.normpath(os.path.abspath(directory_path))
        
        # Replace problematic characters with underscores
        safe_chars = normalized_path.replace('\\', '_')  # Windows backslashes
        safe_chars = safe_chars.replace('/', '_')        # Unix forward slashes
        safe_chars = safe_chars.replace(':', '_')        # Windows drive letters
        safe_chars = safe_chars.replace(' ', '_')        # Spaces
        safe_chars = safe_chars.replace('<', '_')        # Invalid filename chars
        safe_chars = safe_chars.replace('>', '_')
        safe_chars = safe_chars.replace('|', '_')
        safe_chars = safe_chars.replace('*', '_')
        safe_chars = safe_chars.replace('?', '_')
        
        # Remove leading underscores (from root paths like /)
        safe_chars = safe_chars.lstrip('_')
        
        # If the result is too long, use a hash
        if len(safe_chars) > 100:
            # Use the last part of the path + hash for readability
            path_parts = Path(normalized_path).parts
            if len(path_parts) > 0:
                last_part = path_parts[-1]
                # Sanitize the last part
                last_part = last_part.replace('\\', '_').replace('/', '_').replace(':', '_').replace(' ', '_')
                # Create hash of full path
                path_hash = hashlib.md5(normalized_path.encode('utf-8')).hexdigest()[:8]
                safe_chars = f"{last_part}_{path_hash}"
            else:
                # Fallback to just hash
                safe_chars = hashlib.md5(normalized_path.encode('utf-8')).hexdigest()[:12]
        
        # Ensure we have something (fallback for edge cases)
        if not safe_chars:
            safe_chars = "default"
        
        return safe_chars
    
    def start_navigation(self, current_command: str = "") -> None:
        """Start history navigation, saving the current command.
        
        Args:
            current_command: The command currently being typed
        """
        self.original_command = current_command
        self.current_index = -1
    
    def navigate_up(self) -> Optional[str]:
        """Navigate up in history (to older commands).
        
        Returns:
            The command at the new position, or None if at the beginning
        """
        if not self.history:
            return None
        
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[-(self.current_index + 1)]
        
        return None
    
    def navigate_down(self) -> Optional[str]:
        """Navigate down in history (to newer commands).
        
        Returns:
            The command at the new position, original command, or None
        """
        if not self.history:
            return None
        
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[-(self.current_index + 1)]
        elif self.current_index == 0:
            # Return to original command
            self.current_index = -1
            return self.original_command
        
        return None
    
    def get_current_command(self) -> Optional[str]:
        """Get the current command in navigation.
        
        Returns:
            The current command or None
        """
        if self.current_index == -1:
            return self.original_command
        elif 0 <= self.current_index < len(self.history):
            return self.history[-(self.current_index + 1)]
        
        return None
    
    def clear_navigation(self) -> None:
        """Clear navigation state."""
        self.current_index = -1
        self.original_command = ""
    
    def get_history(self) -> List[str]:
        """Get the full command history.
        
        Returns:
            List of commands in chronological order (oldest first)
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear all command history."""
        self.history = []
        self.current_index = -1
        self.original_command = ""
        self.save_history()
    
    def search_history(self, query: str) -> List[str]:
        """Search command history for matching commands.
        
        Args:
            query: The search query
            
        Returns:
            List of matching commands
        """
        if not query:
            return []
        
        query_lower = query.lower()
        return [cmd for cmd in self.history if query_lower in cmd.lower()]