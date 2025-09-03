"""Google Cloud dependencies check and imports."""

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
