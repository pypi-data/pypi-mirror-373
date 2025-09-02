"""Ticket resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class Ticket(Resource):
    """Represents a ticket in Halo."""
    
    def update(self, data: Dict[str, Any]) -> 'Ticket':
        """Update this ticket.
        
        Args:
            data: Fields to update
            
        Returns:
            Updated ticket resource
        """
        # Merge with existing data
        update_data = {'id': self.id}
        update_data.update(data)
        
        response = self._client.session.post(f'/Tickets/{self.id}', json=update_data)
        self._update_from_raw(response)
        return self
    
    def delete(self) -> None:
        """Delete this ticket."""
        self._client.session.delete(f'/Tickets/{self.id}')
    
    def add_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add an action/comment to this ticket.
        
        Args:
            action_data: Action data including note_html, outcome_id, etc.
            
        Returns:
            Created action data
        """
        data = {
            'ticket_id': self.id,
            **action_data
        }
        return self._client.session.post('/Actions', json=data)
    
    def add_attachment(self, filename: str, file_content: bytes, description: str = "") -> Dict[str, Any]:
        """Add an attachment to this ticket.
        
        Args:
            filename: Name of the file
            file_content: File content as bytes
            description: Optional description
            
        Returns:
            Created attachment data
        """
        files = {
            'file': (filename, file_content)
        }
        data = {
            'ticket_id': self.id,
            'description': description
        }
        return self._client.session.post(
            f'/Tickets/{self.id}/attachments',
            files=files,
            data=data
        )
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get all actions for this ticket.
        
        Returns:
            List of action dictionaries
        """
        return self._client.session.get(f'/Tickets/{self.id}/actions')
    
    def get_attachments(self) -> List[Dict[str, Any]]:
        """Get all attachments for this ticket.
        
        Returns:
            List of attachment dictionaries
        """
        return self._client.session.get(f'/Tickets/{self.id}/attachments')


class TicketList(ListResource):
    """Handles list operations for tickets."""
    
    def list(
        self,
        page_size: int = 100,
        page_no: int = 1,
        order: Optional[str] = None,
        order_desc: bool = False,
        search: Optional[str] = None,
        ticket_type_id: Optional[int] = None,
        status_id: Optional[int] = None,
        client_id: Optional[int] = None,
        site_id: Optional[int] = None,
        user_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        team_id: Optional[int] = None,
        **kwargs
    ) -> List[Ticket]:
        """List tickets with filters.
        
        Args:
            page_size: Number of results per page
            page_no: Page number
            order: Field to order by
            order_desc: Order descending
            search: Search term
            ticket_type_id: Filter by ticket type
            status_id: Filter by status
            client_id: Filter by client
            site_id: Filter by site
            user_id: Filter by user
            agent_id: Filter by agent
            team_id: Filter by team
            **kwargs: Additional filters
            
        Returns:
            List of Ticket resources
        """
        params = {
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            'order': order,
            'orderdesc': order_desc,
            'search': search,
            'tickettype_id': ticket_type_id,
            'status_id': status_id,
            'client_id': client_id,
            'site_id': site_id,
            'user_id': user_id,
            'agent_id': agent_id,
            'team_id': team_id,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Tickets', params=params)
        
        # Handle paginated response
        if isinstance(response, dict) and 'tickets' in response:
            items = response['tickets']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, ticket_id: int, **kwargs) -> Ticket:
        """Get a specific ticket.
        
        Args:
            ticket_id: ID of the ticket
            **kwargs: Additional query parameters
            
        Returns:
            Ticket resource
            
        Raises:
            HaloResourceNotFound: If ticket not found
        """
        response = self._client.session.get(f'/Tickets/{ticket_id}', params=kwargs)
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> Ticket:
        """Create a new ticket.
        
        Args:
            data: Ticket data including tickettype_id, summary, details, etc.
            
        Returns:
            Created Ticket resource
        """
        response = self._client.session.post('/Tickets', json=data)
        return self._create_resource(response)
    
    def search(
        self,
        query: str,
        ticket_type_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Ticket]:
        """Search tickets using full-text search.
        
        Args:
            query: Search query
            ticket_type_id: Limit to specific ticket type
            limit: Maximum number of results
            
        Returns:
            List of matching Ticket resources
        """
        return self.list(
            search=query,
            ticket_type_id=ticket_type_id,
            page_size=limit
        )