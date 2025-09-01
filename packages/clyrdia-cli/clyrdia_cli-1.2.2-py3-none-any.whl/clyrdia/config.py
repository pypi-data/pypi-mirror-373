"""
Configuration management for Clyrdia CLI
"""
import os
from pathlib import Path
from typing import Optional

class Config:
    """Global configuration management for Clyrdia"""
    
    def __init__(self, env: str = None):
        self.env = env or os.getenv('CLYRDIA_ENV', 'production')
        self.api_base_url = self._get_api_base_url()
        self.config_dir = Path.home() / ".clyrdia"
        self.config_file = self.config_dir / "config.json"
    
    def _get_api_base_url(self) -> str:
        """Get API base URL based on environment"""
        if self.env == 'development':
            return "http://localhost:8000/api/v1"
        else:
            # Production Supabase URL
            return "https://rsboqbnuxcuncfjvqsio.supabase.co/functions/v1"
    
    def get_api_url(self, endpoint: str) -> str:
        """Get full API URL for an endpoint"""
        # Ensure endpoint starts with / and doesn't have double slashes
        clean_endpoint = endpoint.strip('/')
        return f"{self.api_base_url}/{clean_endpoint}"
    
    def get_dashboard_url(self, port: int = 3000) -> str:
        """Get local dashboard URL"""
        return f"http://localhost:{port}"
    
    def get_web_dashboard_url(self) -> str:
        """Get local dashboard URL (no hosted dashboard)"""
        return "http://localhost:3000"
    
    def get_auth_url(self) -> str:
        """Get authentication URL"""
        return "https://clyrdia.com/auth"
    
    def get_support_url(self) -> str:
        """Get support URL"""
        return "https://clyrdia.com/docs"
    
    def get_docs_url(self) -> str:
        """Get documentation URL"""
        return "https://clyrdia.com/docs"
    
    def get_community_url(self) -> str:
        """Get community URL"""
        return "https://clyrdia.com/docs"

# Global config instance
config = Config()
