"""Authentication handling for Halo API client."""
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .exceptions import HaloAuthenticationError

logger = logging.getLogger(__name__)


class OAuth2TokenManager:
    """Manages OAuth2 token lifecycle for Halo API authentication.
    
    Supports both client credentials and username/password flows.
    Automatically refreshes tokens when they expire.
    """
    
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        session = None
    ):
        """Initialize token manager.
        
        Args:
            base_url: Base URL of the Halo API
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret (for client credentials flow)
            username: Username (for password flow)
            password: Password (for password flow)
            token: Existing access token
            refresh_token: Existing refresh token
            session: HTTP session to use for requests
        """
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self._token = token
        self._refresh_token = refresh_token
        self._token_expires_at = None
        self._session = session
        
        # Validate authentication parameters
        if not self._token:
            if self.client_secret:
                # Client credentials flow
                pass
            elif self.username and self.password:
                # Password flow
                pass
            else:
                raise HaloAuthenticationError(
                    "Must provide either (client_id + client_secret) or "
                    "(client_id + username + password) or existing token"
                )
    
    @property
    def token_url(self) -> str:
        """Get the OAuth2 token endpoint URL."""
        # Remove /api from base URL if present
        if self.base_url.lower().endswith('/api'):
            base = self.base_url[:-4]  # Remove '/api'
        else:
            base = self.base_url
        return f"{base}/auth/token"
    
    def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
            
        Raises:
            HaloAuthenticationError: If authentication fails
        """
        # If we have a valid token, return it
        if self._token and self._is_token_valid():
            return self._token
        
        # Otherwise, get a new token
        self._authenticate()
        return self._token
    
    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self._token:
            return False
        
        if self._token_expires_at:
            # Add 5 minute buffer to avoid edge cases
            return datetime.now() < self._token_expires_at - timedelta(minutes=5)
        
        # If we don't know expiration, assume it's valid
        return True
    
    def _authenticate(self) -> None:
        """Authenticate and obtain a new access token.
        
        Raises:
            HaloAuthenticationError: If authentication fails
        """
        # For refresh, only try if we have refresh token AND this was a password flow
        # Client credentials don't typically get refresh tokens in Halo
        if self._refresh_token and (self.username and self.password):
            try:
                self._refresh_access_token()
                return
            except HaloAuthenticationError:
                logger.warning("Refresh token failed, trying primary authentication")
        
        if self.client_secret:
            self._client_credentials_auth()
        elif self.username and self.password:
            self._password_auth()
        else:
            raise HaloAuthenticationError("No valid authentication method available")
    
    def _client_credentials_auth(self) -> None:
        """Authenticate using client credentials flow.
        
        Raises:
            HaloAuthenticationError: If authentication fails
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'all'
        }
        
        response = self._make_token_request(data)
        self._process_token_response(response)
    
    def _password_auth(self) -> None:
        """Authenticate using username/password flow.
        
        Raises:
            HaloAuthenticationError: If authentication fails
        """
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'username': self.username,
            'password': self.password,
            'scope': 'all'
        }
        
        response = self._make_token_request(data)
        self._process_token_response(response)
    
    def _refresh_access_token(self) -> None:
        """Refresh the access token using refresh token.
        
        Raises:
            HaloAuthenticationError: If refresh fails
        """
        if not self._refresh_token:
            raise HaloAuthenticationError("No refresh token available")
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': self._refresh_token
        }
        
        response = self._make_token_request(data)
        self._process_token_response(response)
    
    def _make_token_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the token endpoint.
        
        Args:
            data: Form data for the request
            
        Returns:
            Response JSON
            
        Raises:
            HaloAuthenticationError: If request fails
        """
        logger.info(f"Making token request to {self.token_url}")
        logger.info(f"Request data: {data}")
        
        if not self._session:
            import requests
            response = requests.post(self.token_url, data=data)
        else:
            response = self._session.post(self.token_url, data=data)
        
        logger.info(f"Token response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Response content: {response.text[:500]}")
        
        if response.status_code != 200:
            error_msg = f"Authentication failed with status {response.status_code} for URL {self.token_url}"
            try:
                error_data = response.json()
                if 'error_description' in error_data:
                    error_msg = error_data['error_description']
                elif 'error' in error_data:
                    error_msg = error_data['error']
            except:
                pass
            
            raise HaloAuthenticationError(error_msg)
        
        return response.json()
    
    def _process_token_response(self, response: Dict[str, Any]) -> None:
        """Process token response and update internal state.
        
        Args:
            response: Token response from API
        """
        self._token = response.get('access_token')
        self._refresh_token = response.get('refresh_token', self._refresh_token)
        
        # Calculate token expiration
        expires_in = response.get('expires_in', 3600)  # Default 1 hour
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        logger.debug(f"Token obtained, expires at {self._token_expires_at}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        return {
            'Authorization': f'Bearer {self.get_token()}'
        }