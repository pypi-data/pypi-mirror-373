from typing import Dict, Any, List, Optional, Union

class BaseMigrationRequestDTO:
    """Base DTO for all migration requests."""
    
    def __init__(self, source=None, target=None):
        self.source = source or {}
        self.target = target or {}
        self.migrate_name = True
        self.migrate_external_id = True
        self.keep_existing_extra_data = True
        self.keep_existing_sdk_configs = True
        self.selected_extra_data_keys = []
        self.selected_sdk_keys = []
        self.target_id = None
        self.target_name = None
    
    @staticmethod
    def validate_environments(source: Dict[str, str], target: Dict[str, str]) -> None:
        """Validate source and target environment configurations."""
        if "api_url" not in source:
            raise ValueError("Source must contain 'api_url'")

        if "version" not in source:
            raise ValueError("Source must contain 'version'")
        
        if "client_identifier" not in source:
            raise ValueError("Source must contain 'client_identifier'")
        
        if "api_url" not in target:
            raise ValueError("Target must contain 'api_url'")

        if "version" not in target:
            raise ValueError("Target must contain 'version'")
        
        if "client_identifier" not in target:
            raise ValueError("Target must contain 'client_identifier'")
    
    def to_api_json(self) -> Dict[str, Any]:
        """Convert BaseMigrationRequestDTO to API JSON."""
        return {
            "source": self.source,
            "target": self.target
        }
