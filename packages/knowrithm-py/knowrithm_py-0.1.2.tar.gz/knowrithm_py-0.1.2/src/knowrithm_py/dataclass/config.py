
from dataclasses import dataclass


@dataclass
class KnowrithmConfig:
    """Configuration for Knowrithm API client"""
    base_url: str
    api_version: str = "v1"
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    retry_backoff_factor: float = 2.0

