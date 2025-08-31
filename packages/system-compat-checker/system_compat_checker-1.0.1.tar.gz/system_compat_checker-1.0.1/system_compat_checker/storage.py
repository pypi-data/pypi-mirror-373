"""Storage module for securely storing API keys.

This module uses the keyring library to securely store and retrieve API keys.
"""

import keyring
from typing import Optional

# Constants
SERVICE_NAME = "system-compat-checker"
USERNAME = "groq-api-key"


def store_api_key(api_key: str) -> bool:
    """Store the API key securely.
    
    Args:
        api_key: The API key to store.
        
    Returns:
        bool: True if the API key was stored successfully, False otherwise.
    """
    try:
        keyring.set_password(SERVICE_NAME, USERNAME, api_key)
        return True
    except Exception:
        return False


def get_api_key() -> Optional[str]:
    """Retrieve the stored API key.
    
    Returns:
        Optional[str]: The stored API key, or None if not found.
    """
    try:
        api_key = keyring.get_password(SERVICE_NAME, USERNAME)
        return api_key
    except Exception:
        return None


def delete_api_key() -> bool:
    """Delete the stored API key.
    
    Returns:
        bool: True if the API key was deleted successfully, False otherwise.
    """
    try:
        keyring.delete_password(SERVICE_NAME, USERNAME)
        return True
    except Exception:
        return False