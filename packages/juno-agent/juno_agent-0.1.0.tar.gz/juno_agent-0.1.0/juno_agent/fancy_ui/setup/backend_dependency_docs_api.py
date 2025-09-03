"""
Backend API client for VibeContext Library Documentation service.

This module provides a real implementation that connects to the VibeContext
backend service for fetching dependency documentation, replacing the mock
implementation when configured.
"""

import asyncio
import logging
import os
import random
from typing import Dict, List, Optional, Any
import httpx
from urllib.parse import urljoin, quote
import time

from .dependency_common import DependencyInfo, DependencyDocsAPIError


logger = logging.getLogger(__name__)


class BackendDependencyDocsAPI:
    """
    Real backend API client for fetching dependency documentation.
    
    This implementation connects to the VibeContext backend service and follows
    the search-first-then-fetch pattern documented in the integration guide.
    """
    
    def __init__(
        self, 
        cache_enabled: bool = True, 
        timeout: float = 30.0,
        max_retries: int = 3,
        base_url: Optional[str] = None,
        request_delay: float = 0.1,
        max_concurrent_requests: int = 3
    ):
        """
        Initialize the backend dependency docs API client.
        
        Args:
            cache_enabled: Whether to enable caching of documentation
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for rate limiting
            base_url: Backend URL (defaults to environment variable or localhost:3000)
        """
        self.cache_enabled = cache_enabled
        self.timeout = timeout
        self.max_retries = max_retries
        self.request_delay = request_delay
        self.max_concurrent_requests = max_concurrent_requests
        self._cache: Dict[str, str] = {}
        self._request_semaphore = None  # Will be created when needed
        self._last_request_time = 0
        self._lock = None  # Will be created when needed
        
        # Configure backend URL
        self.base_url = base_url or os.getenv("VIBE_CONTEXT_BACKEND_URL", "http://localhost:3000")
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        # Get API key from environment
        self.api_key = os.getenv("ASKBUDI_API_KEY")
        if not self.api_key:
            logger.error("ASKBUDI_API_KEY environment variable is required for backend API access")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        if not self.api_key:
            raise DependencyDocsAPIError(
                "ASKBUDI_API_KEY environment variable is required. "
                "Please set it to your VibeContext API key."
            )
        
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "juno-agent/1.0.0"
        }
    
    async def _search_library(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for libraries using the backend search endpoint.
        
        Args:
            query: Search query (library name)
            limit: Maximum number of results to return
            
        Returns:
            List of library search results
            
        Raises:
            DependencyDocsAPIError: If search fails
        """
        try:
            url = urljoin(self.base_url, "api/v1/docs/search")
            params = {"q": query, "limit": limit}
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 401:
                    raise DependencyDocsAPIError("Invalid API key. Please check your ASKBUDI_API_KEY.")
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise DependencyDocsAPIError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                elif response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                    raise DependencyDocsAPIError(f"Search failed: {error_msg}")
                
                try:
                    data = response.json()
                    return data.get("results", [])
                except ValueError as e:
                    logger.error(f"Failed to parse search response JSON: {e}")
                    return []
                    
        except httpx.ConnectError as e:
            logger.error(f"Connection failed to backend at {self.base_url}: {e}")
            raise DependencyDocsAPIError(f"Connection failed to backend: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout to backend: {e}")
            raise DependencyDocsAPIError(f"Request timeout: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in library search: {e}")
            raise DependencyDocsAPIError(f"Search failed: {e}")
    
    async def _fetch_library_docs(self, library_id: str, version: str = "latest") -> Optional[str]:
        """
        Fetch documentation for a specific library using the backend docs endpoint.
        
        Args:
            library_id: Library identifier (e.g., "/websites/textual")
            version: Library version (defaults to "latest")
            
        Returns:
            Documentation content or None if not available
            
        Raises:
            DependencyDocsAPIError: If fetch fails
        """
        try:
            # Remove leading slash from library_id for URL construction
            clean_id = library_id.lstrip('/')
            url = urljoin(self.base_url, f"api/v1/docs/{quote(clean_id, safe='')}")
            params = {"version": version} if version != "latest" else {}
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 404:
                    logger.debug(f"Documentation not found for {library_id}")
                    return None
                elif response.status_code == 401:
                    raise DependencyDocsAPIError("Invalid API key. Please check your ASKBUDI_API_KEY.")
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise DependencyDocsAPIError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                elif response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                    raise DependencyDocsAPIError(f"Documentation fetch failed: {error_msg}")
                
                try:
                    data = response.json()
                    return data.get("content")
                except ValueError as e:
                    logger.error(f"Failed to parse docs response JSON: {e}")
                    return None
                    
        except httpx.ConnectError as e:
            logger.error(f"Connection failed to backend: {e}")
            raise DependencyDocsAPIError(f"Connection failed to backend: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise DependencyDocsAPIError(f"Request timeout: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching docs for {library_id}: {e}")
            return None
    
    async def _fetch_single_dependency_docs(self, dep: DependencyInfo) -> Optional[str]:
        """
        Fetch documentation for a single dependency using search-then-fetch pattern.
        
        Args:
            dep: DependencyInfo object containing name and version
            
        Returns:
            Documentation string or None if not available
        """
        # Check cache first
        cache_key = f"{dep.name}:{dep.version}"
        if self.cache_enabled and cache_key in self._cache:
            logger.debug(f"Returning cached docs for {dep.name}")
            return self._cache[cache_key]
        
        try:
            # Step 1: Search for the library
            logger.debug(f"Searching for library: {dep.name}")
            search_results = await self._search_library(dep.name, limit=5)
            
            if not search_results:
                logger.debug(f"No search results found for {dep.name}")
                return None
            
            # Step 2: Find best match from search results
            best_match = None
            for result in search_results:
                # Look for exact name match first, then partial matches
                result_name = result.get("name", "").lower()
                if result_name == dep.name.lower():
                    best_match = result
                    break
                elif dep.name.lower() in result_name or result_name in dep.name.lower():
                    if best_match is None:
                        best_match = result
            
            if not best_match:
                logger.debug(f"No matching library found in search results for {dep.name}")
                return None
            
            # Step 3: Fetch documentation using library_id
            library_id = best_match.get("id")
            if not library_id:
                logger.warning(f"Search result for {dep.name} missing library ID")
                return None
            
            logger.debug(f"Fetching docs for {dep.name} using library_id: {library_id}")
            docs = await self._fetch_library_docs(library_id, dep.version)
            
            # Cache successful results
            if self.cache_enabled and docs:
                self._cache[cache_key] = docs
                logger.debug(f"Cached docs for {dep.name}")
            
            return docs
            
        except DependencyDocsAPIError:
            # Re-raise API errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching docs for {dep.name}: {e}")
            return None
    
    def _ensure_async_resources(self):
        """Ensure async resources are created in the current event loop."""
        if self._request_semaphore is None:
            self._request_semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        if self._lock is None:
            self._lock = asyncio.Lock()
    
    async def _throttled_request(self, func, *args, **kwargs):
        """
        Execute request with throttling to prevent overwhelming the API.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        self._ensure_async_resources()
        
        async with self._request_semaphore:
            # Enforce minimum delay between requests
            async with self._lock:
                current_time = time.time()
                time_since_last = current_time - self._last_request_time
                if time_since_last < self.request_delay:
                    sleep_time = self.request_delay - time_since_last
                    logger.debug(f"Throttling request, waiting {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                self._last_request_time = time.time()
            
            return await func(*args, **kwargs)
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry for rate limiting.
        
        Args:
            func: Async function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            DependencyDocsAPIError: If all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await self._throttled_request(func, *args, **kwargs)
            except DependencyDocsAPIError as e:
                last_exception = e
                if "Rate limit exceeded" in str(e) and attempt < self.max_retries:
                    # Extract Retry-After header value if available
                    retry_after = self._extract_retry_after(str(e))
                    if retry_after:
                        delay = retry_after + random.uniform(1, 5)  # Add jitter
                        logger.warning(f"Rate limited, respecting Retry-After: {retry_after}s + jitter, total delay: {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                    else:
                        # Enhanced exponential backoff with jitter
                        base_delay = min(60, (2 ** attempt) * 5)  # Cap at 60 seconds
                        jitter = random.uniform(0.5, 1.5)
                        delay = base_delay * jitter
                        logger.warning(f"Rate limited, exponential backoff: {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                    
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in retry attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    raise DependencyDocsAPIError(f"Failed after {self.max_retries + 1} attempts: {e}")
                # Exponential backoff for general errors
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
        
        if last_exception:
            raise last_exception
    
    def _extract_retry_after(self, error_message: str) -> Optional[float]:
        """
        Extract Retry-After value from error message.
        
        Args:
            error_message: Error message containing Retry-After info
            
        Returns:
            Retry-After value in seconds, or None if not found
        """
        import re
        
        # Look for patterns like "Retry after 60 seconds" or "60 seconds"
        patterns = [
            r'Retry after (\d+(?:\.\d+)?) seconds',
            r'retry after (\d+(?:\.\d+)?) seconds',
            r'(\d+(?:\.\d+)?) seconds',
            r'Retry-After: (\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def _process_dependency_batch(self, deps_batch: List[DependencyInfo]) -> Dict[str, Optional[str]]:
        """
        Process a batch of dependencies with controlled concurrency.
        
        Args:
            deps_batch: Batch of DependencyInfo objects
            
        Returns:
            Dictionary mapping dependency names to documentation
        """
        batch_results = {}
        
        # Create tasks for the batch with semaphore control
        tasks = []
        for dep in deps_batch:
            task = asyncio.create_task(
                self._fetch_dependency_with_error_handling(dep),
                name=f"fetch_{dep.name}"
            )
            tasks.append((dep.name, task))
        
        # Wait for all tasks in the batch to complete
        for dep_name, task in tasks:
            try:
                result = await task
                batch_results[dep_name] = result
            except Exception as e:
                logger.error(f"Task failed for {dep_name}: {e}")
                batch_results[dep_name] = None
        
        return batch_results
    
    async def _fetch_dependency_with_error_handling(self, dep: DependencyInfo) -> Optional[str]:
        """
        Fetch dependency documentation with comprehensive error handling.
        
        Args:
            dep: DependencyInfo object
            
        Returns:
            Documentation string or None if failed
        """
        try:
            logger.debug(f"Processing dependency: {dep.name}")
            doc = await self._retry_with_backoff(self._fetch_single_dependency_docs, dep)
            
            if doc:
                logger.debug(f"Successfully fetched docs for {dep.name}")
            else:
                logger.debug(f"No documentation found for {dep.name}")
            
            return doc
            
        except DependencyDocsAPIError as e:
            logger.error(f"API error fetching docs for {dep.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching docs for {dep.name}: {e}")
            return None
    
    async def fetch_dependency_docs(self, dependencies: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """
        Fetch documentation for a list of dependencies with intelligent batching and rate limiting.
        
        Args:
            dependencies: List of dependency dictionaries with 'name' and 'version' keys
            
        Returns:
            Dictionary mapping dependency names to their documentation (or None if not available)
            
        Raises:
            DependencyDocsAPIError: If there's a critical error preventing any documentation fetch
        """
        try:
            logger.info(f"Fetching backend documentation for {len(dependencies)} dependencies")
            
            # Convert to DependencyInfo objects
            deps = [DependencyInfo(name=dep["name"], version=dep["version"]) 
                   for dep in dependencies]
            
            # Process dependencies in controlled batches to avoid overwhelming the API
            batch_size = min(self.max_concurrent_requests, len(deps))
            all_results = {}
            successful_fetches = 0
            
            # Process in batches with delays between batches
            for i in range(0, len(deps), batch_size):
                batch = deps[i:i + batch_size]
                logger.debug(f"Processing batch {i//batch_size + 1}/{(len(deps) + batch_size - 1)//batch_size} with {len(batch)} dependencies")
                
                try:
                    batch_results = await self._process_dependency_batch(batch)
                    all_results.update(batch_results)
                    
                    # Count successful fetches
                    batch_successes = sum(1 for doc in batch_results.values() if doc is not None)
                    successful_fetches += batch_successes
                    
                    logger.debug(f"Batch completed: {batch_successes}/{len(batch)} successful")
                    
                    # Add delay between batches to be nice to the API
                    if i + batch_size < len(deps):
                        inter_batch_delay = self.request_delay * 2  # Longer delay between batches
                        logger.debug(f"Waiting {inter_batch_delay:.2f}s before next batch")
                        await asyncio.sleep(inter_batch_delay)
                        
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
                    # Still add None results for this batch
                    for dep in batch:
                        if dep.name not in all_results:
                            all_results[dep.name] = None
            
            logger.info(f"Backend documentation fetch completed: {successful_fetches}/{len(dependencies)} successful")
            return all_results
            
        except Exception as e:
            logger.error(f"Critical error in batch documentation fetch: {e}")
            raise DependencyDocsAPIError(f"Failed to fetch dependency documentation: {e}")
    
    async def health_check(self) -> bool:
        """
        Perform a health check of the backend API service.
        
        Returns:
            True if the service is healthy and accessible, False otherwise
        """
        try:
            url = urljoin(self.base_url, "")  # Root endpoint for health check
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code in [200, 404]:  # 404 is OK for health check
                    logger.debug("Backend health check successful")
                    return True
                else:
                    logger.warning(f"Backend health check failed: HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return False
    
    def get_supported_packages(self) -> List[str]:
        """
        Get list of packages that have been successfully cached.
        
        Returns:
            List of cached package names
        """
        # Extract package names from cache keys (format: "name:version")
        return list(set(key.split(':')[0] for key in self._cache.keys()))
    
    def clear_cache(self) -> None:
        """Clear the documentation cache."""
        self._cache.clear()
        logger.info("Backend documentation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_enabled": self.cache_enabled,
            "cached_items": len(self._cache),
            "supported_packages": len(self.get_supported_packages()),
            "cache_keys": list(self._cache.keys()),
            "backend_url": self.base_url,
            "api_key_configured": bool(self.api_key)
        }
    
    def get_documentation_summary(self, docs_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the documentation fetching results.
        
        Args:
            docs_result: Result from fetch_dependency_docs
            
        Returns:
            Formatted summary string
        """
        # Handle different result formats
        if isinstance(docs_result, dict):
            if "successful" in docs_result:
                # Structured result format
                successful = docs_result.get("successful", [])
                failed = docs_result.get("failed", [])
                
                summary_parts = []
                
                if successful:
                    summary_parts.append(f"**Successfully fetched documentation for {len(successful)} dependencies:**")
                    summary_parts.append(", ".join(successful))
                
                if failed:
                    summary_parts.append(f"**Failed to fetch documentation for {len(failed)} dependencies:**")
                    summary_parts.append(", ".join(failed))
                
                return "\n".join(summary_parts) if summary_parts else "No documentation was fetched."
            else:
                # Simple dict format (dependency_name -> doc_content or None)
                successful = [name for name, content in docs_result.items() if content is not None]
                failed = [name for name, content in docs_result.items() if content is None]
                
                summary_parts = []
                
                if successful:
                    summary_parts.append(f"**Successfully fetched documentation for {len(successful)} dependencies:**")
                    summary_parts.append(", ".join(successful))
                
                if failed:
                    summary_parts.append(f"**Failed to fetch documentation for {len(failed)} dependencies:**")
                    summary_parts.append(", ".join(failed))
                
                summary_parts.append(f"**Documentation source:** Backend API ({self.base_url})")
                
                return "\n".join(summary_parts) if summary_parts else "No documentation was fetched."
        
        return "Unable to generate documentation summary from the provided result format."


# Factory function for easy instantiation
def create_backend_dependency_docs_api(
    cache_enabled: bool = True, 
    timeout: float = 30.0,
    max_retries: int = 3,
    base_url: Optional[str] = None,
    request_delay: float = 0.1,
    max_concurrent_requests: int = 3
) -> BackendDependencyDocsAPI:
    """
    Factory function to create a BackendDependencyDocsAPI instance.
    
    Args:
        cache_enabled: Whether to enable caching
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for rate limiting
        base_url: Backend URL override
        request_delay: Minimum delay between requests (seconds)
        max_concurrent_requests: Maximum number of concurrent requests
        
    Returns:
        Configured BackendDependencyDocsAPI instance
    """
    return BackendDependencyDocsAPI(
        cache_enabled=cache_enabled,
        timeout=timeout,
        max_retries=max_retries,
        base_url=base_url,
        request_delay=request_delay,
        max_concurrent_requests=max_concurrent_requests
    )