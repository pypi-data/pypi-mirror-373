from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuthResponse:
    """Authentication response data"""
    access_token: str
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    session_expires_at: Optional[datetime] = None
