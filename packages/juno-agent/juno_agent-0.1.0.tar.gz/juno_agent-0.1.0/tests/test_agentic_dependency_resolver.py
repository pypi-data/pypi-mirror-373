"""
Comprehensive behavioral tests for the Agentic Dependency Resolver.

This test suite follows TDD principles and defines the expected behavior
of the Agentic Dependency Resolver before implementation. The resolver
should be an autonomous agent that:
- Scans projects for dependencies
- Searches for relevant documentation using search tools
- Fetches documentation using fetch tools
- Saves documentation with proper naming and structure
- Creates symlinks according to strict rules
- Handles errors gracefully with proper retry mechanisms
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Test fixtures and mock data
@dataclass
class MockSearchResult:
    """Mock search result from dependency search."""
    library_id: str
    name: str
    description: str
    trust_score: int
    snippet_count: int

@dataclass
class MockDocumentationResponse:
    """Mock documentation response from fetch tools."""
    content: str
    source: str
    quality: str
    metadata: Dict[str, Any]

class MockTinyAgent:
    """Mock TinyAgent for testing without actual TinyAgent dependency."""
    
    def __init__(self, **kwargs):
        self.model = kwargs.get('model', 'test-model')
        self.system_prompt = kwargs.get('system_prompt', '')
        self.tools = []
        self.callbacks = []
        self.messages = []
        self.storage = kwargs.get('storage')
        self.session_id = kwargs.get('session_id', 'test-session')
        self.user_id = kwargs.get('user_id', 'test-user')
        
    def add_tool(self, tool):
        self.tools.append(tool)
        
    def add_callback(self, callback):
        self.callbacks.append(callback)
        
    async def run(self, message: str, max_turns: int = 5) -> str:
        # Mock implementation that simulates agent behavior
        self.messages.append({"role": "user", "content": message})
        
        # Simulate agent decision-making based on message content
        if "scan" in message.lower() and "dependencies" in message.lower():
            return await self._mock_dependency_scan_response()
        elif "search" in message.lower() or "find" in message.lower():
            return await self._mock_search_response()
        elif "fetch" in message.lower() or "download" in message.lower():
            return await self._mock_fetch_response()
        else:
            return "I understand you want me to work on dependency resolution."
    
    async def _mock_dependency_scan_response(self) -> str:
        return """I've scanned the project and found these dependencies:
        - requests (Python HTTP library)
        - flask (Python web framework)
        - pytest (Python testing framework)
        
        I'll now search for documentation for these packages."""
    
    async def _mock_search_response(self) -> str:
        return """I found documentation sources for the dependencies:
        - requests: Found in VibeContext MCP server
        - flask: Found in VibeContext MCP server  
        - pytest: Found in VibeContext MCP server
        
        I'll now fetch the documentation."""
    
    async def _mock_fetch_response(self) -> str:
        return """Successfully fetched and saved documentation:
        - requests.md saved to external_context/dependencies/
        - flask.md saved to external_context/dependencies/
        - pytest.md saved to external_context/dependencies/
        
        Created symlinks to project directory."""

@pytest.fixture
def mock_tiny_agent():
    """Fixture providing mock TinyAgent."""
    return MockTinyAgent

@pytest.fixture
def temp_project_dir():
    """Fixture providing temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def temp_askbudi_dir():
    """Fixture providing temporary ASKBUDI directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_requirements_txt():
    """Sample requirements.txt content."""
    return """
requests==2.28.0
flask>=2.0.0
pytest
numpy==1.21.0
# Development dependencies
black
mypy
"""

@pytest.fixture
def sample_pyproject_toml():
    """Sample pyproject.toml content."""
    return """
[build-system]
requires = ["setuptools", "wheel"]

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.95.0"
uvicorn = {extras = ["standard"], version = "^0.21.0"}
pydantic = "^1.10.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
mypy = "^1.0.0"
"""

@pytest.fixture
def mock_search_tool():
    """Mock search tool for testing."""
    async def search_dependencies(search_term: str, limit: int = 10) -> List[MockSearchResult]:
        # Simulate search results
        if search_term.lower() == "requests":
            return [MockSearchResult("/python/requests", "requests", "HTTP library", 9, 25)]
        elif search_term.lower() == "flask":
            return [MockSearchResult("/python/flask", "flask", "Web framework", 9, 30)]
        elif search_term.lower() == "pytest":
            return [MockSearchResult("/python/pytest", "pytest", "Testing framework", 9, 20)]
        else:
            return []
    
    return search_dependencies

@pytest.fixture
def mock_fetch_tool():
    """Mock fetch tool for testing."""
    async def fetch_documentation(library_id: str, prompt: str) -> MockDocumentationResponse:
        # Simulate fetching documentation
        content = f"# {library_id} Documentation\n\nThis is mock documentation for {library_id}."
        return MockDocumentationResponse(
            content=content,
            source="mcp_server",
            quality="mcp_sourced",
            metadata={"library_id": library_id, "prompt": prompt}
        )
    
    return fetch_documentation

class TestAgenticDependencyResolverInitialization:
    """Test agent initialization and configuration."""
    
    def test_agent_initialization_with_correct_system_prompt(self, mock_tiny_agent):
        """
        Test that the agent is initialized with the correct system prompt.
        
        The system prompt should instruct the agent to:
        - Scan projects for dependencies
        - Use search tools to find documentation
        - Use fetch tools to retrieve documentation
        - Save files with proper naming
        - Create symlinks following strict rules
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Mock the actual resolver (to be implemented)
        resolver = AgenticDependencyResolver(project_path="/test/project")
        
        # Verify system prompt contains key instructions
        expected_prompt_elements = [
            "dependency scanning",
            "search for documentation", 
            "fetch documentation",
            "save to external_context",
            "create symlinks",
            "autonomous operation"
        ]
        
        for element in expected_prompt_elements:
            assert element in resolver.system_prompt.lower(), f"System prompt missing: {element}"
    
    def test_agent_initialization_with_required_tools(self, mock_tiny_agent):
        """
        Test that the agent is initialized with required tools.
        
        Required tools:
        - resolve_library_id: For searching dependencies
        - get_library_docs: For fetching documentation  
        - file operations: For saving documentation
        - symlink creation: For project integration
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path="/test/project")
        
        # Verify required tools are registered
        required_tools = [
            "resolve_library_id",
            "get_library_docs", 
            "save_documentation",
            "create_symlink"
        ]
        
        for tool_name in required_tools:
            assert any(tool_name in str(tool) for tool in resolver.agent.tools), \
                f"Required tool not found: {tool_name}"
    
    def test_error_handling_during_initialization(self, mock_tiny_agent):
        """
        Test error handling when initialization fails.
        
        Should handle:
        - Missing API keys gracefully
        - Invalid project paths
        - Tool registration failures
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Test invalid project path
        with pytest.raises(ValueError, match="Invalid project path"):
            AgenticDependencyResolver(project_path="/nonexistent/path")
        
        # Test missing API key
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                AgenticDependencyResolver(project_path="/test/project")

class TestDependencyScanning:
    """Test automatic dependency scanning capabilities."""
    
    async def test_python_requirements_txt_scanning(self, temp_project_dir, sample_requirements_txt, mock_tiny_agent):
        """
        Test scanning Python project with requirements.txt.
        
        Should identify:
        - All dependencies listed in requirements.txt
        - Version constraints
        - Comments and development dependencies
        - Proper parsing of different formats
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Create test project structure
        requirements_file = temp_project_dir / "requirements.txt"
        requirements_file.write_text(sample_requirements_txt)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.scan_dependencies()
        
        # Verify dependencies were found
        expected_deps = ["requests", "flask", "pytest", "numpy", "black", "mypy"]
        assert result["success"] is True
        assert len(result["dependencies"]) == len(expected_deps)
        
        for dep in expected_deps:
            assert any(d["name"] == dep for d in result["dependencies"]), \
                f"Dependency not found: {dep}"
    
    async def test_python_pyproject_toml_scanning(self, temp_project_dir, sample_pyproject_toml, mock_tiny_agent):
        """
        Test scanning Python project with pyproject.toml.
        
        Should identify:
        - Main dependencies
        - Development dependencies  
        - Optional dependencies with extras
        - Poetry/setuptools format handling
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Create test project structure
        pyproject_file = temp_project_dir / "pyproject.toml"
        pyproject_file.write_text(sample_pyproject_toml)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.scan_dependencies()
        
        # Verify dependencies were found
        expected_deps = ["fastapi", "uvicorn", "pydantic", "pytest", "black", "mypy"]
        assert result["success"] is True
        assert len(result["dependencies"]) >= len(expected_deps)
        
        for dep in expected_deps:
            assert any(d["name"] == dep for d in result["dependencies"]), \
                f"Dependency not found: {dep}"
    
    async def test_mixed_dependency_files(self, temp_project_dir, sample_requirements_txt, sample_pyproject_toml, mock_tiny_agent):
        """
        Test scanning project with both requirements.txt and pyproject.toml.
        
        Should:
        - Merge dependencies from both files
        - Remove duplicates intelligently
        - Prioritize pyproject.toml versions when conflicts exist
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Create both files
        (temp_project_dir / "requirements.txt").write_text(sample_requirements_txt)
        (temp_project_dir / "pyproject.toml").write_text(sample_pyproject_toml)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.scan_dependencies()
        
        # Verify merged results
        assert result["success"] is True
        dependency_names = [d["name"] for d in result["dependencies"]]
        
        # Should have dependencies from both files
        assert "requests" in dependency_names  # from requirements.txt
        assert "fastapi" in dependency_names   # from pyproject.toml
        
        # Should not have duplicates
        assert len(dependency_names) == len(set(dependency_names)), \
            "Duplicate dependencies found"
    
    async def test_no_dependency_files_found(self, temp_project_dir, mock_tiny_agent):
        """
        Test behavior when no dependency files are found.
        
        Should:
        - Return empty dependency list
        - Log appropriate warning
        - Not fail the process
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.scan_dependencies()
        
        assert result["success"] is True
        assert result["dependencies"] == []
        assert "No dependency files found" in result["message"]

class TestDependencySearching:
    """Test autonomous searching for dependency documentation."""
    
    async def test_successful_dependency_search(self, mock_search_tool, mock_tiny_agent):
        """
        Test successful search for dependency documentation.
        
        Should:
        - Use resolve_library_id tool for each dependency
        - Select best matches based on trust score and relevance
        - Handle multiple search results appropriately
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = ["requests", "flask", "pytest"]
        
        with patch('juno_agent.agentic_dependency_resolver.resolve_library_id') as mock_resolve:
            mock_resolve.side_effect = mock_search_tool
            
            resolver = AgenticDependencyResolver(project_path="/test/project")
            result = await resolver.search_for_dependencies(dependencies)
            
            assert result["success"] is True
            assert len(result["found"]) == 3
            assert len(result["not_found"]) == 0
            
            # Verify search was called for each dependency
            assert mock_resolve.call_count == 3
    
    async def test_partial_search_results(self, mock_search_tool, mock_tiny_agent):
        """
        Test behavior when some dependencies are not found.
        
        Should:
        - Continue searching for other dependencies
        - Report found and not found separately
        - Provide clear feedback about missing documentation
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = ["requests", "unknown_package", "flask"]
        
        async def partial_search(search_term: str, limit: int = 10):
            if search_term == "unknown_package":
                return []
            return await mock_search_tool(search_term, limit)
        
        with patch('juno_agent.agentic_dependency_resolver.resolve_library_id') as mock_resolve:
            mock_resolve.side_effect = partial_search
            
            resolver = AgenticDependencyResolver(project_path="/test/project")
            result = await resolver.search_for_dependencies(dependencies)
            
            assert result["success"] is True
            assert len(result["found"]) == 2
            assert len(result["not_found"]) == 1
            assert "unknown_package" in result["not_found"]
    
    async def test_search_tool_error_handling(self, mock_tiny_agent):
        """
        Test error handling when search tools fail.
        
        Should:
        - Handle API rate limits (429 errors) with retry
        - Handle network errors gracefully
        - Continue with other dependencies when one fails
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = ["requests", "flask"]
        
        # Simulate 429 error then success
        call_count = 0
        async def rate_limited_search(search_term: str, limit: int = 10):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("429 Too Many Requests")
            return [MockSearchResult(f"/python/{search_term}", search_term, "Description", 9, 20)]
        
        with patch('juno_agent.agentic_dependency_resolver.resolve_library_id') as mock_resolve:
            mock_resolve.side_effect = rate_limited_search
            
            resolver = AgenticDependencyResolver(project_path="/test/project")
            
            # Should retry and eventually succeed
            result = await resolver.search_for_dependencies(dependencies)
            
            # First dependency should succeed after retry
            assert len(result["found"]) >= 1

class TestDocumentationFetching:
    """Test autonomous fetching of dependency documentation."""
    
    async def test_successful_documentation_fetch(self, mock_fetch_tool, temp_project_dir, mock_tiny_agent):
        """
        Test successful fetching and saving of documentation.
        
        Should:
        - Use get_library_docs tool for each found dependency
        - Save documentation with proper file naming
        - Create directory structure automatically
        - Save content in markdown format
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = [
            {"library_id": "/python/requests", "name": "requests"},
            {"library_id": "/python/flask", "name": "flask"}
        ]
        
        with patch('juno_agent.agentic_dependency_resolver.get_library_docs') as mock_fetch:
            mock_fetch.side_effect = mock_fetch_tool
            
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            result = await resolver.fetch_documentation(dependencies)
            
            assert result["success"] is True
            assert len(result["saved_files"]) == 2
            
            # Verify files were saved
            docs_dir = temp_project_dir / "external_context" / "dependencies"
            assert (docs_dir / "requests.md").exists()
            assert (docs_dir / "flask.md").exists()
    
    async def test_documentation_content_formatting(self, mock_fetch_tool, temp_project_dir, mock_tiny_agent):
        """
        Test that saved documentation is properly formatted.
        
        Should:
        - Save as markdown with proper headers
        - Include metadata (source, fetch time, etc.)
        - Include code examples and usage instructions
        - Format content for readability
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = [{"library_id": "/python/requests", "name": "requests"}]
        
        with patch('juno_agent.agentic_dependency_resolver.get_library_docs') as mock_fetch:
            mock_fetch.side_effect = mock_fetch_tool
            
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            await resolver.fetch_documentation(dependencies)
            
            # Check file content
            doc_file = temp_project_dir / "external_context" / "dependencies" / "requests.md"
            content = doc_file.read_text()
            
            # Verify markdown formatting
            assert content.startswith("# ")
            assert "## Metadata" in content
            assert "Source:" in content
            assert "Fetched:" in content
    
    async def test_file_naming_sanitization(self, mock_fetch_tool, temp_project_dir, mock_tiny_agent):
        """
        Test that dependency names are properly sanitized for filenames.
        
        Should handle:
        - Special characters in dependency names
        - Scoped packages (@angular/core -> angular-core.md)
        - URL-like dependencies (github.com/user/repo -> repo.md)
        - Version suffixes and git references
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = [
            {"library_id": "/npm/@angular/core", "name": "@angular/core"},
            {"library_id": "/python/package-name", "name": "package-name"},
            {"library_id": "/go/github.com/gin-gonic/gin", "name": "github.com/gin-gonic/gin"}
        ]
        
        with patch('juno_agent.agentic_dependency_resolver.get_library_docs') as mock_fetch:
            mock_fetch.side_effect = mock_fetch_tool
            
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            result = await resolver.fetch_documentation(dependencies)
            
            # Verify sanitized filenames
            expected_files = [
                "angular-core.md",      # @angular/core
                "package-name.md",      # package-name  
                "gin.md"               # github.com/gin-gonic/gin
            ]
            
            docs_dir = temp_project_dir / "external_context" / "dependencies"
            for filename in expected_files:
                assert (docs_dir / filename).exists(), f"File not found: {filename}"
    
    async def test_fetch_error_handling(self, temp_project_dir, mock_tiny_agent):
        """
        Test error handling during documentation fetching.
        
        Should:
        - Handle 429 rate limit errors with wait and retry
        - Handle network timeouts gracefully
        - Continue with other dependencies when one fails
        - Not crash on malformed responses
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = [
            {"library_id": "/python/requests", "name": "requests"},
            {"library_id": "/python/failing_package", "name": "failing_package"}
        ]
        
        # Simulate errors
        async def error_fetch(library_id: str, prompt: str):
            if "failing_package" in library_id:
                if "429" in library_id:
                    raise Exception("429 Too Many Requests")
                else:
                    raise Exception("Network timeout")
            return await mock_fetch_tool(library_id, prompt)
        
        with patch('juno_agent.agentic_dependency_resolver.get_library_docs') as mock_fetch:
            mock_fetch.side_effect = error_fetch
            
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            result = await resolver.fetch_documentation(dependencies)
            
            # Should have partial success
            assert len(result["saved_files"]) >= 1
            assert len(result["failed_saves"]) >= 1

class TestSymlinkCreation:
    """Test symlink creation following strict rules."""
    
    def test_symlink_creation_to_askbudi_directory(self, temp_project_dir, temp_askbudi_dir, mock_tiny_agent):
        """
        Test creation of symlinks to ASKBUDI directory structure.
        
        Should:
        - Create symlink from project/external_context to ~/.ASKBUDI/{project}/external_context
        - Handle project name generation correctly
        - Create ASKBUDI directory structure if it doesn't exist
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        with patch('pathlib.Path.home', return_value=temp_askbudi_dir.parent):
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            result = resolver.create_symlink()
            
            assert result["success"] is True
            
            # Verify symlink exists
            symlink_path = temp_project_dir / "external_context"
            assert symlink_path.exists() or symlink_path.is_symlink()
            
            # Verify ASKBUDI directory structure
            project_name = resolver._generate_project_name(temp_project_dir)
            askbudi_path = temp_askbudi_dir / ".ASKBUDI" / project_name / "external_context"
            assert askbudi_path.exists()
    
    def test_symlink_fallback_to_regular_directory(self, temp_project_dir, mock_tiny_agent):
        """
        Test fallback to regular directory when symlink creation fails.
        
        Should:
        - Create regular directory when symlink fails
        - Copy existing content from ASKBUDI directory
        - Log appropriate warnings
        - Continue operation successfully
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Mock symlink creation failure
        with patch('os.symlink', side_effect=OSError("Permission denied")):
            resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
            result = resolver.create_symlink()
            
            # Should fallback successfully
            assert result["success"] is True
            assert result["type"] == "directory"  # Not symlink
            
            # Directory should exist
            context_dir = temp_project_dir / "external_context"
            assert context_dir.exists()
            assert context_dir.is_dir()
    
    def test_cross_platform_symlink_creation(self, temp_project_dir, mock_tiny_agent):
        """
        Test symlink creation works across platforms.
        
        Should:
        - Use os.symlink on Unix/Mac
        - Use mklink on Windows
        - Handle platform-specific errors gracefully
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        
        # Test Unix/Mac path
        with patch('sys.platform', 'darwin'):
            with patch('os.symlink') as mock_symlink:
                resolver._create_platform_symlink("source", "target")
                mock_symlink.assert_called_once_with("source", "target")
        
        # Test Windows path
        with patch('sys.platform', 'win32'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                result = resolver._create_platform_symlink("source", "target")
                assert result is True
                mock_run.assert_called_once()

class TestErrorHandlingAndRetryLogic:
    """Test comprehensive error handling and retry mechanisms."""
    
    async def test_rate_limit_handling_429_errors(self, mock_tiny_agent):
        """
        Test handling of 429 rate limit errors.
        
        Should:
        - Detect 429 errors from API calls
        - Implement exponential backoff retry
        - Wait appropriate time between retries
        - Eventually succeed or fail gracefully after max retries
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path="/test/project")
        
        # Test retry mechanism
        call_count = 0
        async def rate_limited_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("429 Too Many Requests")
            return "Success"
        
        result = await resolver._retry_with_backoff(rate_limited_call, max_retries=3)
        assert result == "Success"
        assert call_count == 3
    
    async def test_network_error_handling(self, mock_tiny_agent):
        """
        Test handling of network and connection errors.
        
        Should:
        - Handle connection timeouts
        - Handle DNS resolution failures
        - Handle SSL certificate errors
        - Provide meaningful error messages
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path="/test/project")
        
        # Simulate network errors
        async def network_error():
            raise ConnectionError("Failed to connect to server")
        
        with pytest.raises(ConnectionError):
            await resolver._retry_with_backoff(network_error, max_retries=1)
    
    async def test_partial_failure_handling(self, temp_project_dir, mock_tiny_agent):
        """
        Test handling of partial failures in batch operations.
        
        Should:
        - Continue processing when some dependencies fail
        - Report successful and failed operations separately
        - Provide detailed error information
        - Not fail entire process due to individual failures
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        dependencies = ["requests", "failing_package", "flask"]
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        
        # Mock mixed success/failure scenario
        with patch.object(resolver, '_process_single_dependency') as mock_process:
            async def mixed_results(dep):
                if dep == "failing_package":
                    raise Exception("Processing failed")
                return {"name": dep, "status": "success"}
            
            mock_process.side_effect = mixed_results
            
            result = await resolver.process_dependencies(dependencies)
            
            assert len(result["successful"]) == 2
            assert len(result["failed"]) == 1

class TestCLIEntryPoints:
    """Test command-line interface behaviors."""
    
    async def test_dependency_only_parameter(self, temp_project_dir, sample_requirements_txt, mock_tiny_agent):
        """
        Test dependency_only=True parameter behavior.
        
        Should:
        - Only scan and identify dependencies
        - Skip documentation fetching
        - Skip symlink creation
        - Return dependency list
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        (temp_project_dir / "requirements.txt").write_text(sample_requirements_txt)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.run(dependency_only=True)
        
        assert "dependencies" in result
        assert len(result["dependencies"]) > 0
        assert "documentation_fetched" not in result
        assert "symlinks_created" not in result
    
    async def test_docs_only_flag(self, temp_project_dir, mock_tiny_agent):
        """
        Test --docs-only flag behavior.
        
        Should:
        - Skip dependency scanning
        - Accept provided dependency list
        - Fetch documentation for provided dependencies
        - Create symlinks
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        provided_dependencies = ["requests", "flask", "pytest"]
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.run(docs_only=provided_dependencies)
        
        assert "scanning_skipped" in result
        assert result["provided_dependencies"] == provided_dependencies
        assert "documentation_fetched" in result
        assert "symlinks_created" in result
    
    async def test_invalid_project_structure_handling(self, temp_project_dir, mock_tiny_agent):
        """
        Test behavior with invalid or empty project structures.
        
        Should:
        - Handle missing project files gracefully
        - Provide helpful error messages
        - Suggest next steps to user
        - Not crash or fail silently
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Empty project directory
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.run()
        
        assert result["success"] is True  # Should not fail
        assert "no_dependencies_found" in result
        assert len(result["dependencies"]) == 0
        assert "suggestion" in result
    
    async def test_output_formatting_and_verbosity(self, temp_project_dir, sample_requirements_txt, mock_tiny_agent):
        """
        Test output formatting and verbosity levels.
        
        Should:
        - Provide different verbosity levels
        - Format output appropriately for console
        - Include progress indicators
        - Show summary statistics
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        (temp_project_dir / "requirements.txt").write_text(sample_requirements_txt)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        
        # Test verbose output
        result = await resolver.run(verbose=True)
        assert "detailed_log" in result
        
        # Test quiet output
        result = await resolver.run(verbose=False)
        assert "summary" in result
        assert len(result["summary"]) < 500  # Brief summary

class TestIntegrationWithExistingSystems:
    """Test integration with existing juno-agent systems."""
    
    def test_config_manager_integration(self, temp_project_dir, mock_tiny_agent):
        """
        Test integration with ConfigManager.
        
        Should:
        - Use existing project configuration
        - Respect configured API keys
        - Use configured working directory
        - Save results to project config
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Mock config manager
        mock_config = Mock()
        mock_config.workdir = temp_project_dir
        mock_config.get_model_api_key.return_value = "test-key"
        
        resolver = AgenticDependencyResolver(
            project_path=str(temp_project_dir),
            config_manager=mock_config
        )
        
        assert resolver.config_manager == mock_config
        assert resolver.project_path == temp_project_dir
    
    def test_external_context_manager_integration(self, temp_project_dir, mock_tiny_agent):
        """
        Test integration with ExternalContextManager.
        
        Should:
        - Use existing external context structure
        - Follow established directory conventions
        - Update index files appropriately
        - Maintain compatibility with existing tools
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        
        # Verify external context manager is used
        assert hasattr(resolver, 'context_manager')
        assert resolver.context_manager.project_path == temp_project_dir
    
    def test_textual_worker_pattern_integration(self, mock_tiny_agent):
        """
        Test integration with Textual Worker pattern for UI responsiveness.
        
        Should:
        - Run as background worker when called from UI
        - Provide progress updates to UI
        - Handle cancellation gracefully
        - Return results to main thread
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        resolver = AgenticDependencyResolver(project_path="/test/project")
        
        # Mock UI callback
        ui_updates = []
        def mock_ui_callback(event, data):
            ui_updates.append((event, data))
        
        resolver.set_ui_callback(mock_ui_callback)
        
        # Verify callback is registered
        assert resolver.ui_callback == mock_ui_callback

class TestAgentBehaviorValidation:
    """Test that agent behaves autonomously as expected."""
    
    async def test_agent_decision_making_process(self, temp_project_dir, sample_requirements_txt, mock_tiny_agent):
        """
        Test agent's autonomous decision-making process.
        
        Should:
        - Analyze project structure independently
        - Make decisions about which tools to use
        - Prioritize dependencies based on importance
        - Handle ambiguous situations appropriately
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        (temp_project_dir / "requirements.txt").write_text(sample_requirements_txt)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        
        # Capture agent's decision process
        decisions = []
        def track_decisions(decision, context):
            decisions.append((decision, context))
        
        resolver.set_decision_tracker(track_decisions)
        
        await resolver.run()
        
        # Verify autonomous decisions were made
        assert len(decisions) > 0
        decision_types = [d[0] for d in decisions]
        assert "scan_method" in decision_types
        assert "search_strategy" in decision_types
    
    async def test_agent_adaptation_to_project_type(self, temp_project_dir, mock_tiny_agent):
        """
        Test agent adapts behavior based on project type.
        
        Should:
        - Identify project language/type automatically
        - Adjust search strategies accordingly
        - Use language-specific documentation sources
        - Apply appropriate file naming conventions
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Test Python project
        (temp_project_dir / "requirements.txt").write_text("requests==2.28.0")
        (temp_project_dir / "main.py").write_text("import requests")
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.run()
        
        assert result["detected_language"] == "python"
        assert result["search_strategy"] == "python_packages"
    
    async def test_agent_handles_complex_scenarios(self, temp_project_dir, mock_tiny_agent):
        """
        Test agent handles complex real-world scenarios.
        
        Should:
        - Handle mixed dependency sources
        - Resolve version conflicts appropriately
        - Manage large dependency lists efficiently
        - Make intelligent prioritization decisions
        """
        from juno_agent.agentic_dependency_resolver import AgenticDependencyResolver
        
        # Complex requirements with conflicts
        complex_requirements = """
# Core dependencies
requests>=2.25.0,<3.0.0
flask>=2.0.0
django>=4.0.0

# Development
pytest>=7.0.0
black>=22.0.0
mypy>=0.900

# Optional dependencies
numpy>=1.20.0; sys_platform != "win32"
pandas>=1.3.0; python_version >= "3.8"

# Git dependencies  
git+https://github.com/user/repo.git@v1.2.3#egg=custom_package
-e git+ssh://git@github.com/user/private.git#egg=private_package
"""
        
        (temp_project_dir / "requirements.txt").write_text(complex_requirements)
        
        resolver = AgenticDependencyResolver(project_path=str(temp_project_dir))
        result = await resolver.run()
        
        # Verify complex scenario handling
        assert result["success"] is True
        assert len(result["dependencies"]) > 5
        assert "complex_dependencies_handled" in result