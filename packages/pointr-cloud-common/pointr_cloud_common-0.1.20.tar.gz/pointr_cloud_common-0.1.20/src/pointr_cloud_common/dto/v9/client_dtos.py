from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import (
    ValidationError, validate_required_field, validate_type, 
    validate_feature_collection, ensure_dict
)
from pointr_cloud_common.dto.v9.sdk_dtos import SdkConfigurationDTO

@dataclass
class ClientMetadataDTO(BaseDTO):
    identifier: str
    name: str
    extra: Dict[str, Any]

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "ClientMetadataDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for ClientMetadataDTO")
        
        validate_required_field(data, "identifier")
        validate_required_field(data, "name")
        validate_type(data["identifier"], str, "identifier")
        validate_type(data["name"], str, "name")
        
        extra = ensure_dict(data.get("extra"), "extra")
        
        return ClientMetadataDTO(
            identifier=data["identifier"],
            name=data["name"],
            extra=extra
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "extra": self.extra
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.identifier:
            raise ValidationError("identifier cannot be empty", "identifier", self.identifier)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        return True

    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["ClientMetadataDTO"]:
        return [ClientMetadataDTO.from_api_json(item) for item in data_list]

@dataclass
class GpsGeofenceDTO(BaseDTO):
    fid: str
    name: str
    typeCode: str
    extra: Dict[str, Any]
    geometry: Dict[str, Any]

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "GpsGeofenceDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for GpsGeofenceDTO")
        
        if "properties" not in data:
            raise ValidationError("Missing properties field", "properties", None)
        
        properties = data["properties"]
        if not isinstance(properties, dict):
            raise ValidationError("Expected dictionary for properties", "properties", properties)
        
        validate_required_field(properties, "fid")
        validate_required_field(properties, "name")
        validate_required_field(properties, "typeCode")
        validate_type(properties["fid"], str, "fid")
        validate_type(properties["name"], str, "name")
        validate_type(properties["typeCode"], str, "typeCode")
        
        extra = ensure_dict(properties.get("extra"), "extra")
        
        geometry = data.get("geometry", {})
        if not isinstance(geometry, dict):
            raise ValidationError("Expected dictionary for geometry", "geometry", geometry)
        
        return GpsGeofenceDTO(
            fid=properties["fid"],
            name=properties["name"],
            typeCode=properties["typeCode"],
            extra=extra,
            geometry=geometry
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "properties": {
                "fid": self.fid,
                "name": self.name,
                "typeCode": self.typeCode,
                "extra": self.extra
            },
            "geometry": self.geometry
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        if not self.typeCode:
            raise ValidationError("typeCode cannot be empty", "typeCode", self.typeCode)
        if not isinstance(self.geometry, dict):
            raise ValidationError("geometry must be a dictionary", "geometry", self.geometry)
        return True

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["GpsGeofenceDTO"]:
        if isinstance(data, list):
            return [GpsGeofenceDTO.from_api_json(item) for item in data]
        
        try:
            feature_collection = validate_feature_collection(data)
            return [GpsGeofenceDTO.from_api_json(feature) for feature in feature_collection["features"]]
        except ValidationError as e:
            raise ValidationError(f"Invalid feature collection: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error processing feature collection: {str(e)}")

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
