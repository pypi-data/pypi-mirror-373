# src/ordal_autohire_firebase/services/__init__.py
from .firebase_client import get_db 
__all__ = ["get_db", "init_agent_tools", "mcp_profile_helpers"]