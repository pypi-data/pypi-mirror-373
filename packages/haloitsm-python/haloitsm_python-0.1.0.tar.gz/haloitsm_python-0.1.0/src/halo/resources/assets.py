"""Asset resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource, ListResource


class Asset(Resource):
    """Represents an asset/device in Halo."""
    
    def update(self, data: Dict[str, Any]) -> 'Asset':
        """Update this asset.
        
        Args:
            data: Fields to update
            
        Returns:
            Updated asset resource
        """
        update_data = {'id': self.id}
        update_data.update(data)
        
        response = self._client.session.post(f'/Asset/{self.id}', json=update_data)
        self._update_from_raw(response)
        return self
    
    def delete(self) -> None:
        """Delete this asset."""
        self._client.session.delete(f'/Asset/{self.id}')
    
    def get_software(self) -> List[Dict[str, Any]]:
        """Get installed software for this asset.
        
        Returns:
            List of software applications
        """
        return self._client.session.get(f'/AssetSoftware', params={'asset_id': self.id})
    
    def get_changes(self) -> List[Dict[str, Any]]:
        """Get change history for this asset.
        
        Returns:
            List of asset changes
        """
        return self._client.session.get(f'/AssetChange', params={'asset_id': self.id})


class AssetList(ListResource):
    """Handles list operations for assets."""
    
    def list(
        self,
        client_id: Optional[int] = None,
        site_id: Optional[int] = None,
        asset_type_id: Optional[int] = None,
        inactive: bool = False,
        search: Optional[str] = None,
        page_size: int = 100,
        page_no: int = 1,
        order: Optional[str] = None,
        order_desc: bool = False,
        **kwargs
    ) -> List[Asset]:
        """List assets with filters.
        
        Args:
            client_id: Filter by client
            site_id: Filter by site
            asset_type_id: Filter by asset type
            inactive: Include inactive assets
            search: Search term
            page_size: Number of results per page
            page_no: Page number
            order: Field to order by
            order_desc: Order descending
            **kwargs: Additional filters
            
        Returns:
            List of Asset resources
        """
        params = {
            'client_id': client_id,
            'site_id': site_id,
            'assettype_id': asset_type_id,
            'includeinactive': inactive,
            'search': search,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            'order': order,
            'orderdesc': order_desc,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Asset', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'assets' in response:
            items = response['assets']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, asset_id: int, **kwargs) -> Asset:
        """Get a specific asset.
        
        Args:
            asset_id: ID of the asset
            **kwargs: Additional parameters
            
        Returns:
            Asset resource
        """
        response = self._client.session.get(f'/Asset/{asset_id}', params=kwargs)
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> Asset:
        """Create a new asset.
        
        Args:
            data: Asset data
            
        Returns:
            Created Asset resource
        """
        response = self._client.session.post('/Asset', json=data)
        return self._create_resource(response)
    
    def get_next_tag(self) -> str:
        """Get the next available asset tag.
        
        Returns:
            Next asset tag
        """
        response = self._client.session.get('/Asset/NextTag')
        return response.get('tag', '')
    
    def search(self, query: str, limit: int = 100) -> List[Asset]:
        """Search assets.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching Asset resources
        """
        return self.list(search=query, page_size=limit)