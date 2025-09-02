
from datetime import datetime
from typing import Dict, List

from knowrithm_py.dataclass.response import AuthResponse
from knowrithm_py.knowrithm.client import KnowrithmClient


class AuthService:
    """Authentication and user management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def register(self, email: str, password: str, first_name: str, last_name: str, 
                username: str, **kwargs) -> Dict:
        """Register a new user"""
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            **kwargs
        }
        return self.client._make_request("POST", "/auth/register", data, authenticated=False)
    
    def login(self, email: str, password: str, remember_me: bool = False) -> AuthResponse:
        """Login and set access token"""
        data = {"email": email, "password": password, "remember_me": remember_me}
        response = self.client._make_request("POST", "/auth/login", data, authenticated=False)
        
        auth_response = AuthResponse(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token"),
            user_id=response.get("user_id"),
            role=response.get("role"),
            session_expires_at=datetime.fromisoformat(response["expires_at"]) if response.get("expires_at") else None
        )
        
        self.client.set_access_token(auth_response.access_token, auth_response.refresh_token)
        return auth_response
    
    def logout(self) -> Dict:
        """Logout current user"""
        return self.client._make_request("POST", "/auth/logout")
    
    def refresh_token(self, refresh_token: str) -> AuthResponse:
        """Refresh authentication token"""
        data = {"refresh_token": refresh_token}
        response = self.client._make_request("POST", "/auth/refresh", data, authenticated=False)
        
        auth_response = AuthResponse(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token"),
            user_id=response.get("user_id"),
            role=response.get("role")
        )
        
        self.client.set_access_token(auth_response.access_token, auth_response.refresh_token)
        return auth_response
    
    def verify_email(self, token: str) -> Dict:
        """Verify email address with token"""
        data = {"token": token}
        return self.client._make_request("POST", "/auth/verify-email", data, authenticated=False)
    
    def resend_verification(self, email: str) -> Dict:
        """Resend email verification"""
        data = {"email": email}
        return self.client._make_request("POST", "/auth/resend-verification", data, authenticated=False)
    
    def forgot_password(self, email: str) -> Dict:
        """Request password reset"""
        data = {"email": email}
        return self.client._make_request("POST", "/auth/forgot-password", data, authenticated=False)
    
    def reset_password(self, token: str, new_password: str) -> Dict:
        """Reset password with token"""
        data = {"token": token, "new_password": new_password}
        return self.client._make_request("POST", "/auth/reset-password", data, authenticated=False)
    
    def change_password(self, current_password: str, new_password: str) -> Dict:
        """Change password for authenticated user"""
        data = {"current_password": current_password, "new_password": new_password}
        return self.client._make_request("POST", "/auth/change-password", data)





class SessionService:
    """User session management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def list_active_sessions(self) -> List[Dict]:
        """List active sessions for current user"""
        return self.client._make_request("GET", "/sessions")
    
    def revoke_session(self, session_id: str) -> Dict:
        """Revoke a specific session"""
        return self.client._make_request("DELETE", f"/sessions/{session_id}")
    
    def revoke_all_sessions(self) -> Dict:
        """Revoke all sessions except current"""
        return self.client._make_request("DELETE", "/sessions/all")
    
    def get_current_session(self) -> Dict:
        """Get current session details"""
        return self.client._make_request("GET", "/sessions/current")


class UserService:
    """User management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def get_profile(self) -> Dict:
        """Get current user profile"""
        return self.client._make_request("GET", "/user/profile")
    
    def update_profile(self, profile_data: Dict) -> Dict:
        """Update current user profile"""
        return self.client._make_request("PUT", "/user/profile", profile_data)
    
    def get_user(self, user_id: str) -> Dict:
        """Get specific user details"""
        return self.client._make_request("GET", f"/user/{user_id}")
    
    def update_preferences(self, preferences: Dict) -> Dict:
        """Update user preferences"""
        return self.client._make_request("PATCH", "/user/preferences", {"preferences": preferences})
    
    def enable_two_factor(self) -> Dict:
        """Enable two-factor authentication"""
        return self.client._make_request("POST", "/user/2fa/enable")
    
    def disable_two_factor(self, totp_code: str) -> Dict:
        """Disable two-factor authentication"""
        return self.client._make_request("POST", "/user/2fa/disable", {"totp_code": totp_code})
    
    def verify_two_factor(self, totp_code: str) -> Dict:
        """Verify two-factor authentication code"""
        return self.client._make_request("POST", "/user/2fa/verify", {"totp_code": totp_code})

