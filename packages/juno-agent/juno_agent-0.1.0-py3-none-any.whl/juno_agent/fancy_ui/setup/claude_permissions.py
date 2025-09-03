"""
Claude Code Permissions Configuration Service

This service configures READ ONLY access for the external_context folder
while denying write operations. It manages .claude/settings.json configuration
with proper error handling and preserves existing settings.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import os

# Configure logging
logger = logging.getLogger(__name__)


class ClaudePermissionsService:
    """Service for managing Claude Code permissions configuration."""
    
    def __init__(self):
        """Initialize the Claude permissions service."""
        self.config_dir_name = ".claude"
        self.config_file_name = "settings.json"
        
    def setup_claude_permissions(self, project_path: Path) -> bool:
        """
        Setup Claude Code permissions for the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        try:
            # Ensure project_path is a Path object
            if isinstance(project_path, str):
                project_path = Path(project_path)
                
            project_path = project_path.resolve()
            
            if not project_path.exists():
                logger.error(f"Project path does not exist: {project_path}")
                return False
                
            logger.info(f"Setting up Claude permissions for project: {project_path}")
            
            # Create .claude directory if it doesn't exist
            config_dir = project_path / self.config_dir_name
            config_dir.mkdir(exist_ok=True)
            
            # Path to settings.json
            config_path = config_dir / self.config_file_name
            
            # Get existing configuration
            existing_config = self.get_existing_config(config_path)
            
            # Create new permissions configuration
            new_permissions = self._create_external_context_permissions(project_path)
            
            # Merge with existing configuration
            final_config = self.merge_permissions(existing_config, new_permissions)
            
            # Write configuration
            success = self.write_config(config_path, final_config)
            
            if success:
                logger.info(f"Successfully configured Claude permissions at: {config_path}")
                self._log_configuration_summary(final_config)
            else:
                logger.error("Failed to write Claude permissions configuration")
                
            return success
            
        except Exception as e:
            logger.error(f"Error setting up Claude permissions: {e}")
            return False
    
    def get_existing_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Get existing configuration from settings.json.
        
        Args:
            config_path: Path to the settings.json file
            
        Returns:
            dict: Existing configuration or empty dict if none exists
        """
        try:
            if not config_path.exists():
                logger.info(f"No existing configuration found at: {config_path}")
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            logger.info(f"Loaded existing configuration from: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in existing config file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error reading existing config: {e}")
            return {}
    
    def merge_permissions(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new permissions with existing configuration.
        
        Args:
            existing: Existing configuration dictionary
            new: New permissions configuration
            
        Returns:
            dict: Merged configuration
        """
        try:
            # Start with existing configuration
            merged = existing.copy()
            
            # Ensure permissions section exists
            if "permissions" not in merged:
                merged["permissions"] = {}
            
            # Merge each permission type
            for permission_type in ["allow", "deny", "ask"]:
                if permission_type in new.get("permissions", {}):
                    existing_perms = set(merged["permissions"].get(permission_type, []))
                    new_perms = set(new["permissions"][permission_type])
                    
                    # Combine and deduplicate
                    combined_perms = list(existing_perms | new_perms)
                    merged["permissions"][permission_type] = sorted(combined_perms)
            
            # Merge other top-level keys from new config
            for key, value in new.items():
                if key != "permissions":
                    merged[key] = value
            
            logger.info("Successfully merged permissions configuration")
            return merged
            
        except Exception as e:
            logger.error(f"Error merging permissions: {e}")
            return existing
    
    def write_config(self, config_path: Path, config: Dict[str, Any]) -> bool:
        """
        Write configuration to settings.json file.
        
        Args:
            config_path: Path to write the configuration
            config: Configuration dictionary to write
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration with proper formatting
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully wrote configuration to: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing configuration: {e}")
            return False
    
    def _create_external_context_permissions(self, project_path: Path) -> Dict[str, Any]:
        """
        Create permissions configuration for external_context folder.
        
        Args:
            project_path: Project root path
            
        Returns:
            dict: Permissions configuration
        """
        # Calculate relative and absolute paths for external_context
        external_context_rel = "external_context"
        external_context_abs = (project_path / "external_context").resolve()
        
        # Create permission patterns for both relative and absolute paths
        read_patterns = [
            f"Read({external_context_rel}/**)",
            f"Read({external_context_abs}/**)",
        ]
        
        # Deny patterns for write operations
        deny_patterns = [
            f"Write({external_context_rel}/**)",
            f"Write({external_context_abs}/**)",
            f"Edit({external_context_rel}/**)",
            f"Edit({external_context_abs}/**)",
            f"MultiEdit({external_context_rel}/**)",
            f"MultiEdit({external_context_abs}/**)",
        ]
        
        config = {
            "permissions": {
                "allow": read_patterns,
                "deny": deny_patterns
            }
        }
        
        logger.info(f"Created permissions for external_context:")
        logger.info(f"  - Relative path: {external_context_rel}")
        logger.info(f"  - Absolute path: {external_context_abs}")
        
        return config
    
    def _log_configuration_summary(self, config: Dict[str, Any]) -> None:
        """
        Log a summary of the final configuration.
        
        Args:
            config: Final configuration dictionary
        """
        permissions = config.get("permissions", {})
        
        logger.info("=== Claude Permissions Configuration Summary ===")
        
        if "allow" in permissions:
            logger.info(f"Allowed operations ({len(permissions['allow'])}):")
            for perm in permissions["allow"]:
                logger.info(f"  ✓ {perm}")
        
        if "deny" in permissions:
            logger.info(f"Denied operations ({len(permissions['deny'])}):")
            for perm in permissions["deny"]:
                logger.info(f"  ✗ {perm}")
        
        if "ask" in permissions:
            logger.info(f"Ask for confirmation ({len(permissions['ask'])}):")
            for perm in permissions["ask"]:
                logger.info(f"  ? {perm}")
        
        logger.info("===============================================")
    
    def validate_configuration(self, config_path: Path) -> bool:
        """
        Validate that the configuration file is properly formatted.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            if not config_path.exists():
                logger.warning(f"Configuration file does not exist: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Basic validation
            if not isinstance(config, dict):
                logger.error("Configuration must be a JSON object")
                return False
            
            # Validate permissions structure if present
            if "permissions" in config:
                permissions = config["permissions"]
                if not isinstance(permissions, dict):
                    logger.error("Permissions must be an object")
                    return False
                
                for perm_type in ["allow", "deny", "ask"]:
                    if perm_type in permissions:
                        if not isinstance(permissions[perm_type], list):
                            logger.error(f"Permissions.{perm_type} must be an array")
                            return False
            
            logger.info("Configuration validation passed")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def get_current_permissions(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get current permissions configuration.
        
        Args:
            project_path: Path to project root
            
        Returns:
            dict or None: Current permissions configuration
        """
        try:
            if isinstance(project_path, str):
                project_path = Path(project_path)
                
            config_path = project_path / self.config_dir_name / self.config_file_name
            
            if not config_path.exists():
                return None
                
            config = self.get_existing_config(config_path)
            return config.get("permissions")
            
        except Exception as e:
            logger.error(f"Error getting current permissions: {e}")
            return None


def setup_external_context_permissions(project_path: Union[str, Path] = None) -> bool:
    """
    Convenience function to setup external_context permissions.
    
    Args:
        project_path: Path to project root (defaults to current working directory)
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    if project_path is None:
        project_path = Path.cwd()
    elif isinstance(project_path, str):
        project_path = Path(project_path)
    
    service = ClaudePermissionsService()
    return service.setup_claude_permissions(project_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get project path from command line or use current directory
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path.cwd()
    
    success = setup_external_context_permissions(project_path)
    
    if success:
        print("✓ Claude permissions configured successfully")
        sys.exit(0)
    else:
        print("✗ Failed to configure Claude permissions")
        sys.exit(1)