from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Literal, Set

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError

@dataclass
class EntityDTO:
    """DTO for entity information in migration requests."""
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    
    @staticmethod
    def from_api_json(data: Union[str, Dict[str, Any]]) -> "EntityDTO":
        """
        Convert API JSON to EntityDTO.
        
        Args:
            data: Either a string representing the entity type or a dictionary with type, id, and name
            
        Returns:
            An EntityDTO instance
            
        Raises:
            ValidationError: If the data is invalid
        """
        if isinstance(data, str):
            return EntityDTO(type=data)
        
        if not isinstance(data, dict):
            raise ValidationError("Entity must be a string or dictionary")
        
        if "type" not in data:
            raise ValidationError("Entity dictionary must contain 'type' field")
        
        return EntityDTO(
            type=data["type"],
            id=data.get("id"),
            name=data.get("name")
        )
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert EntityDTO to API JSON."""
        result = {"type": self.type}
        if self.id:
            result["id"] = self.id
        if self.name:
            result["name"] = self.name
        return result
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.type:
            raise ValidationError("Entity type cannot be empty")
        return True

@dataclass
class MigrationOptionsDTO:
    """DTO for enhanced migration options."""
    # Common options
    migrate_name: bool = True
    migrate_external_id: bool = True
    keep_existing_extra_data: bool = True  # If False, delete extraData not in source
    keep_existing_sdk_configs: bool = True  # If False, delete configs not in source
    
    # ExtraData options
    selected_extra_data_keys: Optional[List[str]] = None  # If provided, only migrate these keys
    
    # SDK configuration options
    selected_sdk_keys: Optional[List[str]] = None  # If provided, only migrate these keys
    
    # Site-specific options
    migrate_outdoor_graphs: bool = False
    
    # Building-specific options
    migrate_graphs: bool = False
    migrate_beacons: bool = False
    migrate_beacon_geofences: bool = False
    
    # Client-specific options
    migrate_gps_geofences: bool = False
    
    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "MigrationOptionsDTO":
        """Convert API JSON to MigrationOptionsDTO."""
        if not isinstance(data, dict):
            return MigrationOptionsDTO()
        
        # Extract common options
        migrate_name = data.get("migrate_name", True)
        migrate_external_id = data.get("migrate_external_id", True)
        keep_existing_extra_data = data.get("keep_existing_extra_data", True)
        keep_existing_sdk_configs = data.get("keep_existing_sdk_configs", True)
        
        # Extract ExtraData options
        selected_extra_data_keys = data.get("selected_extra_data_keys")
        
        # Extract SDK configuration options
        selected_sdk_keys = data.get("selected_sdk_keys")
        
        # Extract Site-specific options
        migrate_outdoor_graphs = data.get("migrate_outdoor_graphs", False)
        
        # Extract Building-specific options
        migrate_graphs = data.get("migrate_graphs", False)
        migrate_beacons = data.get("migrate_beacons", False)
        migrate_beacon_geofences = data.get("migrate_beacon_geofences", False)
        
        # Extract Client-specific options
        migrate_gps_geofences = data.get("migrate_gps_geofences", False)
        
        return MigrationOptionsDTO(
            migrate_name=migrate_name,
            migrate_external_id=migrate_external_id,
            keep_existing_extra_data=keep_existing_extra_data,
            keep_existing_sdk_configs=keep_existing_sdk_configs,
            selected_extra_data_keys=selected_extra_data_keys,
            selected_sdk_keys=selected_sdk_keys,
            migrate_outdoor_graphs=migrate_outdoor_graphs,
            migrate_graphs=migrate_graphs,
            migrate_beacons=migrate_beacons,
            migrate_beacon_geofences=migrate_beacon_geofences,
            migrate_gps_geofences=migrate_gps_geofences
        )
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert MigrationOptionsDTO to API JSON."""
        result = {
            "migrate_name": self.migrate_name,
            "migrate_external_id": self.migrate_external_id,
            "keep_existing_extra_data": self.keep_existing_extra_data,
            "keep_existing_sdk_configs": self.keep_existing_sdk_configs,
            "migrate_outdoor_graphs": self.migrate_outdoor_graphs,
            "migrate_graphs": self.migrate_graphs,
            "migrate_beacons": self.migrate_beacons,
            "migrate_beacon_geofences": self.migrate_beacon_geofences,
            "migrate_gps_geofences": self.migrate_gps_geofences
        }
        
        if self.selected_sdk_keys is not None:
            result["selected_sdk_keys"] = self.selected_sdk_keys
            
        if self.selected_extra_data_keys is not None:
            result["selected_extra_data_keys"] = self.selected_extra_data_keys
            
        return result

@dataclass
class MigrationRequestDTO(BaseDTO):
    """DTO for migration requests."""
    entity: EntityDTO
    source: Dict[str, str]
    target: Dict[str, str]
    options: MigrationOptionsDTO = field(default_factory=MigrationOptionsDTO)
    raw_options: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "MigrationRequestDTO":
        """
        Convert API JSON to MigrationRequestDTO.
        
        Args:
            data: The request data
            
        Returns:
            A MigrationRequestDTO instance
            
        Raises:
            ValidationError: If the data is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a dictionary")
        
        if "entity" not in data:
            raise ValidationError("Missing 'entity' field in request")
        
        if "source" not in data:
            raise ValidationError("Missing 'source' field in request")
        
        if "target" not in data:
            raise ValidationError("Missing 'target' field in request")
        
        entity = EntityDTO.from_api_json(data["entity"])
        
        if not isinstance(data["source"], dict):
            raise ValidationError("Source must be a dictionary")
        
        if not isinstance(data["target"], dict):
            raise ValidationError("Target must be a dictionary")
        
        raw_options = data.get("options", {})
        if not isinstance(raw_options, dict):
            raw_options = {}
        
        options = MigrationOptionsDTO.from_api_json(raw_options)
        
        return MigrationRequestDTO(
            entity=entity,
            source=data["source"],
            target=data["target"],
            options=options,
            raw_options=raw_options
        )
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert MigrationRequestDTO to API JSON."""
        return {
            "entity": self.entity.to_api_json(),
            "source": self.source,
            "target": self.target,
            "options": self.options.to_api_json()
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        self.entity.validate()
        
        if "api_url" not in self.source:
            raise ValidationError("Source must contain 'api_url'")

        if "version" not in self.source:
            raise ValidationError("Source must contain 'version'")
        
        if "client_identifier" not in self.source:
            raise ValidationError("Source must contain 'client_identifier'")
        
        if "api_url" not in self.target:
            raise ValidationError("Target must contain 'api_url'")

        if "version" not in self.target:
            raise ValidationError("Target must contain 'version'")
        
        if "client_identifier" not in self.target:
            raise ValidationError("Target must contain 'client_identifier'")
        
        return True
