"""Google Cloud dependencies check and imports."""
import warnings
import os

# Suppress Vertex AI API registration warnings
warnings.filterwarnings("ignore", message=".*Failed to register API methods.*")
warnings.filterwarnings("ignore", message=".*api_mode.*")
os.environ.setdefault("GOOGLE_CLOUD_DISABLE_GRPC_LOGS", "true")

HAS_GOOGLE = True
try:
    import requests
    import google.auth
    from google.auth.transport.requests import Request as GoogleAuthRequest
    import vertexai
    from vertexai.preview import reasoning_engines
    from vertexai import agent_engines
except Exception:
    HAS_GOOGLE = False

__all__ = [
    "HAS_GOOGLE",
    "requests",
    "google",
    "GoogleAuthRequest", 
    "vertexai",
    "reasoning_engines",
    "agent_engines"
]
