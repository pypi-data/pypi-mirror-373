"""
Behavioral tests for backend dependency documentation API integration.

Following TDD principles, these tests define the expected behaviors of the real
backend integration before implementation.
"""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, List, Any, Optional
import httpx

from juno_agent.fancy_ui.setup.dependency_common import DependencyInfo, DependencyDocsAPIError


# Test data fixtures

@pytest.fixture
def backend_search_response():
    """Mock backend search API response."""
    return {
        "results": [
            {
                "id": "/websites/textual",
                "name": "Textual",
                "description": "TUI framework for Python",
                "trust_score": 8.5,
                "stars": 25000,
                "last_updated": "2025-08-07T23:10:27.913Z",
                "cached": True
            },
            {
                "id": "/packages/fastapi",
                "name": "FastAPI",
                "description": "Fast web framework for Python",
                "trust_score": 9.2,
                "stars": 70000,
                "last_updated": "2025-08-07T20:15:30.456Z",
                "cached": True
            }
        ],
        "total_count": 2,
        "query": "textual",
        "from_cache": True
    }


@pytest.fixture
def backend_docs_response():
    """Mock backend documentation fetch response."""
    return {
        "library_id": "/websites/textual",
        "library_name": "Textual",
        "version": "latest",
        "content": "# Textual Documentation\n\nTextual is a TUI framework...",
        "trust_score": 8.5,
        "stars": 25000,
        "last_updated": "2025-08-07T23:10:27.913Z",
        "cached_at": "2025-08-07T23:10:27.913Z",
        "from_cache": True
    }


@pytest.fixture
def backend_error_responses():
    """Mock backend error responses."""
    return {
        "unauthorized": {
            "error": "Authorization header is required",
            "error_code": "UNAUTHORIZED"
        },
        "not_found": {
            "error": "Library not found",
            "error_code": "NOT_FOUND"
        },
        "rate_limit": {
            "error": "Rate limit exceeded. Try again in 60 seconds",
            "error_code": "RATE_LIMIT_EXCEEDED"
        },
        "validation_error": {
            "error": "Query parameter q is required",
            "error_code": "VALIDATION_ERROR"
        }
    }


@pytest.fixture
def test_dependencies():
    """Test dependency data."""
    return [
        {"name": "textual", "version": "0.70.0"},
        {"name": "fastapi", "version": "0.104.0"},
        {"name": "requests", "version": "2.31.0"},
        {"name": "unknown_package", "version": "1.0.0"}
    ]


class TestBackendDependencyDocsAPIBehaviors:
    """
    Test behaviors that the backend integration must implement.
    
    These tests define the expected behavior contract that the real
    backend API implementation must fulfill.
    """

    @pytest.mark.asyncio
    async def test_should_authenticate_with_bearer_token(self):
        """
        BEHAVIOR: Backend API should authenticate using Bearer token from ASKBUDI_API_KEY.
        
        The API must:
        1. Read API key from environment variable
        2. Send Authorization: Bearer {key} header
        3. Reject requests without valid authentication
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        # Test with valid API key
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_valid_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"results": [], "total_count": 0}
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                api = BackendDependencyDocsAPI()
                await api._search_library("test_query")
                
                # Verify Bearer token was sent
                mock_client.return_value.__aenter__.return_value.get.assert_called_once()
                call_kwargs = mock_client.return_value.__aenter__.return_value.get.call_args[1]
                assert "headers" in call_kwargs
                assert call_kwargs["headers"]["Authorization"] == "Bearer test_valid_key"

    @pytest.mark.asyncio
    async def test_should_handle_missing_api_key_gracefully(self):
        """
        BEHAVIOR: API should handle missing API key with clear error.
        
        When ASKBUDI_API_KEY is not set, the API should:
        1. Raise a clear error during initialization or first use
        2. Provide helpful guidance on how to set the key
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(DependencyDocsAPIError, match="ASKBUDI_API_KEY"):
                api = BackendDependencyDocsAPI()
                await api._search_library("test")

    @pytest.mark.asyncio
    async def test_should_search_before_fetching_docs(self, backend_search_response, backend_docs_response):
        """
        BEHAVIOR: API should search for library first, then fetch documentation.
        
        The workflow must be:
        1. Search for library by name using /search endpoint
        2. Extract library_id from search results
        3. Fetch documentation using /docs/{library_id} endpoint
        4. Handle cases where library is not found in search
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock search response
                search_response = Mock()
                search_response.status_code = 200
                search_response.json.return_value = backend_search_response
                
                # Mock docs response
                docs_response = Mock()
                docs_response.status_code = 200
                docs_response.json.return_value = backend_docs_response
                
                # Configure mock to return different responses for different URLs
                def mock_get(url, **kwargs):
                    if "/search" in url:
                        return search_response
                    elif "/docs/" in url:
                        return docs_response
                    else:
                        raise ValueError(f"Unexpected URL: {url}")
                
                mock_client_instance.get = AsyncMock(side_effect=mock_get)
                
                api = BackendDependencyDocsAPI()
                dep_info = DependencyInfo(name="textual", version="0.70.0")
                result = await api._fetch_single_dependency_docs(dep_info)
                
                assert result is not None
                assert "Textual Documentation" in result
                
                # Verify both search and docs endpoints were called
                assert mock_client_instance.get.call_count == 2
                calls = mock_client_instance.get.call_args_list
                
                # First call should be search
                search_call = calls[0]
                assert "/search" in search_call[0][0]
                
                # Second call should be docs fetch
                docs_call = calls[1]
                assert "/docs/" in docs_call[0][0]

    @pytest.mark.asyncio
    async def test_should_handle_library_not_found_in_search(self):
        """
        BEHAVIOR: API should handle when library is not found in search results.
        
        When search returns no results:
        1. Should not attempt to fetch documentation
        2. Should return None for that dependency
        3. Should log appropriate warning
        4. Should continue processing other dependencies
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock empty search response
                search_response = Mock()
                search_response.status_code = 200
                search_response.json.return_value = {"results": [], "total_count": 0}
                
                mock_client_instance.get.return_value = search_response
                
                api = BackendDependencyDocsAPI()
                dep_info = DependencyInfo(name="nonexistent_library", version="1.0.0")
                result = await api._fetch_single_dependency_docs(dep_info)
                
                assert result is None
                # Should only call search endpoint, not docs endpoint
                assert mock_client_instance.get.call_count == 1

    @pytest.mark.asyncio
    async def test_should_handle_rate_limiting_with_retry(self, backend_error_responses):
        """
        BEHAVIOR: API should handle rate limiting with exponential backoff retry.
        
        When receiving 429 Rate Limited:
        1. Should respect Retry-After header if present
        2. Should implement exponential backoff
        3. Should retry up to configured maximum attempts
        4. Should eventually fail with clear error message
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock rate limit response
                rate_limit_response = Mock()
                rate_limit_response.status_code = 429
                rate_limit_response.headers = {"Retry-After": "60"}
                rate_limit_response.json.return_value = backend_error_responses["rate_limit"]
                
                mock_client_instance.get.return_value = rate_limit_response
                
                api = BackendDependencyDocsAPI(max_retries=2)
                
                with pytest.raises(DependencyDocsAPIError, match="Rate limit exceeded"):
                    await api._retry_with_backoff(api._search_library, "test_query")
                
                # Should have retried multiple times (initial + 2 retries = 3 total)
                assert mock_client_instance.get.call_count >= 3

    # Test removed - interface compatibility test no longer needed as mock API was removed

    @pytest.mark.asyncio
    async def test_should_handle_network_errors_gracefully(self):
        """
        BEHAVIOR: API should handle network errors with proper fallback.
        
        Network issues should:
        1. Be caught and wrapped in DependencyDocsAPIError
        2. Include helpful error messages
        3. Allow partial success (some deps succeed, others fail)
        4. Log errors appropriately
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock network error
                mock_client_instance.get.side_effect = httpx.NetworkError("Connection failed")
                
                api = BackendDependencyDocsAPI()
                dep_info = DependencyInfo(name="test_lib", version="1.0.0")
                
                # Should handle network error gracefully
                with pytest.raises(DependencyDocsAPIError, match="Connection failed"):
                    result = await api._fetch_single_dependency_docs(dep_info)

    @pytest.mark.asyncio
    async def test_should_cache_responses_appropriately(self, backend_docs_response):
        """
        BEHAVIOR: API should implement intelligent caching.
        
        Caching behavior should:
        1. Cache successful documentation fetches
        2. Respect cache timeout settings
        3. Allow cache clearing
        4. Skip network requests for cached items
        5. Provide cache statistics
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock responses
                search_response = Mock()
                search_response.status_code = 200
                search_response.json.return_value = {
                    "results": [{"id": "/test/library", "name": "TestLib"}], 
                    "total_count": 1
                }
                
                docs_response = Mock()
                docs_response.status_code = 200
                docs_response.json.return_value = backend_docs_response
                
                def mock_get(url, **kwargs):
                    if "/search" in url:
                        return search_response
                    elif "/docs/" in url:
                        return docs_response
                
                mock_client_instance.get = AsyncMock(side_effect=mock_get)
                
                api = BackendDependencyDocsAPI(cache_enabled=True)
                dep_info = DependencyInfo(name="testlib", version="1.0.0")
                
                # First call should hit network
                result1 = await api._fetch_single_dependency_docs(dep_info)
                assert result1 is not None
                initial_call_count = mock_client_instance.get.call_count
                
                # Second call should use cache
                result2 = await api._fetch_single_dependency_docs(dep_info)
                assert result2 == result1
                assert mock_client_instance.get.call_count == initial_call_count  # No new calls
                
                # Cache stats should reflect cached item
                stats = api.get_cache_stats()
                assert stats["cached_items"] > 0

    @pytest.mark.asyncio
    async def test_should_handle_malformed_responses(self):
        """
        BEHAVIOR: API should handle malformed JSON responses gracefully.
        
        When backend returns invalid data:
        1. Should catch JSON parsing errors
        2. Should log the issue appropriately
        3. Should return None for affected dependencies
        4. Should continue processing other dependencies
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock malformed JSON response
                bad_response = Mock()
                bad_response.status_code = 200
                bad_response.json.side_effect = ValueError("Invalid JSON")
                
                mock_client_instance.get.return_value = bad_response
                
                api = BackendDependencyDocsAPI()
                
                # Should handle malformed response gracefully
                result = await api._search_library("test_query")
                assert result == []  # Should return empty list for malformed search

    @pytest.mark.asyncio
    async def test_should_support_environment_configuration(self):
        """
        BEHAVIOR: API should support environment-based configuration.
        
        Configuration should support:
        1. VIBE_CONTEXT_BACKEND_URL for backend URL (default: localhost:3000)
        2. ASKBUDI_API_KEY for authentication
        3. Timeout configurations
        4. Cache settings
        5. Retry configurations
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        custom_url = "https://custom.backend.com"
        custom_timeout = 30.0
        
        with patch.dict(os.environ, {
            "ASKBUDI_API_KEY": "test_key",
            "VIBE_CONTEXT_BACKEND_URL": custom_url
        }):
            api = BackendDependencyDocsAPI(timeout=custom_timeout)
            
            # Should use custom configuration (with trailing slash normalized)
            expected_url = custom_url if custom_url.endswith('/') else custom_url + '/'
            assert api.base_url == expected_url
            assert api.timeout == custom_timeout

    @pytest.mark.asyncio
    async def test_should_provide_health_check_functionality(self):
        """
        BEHAVIOR: API should provide health check to verify backend connectivity.
        
        Health check should:
        1. Test authentication with backend
        2. Return boolean status
        3. Handle various error conditions
        4. Be fast and lightweight
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock successful health check response
                health_response = Mock()
                health_response.status_code = 200
                health_response.json.return_value = {"status": "healthy"}
                
                mock_client_instance.get.return_value = health_response
                
                api = BackendDependencyDocsAPI()
                health_status = await api.health_check()
                
                assert health_status is True
                
                # Test failure case
                mock_client_instance.get.side_effect = httpx.NetworkError("Connection failed")
                health_status = await api.health_check()
                
                assert health_status is False


class TestBackendDependencyDocsAPIIntegration:
    """
    Integration tests that verify the backend API works with the full setup workflow.
    
    These tests ensure the backend integration doesn't break existing functionality.
    """

    @pytest.mark.asyncio
    async def test_integration_with_setup_workflow(self, test_dependencies):
        """
        BEHAVIOR: Backend API should integrate seamlessly with setup workflow.
        
        Integration requirements:
        1. Should work with existing DependencyScanner
        2. Should integrate with ExternalContextManager
        3. Should maintain existing error handling patterns
        4. Should work with setup progress tracking
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                # Mock successful responses
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                search_response = Mock()
                search_response.status_code = 200
                search_response.json.return_value = {"results": [], "total_count": 0}
                
                mock_client_instance.get.return_value = search_response
                
                api = BackendDependencyDocsAPI()
                
                # Should handle the same input format as mock API
                result = await api.fetch_dependency_docs(test_dependencies)
                
                # Should return results in expected format
                assert isinstance(result, dict)
                assert len(result) == len(test_dependencies)
                
                # All results should be None (no matches in mock response)
                for dep_name, docs in result.items():
                    assert docs is None or isinstance(docs, str)

    @pytest.mark.asyncio
    async def test_graceful_fallback_when_backend_unavailable(self, test_dependencies):
        """
        BEHAVIOR: System should have fallback strategy when backend is unavailable.
        
        When backend is down:
        1. Should detect connection issues
        2. Should provide clear error messages
        3. Should allow setup to continue with warnings
        4. Should not crash the setup process
        """
        from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            with patch('httpx.AsyncClient') as mock_client:
                # Mock connection failure
                mock_client.return_value.__aenter__.side_effect = httpx.ConnectError("Connection refused")
                
                api = BackendDependencyDocsAPI()
                
                # Should handle connection failure gracefully - returns None for all deps
                result = await api.fetch_dependency_docs(test_dependencies)
                
                # All dependencies should return None due to connection failures
                assert isinstance(result, dict)
                for dep_name in ["textual", "fastapi", "requests", "unknown_package"]:
                    assert dep_name in result
                    assert result[dep_name] is None