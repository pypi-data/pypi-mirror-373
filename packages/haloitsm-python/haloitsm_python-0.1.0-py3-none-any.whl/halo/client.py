"""Main Halo API client."""
from typing import Optional, Dict, Any
import logging

from .auth import OAuth2TokenManager
from .session import HaloSession
from .resources.ticket_types import TicketType, TicketTypeList
from .resources.tickets import Ticket, TicketList
from .resources.actions import Action, ActionList
from .resources.assets import Asset, AssetList
from .resources.categories import Category, CategoryList
from .resources.clients import Client, ClientList
from .resources.users import User, UserList
from .resources.kb_articles import KBArticle, KBArticleList
from .resources.reports import Report, ReportList
from .resources.comments import Comment, CommentList
from .resources.attachments import Attachment, AttachmentList
from .exceptions import HaloError

logger = logging.getLogger(__name__)


class HaloClient:
    """Main client for interacting with the Halo API.
    
    This client provides a clean interface to the Halo API, following patterns
    similar to popular API clients like jira-python. All business logic should
    be kept outside of this client.
    
    Example:
        >>> client = HaloClient(
        ...     base_url="https://instance.haloservicedesk.com",
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret"
        ... )
        >>> 
        >>> # List ticket types
        >>> ticket_types = client.ticket_types.list()
        >>> 
        >>> # Get specific ticket type with fields
        >>> ticket_type = client.ticket_types.get(24, include_details=True)
        >>> fields = ticket_type.get_fields()
        >>> 
        >>> # Create a ticket
        >>> ticket = client.tickets.create({
        ...     'tickettype_id': 24,
        ...     'summary': 'New ticket',
        ...     'details': 'Ticket details'
        ... })
        >>> 
        >>> # Update ticket
        >>> ticket.update({'status_id': 2})
    """
    
    def __init__(
        self,
        base_url: str,
        client_id: str = None,
        client_secret: str = None,
        username: str = None,
        password: str = None,
        token: str = None,
        refresh_token: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize Halo client.
        
        Args:
            base_url: Base URL of Halo instance. Can be either:
                      - Instance URL (recommended): https://instance.haloservicedesk.com
                      - API URL (backward compatibility): https://instance.haloservicedesk.com/api
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret (for client credentials flow)
            username: Username (for password flow)
            password: Password (for password flow)
            token: Existing access token
            refresh_token: Existing refresh token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            
        Raises:
            HaloError: If authentication parameters are invalid
        """
        # Handle both instance URLs and API URLs
        base_url_clean = base_url.rstrip('/')
        
        if base_url_clean.endswith('/api'):
            # User provided API URL - extract instance URL
            self.instance_url = base_url_clean[:-4]  # Remove '/api'
            self.api_url = base_url_clean
        else:
            # User provided instance URL - add /api
            self.instance_url = base_url_clean
            self.api_url = f"{base_url_clean}/api"
        
        # Initialize authentication (uses instance URL for auth endpoints)
        self.auth = OAuth2TokenManager(
            base_url=self.instance_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            token=token,
            refresh_token=refresh_token
        )
        
        # Initialize session (uses API URL for REST calls)
        self.session = HaloSession(
            base_url=self.api_url,
            token_manager=self.auth,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Initialize resource managers
        self._init_resources()
    
    def _init_resources(self):
        """Initialize resource managers."""
        # Core ticket management
        self.ticket_types = TicketTypeList(self, TicketType)
        self.tickets = TicketList(self, Ticket)
        self.actions = ActionList(self, Action)
        
        # Comments and attachments
        self.comments = CommentList(self, Comment)
        self.attachments = AttachmentList(self, Attachment)
        
        # Asset management
        self.assets = AssetList(self, Asset)
        
        # User and client management
        self.clients = ClientList(self, Client)
        self.users = UserList(self, User)
        
        # Categories
        self.categories = CategoryList(self, Category)
        
        # Knowledge base
        self.kb_articles = KBArticleList(self, KBArticle)
        
        # Reporting
        self.reports = ReportList(self, Report)
    
    # Convenience methods for backward compatibility
    
    def ticket_type(self, ticket_type_id: int, **kwargs) -> TicketType:
        """Get a ticket type by ID.
        
        Args:
            ticket_type_id: ID of the ticket type
            **kwargs: Additional parameters
            
        Returns:
            TicketType resource
        """
        return self.ticket_types.get(ticket_type_id, **kwargs)
    
    def ticket(self, ticket_id: int, **kwargs) -> Ticket:
        """Get a ticket by ID.
        
        Args:
            ticket_id: ID of the ticket
            **kwargs: Additional parameters
            
        Returns:
            Ticket resource
        """
        return self.tickets.get(ticket_id, **kwargs)
    
    def create_ticket(self, data: Dict[str, Any]) -> Ticket:
        """Create a new ticket.
        
        Args:
            data: Ticket data
            
        Returns:
            Created Ticket resource
        """
        return self.tickets.create(data)
    
    def asset(self, asset_id: int, **kwargs) -> Asset:
        """Get an asset by ID.
        
        Args:
            asset_id: ID of the asset
            **kwargs: Additional parameters
            
        Returns:
            Asset resource
        """
        return self.assets.get(asset_id, **kwargs)
    
    def client(self, client_id: int, **kwargs) -> Client:
        """Get a client by ID.
        
        Args:
            client_id: ID of the client
            **kwargs: Additional parameters
            
        Returns:
            Client resource
        """
        return self.clients.get(client_id, **kwargs)
    
    def user(self, user_id: int, **kwargs) -> User:
        """Get a user by ID.
        
        Args:
            user_id: ID of the user
            **kwargs: Additional parameters
            
        Returns:
            User resource
        """
        return self.users.get(user_id, **kwargs)
    
    def kb_article(self, article_id: int, **kwargs) -> KBArticle:
        """Get a KB article by ID.
        
        Args:
            article_id: ID of the article
            **kwargs: Additional parameters
            
        Returns:
            KBArticle resource
        """
        return self.kb_articles.get(article_id, **kwargs)
    
    def report(self, report_id: int, **kwargs) -> Report:
        """Get a report by ID.
        
        Args:
            report_id: ID of the report
            **kwargs: Additional parameters
            
        Returns:
            Report resource
        """
        return self.reports.get(report_id, **kwargs)
    
    # Additional API endpoints can be added here as needed
    
    def get(self, endpoint: str, **kwargs) -> Any:
        """Make a raw GET request to the API.
        
        Args:
            endpoint: API endpoint
            **kwargs: Request parameters
            
        Returns:
            Response data
        """
        return self.session.get(endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Any:
        """Make a raw POST request to the API.
        
        Args:
            endpoint: API endpoint
            **kwargs: Request parameters
            
        Returns:
            Response data
        """
        return self.session.post(endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Any:
        """Make a raw PUT request to the API.
        
        Args:
            endpoint: API endpoint
            **kwargs: Request parameters
            
        Returns:
            Response data
        """
        return self.session.put(endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Any:
        """Make a raw DELETE request to the API.
        
        Args:
            endpoint: API endpoint
            **kwargs: Request parameters
            
        Returns:
            Response data
        """
        return self.session.delete(endpoint, **kwargs)