
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient

class DatabaseService:
    """Database connection and management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def create_connection(self, connection_data: Dict) -> Dict:
        """Create database connection"""
        return self.client._make_request("POST", "/database-connection", connection_data)
    
    def list_connections(self, active_only: bool = True) -> List[Dict]:
        """List database connections"""
        params = {"active_only": active_only}
        return self.client._make_request("GET", "/database-connection", params=params)
    
    def get_connection(self, connection_id: str) -> Dict:
        """Get database connection details"""
        return self.client._make_request("GET", f"/database-connection/{connection_id}")
    
    def update_connection(self, connection_id: str, connection_data: Dict) -> Dict:
        """Update database connection"""
        return self.client._make_request("PUT", f"/database-connection/{connection_id}", connection_data)
    
    def patch_connection(self, connection_id: str, connection_data: Dict) -> Dict:
        """Partially update database connection"""
        return self.client._make_request("PATCH", f"/database-connection/{connection_id}", connection_data)
    
    def delete_connection(self, connection_id: str) -> Dict:
        """Soft delete database connection"""
        return self.client._make_request("DELETE", f"/database-connection/{connection_id}")
    
    def restore_connection(self, connection_id: str) -> Dict:
        """Restore soft-deleted database connection"""
        return self.client._make_request("PATCH", f"/database-connection/{connection_id}/restore")
    
    def test_connection(self, connection_id: str) -> Dict:
        """Test database connection"""
        return self.client._make_request("POST", f"/database-connection/{connection_id}/test")
    
    def analyze_database(self, connection_id: str) -> Dict:
        """Analyze database schema"""
        return self.client._make_request("POST", f"/database-connection/{connection_id}/analyze")
    
    def get_tables(self, connection_id: str) -> List[Dict]:
        """Get database tables"""
        return self.client._make_request("GET", f"/database-connection/{connection_id}/tables")
    
    def get_table(self, table_id: str) -> Dict:
        """Get table details"""
        return self.client._make_request("GET", f"/database-tables/{table_id}")
    
    def refresh_table_metadata(self, table_id: str) -> Dict:
        """Refresh table metadata"""
        return self.client._make_request("POST", f"/database-tables/{table_id}/refresh")
    
    def search(self, query: str, connection_ids: Optional[List[str]] = None) -> Dict:
        """Search across connected databases"""
        data = {"query": query}
        if connection_ids:
            data["connection_ids"] = connection_ids
        return self.client._make_request("POST", "/database-connection/search", data)
