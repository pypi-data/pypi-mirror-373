

from typing import Any, Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient
from knowrithm_py.models.user import UserRole, UserStatus


class AdminService:
    """Administrative operations service (admin only)"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def list_all_users(self, status: Optional[UserStatus] = None, 
                      role: Optional[UserRole] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all users with filters"""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status.value
        if role:
            params["role"] = role.value
        return self.client._make_request("GET", "/admin/users", params=params)
    
    def get_user_details(self, user_id: str) -> Dict:
        """Get detailed user information"""
        return self.client._make_request("GET", f"/admin/users/{user_id}")
    
    def update_user_status(self, user_id: str, status: UserStatus, reason: Optional[str] = None) -> Dict:
        """Update user status"""
        data = {"status": status.value}
        if reason:
            data["reason"] = reason
        return self.client._make_request("PATCH", f"/admin/users/{user_id}/status", data)
    
    def update_user_role(self, user_id: str, role: UserRole) -> Dict:
        """Update user role"""
        return self.client._make_request("PATCH", f"/admin/users/{user_id}/role", {"role": role.value})
    
    def get_system_metrics(self, metric_type: Optional[str] = None, 
                          start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get system performance metrics"""
        params = {}
        if metric_type:
            params["metric_type"] = metric_type
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.client._make_request("GET", "/admin/metrics", params=params)
    
    def get_audit_logs(self, entity_type: Optional[str] = None, event_type: Optional[str] = None,
                      risk_level: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get audit logs with filters"""
        params = {"limit": limit, "offset": offset}
        if entity_type:
            params["entity_type"] = entity_type
        if event_type:
            params["event_type"] = event_type
        if risk_level:
            params["risk_level"] = risk_level
        return self.client._make_request("GET", "/admin/audit-logs", params=params)
    
    def get_system_configuration(self) -> Dict:
        """Get system configuration"""
        return self.client._make_request("GET", "/admin/config")
    
    def update_system_configuration(self, config_key: str, config_value: Any) -> Dict:
        """Update system configuration"""
        data = {"config_key": config_key, "config_value": config_value}
        return self.client._make_request("PATCH", "/admin/config", data)
    
    def force_password_reset(self, user_id: str) -> Dict:
        """Force password reset for user"""
        return self.client._make_request("POST", f"/admin/users/{user_id}/force-password-reset")
    
    def impersonate_user(self, user_id: str) -> Dict:
        """Impersonate user (super admin only)"""
        return self.client._make_request("POST", f"/admin/users/{user_id}/impersonate")

