from typing import Dict, Any, Optional, List
import json
import logging
from pointr_cloud_common.dto.v9.client_metadata_dto import ClientMetadataDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError

class ClientApiService(BaseApiService):
    """Service for client-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_client_metadata(self) -> ClientMetadataDTO:
        """
        Get metadata for the client.
        
        Returns:
            A ClientMetadataDTO object
        """
        endpoint = f"api/v9/content/published/clients/{self.client_id}"
        data = self._make_request("GET", endpoint)
        try:
            return ClientMetadataDTO.from_api_json(data)
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse client metadata: {str(e)}")

    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """
        Update a client in the target environment.
        
        Args:
            client_id: The ID of the client to update
            client_data: The client data to update
            
        Returns:
            True if the client was updated successfully
        """
        endpoint = f"api/v9/content/published/clients/{client_id}"
        
        self.logger.info(f"Updating client with payload: {json.dumps(client_data)[:1000]}...")
        self._make_request("PUT", endpoint, client_data)
        return True

    def create_client(self, client_data: Dict[str, Any]) -> str:
        """
        Create a client in the target environment.
        
        Args:
            client_data: The client data to create
            
        Returns:
            The identifier of the created client
        """
        endpoint = f"api/v9/content/published/clients"
        
        self.logger.info(f"Creating client with payload: {json.dumps(client_data)[:1000]}...")
        response = self._make_request("POST", endpoint, client_data)
        
        # Extract the client identifier from the response
        if isinstance(response, dict) and "identifier" in response:
            return response["identifier"]
        
        # If we can't extract the identifier, return the client_id from the data
        return client_data.get("identifier", "unknown")

    def get_client_gps_geofences(self) -> List[Dict[str, Any]]:
        """
        Get GPS geofences for the client.
        
        Returns:
            A list of GPS geofence features
        """
        endpoint = f"api/v9/content/published/clients/{self.client_id}/gps-geofences"
        data = self._make_request("GET", endpoint)
        
        if not data or "features" not in data:
            return []
            
        return data["features"]
