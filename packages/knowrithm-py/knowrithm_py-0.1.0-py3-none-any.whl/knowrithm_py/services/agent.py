
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient
from knowrithm_py.models.agent import AgentStatus


class AgentService:
    """Chatbot agent management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def create(self, agent_data: Dict) -> Dict:
        """Create a new chatbot agent"""
        return self.client._make_request("POST", "/agents", agent_data)
    
    def list(self, company_id: Optional[str] = None) -> List[Dict]:
        """List agents"""
        params = {"company_id": company_id} if company_id else {}
        return self.client._make_request("GET", "/agents", params=params)
    
    def get(self, agent_id: str) -> Dict:
        """Get agent details"""
        return self.client._make_request("GET", f"/agents/{agent_id}")
    
    def update(self, agent_id: str, agent_data: Dict) -> Dict:
        """Update agent configuration"""
        return self.client._make_request("PUT", f"/agents/{agent_id}", agent_data)
    
    def patch(self, agent_id: str, agent_data: Dict) -> Dict:
        """Partially update agent configuration"""
        return self.client._make_request("PATCH", f"/agents/{agent_id}", agent_data)
    
    def delete(self, agent_id: str) -> Dict:
        """Soft delete an agent"""
        return self.client._make_request("DELETE", f"/agents/{agent_id}")
    
    def restore(self, agent_id: str) -> Dict:
        """Restore a soft-deleted agent"""
        return self.client._make_request("PATCH", f"/agents/{agent_id}/restore")
    
    def update_status(self, agent_id: str, status: AgentStatus) -> Dict:
        """Update agent status"""
        return self.client._make_request("PATCH", f"/agents/{agent_id}/status", {"status": status.value})
    
    def train(self, agent_id: str, training_data: Dict) -> Dict:
        """Trigger agent training"""
        return self.client._make_request("POST", f"/agents/{agent_id}/train", training_data)
    
    def get_training_status(self, agent_id: str) -> Dict:
        """Get agent training status"""
        return self.client._make_request("GET", f"/agents/{agent_id}/training-status")
