
from typing import Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient
from knowrithm_py.models.document import DocumentStatus



class DocumentService:
    """Document management and processing service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def upload(self, file_path: str, agent_id: Optional[str] = None, **metadata) -> Dict:
        """Upload and process documents"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = metadata.copy()
            if agent_id:
                data['agent_id'] = agent_id
            return self.client._make_request("POST", "/documents/upload", data=data, files=files)
    
    def upload_from_bytes(self, file_data: bytes, filename: str, 
                         agent_id: Optional[str] = None, **metadata) -> Dict:
        """Upload document from bytes"""
        files = {'file': (filename, file_data)}
        data = metadata.copy()
        if agent_id:
            data['agent_id'] = agent_id
        return self.client._make_request("POST", "/documents/upload", data=data, files=files)
    
    def list(self, agent_id: Optional[str] = None, status: Optional[DocumentStatus] = None) -> List[Dict]:
        """List uploaded documents"""
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status.value
        return self.client._make_request("GET", "/documents", params=params)
    
    def get(self, document_id: str) -> Dict:
        """Get document details"""
        return self.client._make_request("GET", f"/documents/{document_id}")
    
    def search(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """Search within documents"""
        data = {"query": query}
        if filters:
            data.update(filters)
        return self.client._make_request("POST", "/documents/search", data)
    
    def delete(self, document_id: str) -> Dict:
        """Soft delete document"""
        return self.client._make_request("DELETE", f"/documents/{document_id}")
    
    def restore(self, document_id: str) -> Dict:
        """Restore soft-deleted document"""
        return self.client._make_request("PATCH", f"/documents/{document_id}/restore")
    
    def get_processing_status(self, document_id: str) -> Dict:
        """Get document processing status"""
        return self.client._make_request("GET", f"/documents/{document_id}/status")
    
    def reprocess(self, document_id: str) -> Dict:
        """Reprocess a document"""
        return self.client._make_request("POST", f"/documents/{document_id}/reprocess")
    
    # Chunk management
    def list_chunks(self, document_id: str) -> List[Dict]:
        """List document chunks"""
        return self.client._make_request("GET", f"/documents/{document_id}/chunks")
    
    def get_chunk(self, chunk_id: str) -> Dict:
        """Get chunk details"""
        return self.client._make_request("GET", f"/chunks/{chunk_id}")
    
    def delete_chunk(self, chunk_id: str) -> Dict:
        """Soft delete document chunk"""
        return self.client._make_request("DELETE", f"/chunks/{chunk_id}")
    
    def restore_chunk(self, chunk_id: str) -> Dict:
        """Restore soft-deleted chunk"""
        return self.client._make_request("PATCH", f"/chunks/{chunk_id}/restore")
