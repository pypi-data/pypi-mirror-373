"""
Shared test fixtures and utilities for the setup command test suite.

This module provides common test fixtures, mock objects, and utilities
used across all setup command component tests.
"""

import json
import os
import platform
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import pytest
from textual.app import App


# Test Data Constants
TEST_API_KEY = "vibe_test_key_12345678901234567890abcdef1234567890"
TEST_PROJECT_NAME = "test_project"
TEST_DEPENDENCIES = ["fastapi", "pytest", "requests", "numpy", "pandas"]


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_project_dir(temp_dir):
    """Create a mock project directory with common structure."""
    project_dir = temp_dir / TEST_PROJECT_NAME
    project_dir.mkdir()
    
    # Create common project files
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "README.md").write_text("# Test Project")
    (project_dir / ".git").mkdir()
    (project_dir / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    
    return project_dir


@pytest.fixture
def python_project(mock_project_dir):
    """Create a Python project structure with dependencies."""
    # Create requirements.txt
    requirements = "\n".join([
        "fastapi>=0.100.0",
        "pytest>=7.0.0",
        "requests>=2.28.0",
        "# Development dependencies",
        "black",
        "flake8"
    ])
    (mock_project_dir / "requirements.txt").write_text(requirements)
    
    # Create pyproject.toml
    pyproject = """
[tool.poetry]
name = "test-project"
version = "0.1.0"
description = ""

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.100.0"
requests = "^2.28.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^22.0.0"
"""
    (mock_project_dir / "pyproject.toml").write_text(pyproject)
    
    # Create Python files
    (mock_project_dir / "src" / "__init__.py").write_text("")
    (mock_project_dir / "src" / "main.py").write_text("# Main module")
    (mock_project_dir / "tests" / "test_main.py").write_text("# Tests")
    
    return mock_project_dir


@pytest.fixture
def javascript_project(mock_project_dir):
    """Create a JavaScript/Node.js project structure with dependencies."""
    # Create package.json
    package_json = {
        "name": "test-js-project",
        "version": "1.0.0",
        "description": "Test JavaScript project",
        "main": "index.js",
        "scripts": {
            "test": "jest",
            "start": "node index.js",
            "build": "webpack --mode production"
        },
        "dependencies": {
            "express": "^4.18.0",
            "axios": "^1.4.0",
            "lodash": "^4.17.0"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "webpack": "^5.88.0",
            "eslint": "^8.44.0"
        }
    }
    (mock_project_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    
    # Create package-lock.json
    (mock_project_dir / "package-lock.json").write_text('{"lockfileVersion": 2}')
    
    # Create JavaScript files
    (mock_project_dir / "index.js").write_text("console.log('Hello World');")
    (mock_project_dir / "tests" / "index.test.js").write_text("// Tests")
    
    return mock_project_dir


@pytest.fixture
def go_project(mock_project_dir):
    """Create a Go project structure with dependencies."""
    # Create go.mod
    go_mod = """
module github.com/test/project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/stretchr/testify v1.8.4
    golang.org/x/net v0.10.0
)
"""
    (mock_project_dir / "go.mod").write_text(go_mod.strip())
    
    # Create Go files
    (mock_project_dir / "main.go").write_text("package main\n\nfunc main() {}")
    (mock_project_dir / "main_test.go").write_text("package main\n\nimport \"testing\"")
    
    return mock_project_dir


@pytest.fixture
def rust_project(mock_project_dir):
    """Create a Rust project structure with dependencies."""
    # Create Cargo.toml
    cargo_toml = """
[package]
name = "test-rust-project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
reqwest = "0.11"

[dev-dependencies]
criterion = "0.5"
"""
    (mock_project_dir / "Cargo.toml").write_text(cargo_toml.strip())
    
    # Create src directory and files
    (mock_project_dir / "src").mkdir(exist_ok=True)
    (mock_project_dir / "src" / "main.rs").write_text("fn main() {}")
    (mock_project_dir / "src" / "lib.rs").write_text("// Library")
    
    return mock_project_dir


@pytest.fixture
def mock_api_responses():
    """Mock API responses for dependency documentation."""
    return {
        "resolve_library_id": {
            "fastapi": [
                {
                    "id": "/tiangolo/fastapi",
                    "name": "FastAPI",
                    "description": "Modern, fast (high-performance), web framework for building APIs with Python 3.7+",
                    "trust_score": 9,
                    "code_snippets": 150
                }
            ],
            "pytest": [
                {
                    "id": "/pytest-dev/pytest",
                    "name": "pytest",
                    "description": "The pytest framework makes it easy to write small tests, yet scales to support complex functional testing",
                    "trust_score": 10,
                    "code_snippets": 200
                }
            ]
        },
        "get_library_docs": {
            "/tiangolo/fastapi": {
                "docs": [
                    {
                        "title": "Quick Start",
                        "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}"
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_tiny_agent():
    """Mock TinyAgent for testing."""
    agent = Mock()
    agent.process_query.return_value = "Mock response from TinyAgent"
    agent.get_context_summary.return_value = "Mock context summary"
    agent.is_ready = True
    return agent


@pytest.fixture
def mock_textual_app():
    """Mock Textual app for widget testing."""
    app = Mock(spec=App)
    app.screen = Mock()
    app.screen.post_message = Mock()
    return app


@pytest.fixture
def sample_editor_configs():
    """Sample editor configurations for testing."""
    return {
        "claude_code": {
            "config_path": "~/.claude_code_config.json",
            "format": "claude_mcp",
            "example_config": {
                "mcpServers": {
                    "vibe_context": {
                        "command": "npx",
                        "args": ["askbudi-context"],
                        "env": {"ASKBUDI_API_KEY": TEST_API_KEY}
                    }
                }
            }
        },
        "cursor": {
            "config_path": ".cursor/mcp.json",
            "format": "standard_mcp",
            "example_config": {
                "vibe_context": {
                    "command": "npx",
                    "args": ["askbudi-context"],
                    "env": {"ASKBUDI_API_KEY": TEST_API_KEY}
                }
            }
        },
        "vscode": {
            "config_path": ".vscode/mcp.json",
            "format": "standard_mcp",
            "example_config": {
                "vibe_context": {
                    "command": "npx",
                    "args": ["askbudi-context"],
                    "env": {"ASKBUDI_API_KEY": TEST_API_KEY}
                }
            }
        }
    }


@pytest.fixture
def mock_platform_detection():
    """Mock platform detection for cross-platform testing."""
    with patch('platform.system') as mock_system:
        yield mock_system


@pytest.fixture
def mock_home_directory(temp_dir):
    """Mock home directory for testing configuration paths."""
    mock_home = temp_dir / "mock_home"
    mock_home.mkdir()
    
    with patch('pathlib.Path.home', return_value=mock_home):
        yield mock_home


@pytest.fixture
def sample_dependencies_by_language():
    """Sample dependencies organized by programming language."""
    return {
        "Python": ["fastapi", "pytest", "requests", "numpy", "pandas"],
        "JavaScript": ["express", "react", "axios", "lodash", "jest"],
        "TypeScript": ["typescript", "@types/node", "ts-node", "jest"],
        "Go": ["github.com/gin-gonic/gin", "github.com/stretchr/testify"],
        "Rust": ["serde", "tokio", "reqwest", "clap"],
        "Java": ["spring-boot-starter", "junit", "mockito-core"]
    }


class MockFileSystem:
    """Mock file system for testing file operations."""
    
    def __init__(self):
        self.files = {}
        self.directories = set()
    
    def create_file(self, path: str, content: str = ""):
        """Create a mock file."""
        self.files[str(Path(path).resolve())] = content
        self.directories.add(str(Path(path).parent.resolve()))
    
    def create_directory(self, path: str):
        """Create a mock directory."""
        self.directories.add(str(Path(path).resolve()))
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        resolved_path = str(Path(path).resolve())
        return resolved_path in self.files or resolved_path in self.directories
    
    def read_file(self, path: str) -> str:
        """Read mock file content."""
        resolved_path = str(Path(path).resolve())
        if resolved_path in self.files:
            return self.files[resolved_path]
        raise FileNotFoundError(f"No such file: {path}")


@pytest.fixture
def mock_filesystem():
    """Provide a mock file system for testing."""
    return MockFileSystem()


# Utility functions for tests
def create_test_config(editor: str, project_path: Path, api_key: str = TEST_API_KEY) -> Dict[str, Any]:
    """Create a test configuration for an editor."""
    base_config = {
        "command": "npx",
        "args": ["askbudi-context"],
        "env": {
            "ASKBUDI_API_KEY": api_key,
            "PLATFORM": platform.system().lower()
        }
    }
    
    if editor == "claude_code":
        return {"mcpServers": {"vibe_context": base_config}}
    else:
        return {"vibe_context": base_config}


def assert_config_file_created(config_path: Path, expected_servers: List[str]):
    """Assert that a configuration file was created with expected servers."""
    assert config_path.exists(), f"Config file not found: {config_path}"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if "mcpServers" in config:
        servers = config["mcpServers"]
    else:
        servers = config
    
    for server_name in expected_servers:
        assert server_name in servers, f"Server {server_name} not found in config"


def create_mock_vibe_context_server(project_path: Path) -> Path:
    """Create a mock VibeContext server structure for testing."""
    server_dir = project_path / "ts_mcp_server" / "ts_mcp_server" / "build"
    server_dir.mkdir(parents=True, exist_ok=True)
    
    server_file = server_dir / "index.js"
    server_file.write_text("// Mock VibeContext MCP Server")
    
    return server_file


# Platform-specific test helpers
def get_platform_config_path(editor: str, project_path: Optional[Path] = None) -> Path:
    """Get platform-specific configuration path for an editor."""
    if editor == "claude_code":
        return Path.home() / ".claude_code_config.json"
    elif editor == "cursor":
        base = project_path or Path.cwd()
        return base / ".cursor" / "mcp.json"
    elif editor == "vscode":
        base = project_path or Path.cwd()
        return base / ".vscode" / "mcp.json"
    elif editor == "windsurf":
        if platform.system() == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Codeium" / "Windsurf" / "mcp_config.json"
        else:
            return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
    else:
        raise ValueError(f"Unsupported editor: {editor}")


# Mock network requests
@pytest.fixture
def mock_requests():
    """Mock HTTP requests for API testing."""
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Default successful responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "success"}
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}
        
        yield {"get": mock_get, "post": mock_post}


# Error simulation helpers
class NetworkError(Exception):
    """Simulate network errors."""
    pass


class PermissionError(Exception):
    """Simulate permission errors."""
    pass


@pytest.fixture
def error_simulator():
    """Fixture to simulate various error conditions."""
    class ErrorSimulator:
        def __init__(self):
            self.network_error = False
            self.permission_error = False
            self.file_not_found = False
            self.invalid_json = False
        
        def enable_network_error(self):
            self.network_error = True
        
        def enable_permission_error(self):
            self.permission_error = True
        
        def enable_file_not_found(self):
            self.file_not_found = True
        
        def enable_invalid_json(self):
            self.invalid_json = True
        
        def check_and_raise(self, operation: str):
            if operation == "network" and self.network_error:
                raise NetworkError("Simulated network error")
            elif operation == "permission" and self.permission_error:
                raise PermissionError("Simulated permission error")
            elif operation == "file" and self.file_not_found:
                raise FileNotFoundError("Simulated file not found")
    
    return ErrorSimulator()