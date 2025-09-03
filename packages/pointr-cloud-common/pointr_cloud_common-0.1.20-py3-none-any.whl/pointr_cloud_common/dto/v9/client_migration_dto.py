from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v9.base_migration_dto import BaseMigrationRequestDTO
from pointr_cloud_common.dto.v9.validation import ValidationError

class ClientMigrationRequestDTO(BaseMigrationRequestDTO):
    """DTO for client migration requests."""
    
    def __init__(self, client_id=None, source=None, target=None, options=None, **kwargs):
        super().__init__(source, target)
        self.client_id = client_id
        
        # Extract options
        options = options or {}
        self.migrate_name = kwargs.get("migrate_name", options.get("migrate_name", True))
        self.migrate_external_id = kwargs.get("migrate_external_id", options.get("migrate_external_id", True))
        self.keep_existing_extra_data = kwargs.get("keep_existing_extra_data", options.get("keep_existing_extra_data", True))
        self.keep_existing_sdk_configs = kwargs.get("keep_existing_sdk_configs", options.get("keep_existing_sdk_configs", True))
        self.migrate_gps_geofences = kwargs.get("migrate_gps_geofences", options.get("migrate_gps_geofences", False))
        self.selected_extra_data_keys = kwargs.get("selected_extra_data_keys", options.get("selected_extra_data_keys"))
        self.selected_sdk_keys = kwargs.get("selected_sdk_keys", options.get("selected_sdk_keys"))
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert ClientMigrationRequestDTO to API JSON."""
        base_json = super().to_api_json()
        base_json.update({
            "client_id": self.client_id,
            "options": {
                "migrate_name": self.migrate_name,
                "migrate_external_id": self.migrate_external_id,
                "keep_existing_extra_data": self.keep_existing_extra_data,
                "keep_existing_sdk_configs": self.keep_existing_sdk_configs,
                "migrate_gps_geofences": self.migrate_gps_geofences,
                "selected_extra_data_keys": self.selected_extra_data_keys,
                "selected_sdk_keys": self.selected_sdk_keys
            }
        })
        return base_json
    
    def validate(self) -> bool:
        """Validate the DTO."""
        # We don't require client_id anymore since we use client_identifier from source and target
        # Instead, we validate that source and target have client_identifier
        if not self.source or not isinstance(self.source, dict):
            raise ValidationError("Source configuration is required")
            
        if not self.target or not isinstance(self.target, dict):
            raise ValidationError("Target configuration is required")
            
        if not self.source.get("client_identifier"):
            raise ValidationError("Source client_identifier is required")
            
        if not self.target.get("client_identifier"):
            raise ValidationError("Target client_identifier is required")
        
        return True

    @classmethod
    def from_api_json(cls, data: Dict[str, Any]) -> "ClientMigrationRequestDTO":
        """Convert API JSON to ClientMigrationRequestDTO."""
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a dictionary")
        
        # client_id is now optional, as we'll use client_identifier from source and target
        client_id = data.get("client_id")
        
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
        
        return cls(
            client_id=client_id,
            source=data["source"],
            target=data["target"],
            options=options,
            migrate_name=options.get("migrate_name", True),
            migrate_external_id=options.get("migrate_external_id", True),
            keep_existing_extra_data=options.get("keep_existing_extra_data", True),
            keep_existing_sdk_configs=options.get("keep_existing_sdk_configs", True),
            migrate_gps_geofences=options.get("migrate_gps_geofences", False),
            selected_extra_data_keys=options.get("selected_extra_data_keys"),
            selected_sdk_keys=options.get("selected_sdk_keys")
        )
