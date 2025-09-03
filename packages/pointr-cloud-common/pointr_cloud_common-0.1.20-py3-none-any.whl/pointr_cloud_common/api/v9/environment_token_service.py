from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def _post_with_fallback(endpoints: list[str], payload: dict) -> requests.Response:
    for endpoint in endpoints:
        try:
            response = requests.post(endpoint, json=payload)
            if response.ok:
                return response
        except requests.RequestException:
            continue  # Try next endpoint
    raise Exception("All attempts to acquire token failed.")


def get_access_token(client_id: str, api_url: str, username: str, password: str) -> Dict[str, Any]:
    endpoints = [
        f"{api_url}/api/v9/identity/clients/{client_id}/auth/token",
        f"{api_url}/api/v9/identity/auth/token"
    ]
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    try:
        response = _post_with_fallback(endpoints, payload)
        data = response.json()
        expires_at = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 10800))).isoformat()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_at": expires_at,
            "client_identifier": client_id
        }
    except Exception as e:
        logger.error(f"Failed to get token: {str(e)}")
        raise


def refresh_access_token(client_id: str, api_url: str, refresh_token: str) -> Dict[str, Any]:
    endpoints = [
        f"{api_url}/api/v9/identity/clients/{client_id}/auth/token",
        f"{api_url}/api/v9/identity/auth/token"
    ]
    payload = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    try:
        response = _post_with_fallback(endpoints, payload)
        data = response.json()
        expires_at = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 10800))).isoformat()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_at": expires_at,
            "client_identifier": client_id
        }
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise


def is_token_valid(token_data: Dict[str, Any]) -> bool:
    """
    Check if a token is still valid.
    
    Args:
        token_data: The token data containing the expiration time
        
    Returns:
        True if the token is still valid, False otherwise
    """
    try:
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        now = datetime.utcnow()
        
        # Add a buffer of 5 minutes to avoid edge cases
        return expires_at > now + timedelta(minutes=5)
    except Exception as e:
        logger.error(f"Error checking token validity: {str(e)}")
        return False
