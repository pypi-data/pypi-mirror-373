



import time
import requests
from typing import Dict, Optional
from knowrithm_py.config.config import Config
from knowrithm_py.dataclass.config import KnowrithmConfig
from knowrithm_py.dataclass.error import KnowrithmAPIError


class KnowrithmClient:
    """
    Main client for interacting with the Knowrithm API
    
    Example usage:
        client = KnowrithmClient("https://app.knowrithm.org")
        auth_response = client.auth.login("user@example.com", "password")
        
        # Create a company
        company = client.companies.create({
            "name": "Acme Corp",
            "email": "contact@acme.com"
        })
        
        # Create an agent
        agent = client.agents.create({
            "name": "Customer Support Bot",
            "company_id": company["id"]
        })
    """
    
    def __init__(self, config: Optional[KnowrithmConfig] = None):
        self.config = config or KnowrithmConfig(base_url=Config.KNOWRITHM_BASE_URL)
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._session = requests.Session()
        
        
        
        from knowrithm_py.services.address import AddressService
        from knowrithm_py.services.admin import AdminService
        from knowrithm_py.services.agent import AgentService
        from knowrithm_py.services.auth import AuthService, SessionService, UserService
        from knowrithm_py.services.company import CompanyService
        from knowrithm_py.services.conversation import ConversationService, MessageService
        from knowrithm_py.services.dashboard import AnalyticsService
        from knowrithm_py.services.database import DatabaseService
        from knowrithm_py.services.document import DocumentService
        from knowrithm_py.services.lead import LeadService
        
        
        # Initialize service modules
        self.auth = AuthService(self)
        self.users = UserService(self)
        self.companies = CompanyService(self)
        self.agents = AgentService(self)
        self.leads = LeadService(self)
        self.documents = DocumentService(self)
        self.databases = DatabaseService(self)
        self.conversations = ConversationService(self)
        self.messages = MessageService(self)
        self.analytics = AnalyticsService(self)
        self.addresses = AddressService(self)
        self.sessions = SessionService(self)
        self.admin = AdminService(self)
    
    @property
    def base_url(self) -> str:
        return f"{self.config.base_url}/{self.config.api_version}"
    
    def set_access_token(self, token: str, refresh_token: Optional[str] = None):
        """Set the access token for authenticated requests"""
        self._access_token = token
        self._refresh_token = refresh_token
        self._session.headers.update({"Authorization": f"Bearer {token}"})
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        authenticated: bool = True
    ) -> Dict:
        """Make HTTP request with error handling and retries"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Add content type for JSON requests
        if data and not files and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=data if data and not files else None,
                    data=data if files else None,
                    params=params,
                    files=files,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )
                
                if response.status_code == 401 and authenticated and self._refresh_token:
                    # Try to refresh token
                    if self._refresh_auth_token():
                        # Retry the request with new token
                        continue
                
                if response.status_code >= 400:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except ValueError:
                        error_data = {"detail": response.text}
                    
                    raise KnowrithmAPIError(
                        message=error_data.get("detail", error_data.get("message", f"HTTP {response.status_code}")),
                        status_code=response.status_code,
                        response_data=error_data,
                        error_code=error_data.get("error_code")
                    )
                
                # Return empty dict for successful requests with no content
                if not response.content:
                    return {"success": True}
                    
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise KnowrithmAPIError(f"Request failed after {self.config.max_retries} attempts: {str(e)}")
                time.sleep(self.config.retry_backoff_factor ** attempt)
        
        raise KnowrithmAPIError("Max retries exceeded")
    
    def _refresh_auth_token(self) -> bool:
        """Attempt to refresh the authentication token"""
        if not self._refresh_token:
            return False
        
        try:
            response = self._session.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self._refresh_token},
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.set_access_token(
                    auth_data["access_token"],
                    auth_data.get("refresh_token", self._refresh_token)
                )
                return True
                
        except Exception:
            pass
            
        return False


