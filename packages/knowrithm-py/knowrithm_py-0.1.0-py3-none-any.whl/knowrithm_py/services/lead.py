
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient


class LeadService:
    """Lead management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def register(self, lead_data: Dict) -> Dict:
        """Lead self-registration"""
        return self.client._make_request("POST", "/leads/register", lead_data, authenticated=False)
    
    def create(self, lead_data: Dict) -> Dict:
        """Create lead (company admin)"""
        return self.client._make_request("POST", "/leads", lead_data)
    
    def list(self, company_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """List leads with optional filters"""
        params = {}
        if company_id:
            params["company_id"] = company_id
        if status:
            params["status"] = status
        return self.client._make_request("GET", "/leads", params=params)
    
    def get(self, lead_id: str) -> Dict:
        """Get lead details"""
        return self.client._make_request("GET", f"/leads/{lead_id}")
    
    def update(self, lead_id: str, lead_data: Dict) -> Dict:
        """Update lead information"""
        return self.client._make_request("PUT", f"/leads/{lead_id}", lead_data)
    
    def patch(self, lead_id: str, lead_data: Dict) -> Dict:
        """Partially update lead information"""
        return self.client._make_request("PATCH", f"/leads/{lead_id}", lead_data)
    
    def delete(self, lead_id: str) -> Dict:
        """Soft delete a lead"""
        return self.client._make_request("DELETE", f"/leads/{lead_id}")
    
    def update_status(self, lead_id: str, status: str, notes: Optional[str] = None) -> Dict:
        """Update lead status"""
        data = {"status": status}
        if notes:
            data["notes"] = notes
        return self.client._make_request("PATCH", f"/leads/{lead_id}/status", data)
    
    def add_notes(self, lead_id: str, notes: str) -> Dict:
        """Add notes to a lead"""
        return self.client._make_request("POST", f"/leads/{lead_id}/notes", {"notes": notes})
