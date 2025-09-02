"""Category resources for Halo ITSM API."""

from .base import Resource, ListResource


class Category(Resource):
    """Represents a Halo Category.
    
    Categories are used for ticket categorization with 4 types (Category1-4).
    Each category has properties like:
    - id: Unique identifier
    - guid: GUID identifier
    - value: The category value/name
    - category_name: Display name
    - type_id: Which category type (1-4)
    - sla_id: Associated SLA if any
    - priority_id: Associated priority if any
    """
    
    def __str__(self):
        """String representation of Category."""
        return f"<Category {self.id}: {self.value} (Type {self.type_id})>"


class CategoryList(ListResource):
    """Handles list operations for Categories."""
    
    _resource_class = Category
    _endpoint = "Category"
    
    def list(self, type_id=None, **kwargs):
        """List categories with optional filtering.
        
        Args:
            type_id: Filter by category type (1-4)
            **kwargs: Additional query parameters
            
        Returns:
            List[Category]: List of Category objects
        """
        params = {}
        if type_id is not None:
            params['type_id'] = type_id
        params.update(kwargs)
        
        response = self._client.session.get(f"/{self._endpoint}", params=params)
        return [self._resource_class(self._client, data) for data in response]
    
    def get_by_type(self, type_id):
        """Get all categories for a specific type.
        
        Args:
            type_id (int): The category type (1-4)
            
        Returns:
            List[Category]: List of categories for that type
        """
        return self.list(type_id=type_id)
    
    def get_all_types(self):
        """Get all categories organized by type.
        
        Returns:
            dict: Dictionary with keys 1-4 containing category lists
        """
        result = {}
        for type_id in range(1, 5):
            result[type_id] = self.get_by_type(type_id)
        return result