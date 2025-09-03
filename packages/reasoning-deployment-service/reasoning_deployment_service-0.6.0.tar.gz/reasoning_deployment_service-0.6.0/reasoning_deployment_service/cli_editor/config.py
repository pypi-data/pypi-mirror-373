"""Configuration management for Agent Space Deployment Service."""
import os
from typing import Dict, Any
try:
    import dotenv
except ImportError:
    dotenv = None


class Config:
    """Configuration class to manage environment variables and defaults."""
    
    def __init__(self, environment: str = "DEV"):
        """Initialize config with environment selection (DEV or PROD)."""
        self.environment = environment.upper()
        
        # Load from environment-specific variables (same as GUI editor)
        self.project_id = os.getenv(f"{self.environment}_PROJECT_ID")
        self.project_number = os.getenv(f"{self.environment}_PROJECT_NUMBER") 
        self.location = os.getenv(f"{self.environment}_PROJECT_LOCATION")
        self.agent_space = os.getenv(f"{self.environment}_AGENT_SPACE_ENGINE")
        self.staging_bucket = os.getenv(f"{self.environment}_STAGING_BUCKET")
        self.oauth_client_id = os.getenv(f"{self.environment}_OAUTH_CLIENT_ID")
        self.oauth_client_secret = os.getenv(f"{self.environment}_OAUTH_CLIENT_SECRET")
        
        # Alias for compatibility
        self.engine_name = self.agent_space
        
        # Legacy fallbacks for backward compatibility
        if not self.project_id:
            self.project_id = os.getenv("PROJECT_ID") or "your-project-id"
        if not self.project_number:
            self.project_number = os.getenv("PROJECT_NUMBER") or "000000000000"
        if not self.location:
            self.location = os.getenv("GCP_LOCATION", "us-central1")
        if not self.agent_space:
            self.agent_space = os.getenv("AGENT_SPACE_ENGINE") or "your-engine"
            self.engine_name = self.agent_space
        if not self.staging_bucket:
            self.staging_bucket = os.getenv("GCS_STAGING_BUCKET", "gs://your-staging")
        if not self.oauth_client_id:
            self.oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "")
        if not self.oauth_client_secret:
            self.oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")
            
        self.agent_import = os.getenv("AGENT_IMPORT", "")  # e.g. "your.module:root_agent"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API client initialization."""
        return {
            "project_id": self.project_id,
            "project_number": self.project_number,
            "location": self.location,
            "engine_name": self.engine_name,
            "agent_space": self.agent_space,
            "staging_bucket": self.staging_bucket,
            "oauth_client_id": self.oauth_client_id,
            "oauth_client_secret": self.oauth_client_secret,
            "agent_import": self.agent_import,
        }
    
    @property
    def is_configured(self) -> bool:
        """Check if minimum required configuration is available."""
        return all([
            self.project_id and self.project_id != "your-project-id",
            self.project_number and self.project_number != "000000000000", 
            self.location,
            self.agent_space and self.agent_space != "your-engine"
        ])


def loadenv(env_path: str):
    """Load environment variables from the specified file."""
    if not dotenv:
        print("⚠️ python-dotenv not available. Please install it or set environment variables manually.")
        return
        
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    dotenv.load_dotenv(env_path)
    print(f"Environment variables loaded from {env_path}")
