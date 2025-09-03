"""
External Context Manager

This service manages the external_context folder for storing documentation
and other context files that AI assistants can access. It provides organized
storage for dependency documentation, project information, and related files.
"""

import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import os

logger = logging.getLogger(__name__)


class ExternalContextManager:
    """Service for managing external context documentation storage."""
    
    def __init__(self, project_path: Path):
        """Initialize the external context manager.
        
        Args:
            project_path: Path to the project root directory
        """
        self.project_path = Path(project_path).resolve()
        self.project_symlink = self.project_path / "external_context"
        
        # Create ASKBUDI directory path
        home_path = Path.home()
        askbudi_dir = home_path / ".ASKBUDI"
        
        # Generate project name from path (escape slashes and remove user prefix)
        project_name = self._generate_project_name(self.project_path)
        self.context_dir = askbudi_dir / project_name / "external_context"
        
        # Standard subdirectories for organization
        self.subdirs = {
            "dependencies": "dependencies",  # Library/package documentation
            "apis": "apis",  # API documentation
            "frameworks": "frameworks",  # Framework documentation  
            "tools": "tools",  # Development tools documentation
            "references": "references",  # General reference materials
            "project": "project"  # Project-specific documentation
        }
    
    def _generate_project_name(self, project_path: Path) -> str:
        """Generate project name for ASKBUDI directory from project path.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            str: Generated project name with path segments
        """
        # Convert path to string and make it relative to user home if possible
        path_str = str(project_path)
        home_str = str(Path.home())
        
        # Remove home prefix if present
        if path_str.startswith(home_str):
            path_str = path_str[len(home_str):].lstrip('/')
        
        # Replace path separators with underscores and remove leading separators
        project_name = path_str.replace('/', '_').replace('\\', '_').strip('_')
        
        # Ensure we have a valid name
        if not project_name:
            project_name = "project_" + str(abs(hash(str(project_path))))[:8]
            
        return project_name
    
    def create_symlink(self) -> bool:
        """Create symlink from project directory to ASKBUDI external_context.
        
        Returns:
            bool: True if symlink was created successfully
        """
        try:
            # Remove existing symlink or directory if it exists
            if self.project_symlink.exists() or self.project_symlink.is_symlink():
                if self.project_symlink.is_symlink():
                    self.project_symlink.unlink()
                    logger.info(f"Removed existing symlink: {self.project_symlink}")
                elif self.project_symlink.is_dir():
                    shutil.rmtree(self.project_symlink)
                    logger.info(f"Removed existing directory: {self.project_symlink}")
            
            # Ensure the ASKBUDI context directory exists
            self.context_dir.mkdir(parents=True, exist_ok=True)
            
            # Create symlink using cross-platform method
            success = self._create_platform_symlink(str(self.context_dir), str(self.project_symlink))
            
            if success:
                logger.info(f"Successfully created symlink: {self.project_symlink} -> {self.context_dir}")
                return True
            else:
                logger.error(f"Failed to create symlink: {self.project_symlink} -> {self.context_dir}")
                return self._create_fallback_directory()
                
        except Exception as e:
            logger.error(f"Error creating symlink: {e}")
            return self._create_fallback_directory()
    
    def _create_platform_symlink(self, source_path: str, link_path: str) -> bool:
        """Create symlink with cross-platform compatibility.
        
        Args:
            source_path: Path to the source directory
            link_path: Path where the symlink should be created
            
        Returns:
            bool: True if successful
        """
        try:
            if sys.platform.startswith('win'):
                # Windows: Use mklink command
                result = subprocess.run([
                    'mklink', '/D', link_path, source_path
                ], shell=True, capture_output=True, text=True)
                return result.returncode == 0
            else:
                # Unix/Mac: Use os.symlink
                os.symlink(source_path, link_path)
                return True
        except Exception as e:
            logger.error(f"Platform symlink creation failed: {e}")
            return False
    
    def _create_fallback_directory(self) -> bool:
        """Create regular directory as fallback when symlink fails.
        
        Returns:
            bool: True if fallback directory was created
        """
        try:
            logger.warning("Symlink creation failed, creating regular directory as fallback")
            self.project_symlink.mkdir(parents=True, exist_ok=True)
            
            # Copy existing content from ASKBUDI to local directory
            if self.context_dir.exists():
                for item in self.context_dir.iterdir():
                    if item.is_dir():
                        shutil.copytree(item, self.project_symlink / item.name, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, self.project_symlink / item.name)
                        
            logger.info(f"Fallback directory created: {self.project_symlink}")
            return True
        except Exception as e:
            logger.error(f"Fallback directory creation failed: {e}")
            return False
    
    def initialize_context_structure(self) -> bool:
        """Initialize the external_context directory structure.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            logger.info(f"Initializing external context structure at: {self.context_dir}")
            logger.info(f"Symlink will be created at: {self.project_symlink}")
            
            # Create main context directory in ASKBUDI folder
            self.context_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            for subdir_key, subdir_name in self.subdirs.items():
                subdir_path = self.context_dir / subdir_name
                subdir_path.mkdir(exist_ok=True)
                
                # Create a README in each subdirectory
                readme_path = subdir_path / "README.md"
                if not readme_path.exists():
                    readme_content = self._generate_subdir_readme(subdir_key, subdir_name)
                    readme_path.write_text(readme_content, encoding='utf-8')
            
            # Create main README
            main_readme = self.context_dir / "README.md"
            if not main_readme.exists():
                readme_content = self._generate_main_readme()
                main_readme.write_text(readme_content, encoding='utf-8')
            
            # Create index file for tracking contents
            index_file = self.context_dir / "index.json"
            if not index_file.exists():
                initial_index = {
                    "created_at": self._get_timestamp(),
                    "last_updated": self._get_timestamp(),
                    "version": "1.0",
                    "structure": self.subdirs,
                    "contents": {subdir: [] for subdir in self.subdirs.keys()}
                }
                index_file.write_text(json.dumps(initial_index, indent=2), encoding='utf-8')
            
            # Create symlink from project directory to ASKBUDI directory
            symlink_success = self.create_symlink()
            if not symlink_success:
                logger.warning("Symlink creation failed, but directory structure is available")
            
            logger.info("External context structure initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize external context structure: {e}")
            return False
    
    def add_dependency_documentation(self, dependency_name: str, documentation: str, 
                                   doc_type: str = "general") -> bool:
        """Add documentation for a specific dependency.
        
        Args:
            dependency_name: Name of the dependency
            documentation: Documentation content
            doc_type: Type of documentation (general, api, examples, etc.)
            
        Returns:
            bool: True if documentation was added successfully
        """
        try:
            dep_dir = self.context_dir / "dependencies" / dependency_name
            dep_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine filename based on doc_type
            if doc_type == "api":
                filename = "api_reference.md"
            elif doc_type == "examples":
                filename = "examples.md"
            elif doc_type == "quickstart":
                filename = "quickstart.md"
            else:
                filename = "overview.md"
            
            doc_file = dep_dir / filename
            doc_file.write_text(documentation, encoding='utf-8')
            
            # Update index
            self._update_index("dependencies", {
                "name": dependency_name,
                "type": doc_type,
                "file": str(dep_dir / filename),
                "added_at": self._get_timestamp()
            })
            
            logger.info(f"Added {doc_type} documentation for {dependency_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add dependency documentation: {e}")
            return False
    
    def add_project_documentation(self, doc_name: str, content: str, 
                                doc_format: str = "md") -> bool:
        """Add project-specific documentation.
        
        Args:
            doc_name: Name/identifier for the document
            content: Document content
            doc_format: File format (md, txt, json, etc.)
            
        Returns:
            bool: True if documentation was added successfully
        """
        try:
            project_dir = self.context_dir / "project"
            filename = f"{doc_name}.{doc_format}"
            doc_file = project_dir / filename
            
            doc_file.write_text(content, encoding='utf-8')
            
            # Update index
            self._update_index("project", {
                "name": doc_name,
                "format": doc_format,
                "file": str(doc_file),
                "added_at": self._get_timestamp()
            })
            
            logger.info(f"Added project documentation: {doc_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add project documentation: {e}")
            return False
    
    def add_reference_material(self, category: str, name: str, content: str,
                              source_url: Optional[str] = None) -> bool:
        """Add reference material to the appropriate category.
        
        Args:
            category: Category (apis, frameworks, tools, references)
            name: Name/identifier for the material
            content: Reference content
            source_url: Optional URL where content was sourced from
            
        Returns:
            bool: True if material was added successfully
        """
        try:
            if category not in self.subdirs:
                logger.error(f"Invalid category: {category}")
                return False
            
            cat_dir = self.context_dir / self.subdirs[category]
            filename = f"{name.replace(' ', '_').lower()}.md"
            doc_file = cat_dir / filename
            
            # Add source URL to content if provided
            full_content = content
            if source_url:
                full_content = f"# {name}\n\n**Source:** {source_url}\n\n{content}"
            else:
                full_content = f"# {name}\n\n{content}"
            
            doc_file.write_text(full_content, encoding='utf-8')
            
            # Update index
            self._update_index(category, {
                "name": name,
                "file": str(doc_file),
                "source_url": source_url,
                "added_at": self._get_timestamp()
            })
            
            logger.info(f"Added {category} reference: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add reference material: {e}")
            return False
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context structure and contents.
        
        Returns:
            Dict containing summary information
        """
        try:
            if not self.context_dir.exists():
                return {"status": "not_initialized", "message": "External context not initialized"}
            
            index_file = self.context_dir / "index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            else:
                index_data = {"contents": {}}
            
            summary = {
                "status": "initialized",
                "path": str(self.context_dir),
                "created_at": index_data.get("created_at"),
                "last_updated": index_data.get("last_updated"),
                "categories": {}
            }
            
            # Count items in each category
            contents = index_data.get("contents", {})
            for category, items in contents.items():
                if category in self.subdirs:
                    category_dir = self.context_dir / self.subdirs[category]
                    file_count = len([f for f in category_dir.glob("**/*") if f.is_file() and f.name != "README.md"])
                    summary["categories"][category] = {
                        "count": file_count,
                        "recent_items": items[-3:] if items else []  # Show last 3 items
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get context summary: {e}")
            return {"status": "error", "message": str(e)}
    
    def cleanup_context(self) -> bool:
        """Clean up the external context directory.
        
        Returns:
            bool: True if cleanup was successful
        """
        try:
            if self.context_dir.exists():
                shutil.rmtree(self.context_dir)
                logger.info("External context directory cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup context: {e}")
            return False
    
    def _update_index(self, category: str, item_info: Dict[str, Any]) -> None:
        """Update the index file with new item information."""
        try:
            index_file = self.context_dir / "index.json"
            
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            else:
                index_data = {
                    "contents": {subdir: [] for subdir in self.subdirs.keys()},
                    "version": "1.0"
                }
            
            # Ensure category exists in contents
            if category not in index_data["contents"]:
                index_data["contents"][category] = []
            
            # Add new item
            index_data["contents"][category].append(item_info)
            index_data["last_updated"] = self._get_timestamp()
            
            # Save updated index
            index_file.write_text(json.dumps(index_data, indent=2), encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Failed to update index: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_main_readme(self) -> str:
        """Generate the main README for the external_context directory."""
        return """# External Context Documentation

This directory contains documentation and reference materials that provide context
to AI assistants working on this project.

## Structure

- **dependencies/**: Documentation for project dependencies and libraries
- **apis/**: API documentation and reference materials  
- **frameworks/**: Framework-specific documentation and guides
- **tools/**: Development tools and utility documentation
- **references/**: General reference materials and guides
- **project/**: Project-specific documentation and context

## Usage

This directory is automatically managed by the juno-agent setup process.
Documentation is organized to help AI assistants understand:

1. Project dependencies and their usage patterns
2. API specifications and integration details
3. Framework conventions and best practices
4. Development tools and their configuration
5. Project-specific context and requirements

## Files

- `index.json`: Metadata and content tracking
- Each subdirectory contains relevant documentation files
- README files provide guidance for each category

---

*This directory is part of the juno-agent enhanced setup process.*
"""
    
    def _generate_subdir_readme(self, subdir_key: str, subdir_name: str) -> str:
        """Generate README content for a subdirectory."""
        descriptions = {
            "dependencies": "This directory contains documentation for project dependencies and external libraries.",
            "apis": "This directory contains API documentation, specifications, and integration guides.",
            "frameworks": "This directory contains framework-specific documentation and best practices.",
            "tools": "This directory contains documentation for development tools and utilities.",
            "references": "This directory contains general reference materials and guides.",
            "project": "This directory contains project-specific documentation and context information."
        }
        
        description = descriptions.get(subdir_key, "This directory contains documentation and reference materials.")
        
        return f"""# {subdir_name.title()} Documentation

{description}

## Contents

Documentation files in this directory are automatically organized by the
juno-agent setup process to provide relevant context to AI assistants.

## Usage

Files here should be:
- Well-structured and clearly written
- Relevant to the project's needs
- Updated as dependencies or requirements change

---

*Managed by juno-agent external context system.*
"""