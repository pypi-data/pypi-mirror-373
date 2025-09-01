"""
Emergence Platform Client

This module provides the EmergenceClient class for communicating with the
Emergence Platform API, handling authentication, agent registration, and
platform operations.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .version import __version__
from .exceptions import (
    EmergenceError,
    AuthenticationError,
    ValidationError,
    PlatformError,
    RateLimitError
)


class EmergenceClient:
    """
    Client for interacting with the Emergence Platform API.
    
    Handles authentication, agent registration, webhook management,
    and all platform communication operations.
    
    Example:
        >>> client = EmergenceClient(api_key="your_api_key")
        >>> agent_data = {"name": "my-agent", "version": "1.0.0"}
        >>> response = client.register_agent(agent_data)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.emergence-platform.com",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """
        Initialize the Emergence Platform client.
        
        Args:
            api_key: Platform API key (can also be set via EMERGENCE_API_KEY env var)
            base_url: Platform API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
        """
        import os
        
        self.api_key = api_key or os.getenv('EMERGENCE_API_KEY')
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set EMERGENCE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'emergence-agent-sdk/{__version__}',
            'Accept': 'application/json',
        })
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
        
        self.logger.info(f"EmergenceClient initialized for {self.base_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the platform API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            data: Request payload
            params: URL parameters
            files: Files to upload
            
        Returns:
            API response data
            
        Raises:
            Various platform-specific exceptions based on response
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            if files:
                # For file uploads, don't set Content-Type (let requests handle it)
                headers = {k: v for k, v in self.session.headers.items() 
                          if k.lower() != 'content-type'}
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,  # Use data instead of json for file uploads
                    params=params,
                    files=files,
                    timeout=self.timeout,
                    headers=headers
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
            
            self._last_request_time = time.time()
            
            # Handle different response status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or expired token")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 404:
                raise PlatformError(f"Endpoint not found: {endpoint}")
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise ValidationError(f"Validation failed: {error_data.get('message', 'Invalid data')}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please retry later.")
            elif response.status_code >= 500:
                raise PlatformError(f"Platform error: HTTP {response.status_code}")
            elif not response.ok:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except:
                    pass
                raise PlatformError(error_msg)
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                if response.content:
                    return {"raw_response": response.text}
                return {"success": True}
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise PlatformError(f"Network error: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the platform.
        
        Returns:
            Connection status and platform info
        """
        try:
            response = self._make_request('GET', '/api/platform/status')
            self.logger.info("Platform connection test successful")
            return response
        except Exception as e:
            self.logger.error(f"Platform connection test failed: {e}")
            raise

    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent with the platform.
        
        Args:
            agent_data: Agent registration data
            
        Returns:
            Registration response with agent_id
        """
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in agent_data:
                raise ValidationError(f"Missing required field: {field}")
        
        self.logger.info(f"Registering agent: {agent_data['name']}")
        response = self._make_request('POST', '/api/agents/register', agent_data)
        
        if response.get('success'):
            self.logger.info(f"Agent registered successfully: {response.get('agent_id')}")
        
        return response

    def unregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Unregister an agent from the platform.
        
        Args:
            agent_id: Agent ID to unregister
            
        Returns:
            Unregistration response
        """
        self.logger.info(f"Unregistering agent: {agent_id}")
        return self._make_request('DELETE', f'/api/agents/{agent_id}')

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent information.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent information
        """
        return self._make_request('GET', f'/api/agents/{agent_id}')

    def list_agents(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available agents.
        
        Args:
            page: Page number
            limit: Results per page
            category: Filter by category
            
        Returns:
            List of agents with pagination info
        """
        params = {'page': page, 'limit': limit}
        if category:
            params['category'] = category
        
        return self._make_request('GET', '/api/agents', params=params)

    def register_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a webhook endpoint.
        
        Args:
            webhook_data: Webhook registration data
            
        Returns:
            Webhook registration response
        """
        return self._make_request('POST', '/api/webhook/register', webhook_data)

    def send_webhook_ping(self, agent_id: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a ping to verify webhook connectivity and send heartbeat data.
        
        Args:
            agent_id: Target agent ID
            additional_data: Additional heartbeat data to include
            
        Returns:
            Ping response
        """
        ping_data = {
            'agent_id': agent_id,
            'timestamp': time.time(),
            'sdk_version': __version__
        }
        
        if additional_data:
            ping_data.update(additional_data)
        
        return self._make_request('POST', '/api/webhook/ping', ping_data)

    def send_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an event to the platform.
        
        Args:
            event_data: Event data
            
        Returns:
            Event response
        """
        return self._make_request('POST', '/api/events', event_data)

    def upload_agent(
        self,
        agent_file_path: str,
        agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Upload an agent file to the platform.
        
        Args:
            agent_file_path: Path to agent zip file
            agent_data: Agent metadata
            
        Returns:
            Upload response
        """
        try:
            with open(agent_file_path, 'rb') as f:
                files = {'file': f}
                self.logger.info(f"Uploading agent file: {agent_file_path}")
                return self._make_request('POST', '/api/agents', data=agent_data, files=files)
        except FileNotFoundError:
            raise ValidationError(f"Agent file not found: {agent_file_path}")

    def get_platform_stats(self) -> Dict[str, Any]:
        """
        Get platform statistics.
        
        Returns:
            Platform statistics
        """
        return self._make_request('GET', '/api/platform/stats')

    def discover_agents(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        live_only: bool = True
    ) -> Dict[str, Any]:
        """
        Discover available agents on the platform.
        
        Args:
            query: Search query
            category: Filter by category
            live_only: Only return live agents
            
        Returns:
            Discovered agents
        """
        params = {}
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        if live_only:
            params['live'] = 'true'
        
        endpoint = '/api/agents/discover/live' if live_only else '/api/agents/discover'
        return self._make_request('GET', endpoint, params=params)

    def create_api_key(self, name: str, permissions: List[str]) -> Dict[str, Any]:
        """
        Create a new API key.
        
        Args:
            name: API key name
            permissions: List of permissions
            
        Returns:
            New API key data
        """
        key_data = {
            'name': name,
            'permissions': permissions
        }
        return self._make_request('POST', '/api/auth/keys', key_data)

    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """
        Revoke an API key.
        
        Args:
            key_id: API key ID to revoke
            
        Returns:
            Revocation response
        """
        return self._make_request('DELETE', f'/api/auth/keys/{key_id}')

    def get_usage_stats(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Args:
            agent_id: Optional specific agent ID
            
        Returns:
            Usage statistics
        """
        endpoint = f'/api/stats/usage/{agent_id}' if agent_id else '/api/stats/usage'
        return self._make_request('GET', endpoint)
    
    def update_agent_capabilities(self, agent_id: str, capabilities_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update agent capabilities on the platform.
        
        Args:
            agent_id: Agent ID
            capabilities_data: Updated capabilities data
            
        Returns:
            Update response
        """
        return self._make_request('PUT', f'/api/agents/{agent_id}/capabilities', capabilities_data)

    def close(self):
        """Close the client session."""
        if self.session:
            self.session.close()
            self.logger.info("Client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"EmergenceClient(base_url='{self.base_url}')"


class AsyncEmergenceClient:
    """
    Async version of the Emergence Platform client.
    
    Provides the same functionality as EmergenceClient but with
    async/await support for non-blocking operations.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.emergence-platform.com",
        timeout: int = 30
    ):
        """Initialize async client."""
        import os
        
        self.api_key = api_key or os.getenv('EMERGENCE_API_KEY')
        if not self.api_key:
            raise AuthenticationError("API key is required")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry."""
        import aiohttp
        
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': f'emergence-agent-sdk/{__version__}',
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_async_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async request to platform API."""
        if not self.session:
            raise EmergenceError("Client not properly initialized. Use async context manager.")
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 500:
                    raise PlatformError(f"Platform error: HTTP {response.status}")
                elif not response.ok:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    raise PlatformError(f"HTTP {response.status}: {error_data.get('message', 'Unknown error')}")
                
                return await response.json()
                
        except Exception as e:
            self.logger.error(f"Async request failed: {e}")
            raise PlatformError(f"Request failed: {e}")

    async def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async agent registration."""
        return await self._make_async_request('POST', '/api/agents/register', agent_data)

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Async get agent information."""
        return await self._make_async_request('GET', f'/api/agents/{agent_id}')

    async def send_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async send event."""
        return await self._make_async_request('POST', '/api/events', event_data)