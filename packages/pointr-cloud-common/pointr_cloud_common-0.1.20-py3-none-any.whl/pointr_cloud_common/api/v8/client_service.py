from typing import Dict, Any
import logging

from pointr_cloud_common.dto.v9 import ClientMetadataDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


class ClientApiService(BaseApiService):
    """Service for client-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_client_metadata(self) -> ClientMetadataDTO:
        endpoint = f"api/v8/clients/{self.client_id}"
        data = self._make_request("GET", endpoint)
        result = data.get("result", data)
        try:
            return ClientMetadataDTO(
                identifier=str(result.get("clientInternalIdentifier")),
                name=result.get("clientTitle", ""),
                extra=result.get("clientExtraData", {}),
                externalIdentifier=result.get("clientExternalIdentifier"),
            )
        except ValidationError as e:
            raise V8ApiError(f"Failed to parse client metadata: {str(e)}")

    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """Update a client using V8 field names."""
        endpoint = f"api/v8/clients/{client_id}"

        payload = {}
        if "extra" in client_data:
            payload["clientExtraData"] = client_data["extra"]

        payload = {k: v for k, v in payload.items() if v is not None}

        self._make_request("PATCH", endpoint, payload)
        return True

    def create_client(self, client_data: Dict[str, Any]) -> str:
        raise NotImplementedError("Client creation is not supported in V8 API")

    def get_client_gps_geofences(self) -> list[Dict[str, Any]]:
        """Return published global geofences for the current client."""
        endpoint = f"api/v8/clients/{self.client_id}/geofences/global"
        data = self._make_request("GET", endpoint)
        # Swagger defines the response as a FeatureCollection with a ``features``
        # array, not ``results``
        return data.get("features", []) if isinstance(data, dict) else []
