





# Convenience classes for common workflows
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient
from knowrithm_py.models.conversation import EntityType


class KnowrithmAgent:
    """High-level interface for agent operations"""
    
    def __init__(self, client: KnowrithmClient, agent_id: str):
        self.client = client
        self.agent_id = agent_id
        self._details = None
    
    def chat(self, message: str, conversation_id: Optional[str] = None, 
             entity_type: EntityType = EntityType.USER, entity_id: Optional[str] = None) -> Dict:
        """Send a message to this agent"""
        if not conversation_id:
            # Create new conversation
            conv = self.client.conversations.create(
                agent_id=self.agent_id,
                entity_type=entity_type,
                entity_id=entity_id
            )
            conversation_id = conv["id"]
        
        return self.client.messages.send_message(conversation_id, message)
    
    def get_details(self, force_refresh: bool = False) -> Dict:
        """Get agent details with caching"""
        if not self._details or force_refresh:
            self._details = self.client.agents.get(self.agent_id)
        return self._details
    
    def update(self, agent_data: Dict) -> Dict:
        """Update agent configuration"""
        result = self.client.agents.update(self.agent_id, agent_data)
        self._details = None  # Clear cache
        return result
    
    def train(self, training_data: Dict) -> Dict:
        """Trigger agent training"""
        return self.client.agents.train(self.agent_id, training_data)
    
    def get_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get agent conversations"""
        return self.client.conversations.list(
            agent_id=self.agent_id, 
            limit=limit, 
            offset=offset
        )
    
    def get_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get agent performance metrics"""
        return self.client.analytics.get_agent_metrics(
            self.agent_id, 
            start_date=start_date, 
            end_date=end_date
        )

