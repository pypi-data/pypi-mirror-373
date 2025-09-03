from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v9.base_migration_dto import BaseMigrationRequestDTO
from pointr_cloud_common.dto.v9.validation import ValidationError

class SiteMigrationRequestDTO(BaseMigrationRequestDTO):
    """DTO for site migration requests."""
    
    def __init__(self, site_id=None, source=None, target=None, options=None, **kwargs):
        super().__init__(source, target)
        self.site_id = site_id
        
        # Extract options
        options = options or {}
        self.migrate_name = kwargs.get("migrate_name", options.get("migrate_name", True))
        self.migrate_external_id = kwargs.get("migrate_external_id", options.get("migrate_external_id", True))
        self.keep_existing_extra_data = kwargs.get("keep_existing_extra_data", options.get("keep_existing_extra_data", True))
        self.keep_existing_sdk_configs = kwargs.get("keep_existing_sdk_configs", options.get("keep_existing_sdk_configs", True))
        self.migrate_outdoor_graphs = kwargs.get("migrate_outdoor_graphs", options.get("migrate_outdoor_graphs", False))
        self.migrate_sdk_configurations = kwargs.get("migrate_sdk_configurations", options.get("migrate_sdk_configurations", True))
        self.selected_extra_data_keys = kwargs.get("selected_extra_data_keys", options.get("selected_extra_data_keys"))
        self.selected_sdk_keys = kwargs.get("selected_sdk_keys", options.get("selected_sdk_keys"))
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert SiteMigrationRequestDTO to API JSON."""
        base_json = super().to_api_json()
        base_json.update({
            "site_id": self.site_id,
            "options": {
                "migrate_name": self.migrate_name,
                "migrate_external_id": self.migrate_external_id,
                "keep_existing_extra_data": self.keep_existing_extra_data,
                "keep_existing_sdk_configs": self.keep_existing_sdk_configs,
                "migrate_outdoor_graphs": self.migrate_outdoor_graphs,
                "migrate_sdk_configurations": self.migrate_sdk_configurations,
                "selected_extra_data_keys": self.selected_extra_data_keys,
                "selected_sdk_keys": self.selected_sdk_keys
            }
        })
        return base_json
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.site_id:
            raise ValidationError("Site ID cannot be empty")
        
        return True

    @classmethod
    def from_api_json(cls, data: Dict[str, Any]) -> "SiteMigrationRequestDTO":
        """Convert API JSON to SiteMigrationRequestDTO."""
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a dictionary")
        
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
        
        return cls(
            site_id=data["site_id"],
            source=data["source"],
            target=data["target"],
            options=options,
            migrate_name=options.get("migrate_name", True),
            migrate_external_id=options.get("migrate_external_id", True),
            keep_existing_extra_data=options.get("keep_existing_extra_data", True),
            keep_existing_sdk_configs=options.get("keep_existing_sdk_configs", True),
            migrate_outdoor_graphs=options.get("migrate_outdoor_graphs", False),
            migrate_sdk_configurations=options.get("migrate_sdk_configurations", True),
            selected_extra_data_keys=options.get("selected_extra_data_keys"),
            selected_sdk_keys=options.get("selected_sdk_keys")
        )
