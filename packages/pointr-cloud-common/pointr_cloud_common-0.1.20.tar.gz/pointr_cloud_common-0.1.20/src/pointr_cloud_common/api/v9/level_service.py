from typing import Dict, Any, List
import logging
from pointr_cloud_common.dto.v9.level_dto import LevelDTO
from pointr_cloud_common.dto.v9.create_response_dto import CreateResponseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError

class LevelApiService(BaseApiService):
    """Service for level-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_levels(self, site_fid: str, building_fid: str) -> List[LevelDTO]:
        """
        Get all levels for a building.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            
        Returns:
            A list of LevelDTO objects
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/levels"
        data = self._make_request("GET", endpoint)
        try:
            # Check if the response is a feature collection
            if isinstance(data, dict) and data.get("type") == "FeatureCollection" and "features" in data:
                # Extract level data from features
                levels = []
                for feature in data["features"]:
                    if isinstance(feature, dict) and "properties" in feature:
                        # Create a level DTO from the feature properties
                        try:
                            level = LevelDTO.from_api_json(feature["properties"])
                            levels.append(level)
                        except ValidationError as e:
                            self.logger.warning(f"Failed to parse level from feature: {str(e)}")
                return levels
            # If not a feature collection, try the original parsing
            return LevelDTO.list_from_api_json(data)
        except ValidationError as e:
            self.logger.error(f"Failed to parse levels: {str(e)}")
            raise V9ApiError(f"Failed to parse levels: {str(e)}")

    def get_level_by_id(self, site_fid: str, building_fid: str, level_id: str) -> LevelDTO:
        """
        Get a level by its ID.

        Args:
            site_fid: The site FID
            building_fid: The building FID
            level_id: The level ID

        Returns:
            A LevelDTO object
        """
        # First get all levels
        all_levels = self.get_levels(site_fid, building_fid)
        
        # Find the level with the matching FID
        for level in all_levels:
            if level.fid == level_id:
                return level
 
        raise V9ApiError(f"No level found with ID {level_id}")

    def create_level(self, site_fid: str, building_fid: str, level: Dict[str, Any]) -> str:
        """
        Create a level in a building.

        Args:
            site_fid: The site FID
            building_fid: The building FID
            level: The level data

        Returns:
            The FID of the created level
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/levels"
        data = self._make_request("POST", endpoint, level)
        try:
            return CreateResponseDTO.from_api_json(data).fid
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse create response: {str(e)}")

    def update_level(self, site_fid: str, building_fid: str, level_id: str, level: Dict[str, Any]) -> str:
        """
        Update a level in a building.

        Args:
            site_fid: The site FID
            building_fid: The building FID
            level_id: The level ID
            level: The level data
            
        Returns:
            The FID of the updated level
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/levels/{level_id}"
        data = self._make_request("PUT", endpoint, level)
        try:
            return CreateResponseDTO.from_api_json(data).fid
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse update response: {str(e)}")

    def delete_level(self, site_fid: str, building_fid: str, level_id: str) -> bool:
        """
        Delete a level from a building.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            level_id: The level ID
            
        Returns:
            True if the level was deleted successfully
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/levels/{level_id}"
        self._make_request("DELETE", endpoint)
        return True
