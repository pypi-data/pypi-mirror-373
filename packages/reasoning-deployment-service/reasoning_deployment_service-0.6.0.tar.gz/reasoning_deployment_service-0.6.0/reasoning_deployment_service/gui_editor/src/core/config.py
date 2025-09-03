"""Configuration management for Agent Space Deployment Service."""
import os
from typing import Dict, Any
import dotenv


class Config:
    """Configuration class to manage environment variables and defaults."""

    def __init__(self):
        # Use new environment variable names
        self.project_id = os.getenv("DEV_PROJECT_ID") if os.getenv("DEV_PROJECT_ID") else os.getenv("PROD_PROJECT_ID")
        self.project_number = os.getenv("DEV_PROJECT_NUMBER") if os.getenv("DEV_PROJECT_NUMBER") else os.getenv("PROD_PROJECT_NUMBER")
        self.location = os.getenv("DEV_PROJECT_LOCATION") if os.getenv("DEV_PROJECT_LOCATION") else os.getenv("PROD_PROJECT_LOCATION")
        self.agent_space = os.getenv("DEV_AGENT_SPACE_ENGINE") if os.getenv("DEV_AGENT_SPACE_ENGINE") else os.getenv("PROD_AGENT_SPACE_ENGINE")
        self.engine_name = self.agent_space  # Alias for compatibility

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API client initialization."""
        return {
            "project_id": self.project_id,
            "project_number": self.project_number,
            "location": self.location,
            "agent_space": self.agent_space,
            "engine_name": self.engine_name,
        }

    @property
    def is_configured(self) -> bool:
        """Check if minimum required configuration is available."""
        return all([
            self.project_id,
            self.project_number,
            self.location,
            self.agent_space
        ])

def loadenv(env_path: str):
    """Load environment variables from the specified file."""
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    dotenv.load_dotenv(env_path)
    print(f"Environment variables loaded from {env_path}")
