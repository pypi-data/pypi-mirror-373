
from typing import Dict, Optional


class KnowrithmAPIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"KnowrithmAPIError(status={self.status_code}, code={self.error_code}): {self.message}"



