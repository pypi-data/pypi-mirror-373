from typing import Dict, Any, Optional
import logging
from pointr_cloud_common.api.v8.errors import V8ApiError


class BaseApiService:
    """Base class for all V8 API services."""

    def __init__(self, api_service):
        """Initialize the base API service."""
        self.api_service = api_service
        self.base_url = getattr(api_service, "base_url", "")
        self.client_id = getattr(api_service, "client_id", "")
        self.user_email = getattr(api_service, "user_email", None)
        self.token = getattr(api_service, "token", "")
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the V8 API."""
        if json_data is None:
            return self.api_service._make_request(method, endpoint)
        return self.api_service._make_request(method, endpoint, json_data)
