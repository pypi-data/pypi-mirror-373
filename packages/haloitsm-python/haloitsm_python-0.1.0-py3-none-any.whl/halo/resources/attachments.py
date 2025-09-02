"""Attachment resources for Halo API."""
import os
import mimetypes
from typing import Dict, Any, Optional
from .base import Resource, ListResource


class Attachment(Resource):
    """Represents an attachment in Halo."""
    
    @property
    def filename(self) -> str:
        """Get the filename."""
        return self.raw.get('filename', '')
    
    @property
    def file_size(self) -> int:
        """Get the file size in bytes."""
        return self.raw.get('filesize', 0)
    
    @property
    def content_type(self) -> str:
        """Get the content type."""
        return self.raw.get('contenttype', '')
    
    @property
    def is_image(self) -> bool:
        """Check if this is an image attachment."""
        return self.content_type.startswith('image/')


class AttachmentList(ListResource):
    """List manager for attachments."""
    
    def add_to_ticket(
        self, 
        ticket_id: int, 
        file_path: str,
        description: Optional[str] = None
    ) -> Attachment:
        """Add an attachment to a ticket.
        
        Args:
            ticket_id: ID of the ticket
            file_path: Path to the file to attach
            description: Optional description for the attachment
            
        Returns:
            Created attachment
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Prepare file for upload
        with open(file_path, 'rb') as f:
            files = {
                'file': (filename, f, content_type)
            }
            
            # Add metadata
            data = {}
            if description:
                data['description'] = description
            
            # Post to the ticket's attachments endpoint
            response = self.session.session.request(
                'POST',
                f"{self.session.base_url}/tickets/{ticket_id}/attachments",
                files=files,
                data=data,
                headers=self.session.token_manager.get_headers()
            )
            
            if response.status_code >= 400:
                from ..exceptions import HaloAPIError
                raise HaloAPIError(f"Failed to upload attachment: {response.status_code}")
            
            # Parse response
            result = response.json() if response.content else {}
            return Attachment(self.session, result)
    
    def add_to_ticket_base64(
        self, 
        ticket_id: int, 
        filename: str,
        file_content: bytes,
        content_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> Attachment:
        """Add an attachment to a ticket using base64 content.
        
        Args:
            ticket_id: ID of the ticket
            filename: Name for the file
            file_content: File content as bytes
            content_type: MIME type of the file
            description: Optional description for the attachment
            
        Returns:
            Created attachment
        """
        import base64
        
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Encode content as base64
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        data = {
            'filename': filename,
            'filedata': file_b64,
            'contenttype': content_type
        }
        
        if description:
            data['description'] = description
        
        # Post to the ticket's attachments endpoint
        response = self.session.post(f'tickets/{ticket_id}/attachments', json=data)
        return Attachment(self.session, response)
    
    def get_for_ticket(self, ticket_id: int) -> list:
        """Get all attachments for a ticket.
        
        Args:
            ticket_id: ID of the ticket
            
        Returns:
            List of attachments
        """
        response = self.session.get(f'tickets/{ticket_id}/attachments')
        
        attachments = []
        if isinstance(response, list):
            for item in response:
                attachments.append(Attachment(self.session, item))
        elif isinstance(response, dict) and 'attachments' in response:
            for item in response['attachments']:
                attachments.append(Attachment(self.session, item))
        
        return attachments