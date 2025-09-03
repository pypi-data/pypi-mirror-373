"""
Common dependency-related classes and utilities.

This module contains shared classes used by the dependency documentation system,
including the BackendDependencyDocsAPI and other components.
"""

import re
from dataclasses import dataclass


class DependencyDocsAPIError(Exception):
    """Base exception for dependency docs API errors."""
    pass


@dataclass
class DependencyInfo:
    """Data class representing a dependency."""
    name: str
    version: str
    
    @property
    def major_version(self) -> str:
        """Extract major version from version string."""
        match = re.match(r'^(\d+)', self.version)
        return match.group(1) if match else '0'
    
    @property
    def docs_filename(self) -> str:
        """Generate documentation filename based on clean naming convention."""
        # Use only the clean library name without version suffixes
        clean_name = self._extract_clean_library_name(self.name)
        return f"{clean_name}.md"
    
    def _extract_clean_library_name(self, dependency: str) -> str:
        """Extract clean library name from dependency identifier."""
        clean_name = dependency
        
        # Handle npm scoped packages FIRST
        if clean_name.startswith("@"):
            clean_name = clean_name[1:].replace("/", "-")
            return self._sanitize_filename(clean_name)
        
        # Handle git+https patterns
        if "git+" in clean_name:
            egg_match = re.search(r'egg=([^&#]+)', clean_name)
            if egg_match:
                clean_name = egg_match.group(1)
                return self._sanitize_filename(clean_name)
            else:
                clean_name = re.sub(r'^git\+https?://[^/]+/', '', clean_name)
                clean_name = re.sub(r'\.git.*$', '', clean_name)
                if "/" in clean_name:
                    clean_name = clean_name.split("/")[-1]
                return self._sanitize_filename(clean_name)
        
        # Handle common version suffixes
        clean_name = re.sub(r'[@v]\d+\.\d+.*$', '', clean_name)
        
        # Handle GitHub URLs and similar patterns
        if "/" in clean_name:
            clean_name = clean_name.split("/")[-1]
        
        return self._sanitize_filename(clean_name)
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be filesystem-safe."""
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        sanitized = sanitized.strip('_.')
        
        if not sanitized:
            sanitized = "unknown"
        elif len(sanitized) > 100:
            sanitized = sanitized[:100].rstrip('_.')
        
        return sanitized