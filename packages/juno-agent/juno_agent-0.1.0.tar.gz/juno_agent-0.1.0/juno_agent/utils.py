"""Utility functions for juno-agent."""

import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

import git
from git.exc import InvalidGitRepositoryError


class SystemStatus:
    """System status checker."""
    
    def __init__(self, workdir: Path):
        self.workdir = workdir
    
    def get_status_info(self) -> Dict[str, str]:
        """Get comprehensive system status information."""
        from .config import ConfigManager
        
        config_manager = ConfigManager(self.workdir)
        config = config_manager.load_config()
        
        git_status = self._get_git_status()
        api_key_status = "✓ Set" if config_manager.has_api_key() else "✗ Not set"
        editor = config.editor or "Not selected"
        
        return {
            "workdir": str(self.workdir),
            "git_status": git_status,
            "api_key_status": api_key_status, 
            "editor": editor,
        }
    
    def _get_git_status(self) -> str:
        """Get git repository status."""
        try:
            repo = git.Repo(self.workdir, search_parent_directories=True)
            git_root = Path(repo.git_dir).parent
            
            if git_root == self.workdir:
                return "✓ Git repository (root)"
            else:
                return f"✓ Git repository (root: {git_root})"
        except InvalidGitRepositoryError:
            return "✗ Not a git repository"
    
    def is_git_controlled(self) -> bool:
        """Check if directory is under git control."""
        try:
            git.Repo(self.workdir, search_parent_directories=True)
            return True
        except InvalidGitRepositoryError:
            return False
    
    def get_git_root(self) -> Optional[Path]:
        """Get git repository root."""
        try:
            repo = git.Repo(self.workdir, search_parent_directories=True)
            return Path(repo.git_dir).parent
        except InvalidGitRepositoryError:
            return None
    
    def is_git_root(self) -> bool:
        """Check if current directory is git root."""
        git_root = self.get_git_root()
        return git_root is not None and git_root == self.workdir


def open_browser(url: str) -> bool:
    """Open URL in default browser."""
    import webbrowser
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def run_command(command: str, cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """Run shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)