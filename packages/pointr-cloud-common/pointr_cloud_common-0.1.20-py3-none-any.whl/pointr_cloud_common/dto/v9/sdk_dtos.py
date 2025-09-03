from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type

@dataclass
class SdkConfigurationDTO(BaseDTO):
    key: str
    value: str
    valueType: str

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SdkConfigurationDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SdkConfigurationDTO")
        
        key = data.get("key") or data.get("configurationKey")
        value = data.get("value") or data.get("configurationValue")
        value_type = data.get("valueType") or data.get("configurationValueType")
        
        if not key:
            raise ValidationError("Missing key/configurationKey", "key", None)
        if value is None:  # Allow empty string but not None
            raise ValidationError("Missing value/configurationValue", "value", None)
        if not value_type:
            raise ValidationError("Missing valueType/configurationValueType", "valueType", None)
        
        validate_type(key, str, "key")
        validate_type(value, str, "value")
        validate_type(value_type, str, "valueType")
        
        return SdkConfigurationDTO(
            key=key,
            value=value,
            valueType=value_type
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "valueType": self.valueType
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.key:
            raise ValidationError("key cannot be empty", "key", self.key)
        if self.value is None:  # Allow empty string but not None
            raise ValidationError("value cannot be None", "value", self.value)
        if not self.valueType:
            raise ValidationError("valueType cannot be empty", "valueType", self.valueType)
        return True

    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["SdkConfigurationDTO"]:
        return [SdkConfigurationDTO.from_api_json(item) for item in data_list]
        
    @staticmethod
    def list_from_client_api_json(data_list: List[Dict[str, Any]]) -> List["SdkConfigurationDTO"]:
        return [SdkConfigurationDTO.from_api_json(item) for item in data_list]
        
    @staticmethod
    def list_from_site_api_json(data_list: List[Dict[str, Any]], site_fid: Optional[str] = None) -> List["SdkConfigurationDTO"]:
        return [SdkConfigurationDTO.from_api_json(item) for item in data_list]
        
    @staticmethod
    def list_from_building_api_json(data_list: List[Dict[str, Any]], building_fid: Optional[str] = None) -> List["SdkConfigurationDTO"]:
        return [SdkConfigurationDTO.from_api_json(item) for item in data_list]
