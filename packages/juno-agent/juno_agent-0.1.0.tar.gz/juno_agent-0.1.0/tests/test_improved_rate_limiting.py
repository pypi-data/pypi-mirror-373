"""
Tests for improved rate limiting implementation in backend dependency docs API.

This module tests the enhanced rate limiting features including:
- Exponential backoff with jitter
- Proper Retry-After header handling
- Request throttling and batching
- Concurrent request limiting
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
import os

from juno_agent.fancy_ui.setup.backend_dependency_docs_api import BackendDependencyDocsAPI
from juno_agent.fancy_ui.setup.dependency_common import DependencyDocsAPIError


@pytest.fixture
def rate_limited_api():
    """Create API instance with rate limiting configuration."""
    with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
        return BackendDependencyDocsAPI(
            max_retries=3,
            request_delay=0.1,
            max_concurrent_requests=2
        )


class TestImprovedRateLimiting:
    """Test improved rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_request_throttling_enforces_delay(self, rate_limited_api):
        """Test that request throttling enforces minimum delay between requests."""
        
        async def mock_func():
            return "success"
        
        start_time = time.time()
        
        # Make multiple throttled requests
        await rate_limited_api._throttled_request(mock_func)
        await rate_limited_api._throttled_request(mock_func)
        
        elapsed = time.time() - start_time
        
        # Should take at least the request_delay time
        assert elapsed >= rate_limited_api.request_delay

    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self, rate_limited_api):
        """Test that concurrent requests are limited by semaphore."""
        
        call_times = []
        
        async def slow_mock_func():
            call_times.append(time.time())
            await asyncio.sleep(0.2)  # Simulate slow API call
            return "success"
        
        # Start multiple concurrent requests (more than max_concurrent_requests)
        tasks = [
            rate_limited_api._throttled_request(slow_mock_func)
            for _ in range(5)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # All should succeed
        assert all(result == "success" for result in results)
        assert len(call_times) == 5
        
        # With max_concurrent_requests=2, this should take longer than if all ran concurrently
        # But less than if they ran sequentially
        assert total_time > 0.4  # At least 2 batches of 0.2s each
        assert total_time < 1.0  # But not fully sequential (which would be ~1.0s)

    @pytest.mark.asyncio
    async def test_retry_after_header_parsing(self, rate_limited_api):
        """Test extraction of Retry-After values from error messages."""
        
        test_cases = [
            ("Rate limit exceeded. Retry after 60 seconds.", 60.0),
            ("Rate limit exceeded. retry after 30.5 seconds", 30.5),
            ("Rate limit exceeded. 45 seconds", 45.0),
            ("Retry-After: 120", 120.0),
            ("No retry info here", None),
            ("", None)
        ]
        
        for message, expected in test_cases:
            result = rate_limited_api._extract_retry_after(message)
            assert result == expected, f"Failed for message: '{message}'"

    @pytest.mark.asyncio
    async def test_exponential_backoff_with_retry_after(self, rate_limited_api):
        """Test that retry logic respects Retry-After headers."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock 429 response with Retry-After header
            rate_limit_response = Mock()
            rate_limit_response.status_code = 429
            rate_limit_response.headers = {"Retry-After": "2"}
            rate_limit_response.json.return_value = {
                "error": "Rate limit exceeded. Retry after 2 seconds."
            }
            
            # Success response for retry
            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = {"results": [], "total_count": 0}
            
            # First call fails with 429, second succeeds
            mock_client_instance.get.side_effect = [rate_limit_response, success_response]
            
            start_time = time.time()
            
            # This should retry after respecting the Retry-After header
            result = await rate_limited_api._retry_with_backoff(
                rate_limited_api._search_library, "test_query"
            )
            
            elapsed = time.time() - start_time
            
            # Should have waited at least 2 seconds (Retry-After value) plus jitter
            assert elapsed >= 2.0
            assert result == []
            
            # Should have made 2 calls (initial + retry)
            assert mock_client_instance.get.call_count == 2

    @pytest.mark.asyncio
    async def test_batch_processing_with_delays(self, rate_limited_api):
        """Test that batch processing includes delays between batches."""
        
        dependencies = [
            {"name": f"test_lib_{i}", "version": "1.0.0"} for i in range(6)
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock successful responses
            search_response = Mock()
            search_response.status_code = 200
            search_response.json.return_value = {"results": [], "total_count": 0}
            
            mock_client_instance.get.return_value = search_response
            
            start_time = time.time()
            
            # This should process in batches with delays
            result = await rate_limited_api.fetch_dependency_docs(dependencies)
            
            elapsed = time.time() - start_time
            
            # Should include processing time plus inter-batch delays
            expected_min_time = rate_limited_api.request_delay * 2  # Inter-batch delay
            assert elapsed >= expected_min_time
            
            # All dependencies should be processed (returning None due to no matches)
            assert len(result) == 6
            assert all(dep["name"] in result for dep in dependencies)

    @pytest.mark.asyncio
    async def test_enhanced_exponential_backoff(self, rate_limited_api):
        """Test enhanced exponential backoff without Retry-After."""
        
        async def failing_func():
            raise DependencyDocsAPIError("Rate limit exceeded")
        
        start_time = time.time()
        
        with pytest.raises(DependencyDocsAPIError):
            await rate_limited_api._retry_with_backoff(failing_func)
        
        elapsed = time.time() - start_time
        
        # Should have done multiple retries with increasing delays
        # First retry: ~5s, Second retry: ~10s, Third retry: ~20s (with jitter)
        # Total should be at least 25 seconds accounting for jitter variance
        assert elapsed >= 25.0

    @pytest.mark.asyncio
    async def test_successful_retry_after_rate_limit(self, rate_limited_api):
        """Test successful operation after initial rate limiting."""
        
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise DependencyDocsAPIError("Rate limit exceeded. Retry after 0.1 seconds.")
            return "success"
        
        result = await rate_limited_api._retry_with_backoff(mock_func)
        
        assert result == "success"
        assert call_count == 2  # Failed once, then succeeded

    # Test removed - factory no longer exists, rate limiting is now handled directly by BackendDependencyDocsAPI

    @pytest.mark.asyncio
    async def test_error_handling_in_batch_processing(self, rate_limited_api):
        """Test that batch processing handles errors gracefully."""
        
        dependencies = [
            {"name": "good_lib", "version": "1.0.0"},
            {"name": "bad_lib", "version": "1.0.0"},
            {"name": "another_good_lib", "version": "1.0.0"}
        ]
        
        async def mock_fetch(dep):
            if dep.name == "bad_lib":
                raise DependencyDocsAPIError("Simulated API error")
            return None  # No docs found, but no error
        
        with patch.object(rate_limited_api, '_fetch_single_dependency_docs', side_effect=mock_fetch):
            result = await rate_limited_api.fetch_dependency_docs(dependencies)
            
            # Should handle the error and continue with other dependencies
            assert len(result) == 3
            assert "good_lib" in result
            assert "bad_lib" in result
            assert "another_good_lib" in result
            
            # The errored dependency should have None result
            assert result["bad_lib"] is None


@pytest.mark.integration
class TestRateLimitingIntegration:
    """Integration tests for rate limiting with real-like scenarios."""

    @pytest.mark.asyncio
    async def test_high_volume_request_handling(self):
        """Test handling of high volume requests with rate limiting."""
        
        # Create many dependencies to simulate high volume
        dependencies = [
            {"name": f"lib_{i:03d}", "version": "1.0.0"} for i in range(20)
        ]
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            api = BackendDependencyDocsAPI(
                max_retries=2,
                request_delay=0.05,  # Faster for testing
                max_concurrent_requests=3
            )
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                # Mock responses
                search_response = Mock()
                search_response.status_code = 200
                search_response.json.return_value = {"results": [], "total_count": 0}
                
                mock_client_instance.get.return_value = search_response
                
                start_time = time.time()
                result = await api.fetch_dependency_docs(dependencies)
                elapsed = time.time() - start_time
                
                # Should complete all requests
                assert len(result) == 20
                
                # Should have taken reasonable time (not too fast due to throttling)
                assert elapsed >= 0.1  # Some minimum time due to throttling
                
                # Should have made search calls for all dependencies
                assert mock_client_instance.get.call_count >= 20

    @pytest.mark.asyncio
    async def test_mixed_success_failure_scenarios(self):
        """Test scenarios with mixed success and failure responses."""
        
        dependencies = [
            {"name": "success_lib", "version": "1.0.0"},
            {"name": "rate_limited_lib", "version": "1.0.0"},
            {"name": "not_found_lib", "version": "1.0.0"}
        ]
        
        with patch.dict(os.environ, {"ASKBUDI_API_KEY": "test_key"}):
            api = BackendDependencyDocsAPI(
                max_retries=1,
                request_delay=0.05,
                max_concurrent_requests=2
            )
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = mock_client.return_value.__aenter__.return_value
                
                def mock_get(url, **kwargs):
                    if "success_lib" in kwargs.get('params', {}).get('q', ''):
                        response = Mock()
                        response.status_code = 200
                        response.json.return_value = {"results": [{"id": "/test/success", "name": "SuccessLib"}], "total_count": 1}
                        return response
                    elif "rate_limited_lib" in kwargs.get('params', {}).get('q', ''):
                        response = Mock()
                        response.status_code = 429
                        response.headers = {"Retry-After": "1"}
                        response.json.return_value = {"error": "Rate limit exceeded"}
                        return response
                    else:
                        response = Mock()
                        response.status_code = 200
                        response.json.return_value = {"results": [], "total_count": 0}
                        return response
                
                mock_client_instance.get.side_effect = mock_get
                
                result = await api.fetch_dependency_docs(dependencies)
                
                # Should handle mixed scenarios appropriately
                assert len(result) == 3
                assert "success_lib" in result
                assert "rate_limited_lib" in result
                assert "not_found_lib" in result