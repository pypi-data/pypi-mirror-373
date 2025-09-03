from typing import List
import json
import logging
from pointr_cloud_common.dto.v9.sdk_configuration_dto import SdkConfigurationDTO
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError

class SdkApiService(BaseApiService):
    """Service for SDK configuration-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_client_sdk_config(self) -> List[SdkConfigurationDTO]:
        """
        Get SDK configurations for the client.
        
        Returns:
            A list of SdkConfigurationDTO objects
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sdk-configurations"
        try:
            data = self._make_request("GET", endpoint)
            self.logger.info(f"Retrieved client SDK config: {json.dumps(data)[:200]}...")
            return SdkConfigurationDTO.list_from_client_api_json(data)
        except V9ApiError as e:
            self.logger.warning(f"Failed to get client SDK config: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting client SDK config: {str(e)}")
            return []

    def get_site_sdk_config(self, site_fid: str) -> List[SdkConfigurationDTO]:
        """
        Get SDK configurations for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            A list of SdkConfigurationDTO objects
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/sdk-configurations"
        try:
            data = self._make_request("GET", endpoint)
            self.logger.info(f"Retrieved site SDK config for site {site_fid}: {json.dumps(data)[:200]}...")
            return SdkConfigurationDTO.list_from_site_api_json(data, site_fid)
        except V9ApiError as e:
            self.logger.warning(f"Failed to get site SDK config for site {site_fid}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting site SDK config for site {site_fid}: {str(e)}")
            return []

    def get_building_sdk_config(self, site_fid: str, building_fid: str) -> List[SdkConfigurationDTO]:
        """
        Get SDK configurations for a building.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            
        Returns:
            A list of SdkConfigurationDTO objects
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/sdk-configurations"
        try:
            data = self._make_request("GET", endpoint)
            self.logger.info(f"Retrieved building SDK config for building {building_fid}: {json.dumps(data)[:200]}...")
            return SdkConfigurationDTO.list_from_building_api_json(data, building_fid)
        except V9ApiError as e:
            self.logger.warning(f"Failed to get building SDK config for building {building_fid}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting building SDK config: {str(e)}")
            return []

    def put_global_sdk_configurations(self, configs: List[SdkConfigurationDTO]) -> bool:
        """
        Update global SDK configurations.
        
        Args:
            configs: The SDK configurations to update
            
        Returns:
            True if the update was successful
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sdk-configurations"
        return self._put_sdk(endpoint, configs)

    def put_site_sdk_configurations(self, site_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        """
        Update site SDK configurations.
        
        Args:
            site_fid: The site FID
            configs: The SDK configurations to update
            
        Returns:
            True if the update was successful
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/sdk-configurations"
        return self._put_sdk(endpoint, configs)

    def put_building_sdk_configurations(self, site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]) -> bool:
        """
        Update building SDK configurations.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            configs: The SDK configurations to update
            
        Returns:
            True if the update was successful
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/sdk-configurations"
        return self._put_sdk(endpoint, configs)

    def _put_sdk(self, endpoint: str, configs: List[SdkConfigurationDTO]) -> bool:
        """
        Update SDK configurations.
        
        Args:
            endpoint: The API endpoint to call
            configs: The SDK configurations to update
            
        Returns:
            True if the update was successful
        """
        # Convert DTOs to API format
        payload = [c.to_api_json() for c in configs]
        
        # Log the payload for debugging
        if configs:
            sample_payload = payload[:min(3, len(payload))]
            self.logger.info(f"SDK configuration payload sample: {json.dumps(sample_payload)}")
        
        self._make_request("PUT", endpoint, payload)
        return True
