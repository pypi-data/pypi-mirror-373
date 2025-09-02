"""Comment resources for Halo API."""
from typing import Dict, Any, Optional
from .base import Resource, ListResource


class Comment(Resource):
    """Represents a comment/action in Halo."""
    
    @property
    def note(self) -> str:
        """Get the comment text."""
        return self.raw.get('note', '')
    
    @property
    def note_html(self) -> str:
        """Get the comment HTML."""
        return self.raw.get('note_html', '')
    
    @property
    def is_private(self) -> bool:
        """Check if this is a private comment."""
        return self.raw.get('hiddenfromuser', False)
    
    @property
    def who(self) -> str:
        """Get who made the comment."""
        return self.raw.get('who', '')
    
    @property
    def when(self) -> str:
        """Get when the comment was made."""
        return self.raw.get('when', '')


class CommentList(ListResource):
    """List manager for comments."""
    
    def add_to_ticket(
        self, 
        ticket_id: int, 
        note: str,
        is_private: bool = False,
        **kwargs
    ) -> Comment:
        """Add a comment to a ticket.
        
        Args:
            ticket_id: ID of the ticket
            note: Comment text
            is_private: Whether the comment is private (hidden from user)
            **kwargs: Additional comment properties
            
        Returns:
            Created comment
        """
        data = {
            'note': note,
            'hiddenfromuser': is_private,
            **kwargs
        }
        
        # Post to the ticket's actions endpoint
        response = self.session.post(f'tickets/{ticket_id}/actions', json=data)
        return Comment(self.session, response)
    
    def get_for_ticket(self, ticket_id: int) -> list:
        """Get all comments for a ticket.
        
        Args:
            ticket_id: ID of the ticket
            
        Returns:
            List of comments
        """
        response = self.session.get(f'tickets/{ticket_id}/actions')
        
        comments = []
        if isinstance(response, list):
            for item in response:
                comments.append(Comment(self.session, item))
        elif isinstance(response, dict) and 'actions' in response:
            for item in response['actions']:
                comments.append(Comment(self.session, item))
        
        return comments