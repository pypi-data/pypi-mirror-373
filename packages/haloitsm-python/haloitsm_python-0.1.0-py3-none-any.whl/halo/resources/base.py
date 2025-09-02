"""Base resource class for Halo API resources."""
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..client import HaloClient


class Resource:
    """Base class for all Halo API resources.
    
    Provides common functionality for API resources including:
    - Initialization from API response data
    - Access to raw API data
    - Update and delete operations
    - Automatic attribute setting from API responses
    """
    
    def __init__(self, client: 'HaloClient', raw: Dict[str, Any]):
        """Initialize a resource with raw API data.
        
        Args:
            client: The HaloClient instance
            raw: Raw JSON response from the API
        """
        self._client = client
        self._raw = raw
        self._update_from_raw(raw)
    
    def _update_from_raw(self, raw: Dict[str, Any]) -> None:
        """Update resource attributes from raw API data.
        
        Args:
            raw: Raw JSON response from the API
        """
        self._raw = raw
        # Set all top-level keys as attributes
        for key, value in raw.items():
            # Convert datetime strings to datetime objects
            if isinstance(value, str) and key.endswith(('_date', '_at')):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            setattr(self, key, value)
    
    @property
    def raw(self) -> Dict[str, Any]:
        """Get the raw API response data."""
        return self._raw
    
    def __repr__(self) -> str:
        """String representation of the resource."""
        id_attr = getattr(self, 'id', None)
        name_attr = getattr(self, 'name', getattr(self, 'summary', None))
        
        if id_attr and name_attr:
            return f"<{self.__class__.__name__} [{id_attr}] {name_attr}>"
        elif id_attr:
            return f"<{self.__class__.__name__} [{id_attr}]>"
        else:
            return f"<{self.__class__.__name__}>"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality based on resource ID."""
        if not isinstance(other, self.__class__):
            return False
        return getattr(self, 'id', None) == getattr(other, 'id', None)
    
    def __hash__(self) -> int:
        """Hash based on resource ID."""
        return hash((self.__class__.__name__, getattr(self, 'id', None)))


class ListResource:
    """Base class for list operations on resources."""
    
    def __init__(self, client: 'HaloClient', resource_class: type):
        """Initialize list resource.
        
        Args:
            client: The HaloClient instance
            resource_class: The resource class to instantiate items with
        """
        self._client = client
        self._resource_class = resource_class
    
    def _create_resource(self, raw: Dict[str, Any]) -> Resource:
        """Create a resource instance from raw data.
        
        Args:
            raw: Raw JSON response from the API
            
        Returns:
            Resource instance
        """
        return self._resource_class(self._client, raw)