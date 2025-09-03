from typing import Dict, Any, List, Optional
from pointr_cloud_common.dto.v9.base_migration_dto import BaseMigrationRequestDTO
from pointr_cloud_common.dto.v9.validation import ValidationError

class BuildingMigrationRequestDTO(BaseMigrationRequestDTO):
    """
    Data Transfer Object for building migration requests.
    """
    
    def __init__(self):
        super().__init__()
        self.building_id = None
        self.site_id = None
        self.migrate_graphs = False
        self.migrate_beacons = False
        self.migrate_beacon_geofences = False
        self.migrate_sdk_configurations = True
        self.display_name = None  # Add display_name field
        
    @classmethod
    def from_api_json(cls, data: Dict[str, Any]) -> 'BuildingMigrationRequestDTO':
        """
        Create a DTO from API JSON data.
        
        Args:
            data: Dictionary containing API data
            
        Returns:
            Populated DTO
        """
        # Create a new instance instead of calling super().from_api_json
        dto = cls()
        
        # Extract base fields from BaseMigrationRequestDTO
        dto.source = data.get("source", {})
        dto.target = data.get("target", {})
        
        # Extract options
        options = data.get("options", {})
        if isinstance(options, dict):
            dto.migrate_name = options.get("migrate_name", True)
            dto.migrate_external_id = options.get("migrate_external_id", True)
            dto.keep_existing_extra_data = options.get("keep_existing_extra_data", True)
            dto.keep_existing_sdk_configs = options.get("keep_existing_sdk_configs", True)
            dto.selected_extra_data_keys = options.get("selected_extra_data_keys", [])
            dto.selected_sdk_keys = options.get("selected_sdk_keys", [])
            dto.migrate_sdk_configurations = options.get("migrate_sdk_configurations", True)
        
        # Extract target mapping
        target_mapping = data.get("target_mapping", {})
        if isinstance(target_mapping, dict):
            dto.target_id = target_mapping.get("target_id")
            dto.target_name = target_mapping.get("target_name")
        
        # Extract building-specific fields
        dto.building_id = data.get("building_id")
        dto.site_id = data.get("site_id")
        
        # Extract building-specific options
        if isinstance(options, dict):
            dto.migrate_graphs = options.get("migrate_graphs", False)
            dto.migrate_beacons = options.get("migrate_beacons", False)
            dto.migrate_beacon_geofences = options.get("migrate_beacon_geofences", False)
            
        # Extract display_name
        dto.display_name = data.get("display_name")
        
        return dto
    
    def validate(self) -> None:
        """
        Validate the DTO.
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate base fields
        if not self.source:
            raise ValidationError("Missing source environment configuration")
            
        if not self.target:
            raise ValidationError("Missing target environment configuration")
        
        # Validate building-specific fields
        if not self.building_id:
            raise ValidationError("Missing building_id")
            
        if not self.site_id:
            raise ValidationError("Missing site_id")
    
    def to_api_json(self) -> Dict[str, Any]:
        """
        Convert DTO to API JSON format.
        
        Returns:
            Dictionary in API format
        """
        # Create base result
        result = {
            "source": self.source,
            "target": self.target,
            "building_id": self.building_id,
            "site_id": self.site_id,
            "options": {
                "migrate_name": self.migrate_name,
                "migrate_external_id": self.migrate_external_id,
                "keep_existing_extra_data": self.keep_existing_extra_data,
                "keep_existing_sdk_configs": self.keep_existing_sdk_configs,
                "migrate_graphs": self.migrate_graphs,
                "migrate_beacons": self.migrate_beacons,
                "migrate_beacon_geofences": self.migrate_beacon_geofences,
                "migrate_sdk_configurations": self.migrate_sdk_configurations
            }
        }
        
        # Add target mapping if present
        if self.target_id or self.target_name:
            result["target_mapping"] = {
                "target_id": self.target_id,
                "target_name": self.target_name
            }
        
        # Add selected keys if present
        if self.selected_extra_data_keys:
            result["options"]["selected_extra_data_keys"] = self.selected_extra_data_keys
            
        if self.selected_sdk_keys:
            result["options"]["selected_sdk_keys"] = self.selected_sdk_keys
            
        # Add display_name if present
        if self.display_name:
            result["display_name"] = self.display_name
        
        return result
