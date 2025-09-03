from datetime import datetime, timedelta
from typing import Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


def get_access_token(api_url: str, username: str, password: str) -> Dict[str, Any]:
    """Acquire an access token for V8 API."""
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    url = f"{api_url}/api/v8/auth/token"
    
    response = requests.post(url, json=payload)
    
    if not response.ok:
        logger.error("Failed to get V8 token: %s", response.text)
        response.raise_for_status()

    data = response.json()
    
    # Extract token data from the result field
    token_data = data.get("result", {})
    if not token_data:
        raise ValueError("No token data in response")
        
    expires_at = (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 7200))).isoformat()
    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": expires_at,
    }


def refresh_access_token(api_url: str, refresh_token: str) -> Dict[str, Any]:
    """Refresh an access token using a refresh token."""
    payload = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    url = f"{api_url}/api/v8/auth/token"
    
    response = requests.post(url, json=payload)
    
    if not response.ok:
        logger.error("Failed to refresh V8 token: %s", response.text)
        response.raise_for_status()

    data = response.json()
    
    # Extract token data from the result field
    token_data = data.get("result", {})
    if not token_data:
        raise ValueError("No token data in response")
        
    expires_at = (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 7200))).isoformat()
    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token", refresh_token),
        "expires_at": expires_at,
    }
