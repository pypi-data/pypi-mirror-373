from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.api.v8.base_service import BaseApiService


class FeatureApiService(BaseApiService):
    """Service for handling feature operations in V8 API."""

    def __init__(self, api_service):
        """Initialize the feature service."""
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_building_features(self, building_id: str) -> Dict[str, Any]:
        """
        Fetch all features for a building (V8: /api/v8/buildings/{building_id}/features/draft).
        Always returns a FeatureCollection (extracts from response['result']['features']).
        """
        endpoint = f"api/v8/buildings/{building_id}/features/draft"
        response = self._make_request("GET", endpoint)
       
        # Extract features from the result field when present
        if response and "result" in response:
            return response["result"]

        # If the API already returns a FeatureCollection, pass it through
        if response:
            return response
        return {"type": "FeatureCollection", "features": []}

    def get_building_features_by_type(self, building_id: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a building.
        
        Args:
            building_id: The building identifier
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type
        """
        endpoint = f"api/v8/buildings/{building_id}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_level_features(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """
        Get all features for a specific level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            
        Returns:
            Dictionary containing all features for the level
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/draft"
        return self._make_request("GET", endpoint)

    def get_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type for the level
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_site_features(self, site_id: str) -> Dict[str, Any]:
        """
        Get all features for a site.
        
        Args:
            site_id: The site identifier
            
        Returns:
            Dictionary containing all features for the site
        """
        endpoint = f"api/v8/sites/{site_id}/features/draft"
        return self._make_request("GET", endpoint)

    def get_site_features_by_type(self, site_id: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a site.
        
        Args:
            site_id: The site identifier
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type for the site
        """
        endpoint = f"api/v8/sites/{site_id}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_site_paths(self, site_id: str) -> Dict[str, Any]:
        """
        Get all paths for a site (alias for get_site_features_by_type with 'Paths' type).
        
        Args:
            site_id: The site identifier
            
        Returns:
            Dictionary containing all paths for the site
        """
        return self.get_site_features_by_type(site_id, "Paths")
    
    def get_site_graphs(self, site_id: str) -> Dict[str, Any]:
        """
        Get all graphs (paths) for a site using the V8 graphs endpoint.
        
        Args:
            site_id: The site identifier
            
        Returns:
            Dictionary containing all graphs for the site
        """
        endpoint = f"api/v8/sites/{site_id}/graphs/draft"
        response = self._make_request("GET", endpoint)
        
        # V8 API returns data in the 'result' field
        if response and "result" in response and response["result"]:
            return response["result"]
        
        return {"type": "FeatureCollection", "features": []}
    
    def create_site_graphs(self, site_id: str, graphs: Dict[str, Any]) -> bool:
        """
        Create graphs (paths) for a site using the V8 graphs endpoint.
        
        Args:
            site_id: The site identifier
            graphs: The graphs to create
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"api/v8/sites/{site_id}/graphs"
        try:
            self._make_request("POST", endpoint, graphs)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create site graphs for {site_id}: {str(e)}")
            return False

    def upsert_building_features(self, site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upsert (create or update) all features for a building (V8: /api/v8/sites/{site_id}/buildings/{building_id}/features).
        """
        endpoint = f"api/v8/sites/{site_id}/buildings/{building_id}/features"
        return self._make_request("PUT", endpoint, features)

    # Backwards compatibility
    def create_or_update_building_features(self, site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for ``upsert_building_features`` for legacy callers."""
        return self.upsert_building_features(site_id, building_id, features)

    def create_or_update_level_features(self, building_id: str, level_index: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update features for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            features: The features to create or update
            
        Returns:
            Response from the API
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features"
        return self._make_request("PUT", endpoint, features)

    def create_or_update_site_features(self, site_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update features for a site.
        
        Args:
            site_id: The site identifier
            features: The features to create or update
            
        Returns:
            Response from the API
        """
        endpoint = f"api/v8/sites/{site_id}/features"
        return self._make_request("PUT", endpoint, features)

    def delete_building_features(self, site_id: str, building_id: str) -> bool:
        """
        Delete all features for a building.
        
        Args:
            site_id: The site identifier
            building_id: The building identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_building_features_by_type(self, building_id: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a building.
        
        Args:
            building_id: The building identifier
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def delete_level_features(self, building_id: str, level_index: str) -> bool:
        """
        Delete all features for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def delete_site_features(self, site_id: str) -> bool:
        """
        Delete all features for a site.
        
        Args:
            site_id: The site identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/sites/{site_id}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_site_features_by_type(self, site_id: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a site.
        
        Args:
            site_id: The site identifier
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/sites/{site_id}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def get_feature_by_id(self, feature_id: str) -> Dict[str, Any]:
        """
        Get a specific feature by its ID.
        
        Args:
            feature_id: The feature identifier
            
        Returns:
            Dictionary containing the feature data
        """
        endpoint = f"api/v8/features/{feature_id}"
        return self._make_request("GET", endpoint)

    def create_or_update_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a single feature.
        
        Args:
            feature: The feature data
            
        Returns:
            Response from the API
        """
        endpoint = "api/v8/features"
        return self._make_request("PUT", endpoint, {"features": [feature]})

    def delete_feature(self, feature_id: str) -> bool:
        """
        Delete a specific feature.
        
        Args:
            feature_id: The feature identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/features/{feature_id}"
        self._make_request("DELETE", endpoint)
        return True

    def get_all_building_features_by_level(self, building_id: str, site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all features for a building organized by level.
        This is useful for migration scenarios where we need to collect all features
        from all levels of a building.
        
        Args:
            building_id: The building identifier
            site_id: Optional site identifier. If not provided, ``self.api_service.site_id`` is used.
            
        Returns:
            Dictionary containing all features organized by level
        """
        try:
            if site_id is None:
                site_id = self.api_service.site_id

            # First get all levels for the building
            levels = self.api_service.get_levels(site_id, building_id)
            
            all_features = {
                "type": "FeatureCollection",
                "features": []
            }
            
            # Collect features from each level
            for level in levels:
                level_id = getattr(level, "fid", level)
                try:
                    level_features = self.get_level_features(building_id, level_id)
                    if level_features and "features" in level_features and level_features["features"]:
                        all_features["features"].extend(level_features["features"])
                except Exception as e:
                    self.logger.warning(f"Failed to get features for level {level_id}: {str(e)}")
                    continue
            
            return all_features
            
        except Exception as e:
            self.logger.error(f"Failed to get all building features by level: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def migrate_building_features(self, source_building_id: str, target_site_id: str, target_building_id: str, 
                                feature_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Migrate all features from a source building to a target building.
        
        Args:
            source_building_id: The source building identifier
            target_site_id: The target site identifier
            target_building_id: The target building identifier
            feature_types: Optional list of feature types to migrate (if None, migrates all)
            
        Returns:
            Dictionary containing migration results
        """
        try:
            # Get all features from source building
            source_features = self.get_all_building_features_by_level(source_building_id, self.api_service.site_id)
            
            if not source_features or "features" not in source_features or not source_features["features"]:
                return {
                    "success": True,
                    "message": "No features found in source building",
                    "migrated_count": 0
                }
            
            # Filter by feature types if specified
            if feature_types:
                filtered_features = []
                for feature in source_features["features"]:
                    if "properties" in feature and "typeCode" in feature["properties"]:
                        if feature["properties"]["typeCode"] in feature_types:
                            filtered_features.append(feature)
                source_features["features"] = filtered_features
            
            # Update building and site IDs in all features
            for feature in source_features["features"]:
                if "properties" in feature:
                    feature["properties"]["bid"] = target_building_id
                    feature["properties"]["sid"] = target_site_id
            
            # Create or update features in target building
            result = self.create_or_update_building_features(target_site_id, target_building_id, source_features)
            
            return {
                "success": True,
                "message": f"Successfully migrated {len(source_features['features'])} features",
                "migrated_count": len(source_features["features"]),
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to migrate building features: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to migrate features: {str(e)}",
                "migrated_count": 0,
                "error": str(e)
            } 