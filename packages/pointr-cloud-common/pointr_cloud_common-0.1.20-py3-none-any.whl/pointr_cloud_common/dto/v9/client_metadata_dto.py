from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type, ensure_dict

@dataclass
class ClientMetadataDTO(BaseDTO):
    identifier: str
    name: str
    extra: Dict[str, Any]
    externalIdentifier: Optional[str] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "ClientMetadataDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for ClientMetadataDTO")
        
        validate_required_field(data, "identifier")
        validate_required_field(data, "name")
        validate_type(data["identifier"], str, "identifier")
        validate_type(data["name"], str, "name")
        
        extra = ensure_dict(data.get("extra"), "extra")
        
        # Extract optional externalIdentifier
        external_id = data.get("externalIdentifier")
        if external_id is not None:
            validate_type(external_id, str, "externalIdentifier")
        
        return ClientMetadataDTO(
            identifier=data["identifier"],
            name=data["name"],
            extra=extra,
            externalIdentifier=external_id
        )

    def to_api_json(self) -> Dict[str, Any]:
        result = {
            "identifier": self.identifier,
            "name": self.name,
            "extra": self.extra
        }
        
        if self.externalIdentifier:
            result["externalIdentifier"] = self.externalIdentifier
            
        return result
    
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
