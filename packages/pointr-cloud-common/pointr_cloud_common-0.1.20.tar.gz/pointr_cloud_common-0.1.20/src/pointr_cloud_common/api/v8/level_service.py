from typing import Dict, Any, List
import logging

from pointr_cloud_common.dto.v9 import LevelDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


class LevelApiService(BaseApiService):
    """Service for level-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _to_level_dto(self, data: Dict[str, Any], site_fid: str, building_fid: str) -> LevelDTO:
        try:
            return LevelDTO(
                fid=str(data.get("levelIndex")),
                name=data.get("levelLongTitle", ""),
                shortName=data.get("levelShortTitle"),
                levelNumber=data.get("levelIndex"),
                typeCode="level-outline",
                sid=site_fid,
                bid=building_fid,
            )
        except ValidationError as e:
            raise V8ApiError(f"Failed to parse level: {str(e)}")

    def get_levels(self, site_fid: str, building_fid: str) -> List[LevelDTO]:
        endpoint = f"api/v8/buildings/{building_fid}/levels/draft"
        data = self._make_request("GET", endpoint)
        results = data.get("results", []) if isinstance(data, dict) else []
        return [self._to_level_dto(l, site_fid, building_fid) for l in results]

    def get_level_by_id(self, site_fid: str, building_fid: str, level_id: str) -> LevelDTO:
        levels = self.get_levels(site_fid, building_fid)
        for level in levels:
            if level.fid == level_id:
                return level
        raise V8ApiError(f"No level found with id {level_id}")


    def create_level(
        self,
        site_fid: str,
        building_fid: str,
        level_id: str,
        level: Dict[str, Any],
    ) -> str:
        """Create a level using the swagger specified endpoint."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_id}"
        self._make_request("POST", endpoint, level)
        return level_id


    def update_level(
        self,
        site_fid: str,
        building_fid: str,
        level_id: str,
        level: Dict[str, Any],
    ) -> str:
        """Update a level using the swagger specified endpoint."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_id}"
        self._make_request("PATCH", endpoint, level)
        return level_id


    def delete_level(self, site_fid: str, building_fid: str, level_id: str) -> bool:
        """Delete a level using the swagger specified endpoint."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_id}"
        self._make_request("DELETE", endpoint)
        return True
