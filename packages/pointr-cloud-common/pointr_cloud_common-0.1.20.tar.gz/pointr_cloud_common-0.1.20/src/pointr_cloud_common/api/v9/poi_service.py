from typing import Dict, Any
import logging

from pointr_cloud_common.api.v9.base_service import BaseApiService
from pointr_cloud_common.helpers.poi_excel_service_base import PoiExcelServiceBase


class PoiApiService(BaseApiService):
    """Service for POI related V9 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _draft_site_endpoint(self, site_fid: str) -> str:
        return f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/pois"

    def _draft_building_endpoint(self, site_fid: str, building_fid: str) -> str:
        return (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/pois"
        )

    def _draft_level_endpoint(self, site_fid: str, building_fid: str, level_fid: str) -> str:
        return (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/levels/{level_fid}/pois"
        )

    def get_site_pois(self, site_fid: str, published: bool = False) -> Dict[str, Any]:
        """Retrieve POIs for a site."""
        if published:
            endpoint = (
                f"api/v9/content/published/clients/{self.client_id}/sites/{site_fid}/pois"
            )
        else:
            endpoint = self._draft_site_endpoint(site_fid)
        return self._make_request("GET", endpoint)

    def create_site_pois(self, site_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        """Create POIs at site level."""
        endpoint = self._draft_site_endpoint(site_fid)
        return self._make_request("POST", endpoint, pois)

    def delete_site_pois(self, site_fid: str) -> bool:
        """Delete all site level POIs."""
        endpoint = self._draft_site_endpoint(site_fid)
        self._make_request("DELETE", endpoint)
        return True

    def get_building_pois(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        """Retrieve POIs for a building."""
        endpoint = self._draft_building_endpoint(site_fid, building_fid)
        return self._make_request("GET", endpoint)

    def create_building_pois(self, site_fid: str, building_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        """Create POIs for a building."""
        endpoint = self._draft_building_endpoint(site_fid, building_fid)
        return self._make_request("POST", endpoint, pois)

    def delete_building_pois(self, site_fid: str, building_fid: str) -> bool:
        """Delete all POIs for a building."""
        endpoint = self._draft_building_endpoint(site_fid, building_fid)
        self._make_request("DELETE", endpoint)
        return True

    def get_level_pois(self, site_fid: str, building_fid: str, level_fid: str) -> Dict[str, Any]:
        """Retrieve POIs for a level."""
        endpoint = self._draft_level_endpoint(site_fid, building_fid, level_fid)
        return self._make_request("GET", endpoint)

    def create_level_pois(self, site_fid: str, building_fid: str, level_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        """Create POIs for a level."""
        endpoint = self._draft_level_endpoint(site_fid, building_fid, level_fid)
        return self._make_request("POST", endpoint, pois)

    def delete_level_pois(self, site_fid: str, building_fid: str, level_fid: str) -> bool:
        """Delete all POIs for a level."""
        endpoint = self._draft_level_endpoint(site_fid, building_fid, level_fid)
        self._make_request("DELETE", endpoint)
        return True

    def get_site_pois_excel(self, site_fid: str, published: bool = False) -> str:
        """Retrieve POIs for a site in Excel-compatible CSV format."""
        endpoint = (f"api/v9/content/published/clients/{self.client_id}/sites/{site_fid}/pois" 
                   if published else self._draft_site_endpoint(site_fid))
        response = self._make_request("GET", endpoint)
        return self._excel_service._convert_to_excel_csv(response)

    def get_building_pois_excel(self, site_fid: str, building_fid: str) -> str:
        """Retrieve POIs for a building in Excel-compatible CSV format."""
        response = self._make_request("GET", self._draft_building_endpoint(site_fid, building_fid))
        return self._excel_service._convert_to_excel_csv(response)

