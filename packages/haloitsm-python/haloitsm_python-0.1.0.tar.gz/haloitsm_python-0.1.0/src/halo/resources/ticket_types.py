"""TicketType resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class TicketType(Resource):
    """Represents a ticket type in Halo."""
    
    def get_fields(self, include_details: bool = True) -> List[Dict[str, Any]]:
        """Get all fields for this ticket type.
        
        Args:
            include_details: Whether to include field details
            
        Returns:
            List of field dictionaries
        """
        # Get ticket type with details to include fields
        response = self._client.session.get(
            f"/tickettype/{self.id}",
            params={'includedetails': include_details}
        )
        
        # Update self with new data
        self._update_from_raw(response)
        
        # Extract and flatten fields
        fields = []
        if 'customfields' in response:
            for group in response['customfields']:
                if isinstance(group, dict) and 'fields' in group:
                    # Nested group structure
                    group_header = group.get('group', {}).get('header', '')
                    for field in group['fields']:
                        field['group_header'] = group_header
                        fields.append(field)
                else:
                    # Direct field
                    fields.append(group)
        
        return fields
    
    def delete(self) -> None:
        """Delete this ticket type."""
        self._client.session.delete(f"/tickettype/{self.id}")


class TicketTypeList(ListResource):
    """Handles list operations for ticket types."""
    
    def list(
        self,
        access_control_level: Optional[int] = None,
        can_create_only: Optional[bool] = None,
        can_edit_only: Optional[bool] = None,
        client_id: Optional[int] = None,
        show_inactive: bool = False,
        show_counts: bool = False,
        **kwargs
    ) -> List[TicketType]:
        """List ticket types.
        
        Args:
            access_control_level: Filter by access control level
            can_create_only: Only show types user can create
            can_edit_only: Only show types user can edit
            client_id: Filter by client ID
            show_inactive: Include inactive ticket types
            show_counts: Include ticket counts
            **kwargs: Additional query parameters
            
        Returns:
            List of TicketType resources
        """
        params = {
            'access_control_level': access_control_level,
            'can_create_only': can_create_only,
            'can_edit_only': can_edit_only,
            'client_id': client_id,
            'showinactive': show_inactive,
            'showcounts': show_counts,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/tickettype', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'tickettypes' in response:
            items = response['tickettypes']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(
        self,
        ticket_type_id: int,
        include_details: bool = False,
        include_config: bool = False,
        **kwargs
    ) -> TicketType:
        """Get a specific ticket type.
        
        Args:
            ticket_type_id: ID of the ticket type
            include_details: Include field details
            include_config: Include configuration
            **kwargs: Additional query parameters
            
        Returns:
            TicketType resource
            
        Raises:
            HaloResourceNotFound: If ticket type not found
        """
        params = {
            'includedetails': include_details,
            'includeconfig': include_config,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get(f'/tickettype/{ticket_type_id}', params=params)
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> TicketType:
        """Create a new ticket type.
        
        Args:
            data: Ticket type data
            
        Returns:
            Created TicketType resource
        """
        response = self._client.session.post('/tickettype', json=data)
        return self._create_resource(response)