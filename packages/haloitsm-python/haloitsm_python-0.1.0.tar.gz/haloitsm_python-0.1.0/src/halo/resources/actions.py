"""Action resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class Action(Resource):
    """Represents an action/update on a ticket in Halo."""
    
    def add_reaction(self, reaction_type: str) -> Dict[str, Any]:
        """Add a reaction to this action.
        
        Args:
            reaction_type: Type of reaction to add
            
        Returns:
            Reaction response
        """
        return self._client.session.post('/Actions/reaction', json={
            'action_id': self.id,
            'type': reaction_type
        })
    
    def mark_as_reviewed(self) -> Dict[str, Any]:
        """Mark this action as reviewed.
        
        Returns:
            Review response
        """
        return self._client.session.post('/Actions/Review', json={
            'action_id': self.id
        })


class ActionList(ListResource):
    """Handles list operations for actions."""
    
    def list(
        self,
        ticket_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_private: bool = False,
        page_size: int = 100,
        page_no: int = 1,
        **kwargs
    ) -> List[Action]:
        """List actions with filters.
        
        Args:
            ticket_id: Filter by ticket ID
            user_id: Filter by user ID
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            include_private: Include private actions
            page_size: Number of results per page
            page_no: Page number
            **kwargs: Additional filters
            
        Returns:
            List of Action resources
        """
        params = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'startdate': start_date,
            'enddate': end_date,
            'includeprivate': include_private,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Actions', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'actions' in response:
            items = response['actions']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, action_id: int, **kwargs) -> Action:
        """Get a specific action.
        
        Args:
            action_id: ID of the action
            **kwargs: Additional parameters
            
        Returns:
            Action resource
        """
        response = self._client.session.get(f'/Actions/{action_id}', params=kwargs)
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> Action:
        """Create a new action.
        
        Args:
            data: Action data including ticket_id, note_html, outcome_id, etc.
            
        Returns:
            Created Action resource
        """
        response = self._client.session.post('/Actions', json=data)
        return self._create_resource(response)
    
    def delete(self, action_id: int) -> None:
        """Delete an action.
        
        Args:
            action_id: ID of the action to delete
        """
        self._client.session.delete(f'/Actions/{action_id}')