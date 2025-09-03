"""Setup widgets and services for the TUI application."""

from .editor_selector import EditorSelectorMenu
from .claude_permissions import ClaudePermissionsService, setup_external_context_permissions
from .mcp_installer import (
    MCPInstaller,
    MCPInstallationError,
    install_vibe_context_for_editor,
    get_supported_editors,
    get_editor_display_names
)
from .dependency_scanner import DependencyScanner
from .external_context_manager import ExternalContextManager
from .dependency_common import DependencyDocsAPIError, DependencyInfo
from .backend_dependency_docs_api import BackendDependencyDocsAPI

__all__ = [
    "EditorSelectorMenu",
    "ClaudePermissionsService",
    "setup_external_context_permissions",
    "MCPInstaller",
    "MCPInstallationError",
    "install_vibe_context_for_editor",
    "get_supported_editors",
    "get_editor_display_names",
    "DependencyScanner",
    "ExternalContextManager",
    # Common dependency classes
    "DependencyDocsAPIError",
    "DependencyInfo",
    # Backend API (main implementation)
    "BackendDependencyDocsAPI",
]