"""Knowledge Base Article resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class KBArticle(Resource):
    """Represents a knowledge base article in Halo."""
    
    def update(self, data: Dict[str, Any]) -> 'KBArticle':
        """Update this KB article.
        
        Args:
            data: Fields to update
            
        Returns:
            Updated KB article resource
        """
        update_data = {'id': self.id}
        update_data.update(data)
        
        response = self._client.session.post(f'/KBArticle/{self.id}', json=update_data)
        self._update_from_raw(response)
        return self
    
    def delete(self) -> None:
        """Delete this KB article."""
        self._client.session.delete(f'/KBArticle/{self.id}')
    
    def vote(self, helpful: bool) -> Dict[str, Any]:
        """Vote on this KB article.
        
        Args:
            helpful: True if helpful, False if not helpful
            
        Returns:
            Vote response
        """
        return self._client.session.post('/KBArticle/vote', json={
            'kb_id': self.id,
            'helpful': helpful
        })
    
    @property
    def url(self) -> str:
        """Get the URL for this KB article."""
        slug = getattr(self, 'slug', str(self.id))
        return f"{self._client.base_url.replace('/api', '')}/kb/{slug}"


class KBArticleList(ListResource):
    """Handles list operations for KB articles."""
    
    def list(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        page_size: int = 100,
        page_no: int = 1,
        order: Optional[str] = None,
        order_desc: bool = False,
        **kwargs
    ) -> List[KBArticle]:
        """List KB articles with filters.
        
        Args:
            search: Search term
            category_id: Filter by category
            tags: Filter by tags
            status: Filter by status (published, draft, etc.)
            page_size: Number of results per page
            page_no: Page number
            order: Field to order by
            order_desc: Order descending
            **kwargs: Additional filters
            
        Returns:
            List of KBArticle resources
        """
        params = {
            'search': search,
            'category_id': category_id,
            'tags': ','.join(tags) if tags else None,
            'status': status,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            'order': order,
            'orderdesc': order_desc,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/KBArticle', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'kbarticles' in response:
            items = response['kbarticles']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, article_id: int, **kwargs) -> KBArticle:
        """Get a specific KB article.
        
        Args:
            article_id: ID of the article
            **kwargs: Additional parameters
            
        Returns:
            KBArticle resource
        """
        response = self._client.session.get(f'/KBArticle/{article_id}', params=kwargs)
        return self._create_resource(response)
    
    def get_by_slug(self, slug: str) -> KBArticle:
        """Get a KB article by its slug (for anonymous access).
        
        Args:
            slug: Article slug
            
        Returns:
            KBArticle resource
        """
        response = self._client.session.get(f'/KBArticleAnon/{slug}')
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> KBArticle:
        """Create a new KB article.
        
        Args:
            data: Article data including title, content, category_id, etc.
            
        Returns:
            Created KBArticle resource
        """
        response = self._client.session.post('/KBArticle', json=data)
        return self._create_resource(response)
    
    def search(self, query: str, limit: int = 100) -> List[KBArticle]:
        """Search KB articles.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching KBArticle resources
        """
        return self.list(search=query, page_size=limit)