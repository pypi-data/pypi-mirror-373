"""
Mock implementations and test utilities for Agentic Dependency Resolver tests.

This file provides comprehensive mocks and utilities that simulate the behavior
of external dependencies and systems that the Agentic Dependency Resolver
interacts with. These mocks enable thorough testing without requiring actual
API calls or external services.
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class MockLibrarySearchResult:
    """Mock result from mcp__vibe_context__resolve_library_id."""
    library_id: str
    name: str
    description: str
    trust_score: int
    snippet_count: int
    language: str = "python"
    version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MockDocumentationContent:
    """Mock documentation content from mcp__vibe_context__get_library_docs."""
    content: str
    source_url: str
    quality_score: int
    last_updated: str
    code_examples: List[str] = None
    
    def __post_init__(self):
        if self.code_examples is None:
            self.code_examples = []


class MockVibeContextMCP:
    """
    Mock implementation of VibeContext MCP server functionality.
    
    Simulates the behavior of:
    - mcp__vibe_context__resolve_library_id
    - mcp__vibe_context__get_library_docs
    - Rate limiting and error scenarios
    """
    
    def __init__(self):
        self.call_count = {}
        self.rate_limit_calls = {}
        self.max_calls_per_minute = 30
        self.documentation_db = self._initialize_mock_docs()
        self.search_db = self._initialize_mock_search()
        
    def _initialize_mock_docs(self) -> Dict[str, MockDocumentationContent]:
        """Initialize mock documentation database."""
        return {
            "/python/requests": MockDocumentationContent(
                content="""# Requests Documentation

Requests is an elegant and simple HTTP library for Python.

## Installation

```bash
pip install requests
```

## Quick Start

```python
import requests

response = requests.get('https://api.github.com/user', auth=('user', 'pass'))
print(response.status_code)
print(response.json())
```

## Making Requests

Requests supports all HTTP methods:

```python
r = requests.post('https://httpbin.org/post', data={'key': 'value'})
r = requests.put('https://httpbin.org/put', data={'key': 'value'})
r = requests.delete('https://httpbin.org/delete')
r = requests.head('https://httpbin.org/get')
r = requests.options('https://httpbin.org/get')
```

## Session Objects

Use session objects for persistent parameters:

```python
s = requests.Session()
s.auth = ('user', 'pass')
s.headers.update({'x-test': 'true'})

r = s.get('https://httpbin.org/headers')
```
""",
                source_url="https://docs.python-requests.org/",
                quality_score=9,
                last_updated="2024-01-15",
                code_examples=[
                    "requests.get('https://api.github.com/user')",
                    "requests.post('https://httpbin.org/post', data={'key': 'value'})",
                    "session = requests.Session()"
                ]
            ),
            "/python/flask": MockDocumentationContent(
                content="""# Flask Documentation

Flask is a lightweight web framework for Python.

## Installation

```bash
pip install Flask
```

## Minimal Application

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'

if __name__ == '__main__':
    app.run(debug=True)
```

## Routing

```python
@app.route('/user/<name>')
def show_user_profile(name):
    return f'User {name}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'
```

## Templates

```python
from flask import render_template

@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
```
""",
                source_url="https://flask.palletsprojects.com/",
                quality_score=9,
                last_updated="2024-01-10",
                code_examples=[
                    "app = Flask(__name__)",
                    "@app.route('/')",
                    "render_template('hello.html', name=name)"
                ]
            ),
            "/python/pytest": MockDocumentationContent(
                content="""# Pytest Documentation

pytest is a mature testing framework for Python.

## Installation

```bash
pip install pytest
```

## Writing Tests

```python
def test_addition():
    assert 1 + 1 == 2

def test_string_operations():
    assert "hello".upper() == "HELLO"
```

## Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value", "number": 42}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
    assert sample_data["number"] == 42
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```
""",
                source_url="https://docs.pytest.org/",
                quality_score=9,
                last_updated="2024-01-12",
                code_examples=[
                    "assert 1 + 1 == 2",
                    "@pytest.fixture",
                    "@pytest.mark.parametrize"
                ]
            )
        }
    
    def _initialize_mock_search(self) -> Dict[str, List[MockLibrarySearchResult]]:
        """Initialize mock search results database."""
        return {
            "requests": [
                MockLibrarySearchResult(
                    library_id="/python/requests",
                    name="requests",
                    description="HTTP library for Python",
                    trust_score=9,
                    snippet_count=25,
                    language="python",
                    version="2.28.0"
                )
            ],
            "flask": [
                MockLibrarySearchResult(
                    library_id="/python/flask",
                    name="Flask",
                    description="Lightweight web framework",
                    trust_score=9,
                    snippet_count=30,
                    language="python",
                    version="2.3.0"
                )
            ],
            "pytest": [
                MockLibrarySearchResult(
                    library_id="/python/pytest",
                    name="pytest",
                    description="Testing framework",
                    trust_score=9,
                    snippet_count=20,
                    language="python",
                    version="7.4.0"
                )
            ],
            "numpy": [
                MockLibrarySearchResult(
                    library_id="/python/numpy",
                    name="NumPy",
                    description="Numerical computing library",
                    trust_score=10,
                    snippet_count=50,
                    language="python",
                    version="1.24.0"
                )
            ],
            "fastapi": [
                MockLibrarySearchResult(
                    library_id="/python/fastapi",
                    name="FastAPI",
                    description="Modern, fast web framework",
                    trust_score=9,
                    snippet_count=35,
                    language="python",
                    version="0.95.0"
                )
            ]
        }
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if rate limit is exceeded for endpoint."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        if endpoint not in self.rate_limit_calls:
            self.rate_limit_calls[endpoint] = []
        
        # Remove calls older than 1 minute
        self.rate_limit_calls[endpoint] = [
            call_time for call_time in self.rate_limit_calls[endpoint] 
            if call_time > minute_ago
        ]
        
        return len(self.rate_limit_calls[endpoint]) >= self.max_calls_per_minute
    
    def _record_call(self, endpoint: str):
        """Record a call for rate limiting."""
        if endpoint not in self.rate_limit_calls:
            self.rate_limit_calls[endpoint] = []
        
        self.rate_limit_calls[endpoint].append(time.time())
        
        if endpoint not in self.call_count:
            self.call_count[endpoint] = 0
        self.call_count[endpoint] += 1
    
    async def resolve_library_id(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mock implementation of mcp__vibe_context__resolve_library_id.
        
        Args:
            search_term: Library name to search for
            limit: Maximum number of results
            
        Returns:
            List of search results
            
        Raises:
            Exception: If rate limited or network error simulation
        """
        endpoint = "resolve_library_id"
        
        # Check rate limiting
        if self._check_rate_limit(endpoint):
            raise Exception("429 Too Many Requests")
        
        self._record_call(endpoint)
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Simulate occasional network errors
        if self.call_count[endpoint] % 20 == 0:  # Every 20th call
            raise ConnectionError("Network timeout")
        
        # Return mock results
        search_term_lower = search_term.lower()
        if search_term_lower in self.search_db:
            results = self.search_db[search_term_lower][:limit]
            return [result.to_dict() for result in results]
        
        # Return empty list for unknown libraries
        return []
    
    async def get_library_docs(self, library_id: str, prompt: str, limit: int = 5) -> Dict[str, Any]:
        """
        Mock implementation of mcp__vibe_context__get_library_docs.
        
        Args:
            library_id: Library identifier from search results
            prompt: Documentation request prompt
            limit: Maximum number of documentation snippets
            
        Returns:
            Documentation content and metadata
            
        Raises:
            Exception: If rate limited or network error simulation
        """
        endpoint = "get_library_docs"
        
        # Check rate limiting
        if self._check_rate_limit(endpoint):
            raise Exception("429 Too Many Requests")
        
        self._record_call(endpoint)
        
        # Simulate network delay
        await asyncio.sleep(0.2)
        
        # Simulate occasional failures
        if self.call_count[endpoint] % 15 == 0:  # Every 15th call
            raise Exception("Documentation server unavailable")
        
        # Return mock documentation
        if library_id in self.documentation_db:
            doc = self.documentation_db[library_id]
            
            return {
                "content": doc.content,
                "metadata": {
                    "library_id": library_id,
                    "source_url": doc.source_url,
                    "quality_score": doc.quality_score,
                    "last_updated": doc.last_updated,
                    "fetched_at": datetime.now().isoformat(),
                    "prompt_used": prompt
                },
                "code_examples": doc.code_examples,
                "success": True
            }
        
        # Return empty result for unknown library
        return {
            "content": "",
            "metadata": {"error": f"No documentation found for {library_id}"},
            "code_examples": [],
            "success": False
        }


class MockTinyAgent:
    """
    Comprehensive mock of TinyAgent for testing Agentic Dependency Resolver.
    
    This mock simulates TinyAgent's behavior patterns:
    - Tool execution and decision making
    - Message processing and responses
    - Storage integration
    - Callback handling
    """
    
    def __init__(self, **kwargs):
        self.model = kwargs.get('model', 'test-model')
        self.system_prompt = kwargs.get('system_prompt', '')
        self.tools = []
        self.callbacks = []
        self.messages = []
        self.storage = kwargs.get('storage')
        self.session_id = kwargs.get('session_id', 'test-session')
        self.user_id = kwargs.get('user_id', 'test-user')
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens')
        self.workdir = Path(kwargs.get('default_workdir', '/tmp'))
        
        # Mock decision-making state
        self.decision_history = []
        self.tool_calls = []
        self.current_context = {}
        
        # Initialize mock MCP
        self.mock_mcp = MockVibeContextMCP()
        
    def add_tool(self, tool):
        """Add a tool to the agent."""
        self.tools.append(tool)
        
    def add_callback(self, callback):
        """Add a callback to the agent."""
        self.callbacks.append(callback)
    
    async def run(self, message: str, max_turns: int = 5) -> str:
        """
        Mock agent execution that simulates autonomous dependency resolution.
        
        Args:
            message: User message requesting dependency resolution
            max_turns: Maximum number of agent turns
            
        Returns:
            Agent response after completing dependency resolution
        """
        self.messages.append({"role": "user", "content": message})
        
        # Analyze message to determine intent
        intent = self._analyze_intent(message)
        self.current_context["intent"] = intent
        
        # Execute appropriate workflow based on intent
        if intent == "full_dependency_resolution":
            return await self._execute_full_workflow(message, max_turns)
        elif intent == "dependency_scan_only":
            return await self._execute_scan_workflow(message)
        elif intent == "docs_only":
            return await self._execute_docs_workflow(message)
        else:
            return await self._execute_general_response(message)
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent."""
        message_lower = message.lower()
        
        if "--docs-only" in message_lower:
            return "docs_only"
        elif any(keyword in message_lower for keyword in [
            "resolve dependencies", "fetch documentation", "setup documentation"
        ]):
            return "full_dependency_resolution"
        else:
            return "general_inquiry"
    
    async def _execute_full_workflow(self, message: str, max_turns: int) -> str:
        """Execute full dependency resolution workflow."""
        workflow_steps = [
            "Scanning project for dependencies",
            "Searching for documentation sources",
            "Fetching documentation",
            "Saving documentation files",
            "Creating symlinks"
        ]
        
        results = {
            "dependencies_found": [],
            "documentation_fetched": [],
            "files_saved": [],
            "symlinks_created": False
        }
        
        try:
            # Step 1: Scan for dependencies
            dependencies = await self._mock_scan_dependencies()
            results["dependencies_found"] = dependencies
            self.decision_history.append(("scan_completed", len(dependencies)))
            
            # Step 2: Search for documentation
            search_results = await self._mock_search_dependencies(dependencies)
            self.decision_history.append(("search_completed", len(search_results)))
            
            # Step 3: Fetch documentation
            docs_results = await self._mock_fetch_documentation(search_results)
            results["documentation_fetched"] = docs_results
            self.decision_history.append(("fetch_completed", len(docs_results)))
            
            # Step 4: Save files
            saved_files = await self._mock_save_files(docs_results)
            results["files_saved"] = saved_files
            self.decision_history.append(("files_saved", len(saved_files)))
            
            # Step 5: Create symlinks
            symlink_result = await self._mock_create_symlinks()
            results["symlinks_created"] = symlink_result
            self.decision_history.append(("symlinks_created", symlink_result))
            
            return self._format_success_response(results)
            
        except Exception as e:
            return self._format_error_response(e, results)
    
    async def _execute_scan_workflow(self, message: str) -> str:
        """Execute dependency scanning only workflow."""
        try:
            dependencies = await self._mock_scan_dependencies()
            
            response = f"""I've scanned the project and found {len(dependencies)} dependencies:

"""
            for dep in dependencies:
                response += f"• {dep['name']} ({dep.get('version', 'latest')})\n"
            
            response += "\nUse the full setup command to fetch documentation."
            return response
            
        except Exception as e:
            return f"Error scanning dependencies: {str(e)}"
    
    async def _execute_docs_workflow(self, message: str) -> str:
        """Execute documentation-only workflow."""
        # Extract provided dependencies from message
        # This would be more sophisticated in real implementation
        provided_deps = self._extract_provided_dependencies(message)
        
        if not provided_deps:
            return "No dependencies provided. Please specify dependencies to fetch documentation for."
        
        try:
            # Search and fetch documentation
            search_results = await self._mock_search_dependencies(provided_deps)
            docs_results = await self._mock_fetch_documentation(search_results)
            saved_files = await self._mock_save_files(docs_results)
            symlink_result = await self._mock_create_symlinks()
            
            return f"""Documentation fetched for provided dependencies:

Saved {len(saved_files)} documentation files:
""" + "\n".join(f"• {f['filename']}" for f in saved_files) + f"""

Symlinks created: {'✅' if symlink_result else '❌'}
"""
            
        except Exception as e:
            return f"Error fetching documentation: {str(e)}"
    
    async def _execute_general_response(self, message: str) -> str:
        """Execute general inquiry response."""
        return """I'm ready to help with dependency resolution. I can:

• Scan your project for dependencies
• Search for relevant documentation
• Fetch and save documentation locally
• Create symlinks for easy access

Would you like me to start with a full dependency resolution?"""
    
    async def _mock_scan_dependencies(self) -> List[Dict[str, Any]]:
        """Mock dependency scanning."""
        # Simulate finding common dependencies
        mock_dependencies = [
            {"name": "requests", "version": "2.28.0", "source": "requirements.txt"},
            {"name": "flask", "version": "2.3.0", "source": "requirements.txt"},
            {"name": "pytest", "version": "7.4.0", "source": "requirements.txt"}
        ]
        
        # Simulate some variation based on context
        if "fastapi" in self.system_prompt.lower():
            mock_dependencies.extend([
                {"name": "fastapi", "version": "0.95.0", "source": "pyproject.toml"},
                {"name": "uvicorn", "version": "0.21.0", "source": "pyproject.toml"}
            ])
        
        return mock_dependencies
    
    async def _mock_search_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock searching for documentation sources."""
        search_results = []
        
        for dep in dependencies:
            try:
                # Use mock MCP to search
                results = await self.mock_mcp.resolve_library_id(dep["name"])
                if results:
                    search_results.extend([
                        {**result, "dependency_info": dep} 
                        for result in results
                    ])
                else:
                    # Record failed search
                    search_results.append({
                        "library_id": None,
                        "name": dep["name"],
                        "search_failed": True,
                        "dependency_info": dep
                    })
                    
            except Exception as e:
                # Record search error
                search_results.append({
                    "library_id": None,
                    "name": dep["name"],
                    "search_error": str(e),
                    "dependency_info": dep
                })
        
        return search_results
    
    async def _mock_fetch_documentation(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock fetching documentation."""
        docs_results = []
        
        for result in search_results:
            if not result.get("library_id"):
                continue  # Skip failed searches
                
            try:
                # Use mock MCP to fetch docs
                doc_data = await self.mock_mcp.get_library_docs(
                    result["library_id"],
                    f"Comprehensive documentation for {result['name']}"
                )
                
                if doc_data.get("success"):
                    docs_results.append({
                        **result,
                        "documentation": doc_data,
                        "fetch_success": True
                    })
                else:
                    docs_results.append({
                        **result,
                        "fetch_error": doc_data.get("metadata", {}).get("error", "Unknown error"),
                        "fetch_success": False
                    })
                    
            except Exception as e:
                docs_results.append({
                    **result,
                    "fetch_error": str(e),
                    "fetch_success": False
                })
        
        return docs_results
    
    async def _mock_save_files(self, docs_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock saving documentation files."""
        saved_files = []
        
        for doc_result in docs_results:
            if not doc_result.get("fetch_success"):
                continue
                
            # Generate filename
            filename = self._sanitize_filename(doc_result["name"]) + ".md"
            
            # Mock file save
            saved_files.append({
                "dependency": doc_result["name"],
                "filename": filename,
                "path": f"external_context/dependencies/{filename}",
                "size": len(doc_result["documentation"]["content"]),
                "source": doc_result.get("library_id", "unknown")
            })
        
        return saved_files
    
    async def _mock_create_symlinks(self) -> bool:
        """Mock symlink creation."""
        # Simulate successful symlink creation most of the time
        return True
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize dependency name for filename."""
        # Simple sanitization
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        return sanitized.strip('_').lower()
    
    def _extract_provided_dependencies(self, message: str) -> List[Dict[str, Any]]:
        """Extract dependencies provided in --docs-only command."""
        # Simple extraction - in real implementation would be more sophisticated
        deps = []
        if "requests" in message.lower():
            deps.append({"name": "requests", "version": "latest"})
        if "flask" in message.lower():
            deps.append({"name": "flask", "version": "latest"})
        return deps
    
    def _format_success_response(self, results: Dict[str, Any]) -> str:
        """Format successful completion response."""
        response = f"""✅ Dependency resolution completed successfully!

📋 **Dependencies Found**: {len(results['dependencies_found'])}
"""
        for dep in results['dependencies_found']:
            response += f"   • {dep['name']} ({dep.get('version', 'latest')})\n"
        
        response += f"""
📚 **Documentation Fetched**: {len(results['documentation_fetched'])}
"""
        for doc in results['documentation_fetched']:
            status = "✅" if doc.get('fetch_success') else "❌"
            response += f"   {status} {doc['name']}\n"
        
        response += f"""
💾 **Files Saved**: {len(results['files_saved'])}
"""
        for file in results['files_saved']:
            response += f"   📄 {file['filename']} ({file['size']} chars)\n"
        
        response += f"""
🔗 **Symlinks Created**: {'✅ Yes' if results['symlinks_created'] else '❌ No'}

All documentation is now available in the external_context directory and accessible from your project.
"""
        return response
    
    def _format_error_response(self, error: Exception, partial_results: Dict[str, Any]) -> str:
        """Format error response with partial results."""
        response = f"❌ **Error during dependency resolution**: {str(error)}\n\n"
        
        if partial_results.get('dependencies_found'):
            response += f"✅ Successfully found {len(partial_results['dependencies_found'])} dependencies\n"
        
        if partial_results.get('files_saved'):
            response += f"✅ Successfully saved {len(partial_results['files_saved'])} documentation files\n"
        
        response += "\nYou can retry the operation or run setup to see what dependencies were found."
        
        return response


class MockExternalContextManager:
    """Mock implementation of ExternalContextManager for testing."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.context_dir = project_path / ".test_context"  # Use test directory
        self.symlink_created = False
        self.directories_created = []
        self.files_created = []
    
    def create_symlink(self) -> Dict[str, Any]:
        """Mock symlink creation."""
        # Simulate symlink creation
        symlink_path = self.project_path / "external_context"
        
        # Create the context directory
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        # Simulate symlink (don't actually create on filesystem)
        self.symlink_created = True
        
        return {
            "success": True,
            "type": "symlink",
            "source": str(self.context_dir),
            "target": str(symlink_path)
        }
    
    def initialize_context_structure(self) -> bool:
        """Mock context structure initialization."""
        subdirs = ["dependencies", "apis", "frameworks", "tools", "references", "project"]
        
        for subdir in subdirs:
            subdir_path = self.context_dir / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            self.directories_created.append(str(subdir_path))
        
        return True
    
    def save_dependency_documentation(self, name: str, content: str, filename: str) -> bool:
        """Mock saving dependency documentation."""
        deps_dir = self.context_dir / "dependencies"
        deps_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = deps_dir / filename
        # Don't actually write to filesystem, just record
        self.files_created.append({
            "path": str(file_path),
            "content_length": len(content),
            "name": name
        })
        
        return True


def create_mock_agent_with_tools(**kwargs) -> MockTinyAgent:
    """
    Factory function to create a fully configured MockTinyAgent with tools.
    
    Args:
        **kwargs: Agent configuration parameters
        
    Returns:
        Configured MockTinyAgent instance
    """
    agent = MockTinyAgent(**kwargs)
    
    # Add mock tools that the real agent would have
    tools = [
        Mock(name="resolve_library_id"),
        Mock(name="get_library_docs"),
        Mock(name="save_documentation"),
        Mock(name="create_symlink")
    ]
    
    for tool in tools:
        agent.add_tool(tool)
    
    return agent


def create_test_project_structure(project_dir: Path, project_type: str = "python") -> None:
    """
    Create a realistic test project structure.
    
    Args:
        project_dir: Path to create project in
        project_type: Type of project (python, javascript, etc.)
    """
    project_dir.mkdir(parents=True, exist_ok=True)
    
    if project_type == "python":
        # Create Python project structure
        (project_dir / "src").mkdir()
        (project_dir / "tests").mkdir()
        
        # Create main Python file
        (project_dir / "src" / "main.py").write_text("""
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
""")
        
        # Create requirements.txt
        (project_dir / "requirements.txt").write_text("""
requests>=2.25.0
flask>=2.0.0
pytest>=7.0.0
black>=22.0.0
""")
        
        # Create pyproject.toml
        (project_dir / "pyproject.toml").write_text("""
[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "requests>=2.25.0",
    "flask>=2.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0"
]
""")


class ErrorSimulator:
    """Utility class for simulating various error conditions."""
    
    @staticmethod
    def create_rate_limit_error():
        """Create a 429 rate limit error."""
        return Exception("429 Too Many Requests")
    
    @staticmethod
    def create_network_error():
        """Create a network connectivity error."""
        return ConnectionError("Failed to establish connection")
    
    @staticmethod
    def create_timeout_error():
        """Create a timeout error."""
        return TimeoutError("Request timed out")
    
    @staticmethod
    def create_api_key_error():
        """Create an API key authentication error."""
        return Exception("401 Unauthorized: Invalid API key")


# Test utilities for assertion patterns
class TestAssertions:
    """Common assertion patterns for dependency resolver tests."""
    
    @staticmethod
    def assert_valid_dependency_list(dependencies: List[Dict[str, Any]]):
        """Assert that a dependency list has valid structure."""
        assert isinstance(dependencies, list)
        for dep in dependencies:
            assert isinstance(dep, dict)
            assert "name" in dep
            assert isinstance(dep["name"], str)
            assert len(dep["name"]) > 0
    
    @staticmethod
    def assert_valid_documentation_content(content: str, dependency_name: str):
        """Assert that documentation content is properly formatted."""
        assert isinstance(content, str)
        assert len(content) > 100  # Should have substantial content
        assert f"# {dependency_name}" in content or f"# {dependency_name.title()}" in content
        assert "##" in content  # Should have sections
    
    @staticmethod
    def assert_valid_file_saved(file_info: Dict[str, Any]):
        """Assert that a file save result has valid structure."""
        assert isinstance(file_info, dict)
        assert "filename" in file_info
        assert "path" in file_info
        assert "dependency" in file_info
        assert file_info["filename"].endswith(".md")
    
    @staticmethod
    def assert_symlink_created(result: Dict[str, Any]):
        """Assert that symlink creation result is valid."""
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "type" in result
        assert result["type"] in ["symlink", "directory"]