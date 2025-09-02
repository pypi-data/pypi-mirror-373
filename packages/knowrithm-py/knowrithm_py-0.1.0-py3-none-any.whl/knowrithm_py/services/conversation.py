
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient
from knowrithm_py.models.conversation import ConversationStatus, EntityType


class ConversationService:
    """Conversation management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def create(self, agent_id: str, entity_type: EntityType = EntityType.USER,
               entity_id: Optional[str] = None, **kwargs) -> Dict:
        """Create new conversation"""
        data = {
            "agent_id": agent_id,
            "entity_type": entity_type.value,
            **kwargs
        }
        if entity_id:
            data["entity_id"] = entity_id
        return self.client._make_request("POST", "/conversations", data)
    
    def list(self, agent_id: Optional[str] = None, status: Optional[ConversationStatus] = None,
             limit: int = 50, offset: int = 0) -> List[Dict]:
        """List conversations with pagination"""
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status.value
        return self.client._make_request("GET", "/conversations", params=params)
    
    def get(self, conversation_id: str) -> Dict:
        """Get conversation details"""
        return self.client._make_request("GET", f"/conversations/{conversation_id}")
    
    def update(self, conversation_id: str, conversation_data: Dict) -> Dict:
        """Update conversation metadata"""
        return self.client._make_request("PUT", f"/conversations/{conversation_id}", conversation_data)
    
    def delete(self, conversation_id: str) -> Dict:
        """Soft delete conversation"""
        return self.client._make_request("DELETE", f"/conversations/{conversation_id}")
    
    def restore(self, conversation_id: str) -> Dict:
        """Restore soft-deleted conversation"""
        return self.client._make_request("PATCH", f"/conversations/{conversation_id}/restore")
    
    def archive(self, conversation_id: str) -> Dict:
        """Archive conversation"""
        return self.client._make_request("PATCH", f"/conversations/{conversation_id}/archive")
    
    def end_conversation(self, conversation_id: str, satisfaction_rating: Optional[int] = None) -> Dict:
        """End a conversation"""
        data = {}
        if satisfaction_rating:
            data["satisfaction_rating"] = satisfaction_rating
        return self.client._make_request("POST", f"/conversations/{conversation_id}/end", data)


class MessageService:
    """Message management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def send_message(self, conversation_id: str, content: str, role: str = "user", **kwargs) -> Dict:
        """Send message to conversation"""
        data = {
            "content": content,
            "role": role,
            **kwargs
        }
        return self.client._make_request("POST", f"/conversations/{conversation_id}/messages", data)
    
    def list_messages(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get conversation messages with pagination"""
        params = {"limit": limit, "offset": offset}
        return self.client._make_request("GET", f"/conversations/{conversation_id}/messages", params=params)
    
    def get_message(self, message_id: str) -> Dict:
        """Get message details"""
        return self.client._make_request("GET", f"/messages/{message_id}")
    
    def delete_message(self, message_id: str) -> Dict:
        """Soft delete message"""
        return self.client._make_request("DELETE", f"/messages/{message_id}")
    
    def restore_message(self, message_id: str) -> Dict:
        """Restore soft-deleted message"""
        return self.client._make_request("PATCH", f"/messages/{message_id}/restore")
    
    def rate_message(self, message_id: str, rating: int, feedback: Optional[str] = None) -> Dict:
        """Rate a message (1-5 stars)"""
        data = {"rating": rating}
        if feedback:
            data["feedback"] = feedback
        return self.client._make_request("POST", f"/messages/{message_id}/rate", data)
