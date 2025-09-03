from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError


class FeatureApiService(BaseApiService):
    """Service for handling feature operations in V9 API."""

    def __init__(self, api_service):
        """Initialize the feature service."""
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_site_features(self, site_fid: str) -> Dict[str, Any]:
        """
        Get all features for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            Dictionary containing all features for the site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site features for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def get_site_features_by_type(self, site_fid: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a site.
        
        Args:
            site_fid: The site FID
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features/type-code/{type_code}"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site features by type {type_code} for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def get_site_paths(self, site_fid: str) -> Dict[str, Any]:
        """
        Get all paths for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            Dictionary containing all paths for the site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/paths"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site paths for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def create_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        """
        Create features for a site.
        
        Args:
            site_fid: The site FID
            features: The features to create
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            response = self._make_request("PUT", endpoint, features)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create site features for {site_fid}: {str(e)}")
            return False

    def update_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        """
        Update features for a site.
        
        Args:
            site_fid: The site FID
            features: The features to update
            
        Returns:
            True if successful, False otherwise
        """
        return self.create_site_features(site_fid, features)

    def delete_site_features(self, site_fid: str) -> bool:
        """
        Delete all features for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            self._make_request("DELETE", endpoint)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete site features for {site_fid}: {str(e)}")
            return False
