import logging
from pointr_cloud_common.dto.v9 import (
  ClientMetadataDTO, CreateResponseDTO, GpsGeofenceDTO, SdkConfigurationDTO, SiteDTO, BuildingDTO, LevelDTO
)
from pointr_cloud_common.dto.v9.validation import ValidationError
from typing import List, Dict, Any, Optional, Union, cast
import json
import requests
import time

from pointr_cloud_common.api.v9.base_service import V9ApiError
from pointr_cloud_common.api.v9.site_service import SiteApiService
from pointr_cloud_common.api.v9.building_service import BuildingApiService
from pointr_cloud_common.api.v9.level_service import LevelApiService
from pointr_cloud_common.api.v9.sdk_service import SdkApiService
from pointr_cloud_common.api.v9.client_service import ClientApiService
from pointr_cloud_common.api.v9.poi_service import PoiApiService
from pointr_cloud_common.api.v9.feature_service import FeatureApiService
from pointr_cloud_common.api.v9.environment_token_service import get_access_token, refresh_access_token

class V9ApiService:
    def __init__(
        self,
        config: Dict[str, str],
        user_email: Optional[str] = None,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ):
        """
        Initialize the V9 API service with configuration and authentication.
        
        Args:
            config: Configuration for the API service containing:
                - api_url: Base URL for the API
                - client_identifier: Client identifier
                - username: Username for authentication (if token/refresh_token not provided)
                - password: Password for authentication (if token/refresh_token not provided)
            user_email: Optional user email for logging
            token: Optional pre-authenticated access token
            refresh_token: Optional refresh token to obtain a new access token if token not provided
        """
        self.base_url = config["api_url"]
        self.client_id = config["client_identifier"]
        self.user_email = user_email
        self.config = config
        self.logger = logging.getLogger(__name__)

        if token:
            self.token = token
        elif refresh_token:
            token_data = refresh_access_token(
                client_id=config["client_identifier"],
                api_url=config["api_url"],
                refresh_token=refresh_token
            )
            self.token = token_data["access_token"]
        else:
            token_data = get_access_token(
                client_id=config["client_identifier"],
                api_url=config["api_url"],
                username=config["username"],
                password=config["password"]
            )
            self.token = token_data["access_token"]

        # Initialize sub-services
        self.site_service = SiteApiService(self)
        self.building_service = BuildingApiService(self)
        self.level_service = LevelApiService(self)
        self.sdk_service = SdkApiService(self)
        self.client_service = ClientApiService(self)
        self.feature_service = FeatureApiService(self)
        self.poi_service = PoiApiService(self)


    def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the V9 API with error handling."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Track operation time
        start_time = time.time()
        operation_name = f"{method} {endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Log the operation duration
            duration = time.time() - start_time
            self.logger.debug(f"API operation {operation_name} completed in {duration:.2f}s")
            
            if not response.ok:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_details = response.json()
                    if isinstance(error_details, dict):
                        if "message" in error_details:
                            error_msg += f", message: {error_details['message']}"
                        elif "error" in error_details:
                            error_msg += f", error: {error_details['error']}"
                        else:
                            error_msg += f", details: {error_details}"
                    else:
                        error_msg += f", details: {error_details}"
                except:
                    error_msg += f", response: {response.text[:200]}"
                
                raise V9ApiError(
                    error_msg, 
                    status_code=response.status_code, 
                    response_text=response.text
                )
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # If the response is not JSON, return an empty dict
                if response.text.strip():
                    self.logger.warning(f"Non-JSON response from API: {response.text[:200]}")
                return {}
                
        except requests.RequestException as e:
            # Log the operation failure
            duration = time.time() - start_time
            self.logger.error(f"API operation {operation_name} failed after {duration:.2f}s: {str(e)}")
            raise V9ApiError(f"Request error: {str(e)}")

    # Site methods - delegated to site_service
    def get_sites(self) -> List[SiteDTO]:
        return self.site_service.get_sites()

    def create_site(self, site: SiteDTO, source_api_service=None) -> str:
        return self.site_service.create_site(site, source_api_service)

    def update_site(self, site_id: str, site: SiteDTO, source_api_service=None) -> str:
        return self.site_service.update_site(site_id, site, source_api_service)

    def update_site_extra_data(self, site_fid: str, extra_data: Dict[str, Any]) -> bool:
        """
        Update only the extra data for a site.
        
        Args:
            site_fid: The FID of the site to update
            extra_data: The extra data to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        return self.site_service.update_site_extra_data(site_fid, extra_data)

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        return self.site_service.get_site_by_fid(site_fid)

    # Building methods - delegated to building_service
    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        return self.building_service.get_buildings(site_fid)

    def get_building_by_fid(self, site_fid: str, building_fid: str) -> BuildingDTO:
        return self.building_service.get_building_by_fid(site_fid, building_fid)

    def create_building(self, site_fid: str, building: BuildingDTO, source_api_service=None) -> str:
        return self.building_service.create_building(site_fid, building, source_api_service)

    def update_building(self, site_fid: str, building_fid: str, building: BuildingDTO, source_api_service=None) -> str:
        return self.building_service.update_building(site_fid, building_fid, building, source_api_service)

    def update_building_extra_data(self, site_fid: str, building_fid: str, extra_data: Dict[str, Any]) -> bool:
        """
        Update only the extra data for a building.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            extra_data: The extra data to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        return self.building_service.update_building_extra_data(site_fid, building_fid, extra_data)

    # Level methods - delegated to level_service
    def get_levels(self, site_fid: str, building_fid: str) -> List[LevelDTO]:
        return self.level_service.get_levels(site_fid, building_fid)

    def get_level_by_id(self, site_fid: str, building_fid: str, level_id: str) -> LevelDTO:
        return self.level_service.get_level_by_id(site_fid, building_fid, level_id)

    def create_level(self, site_fid: str, building_fid: str, level: Dict[str, Any]) -> str:
        return self.level_service.create_level(site_fid, building_fid, level)

    def update_level(self, site_fid: str, building_fid: str, level_id: str, level: Dict[str, Any]) -> str:
        return self.level_service.update_level(site_fid, building_fid, level_id, level)

    def delete_level(self, site_fid: str, building_fid: str, level_id: str) -> bool:
        return self.level_service.delete_level(site_fid, building_fid, level_id)

    # Client methods - delegated to client_service
    def get_client_metadata(self) -> ClientMetadataDTO:
        return self.client_service.get_client_metadata()

    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        return self.client_service.update_client(client_id, client_data)

    def create_client(self, client_data: Dict[str, Any]) -> str:
        return self.client_service.create_client(client_data)

    # SDK Configuration methods - delegated to sdk_service
    def get_client_sdk_config(self) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_client_sdk_config()

    def get_site_sdk_config(self, site_fid: str) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_site_sdk_config(site_fid)

    def get_building_sdk_config(self, site_fid: str, building_fid: str) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_building_sdk_config(site_fid, building_fid)

    def get_client_gps_geofences(self) -> list[dict]:
        # GPS_GEOFENCES_REMOVED: This method is temporarily disabled as client-level GPS geofences are deprecated.
        return []
    # GPS_GEOFENCES_REMOVED END

    def put_global_sdk_configurations(self, configs: List[SdkConfigurationDTO]) -> bool:
        return self.sdk_service.put_global_sdk_configurations(configs)

    def put_site_sdk_configurations(self, site_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        return self.sdk_service.put_site_sdk_configurations(site_fid, configs)

    def put_building_sdk_configurations(self, site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        return self.sdk_service.put_building_sdk_configurations(site_fid, building_fid, configs)

    # POI methods - delegated to poi_service
    def get_site_pois(self, site_fid: str, published: bool = False) -> Dict[str, Any]:
        return self.poi_service.get_site_pois(site_fid, published)

    def create_site_pois(self, site_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        return self.poi_service.create_site_pois(site_fid, pois)

    def delete_site_pois(self, site_fid: str) -> bool:
        return self.poi_service.delete_site_pois(site_fid)

    def get_building_pois(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        return self.poi_service.get_building_pois(site_fid, building_fid)

    def create_building_pois(self, site_fid: str, building_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        return self.poi_service.create_building_pois(site_fid, building_fid, pois)

    def delete_building_pois(self, site_fid: str, building_fid: str) -> bool:
        return self.poi_service.delete_building_pois(site_fid, building_fid)

    def get_level_pois(self, site_fid: str, building_fid: str, level_fid: str) -> Dict[str, Any]:
        return self.poi_service.get_level_pois(site_fid, building_fid, level_fid)

    def create_level_pois(self, site_fid: str, building_fid: str, level_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]:
        return self.poi_service.create_level_pois(site_fid, building_fid, level_fid, pois)

    def delete_level_pois(self, site_fid: str, building_fid: str, level_fid: str) -> bool:
        return self.poi_service.delete_level_pois(site_fid, building_fid, level_fid)

    # Feature methods - delegated to feature_service
    def get_site_features(self, site_fid: str) -> Dict[str, Any]:
        return self.feature_service.get_site_features(site_fid)

    def get_site_features_by_type(self, site_fid: str, type_code: str) -> Dict[str, Any]:
        return self.feature_service.get_site_features_by_type(site_fid, type_code)

    def get_site_paths(self, site_fid: str) -> Dict[str, Any]:
        return self.feature_service.get_site_paths(site_fid)

    def create_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        return self.feature_service.create_site_features(site_fid, features)

    def update_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        return self.feature_service.update_site_features(site_fid, features)

    def delete_site_features(self, site_fid: str) -> bool:
        return self.feature_service.delete_site_features(site_fid)
