"""HTTP session management for Halo API client."""
import time
import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    HaloAPIError,
    HaloResourceNotFound,
    HaloValidationError,
    HaloRateLimitError,
    HaloAuthenticationError
)

logger = logging.getLogger(__name__)


class HaloSession:
    """HTTP session with retry logic and error handling for Halo API."""
    
    def __init__(
        self,
        base_url: str,
        token_manager,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """Initialize session.
        
        Args:
            base_url: Base URL of the Halo API
            token_manager: OAuth2TokenManager instance
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
        """
        self.base_url = base_url.rstrip('/')
        self.token_manager = token_manager
        self.timeout = timeout
        
        # Create session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set token manager's session
        self.token_manager._session = self.session
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], list]:
        """Make an authenticated request to the Halo API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            json: JSON body
            data: Form data
            headers: Additional headers
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON
            
        Raises:
            HaloAPIError: If the request fails
        """
        # Build full URL
        # Ensure base_url ends with / and endpoint doesn't start with /
        base = self.base_url.rstrip('/') + '/'
        endpoint_clean = endpoint.lstrip('/')
        url = urljoin(base, endpoint_clean)
        
        # Get auth headers
        auth_headers = self.token_manager.get_headers()
        if headers:
            auth_headers.update(headers)
        
        # Make request with retry logic for auth failures
        max_auth_retries = 2
        for attempt in range(max_auth_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=auth_headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Handle response
                return self._handle_response(response)
                
            except HaloAuthenticationError:
                if attempt < max_auth_retries - 1:
                    logger.warning("Authentication failed, retrying...")
                    # Force token refresh
                    self.token_manager._token = None
                    auth_headers = self.token_manager.get_headers()
                else:
                    raise
    
    def _handle_response(self, response: requests.Response) -> Union[Dict[str, Any], list]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object
            
        Returns:
            Response JSON
            
        Raises:
            HaloAPIError: If the request failed
        """
        # Check for authentication errors
        if response.status_code in (401, 403):
            raise HaloAuthenticationError(
                f"Authentication failed: {response.status_code}"
            )
        
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise HaloRateLimitError(retry_after=int(retry_after) if retry_after else None)
        
        # Check for not found
        if response.status_code == 404:
            # Try to extract resource info from URL
            parts = response.url.split('/')
            resource_type = parts[-2] if len(parts) > 1 else 'resource'
            resource_id = parts[-1] if len(parts) > 0 else 'unknown'
            raise HaloResourceNotFound(resource_type, resource_id)
        
        # Check for validation errors
        if response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get('message', 'Validation failed')
                errors = error_data.get('errors', {})
                raise HaloValidationError(message, errors)
            except ValueError:
                raise HaloValidationError("Validation failed")
        
        # Check for other errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get('message', f"API error: {response.status_code}")
            except ValueError:
                message = f"API error: {response.status_code}"
            
            raise HaloAPIError(message, response.status_code)
        
        # Parse JSON response
        try:
            return response.json()
        except ValueError:
            # Some endpoints return empty responses
            if response.status_code == 204 or not response.content:
                return {}
            # Log the problematic response for debugging
            logger.error(f"Invalid JSON response from {response.url}")
            logger.error(f"Response status: {response.status_code}")
            logger.error(f"Response content: {repr(response.text[:200])}")
            logger.error(f"Response headers: {dict(response.headers)}")
            raise HaloAPIError(f"Invalid JSON response: {repr(response.text[:100])}")
    
    def get(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], list]:
        """Make a GET request."""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], list]:
        """Make a POST request."""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], list]:
        """Make a PUT request."""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], list]:
        """Make a DELETE request."""
        return self.request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], list]:
        """Make a PATCH request."""
        return self.request('PATCH', endpoint, **kwargs)