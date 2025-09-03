from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import (
    ValidationError, validate_required_field, validate_type, 
    validate_feature_collection, ensure_dict
)
from pointr_cloud_common.dto.v9.level_dto import LevelDTO
from pointr_cloud_common.dto.v9.sdk_configuration_dto import SdkConfigurationDTO

@dataclass
class BuildingDTO(BaseDTO):
    fid: str
    name: str
    typeCode: str  # Added typeCode field
    sid: Optional[str] = None  # Added sid field
    bid: Optional[str] = None  # Added bid field
    extraData: Dict[str, Any] = field(default_factory=dict)
    sdkConfigurations: List[SdkConfigurationDTO] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    levels: List[LevelDTO] = field(default_factory=list)

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "BuildingDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for BuildingDTO")
        
        # Handle both direct properties and nested properties
        properties = data.get("properties", data)
        if not isinstance(properties, dict):
            raise ValidationError("Expected dictionary for properties", "properties", properties)
        
        validate_required_field(properties, "fid")
        validate_required_field(properties, "name")
        validate_type(properties["fid"], str, "fid")
        validate_type(properties["name"], str, "name")
        
        # Extract typeCode with default
        typeCode = properties.get("typeCode", "building-outline")
        
        # Extract optional sid and bid
        sid = properties.get("sid")
        bid = properties.get("bid")
        
        # Use the ensure_dict helper to safely handle extraData
        extra_data = ensure_dict(properties.get("extraData", properties.get("extra")), "extraData")
        
        sdk_configs = data.get("sdkConfigurations", [])
        if not isinstance(sdk_configs, list):
            raise ValidationError("Expected list for sdkConfigurations", "sdkConfigurations", sdk_configs)
        
        options = data.get("options", {})
        if not isinstance(options, dict):
            raise ValidationError("Expected dictionary for options", "options", options)
        
        levels_data = data.get("levels", [])
        if not isinstance(levels_data, list):
            raise ValidationError("Expected list for levels", "levels", levels_data)
        
        sdk_config_dtos = [SdkConfigurationDTO.from_api_json(c) for c in sdk_configs]
        level_dtos = [LevelDTO.from_api_json(l) for l in levels_data]
        
        return BuildingDTO(
            fid=properties["fid"],
            name=properties["name"],
            typeCode=typeCode,
            sid=sid,
            bid=bid,
            extraData=extra_data,
            sdkConfigurations=sdk_config_dtos,
            options=options,
            levels=level_dtos
        )

    def to_api_json(self) -> Dict[str, Any]:
        result = {
            "fid": self.fid,
            "name": self.name,
            "typeCode": self.typeCode,
            "extraData": self.extraData,
            "sdkConfigurations": [c.to_api_json() for c in self.sdkConfigurations],
            "options": self.options,
            "levels": [l.to_api_json() for l in self.levels]
        }
        
        if self.sid:
            result["sid"] = self.sid
        if self.bid:
            result["bid"] = self.bid
            
        return result
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        
        # Validate nested objects
        for i, config in enumerate(self.sdkConfigurations):
            try:
                config.validate()
            except ValidationError as e:
                raise ValidationError(f"Invalid SDK configuration at index {i}: {str(e)}")
        
        for i, level in enumerate(self.levels):
            try:
                level.validate()
            except ValidationError as e:
                raise ValidationError(f"Invalid level at index {i}: {str(e)}")
        
        return True

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["BuildingDTO"]:
        if isinstance(data, list):
            return [BuildingDTO.from_api_json(item) for item in data]
        
        try:
            feature_collection = validate_feature_collection(data)
            return [BuildingDTO.from_api_json({"properties": feature["properties"]}) 
                   for feature in feature_collection["features"]]
        except ValidationError as e:
            raise ValidationError(f"Invalid feature collection: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error processing feature collection: {str(e)}")
