from dataclasses import dataclass
from typing import Dict, Any, List, Union

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import (
    ValidationError, validate_required_field, validate_type, 
    validate_feature_collection, ensure_dict
)

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
