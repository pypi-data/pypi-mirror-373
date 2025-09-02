"""User resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class User(Resource):
    """Represents a user in Halo."""
    
    def update(self, data: Dict[str, Any]) -> 'User':
        """Update this user.
        
        Args:
            data: Fields to update
            
        Returns:
            Updated user resource
        """
        update_data = {'id': self.id}
        update_data.update(data)
        
        response = self._client.session.post(f'/Users/{self.id}', json=update_data)
        self._update_from_raw(response)
        return self
    
    def delete(self) -> None:
        """Delete this user."""
        self._client.session.delete(f'/Users/{self.id}')
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """Get roles assigned to this user.
        
        Returns:
            List of role dictionaries
        """
        return self._client.session.get('/UserRoles', params={'user_id': self.id})
    
    def add_role(self, role_id: int) -> Dict[str, Any]:
        """Add a role to this user.
        
        Args:
            role_id: ID of the role to add
            
        Returns:
            Created role assignment
        """
        return self._client.session.post('/UserRoles', json={
            'user_id': self.id,
            'role_id': role_id
        })
    
    def remove_role(self, role_id: int) -> None:
        """Remove a role from this user.
        
        Args:
            role_id: ID of the role to remove
        """
        # Find the user role assignment
        roles = self.get_roles()
        for role in roles:
            if role.get('role_id') == role_id:
                self._client.session.delete(f'/UserRoles/{role["id"]}')
                break
    
    def get_tickets(self, **kwargs) -> List[Dict[str, Any]]:
        """Get tickets for this user.
        
        Args:
            **kwargs: Additional filters
            
        Returns:
            List of ticket dictionaries
        """
        params = {'user_id': self.id, **kwargs}
        return self._client.session.get('/Tickets', params=params)


class UserList(ListResource):
    """Handles list operations for users."""
    
    def list(
        self,
        client_id: Optional[int] = None,
        site_id: Optional[int] = None,
        search: Optional[str] = None,
        inactive: bool = False,
        is_agent: Optional[bool] = None,
        page_size: int = 100,
        page_no: int = 1,
        order: Optional[str] = None,
        order_desc: bool = False,
        **kwargs
    ) -> List[User]:
        """List users with filters.
        
        Args:
            client_id: Filter by client
            site_id: Filter by site
            search: Search term
            inactive: Include inactive users
            is_agent: Filter by agent status
            page_size: Number of results per page
            page_no: Page number
            order: Field to order by
            order_desc: Order descending
            **kwargs: Additional filters
            
        Returns:
            List of User resources
        """
        params = {
            'client_id': client_id,
            'site_id': site_id,
            'search': search,
            'includeinactive': inactive,
            'isagent': is_agent,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            'order': order,
            'orderdesc': order_desc,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Users', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'users' in response:
            items = response['users']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, user_id: int, **kwargs) -> User:
        """Get a specific user.
        
        Args:
            user_id: ID of the user
            **kwargs: Additional parameters
            
        Returns:
            User resource
        """
        response = self._client.session.get(f'/Users/{user_id}', params=kwargs)
        return self._create_resource(response)
    
    def get_me(self) -> User:
        """Get the current authenticated user.
        
        Returns:
            User resource for current user
        """
        response = self._client.session.get('/Users/me')
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user.
        
        Args:
            data: User data including name, email, client_id, etc.
            
        Returns:
            Created User resource
        """
        response = self._client.session.post('/Users', json=data)
        return self._create_resource(response)
    
    def search(self, query: str, limit: int = 100) -> List[User]:
        """Search users.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching User resources
        """
        return self.list(search=query, page_size=limit)