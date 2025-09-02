"""Exceptions for Halo API client."""


class HaloError(Exception):
    """Base exception for all Halo API errors."""
    pass


class HaloAuthenticationError(HaloError):
    """Raised when authentication fails."""
    pass


class HaloAPIError(HaloError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        """Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Raw response data from API
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class HaloResourceNotFound(HaloAPIError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error.
        
        Args:
            resource_type: Type of resource (e.g., 'ticket', 'ticket_type')
            resource_id: ID of the resource that was not found
        """
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, status_code=404)
        self.resource_type = resource_type
        self.resource_id = resource_id


class HaloValidationError(HaloAPIError):
    """Raised when the API returns validation errors."""
    
    def __init__(self, message: str, errors: dict = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            errors: Dictionary of field-specific errors
        """
        super().__init__(message, status_code=400)
        self.errors = errors or {}


class HaloRateLimitError(HaloAPIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = None, retry_after: int = None):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        message = message or "API rate limit exceeded"
        super().__init__(message, status_code=429)
        self.retry_after = retry_after