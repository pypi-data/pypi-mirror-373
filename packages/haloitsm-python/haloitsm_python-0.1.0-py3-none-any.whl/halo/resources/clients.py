"""Client resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class Client(Resource):
    """Represents a client/customer in Halo."""
    
    def update(self, data: Dict[str, Any]) -> 'Client':
        """Update this client.
        
        Args:
            data: Fields to update
            
        Returns:
            Updated client resource
        """
        update_data = {'id': self.id}
        update_data.update(data)
        
        response = self._client.session.post(f'/Client/{self.id}', json=update_data)
        self._update_from_raw(response)
        return self
    
    def delete(self) -> None:
        """Delete this client."""
        self._client.session.delete(f'/Client/{self.id}')
    
    def get_sites(self) -> List[Dict[str, Any]]:
        """Get all sites for this client.
        
        Returns:
            List of site dictionaries
        """
        return self._client.session.get('/Site', params={'client_id': self.id})
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users for this client.
        
        Returns:
            List of user dictionaries
        """
        return self._client.session.get('/Users', params={'client_id': self.id})
    
    def get_contracts(self) -> List[Dict[str, Any]]:
        """Get all contracts for this client.
        
        Returns:
            List of contract dictionaries
        """
        return self._client.session.get('/ClientContract', params={'client_id': self.id})
    
    def get_tickets(self, **kwargs) -> List[Dict[str, Any]]:
        """Get tickets for this client.
        
        Args:
            **kwargs: Additional filters
            
        Returns:
            List of ticket dictionaries
        """
        params = {'client_id': self.id, **kwargs}
        return self._client.session.get('/Tickets', params=params)


class ClientList(ListResource):
    """Handles list operations for clients."""
    
    def list(
        self,
        search: Optional[str] = None,
        inactive: bool = False,
        client_type: Optional[str] = None,
        page_size: int = 100,
        page_no: int = 1,
        order: Optional[str] = None,
        order_desc: bool = False,
        **kwargs
    ) -> List[Client]:
        """List clients with filters.
        
        Args:
            search: Search term
            inactive: Include inactive clients
            client_type: Filter by client type
            page_size: Number of results per page
            page_no: Page number
            order: Field to order by
            order_desc: Order descending
            **kwargs: Additional filters
            
        Returns:
            List of Client resources
        """
        params = {
            'search': search,
            'includeinactive': inactive,
            'clienttype': client_type,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            'order': order,
            'orderdesc': order_desc,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Client', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'clients' in response:
            items = response['clients']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, client_id: int, **kwargs) -> Client:
        """Get a specific client.
        
        Args:
            client_id: ID of the client
            **kwargs: Additional parameters
            
        Returns:
            Client resource
        """
        response = self._client.session.get(f'/Client/{client_id}', params=kwargs)
        return self._create_resource(response)
    
    def get_me(self) -> Client:
        """Get the current user's client.
        
        Returns:
            Client resource for current user
        """
        response = self._client.session.get('/Client/me')
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> Client:
        """Create a new client.
        
        Args:
            data: Client data
            
        Returns:
            Created Client resource
        """
        response = self._client.session.post('/Client', json=data)
        return self._create_resource(response)
    
    def search(self, query: str, limit: int = 100) -> List[Client]:
        """Search clients.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching Client resources
        """
        return self.list(search=query, page_size=limit)