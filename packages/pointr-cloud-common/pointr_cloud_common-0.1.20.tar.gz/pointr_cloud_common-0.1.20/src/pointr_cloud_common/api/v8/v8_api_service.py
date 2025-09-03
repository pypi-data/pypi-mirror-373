from typing import Dict, Any, List, Optional
import logging
import time
import requests
import json

from pointr_cloud_common.dto.v9 import (
    SiteDTO,
    BuildingDTO,
    LevelDTO,
    ClientMetadataDTO,
    SdkConfigurationDTO,
)
from pointr_cloud_common.api.v8.errors import V8ApiError
from pointr_cloud_common.api.v8.site_service import SiteApiService
from pointr_cloud_common.api.v8.building_service import BuildingApiService
from pointr_cloud_common.api.v8.level_service import LevelApiService
from pointr_cloud_common.api.v8.client_service import ClientApiService
from pointr_cloud_common.api.v8.sdk_service import SdkApiService
from pointr_cloud_common.api.v8.feature_service import FeatureApiService
from pointr_cloud_common.api.v8.poi_service import PoiApiService
from pointr_cloud_common.api.v8.environment_token_service import (
    get_access_token,
    refresh_access_token,
)


class V8ApiService:
    """Main entry point for interacting with the V8 API."""

    def __init__(
        self,
        config: Dict[str, str],
        user_email: Optional[str] = None,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        """Initialize the V8 API service."""
        self.base_url = config["api_url"]
        self.client_id = config["client_identifier"]
        self.user_email = user_email
        self.config = config
        self.logger = logging.getLogger(__name__)

        if token:
            self.token = token
        elif refresh_token:
            # V8 token helpers don't require the client identifier
            token_data = refresh_access_token(
                api_url=config["api_url"],
                refresh_token=refresh_token
            )
            self.token = token_data["access_token"]
        else:
            # V8 token helpers don't require the client identifier
            token_data = get_access_token(
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

    def _make_request(
        self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        start_time = time.time()
        try:
            method_upper = method.upper()
            if method_upper == "GET":
                response = requests.get(url, headers=headers)
            elif method_upper in {"POST", "PUT", "PATCH"}:
                request_fn = {
                    "POST": requests.post,
                    "PUT": requests.put,
                    "PATCH": requests.patch,
                }[method_upper]
                response = request_fn(url, headers=headers, json=json_data)
            elif method_upper == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            duration = time.time() - start_time
            self.logger.debug(
                f"V8 API {method} {endpoint} completed in {duration:.2f}s"
            )

            if not response.ok:
                # Attempt to extract an error message from the response body
                error_detail = ""
                try:
                    body = response.json()
                    error_detail = body.get("message") or body.get("error") or ""
                except ValueError:
                    body = None

                # Log full response text and status code for troubleshooting
                self.logger.error(
                    f"V8 API error {response.status_code}: {response.text}"
                )

                message = f"API request failed: {response.status_code}"
                if error_detail:
                    message += f" - {error_detail}"

                raise V8ApiError(
                    message,
                    response.status_code,
                    response.text,
                )

            return response.json()
        except requests.RequestException as e:
            duration = time.time() - start_time
            self.logger.error(
                f"V8 API {method} {endpoint} failed after {duration:.2f}s: {e}"
            )
            raise V8ApiError(f"Request error: {str(e)}")

    # Site methods
    def get_sites(self) -> List[SiteDTO]:
        return self.site_service.get_sites()

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        return self.site_service.get_site_by_fid(site_fid)

    def create_site(
        self, site: SiteDTO, source_api_service: Optional[Any] = None
    ) -> str:
        return self.site_service.create_site(site, source_api_service)

    def update_site(
        self,
        site_id: str,
        site: SiteDTO,
        source_api_service: Optional[Any] = None
    ) -> str:
        return self.site_service.update_site(site_id, site, source_api_service)

    def update_site_extra_data(self, site_fid: str, extra_data: Dict[str, Any]) -> bool:
        return self.site_service.update_site_extra_data(site_fid, extra_data)

    # Building methods
    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        return self.building_service.get_buildings(site_fid)

    def get_building_by_fid(self, site_fid: str, building_fid: str) -> BuildingDTO:
        return self.building_service.get_building_by_fid(site_fid, building_fid)

    def create_building(
        self,
        site_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
    ) -> str:
        return self.building_service.create_building(
            site_fid, building, source_api_service
        )

    def update_building(
        self,
        site_fid: str,
        building_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
    ) -> str:
        return self.building_service.update_building(
            site_fid, building_fid, building, source_api_service
        )

    def update_building_extra_data(
        self, site_fid: str, building_fid: str, extra_data: Dict[str, Any]
    ) -> bool:
        return self.building_service.update_building_extra_data(
            site_fid, building_fid, extra_data
        )

    # Level methods
    def get_levels(self, site_fid: str, building_fid: str) -> List[LevelDTO]:
        return self.level_service.get_levels(site_fid, building_fid)

    def get_level_by_id(
        self, site_fid: str, building_fid: str, level_id: str
    ) -> LevelDTO:
        return self.level_service.get_level_by_id(site_fid, building_fid, level_id)

    def create_level(
        self, site_fid: str, building_fid: str, level: Dict[str, Any]
    ) -> str:
        """Create a level extracting levelIndex from the payload."""
        level_id = str(level.get("levelIndex"))
        return self.level_service.create_level(
            site_fid, building_fid, level_id, level
        )

    def update_level(
        self,
        site_fid: str,
        building_fid: str,
        level_id: str,
        level: Dict[str, Any],
    ) -> str:
        return self.level_service.update_level(
            site_fid, building_fid, level_id, level
        )

    def delete_level(
        self, site_fid: str, building_fid: str, level_id: str
    ) -> bool:
        return self.level_service.delete_level(site_fid, building_fid, level_id)

    # Client methods
    def get_client_metadata(self) -> ClientMetadataDTO:
        return self.client_service.get_client_metadata()

    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        return self.client_service.update_client(client_id, client_data)

    def create_client(self, client_data: Dict[str, Any]) -> str:
        return self.client_service.create_client(client_data)

    def get_client_gps_geofences(self) -> List[Dict[str, Any]]:
        return self.client_service.get_client_gps_geofences()

    # SDK Config methods
    def get_client_sdk_config(self) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_client_sdk_config()

    def get_site_sdk_config(self, site_fid: str) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_site_sdk_config(site_fid)

    def get_building_sdk_config(
        self, site_fid: str, building_fid: str
    ) -> List[SdkConfigurationDTO]:
        return self.sdk_service.get_building_sdk_config(site_fid, building_fid)

    def put_global_sdk_configurations(
        self, configs: List[SdkConfigurationDTO]
    ) -> bool:
        return self.sdk_service.put_global_sdk_configurations(configs)

    def put_site_sdk_configurations(
        self, site_fid: str, configs: List[SdkConfigurationDTO]
    ) -> bool:
        return self.sdk_service.put_site_sdk_configurations(site_fid, configs)

    def put_building_sdk_configurations(
        self, site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]
    ) -> bool:
        return self.sdk_service.put_building_sdk_configurations(site_fid, building_fid, configs)

    # Feature methods
    def get_building_features(self, building_id: str) -> Dict[str, Any]:
        """Get all features for a building."""
        return self.feature_service.get_building_features(building_id)

    def get_building_features_by_type(self, building_id: str, type_code: str) -> Dict[str, Any]:
        """Get features of a specific type for a building."""
        return self.feature_service.get_building_features_by_type(building_id, type_code)

    def get_level_features(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """Get all features for a specific level."""
        return self.feature_service.get_level_features(building_id, level_index)

    def get_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> Dict[str, Any]:
        """Get features of a specific type for a level."""
        return self.feature_service.get_level_features_by_type(building_id, level_index, type_code)

    def get_site_features(self, site_id: str) -> Dict[str, Any]:
        """Get all features for a site."""
        return self.feature_service.get_site_features(site_id)

    def get_site_features_by_type(self, site_id: str, type_code: str) -> Dict[str, Any]:
        """Get features of a specific type for a site."""
        return self.feature_service.get_site_features_by_type(site_id, type_code)

    def get_site_paths(self, site_id: str) -> Dict[str, Any]:
        """Get all paths for a site."""
        return self.feature_service.get_site_paths(site_id)
    
    def get_site_graphs(self, site_id: str) -> Dict[str, Any]:
        """Get all graphs (paths) for a site using V8 graphs endpoint."""
        return self.feature_service.get_site_graphs(site_id)
    
    def create_site_features(self, site_id: str, features: Dict[str, Any]) -> bool:
        """Create features for a site."""
        try:
            self.feature_service.create_or_update_site_features(site_id, features)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create site features: {str(e)}")
            return False
    
    def create_site_graphs(self, site_id: str, graphs: Dict[str, Any]) -> bool:
        """Create graphs (paths) for a site using V8 graphs endpoint."""
        return self.feature_service.create_site_graphs(site_id, graphs)
    
    def update_site_features(self, site_id: str, features: Dict[str, Any]) -> bool:
        """Update features for a site."""
        try:
            self.feature_service.create_or_update_site_features(site_id, features)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update site features: {str(e)}")
            return False

    def create_or_update_building_features(self, site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update features for a building."""
        return self.feature_service.create_or_update_building_features(site_id, building_id, features)

    def create_or_update_level_features(self, building_id: str, level_index: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update features for a level."""
        return self.feature_service.create_or_update_level_features(building_id, level_index, features)

    def create_or_update_site_features(self, site_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update features for a site."""
        return self.feature_service.create_or_update_site_features(site_id, features)

    def delete_building_features(self, site_id: str, building_id: str) -> bool:
        """Delete all features for a building."""
        return self.feature_service.delete_building_features(site_id, building_id)

    def delete_building_features_by_type(self, building_id: str, type_code: str) -> bool:
        """Delete features of a specific type for a building."""
        return self.feature_service.delete_building_features_by_type(building_id, type_code)

    def delete_level_features(self, building_id: str, level_index: str) -> bool:
        """Delete all features for a level."""
        return self.feature_service.delete_level_features(building_id, level_index)

    def delete_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> bool:
        """Delete features of a specific type for a level."""
        return self.feature_service.delete_level_features_by_type(building_id, level_index, type_code)

    def delete_site_features(self, site_id: str) -> bool:
        """Delete all features for a site."""
        return self.feature_service.delete_site_features(site_id)

    def delete_site_features_by_type(self, site_id: str, type_code: str) -> bool:
        """Delete features of a specific type for a site."""
        return self.feature_service.delete_site_features_by_type(site_id, type_code)

    def get_feature_by_id(self, feature_id: str) -> Dict[str, Any]:
        """Get a specific feature by its ID."""
        return self.feature_service.get_feature_by_id(feature_id)

    def create_or_update_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a single feature."""
        return self.feature_service.create_or_update_feature(feature)

    def delete_feature(self, feature_id: str) -> bool:
        """Delete a specific feature."""
        return self.feature_service.delete_feature(feature_id)

    def get_all_building_features_by_level(self, site_id: str, building_id: str) -> Dict[str, Any]:
        """Get all features for a building organized by level."""
        return self.feature_service.get_all_building_features_by_level(site_id, building_id)

    def migrate_building_features(self, source_site_id: str, source_building_id: str, target_site_id: str, target_building_id: str,
                                feature_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Migrate all features from a source building to a target building."""
        return self.feature_service.migrate_building_features(source_site_id, source_building_id, target_site_id, target_building_id, feature_types)

    # POI methods
    def get_level_pois(self, building_fid: str, level_index: str) -> Dict[str, Any]:
        return self.poi_service.get_level_pois(building_fid, level_index)

    def delete_level_pois(self, building_fid: str, level_index: str) -> bool:
        return self.poi_service.delete_level_pois(building_fid, level_index)

    def get_site_pois(self, site_fid: str) -> Dict[str, Any]:
        return self.poi_service.get_site_pois(site_fid)

    def delete_site_pois(self, site_fid: str) -> bool:
        return self.poi_service.delete_site_pois(site_fid)

    def get_site_pois_draft(self, site_fid: str) -> Dict[str, Any]:
        return self.poi_service.get_site_pois_draft(site_fid)

    def get_level_pois_draft(self, building_fid: str, level_index: str) -> Dict[str, Any]:
        return self.poi_service.get_level_pois_draft(building_fid, level_index)

    def delete_building_pois(self, building_fid: str) -> bool:
        return self.poi_service.delete_building_pois(building_fid)
