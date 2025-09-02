"""Report resource for Halo API."""
from typing import List, Dict, Any, Optional, Union
from .base import Resource, ListResource


class Report(Resource):
    """Represents a report in Halo."""
    
    def run(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run this report with parameters.
        
        Args:
            parameters: Report parameters
            
        Returns:
            Report execution result
        """
        data = {
            'report_id': self.id,
            'parameters': parameters or {}
        }
        return self._client.session.post('/Report/print', json=data)
    
    def generate_pdf(
        self,
        parameters: Optional[Dict[str, Any]] = None,
        format_type: str = 'pdf'
    ) -> Dict[str, Any]:
        """Generate a PDF version of this report.
        
        Args:
            parameters: Report parameters
            format_type: Output format (pdf, excel, etc.)
            
        Returns:
            PDF generation result with download URL
        """
        data = {
            'report_id': self.id,
            'parameters': parameters or {},
            'format': format_type
        }
        return self._client.session.post('/Report/createpdf', json=data)
    
    def bookmark(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a bookmark for this report with parameters.
        
        Args:
            parameters: Report parameters to save
            
        Returns:
            Bookmark creation result
        """
        data = {
            'report_id': self.id,
            'parameters': parameters or {}
        }
        return self._client.session.post('/Report/Bookmark', json=data)
    
    def get_data(self, published_id: str) -> Union[Dict[str, Any], bytes]:
        """Get report data by published ID.
        
        Args:
            published_id: Published report ID
            
        Returns:
            Report data
        """
        return self._client.session.get(f'/ReportData/{published_id}')


class ReportList(ListResource):
    """Handles list operations for reports."""
    
    def list(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_dashboard: Optional[bool] = None,
        page_size: int = 100,
        page_no: int = 1,
        **kwargs
    ) -> List[Report]:
        """List reports with filters.
        
        Args:
            category: Filter by report category
            search: Search term
            is_dashboard: Filter dashboard reports
            page_size: Number of results per page
            page_no: Page number
            **kwargs: Additional filters
            
        Returns:
            List of Report resources
        """
        params = {
            'category': category,
            'search': search,
            'isdashboard': is_dashboard,
            'pageinate': True,
            'page_size': page_size,
            'page_no': page_no,
            **kwargs
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._client.session.get('/Report', params=params)
        
        # Handle response format
        if isinstance(response, dict) and 'reports' in response:
            items = response['reports']
        elif isinstance(response, list):
            items = response
        else:
            items = []
        
        return [self._create_resource(item) for item in items]
    
    def get(self, report_id: int, **kwargs) -> Report:
        """Get a specific report.
        
        Args:
            report_id: ID of the report
            **kwargs: Additional parameters
            
        Returns:
            Report resource
        """
        response = self._client.session.get(f'/Report/{report_id}', params=kwargs)
        return self._create_resource(response)
    
    def create(self, data: Dict[str, Any]) -> Report:
        """Create a new report.
        
        Args:
            data: Report data including name, description, SQL, etc.
            
        Returns:
            Created Report resource
        """
        response = self._client.session.post('/Report', json=data)
        return self._create_resource(response)
    
    def get_dashboards(self) -> List[Report]:
        """Get all dashboard reports.
        
        Returns:
            List of dashboard Report resources
        """
        return self.list(is_dashboard=True)
    
    def search(self, query: str, limit: int = 100) -> List[Report]:
        """Search reports.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching Report resources
        """
        return self.list(search=query, page_size=limit)