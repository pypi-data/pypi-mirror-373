from dataclasses import dataclass, field
from typing import Dict, Any, List

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type, ensure_dict
from pointr_cloud_common.dto.v9.sdk_configuration_dto import SdkConfigurationDTO
from pointr_cloud_common.dto.v9.gps_geofence_dto import GpsGeofenceDTO

@dataclass
class ClientDTO(BaseDTO):
    identifier: str
    name: str
    extraData: Dict[str, Any] = field(default_factory=dict)
    sdkConfigurations: List[SdkConfigurationDTO] = field(default_factory=list)
    gpsGeofences: List[GpsGeofenceDTO] = field(default_factory=list)

    @staticmethod
    def from_api_json(metadata: Dict[str, Any], sdk_configs: List[Dict[str, Any]], gps_geofences: List[Dict[str, Any]]) -> "ClientDTO":
        if not isinstance(metadata, dict):
            raise ValidationError("Expected dictionary for metadata")
        
        validate_required_field(metadata, "identifier")
        validate_required_field(metadata, "name")
        validate_type(metadata["identifier"], str, "identifier")
        validate_type(metadata["name"], str, "name")
        
        extra_data = ensure_dict(metadata.get("extra"), "extra")
        
        if not isinstance(sdk_configs, list):
            raise ValidationError("Expected list for sdk_configs")
        
        if not isinstance(gps_geofences, list):
            raise ValidationError("Expected list for gps_geofences")
        
        sdk_config_dtos = [SdkConfigurationDTO.from_api_json(c) for c in sdk_configs]
        gps_geofence_dtos = [GpsGeofenceDTO.from_api_json(g) for g in gps_geofences]
        
        return ClientDTO(
            identifier=metadata["identifier"],
            name=metadata["name"],
            extraData=extra_data,
            sdkConfigurations=sdk_config_dtos,
            gpsGeofences=gps_geofence_dtos
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "extra": self.extraData
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.identifier:
            raise ValidationError("identifier cannot be empty", "identifier", self.identifier)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        
        # Validate nested objects
        for i, config in enumerate(self.sdkConfigurations):
            try:
                config.validate()
            except ValidationError as e:
                raise ValidationError(f"Invalid SDK configuration at index {i}: {str(e)}")
        
        for i, geofence in enumerate(self.gpsGeofences):
            try:
                geofence.validate()
            except ValidationError as e:
                raise ValidationError(f"Invalid GPS geofence at index {i}: {str(e)}")
        
        return True
