from typing import List
import logging

from pointr_cloud_common.dto.v9 import SdkConfigurationDTO
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


class SdkApiService(BaseApiService):
    """Service for SDK configuration-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_client_sdk_config(self) -> List[SdkConfigurationDTO]:
        """Retrieve draft SDK configurations for the client."""
        endpoint = (
            f"api/v8/clients/{self.client_id}/configurations/sdk-configurations/typed"
        )
        try:
            data = self._make_request("GET", endpoint)
            configs = data.get("results", []) if isinstance(data, dict) else []
            return [SdkConfigurationDTO.from_api_json(c) for c in configs]
        except Exception as e:
            raise V8ApiError(f"Failed to get SDK config: {str(e)}")

    def get_site_sdk_config(self, site_fid: str) -> List[SdkConfigurationDTO]:
        endpoint = (
            f"api/v8/sites/{site_fid}/configurations/sdk-configurations/typed"
        )
        try:
            data = self._make_request("GET", endpoint)
            configs = data.get("results", []) if isinstance(data, dict) else []
            return [SdkConfigurationDTO.from_api_json(c) for c in configs]
        except Exception as e:
            raise V8ApiError(f"Failed to get SDK config: {str(e)}")

    def get_building_sdk_config(self, site_fid: str, building_fid: str) -> List[SdkConfigurationDTO]:
        endpoint = (
            f"api/v8/buildings/{building_fid}/configurations/sdk-configurations/typed"
        )
        try:
            data = self._make_request("GET", endpoint)
            configs = data.get("results", []) if isinstance(data, dict) else []
            return [SdkConfigurationDTO.from_api_json(c) for c in configs]
        except Exception as e:
            raise V8ApiError(f"Failed to get SDK config: {str(e)}")

    def put_global_sdk_configurations(self, configs: List[SdkConfigurationDTO]) -> bool:
        endpoint = f"api/v8/clients/{self.client_id}/configurations/sdk-configurations"
        return self._post_sdk(endpoint, configs)

    def put_site_sdk_configurations(self, site_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        endpoint = f"api/v8/sites/{site_fid}/configurations/sdk-configurations"
        return self._post_sdk(endpoint, configs)

    def put_building_sdk_configurations(self, site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        endpoint = f"api/v8/buildings/{building_fid}/configurations/sdk-configurations"
        return self._post_sdk(endpoint, configs)

    def _post_sdk(self, endpoint: str, configs: List[SdkConfigurationDTO]) -> bool:
        payload = [c.to_api_json() for c in configs]
        self._make_request("POST", endpoint, payload)
        return True
