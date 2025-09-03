from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v9.base_migration_dto import BaseMigrationRequestDTO
from pointr_cloud_common.dto.v9.validation import ValidationError

@dataclass
class LevelMigrationRequestDTO(BaseMigrationRequestDTO):
    """DTO for level migration requests."""
    level_id: str  # ID of the level to migrate
    building_id: str  # Building ID is required for level migration
    site_id: str  # Site ID is required for level migration
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert LevelMigrationRequestDTO to API JSON."""
        return {
            "level_id": self.level_id,
            "building_id": self.building_id,
            "site_id": self.site_id,
            "source": self.source,
            "target": self.target,
            "options": self.options
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.level_id:
            raise ValidationError("Level ID cannot be empty")
            
        if not self.building_id:
            raise ValidationError("Building ID cannot be empty")
            
        if not self.site_id:
            raise ValidationError("Site ID cannot be empty")
        
        return True

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "LevelMigrationRequestDTO":
        """Convert API JSON to LevelMigrationRequestDTO."""
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a dictionary")
        
        if "level_id" not in data:
            raise ValidationError("Missing 'level_id' field in request")
            
        if "building_id" not in data:
            raise ValidationError("Missing 'building_id' field in request")
            
        if "site_id" not in data:
            raise ValidationError("Missing 'site_id' field in request")
        
        if "source" not in data:
            raise ValidationError("Missing 'source' field in request")
        
        if "target" not in data:
            raise ValidationError("Missing 'target' field in request")
        
        # Validate environments
        BaseMigrationRequestDTO.validate_environments(data["source"], data["target"])
        
        # Extract options
        options = data.get("options", {})
        if not isinstance(options, dict):
            options = {}
        
        return LevelMigrationRequestDTO(
            level_id=data["level_id"],
            building_id=data["building_id"],
            site_id=data["site_id"],
            source=data["source"],
            target=data["target"],
            options=options
        )
