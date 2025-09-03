from datetime import datetime, timedelta
from typing import Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


def get_access_token(api_url: str, username: str, password: str) -> Dict[str, Any]:
    """Acquire an access token for the Mapscale API."""
    url = f"{api_url}/api/v9/mapscale/auth/token"
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        logger.error("Failed to get Mapscale token: %s", response.text)
        response.raise_for_status()
    data = response.json()
    expires_at = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200))).isoformat()
    return {
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "expires_at": expires_at,
    }


def refresh_access_token(api_url: str, client_id: str, refresh_token: str) -> Dict[str, Any]:
    """Refresh an access token for the Mapscale API."""
    url = f"{api_url}/api/v9/mapscale/auth/token"
    payload = {
        "client_id": client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        logger.error("Failed to refresh Mapscale token: %s", response.text)
        response.raise_for_status()
    data = response.json()
    expires_at = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200))).isoformat()
    return {
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token", refresh_token),
        "expires_at": expires_at,
    }

