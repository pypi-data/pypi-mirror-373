
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient


class AddressService:
    """Geographic data management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def seed_addresses(self) -> Dict:
        """Seed geographic data"""
        return self.client._make_request("POST", "/addresses/seed")
    
    # Country operations
    def create_country(self, name: str, iso_code: Optional[str] = None) -> Dict:
        """Create country"""
        data = {"name": name}
        if iso_code:
            data["iso_code"] = iso_code
        return self.client._make_request("POST", "/countries", data)
    
    def list_countries(self) -> List[Dict]:
        """List all countries"""
        return self.client._make_request("GET", "/countries")
    
    def get_country(self, country_id: int) -> Dict:
        """Get country details"""
        return self.client._make_request("GET", f"/countries/{country_id}")
    
    def update_country(self, country_id: int, country_data: Dict) -> Dict:
        """Update country"""
        return self.client._make_request("PATCH", f"/countries/{country_id}", country_data)
    
    # State operations
    def create_state(self, name: str, country_id: int) -> Dict:
        """Create state"""
        data = {"name": name, "country_id": country_id}
        return self.client._make_request("POST", "/states", data)
    
    def list_states_by_country(self, country_id: int) -> List[Dict]:
        """List states by country"""
        return self.client._make_request("GET", f"/countries/{country_id}/states")
    
    def get_state(self, state_id: int) -> Dict:
        """Get state details"""
        return self.client._make_request("GET", f"/states/{state_id}")
    
    def update_state(self, state_id: int, state_data: Dict) -> Dict:
        """Update state"""
        return self.client._make_request("PATCH", f"/states/{state_id}", state_data)
    
    # City operations
    def create_city(self, name: str, state_id: int, postal_code_prefix: Optional[str] = None) -> Dict:
        """Create city"""
        data = {"name": name, "state_id": state_id}
        if postal_code_prefix:
            data["postal_code_prefix"] = postal_code_prefix
        return self.client._make_request("POST", "/cities", data)
    
    def list_cities_by_state(self, state_id: int) -> List[Dict]:
        """List cities by state"""
        return self.client._make_request("GET", f"/states/{state_id}/cities")
    
    def get_city(self, city_id: int) -> Dict:
        """Get city details"""
        return self.client._make_request("GET", f"/cities/{city_id}")
    
    def update_city(self, city_id: int, city_data: Dict) -> Dict:
        """Update city"""
        return self.client._make_request("PATCH", f"/cities/{city_id}", city_data)
    
    # Address operations
    def create_address(self, street_address: str, city_id: int, state_id: int, 
                      country_id: int, postal_code: Optional[str] = None, 
                      lat: Optional[float] = None, lan: Optional[float] = None,
                      is_primary: bool = False) -> Dict:
        """Create address"""
        data = {
            "street_address": street_address,
            "city_id": city_id,
            "state_id": state_id,
            "country_id": country_id,
            "is_primary": is_primary
        }
        if postal_code:
            data["postal_code"] = postal_code
        if lat is not None:
            data["lat"] = lat
        if lan is not None:
            data["lan"] = lan
        return self.client._make_request("POST", "/addresses", data)
    
    def list_addresses(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List addresses with pagination"""
        params = {"limit": limit, "offset": offset}
        return self.client._make_request("GET", "/addresses", params=params)
    
    def get_address(self, address_id: int) -> Dict:
        """Get address details"""
        return self.client._make_request("GET", f"/addresses/{address_id}")
    
    def update_address(self, address_id: int, address_data: Dict) -> Dict:
        """Update address"""
        return self.client._make_request("PATCH", f"/addresses/{address_id}", address_data)
    
    def delete_address(self, address_id: int) -> Dict:
        """Delete address"""
        return self.client._make_request("DELETE", f"/addresses/{address_id}")

