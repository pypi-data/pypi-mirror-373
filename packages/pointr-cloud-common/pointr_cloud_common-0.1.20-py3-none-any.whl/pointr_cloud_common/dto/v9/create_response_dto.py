from dataclasses import dataclass
from typing import Dict, Any, List

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type

@dataclass
class CreateResponseDTO(BaseDTO):
    fid: str

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "CreateResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for CreateResponseDTO")
        
        validate_required_field(data, "fid")
        validate_type(data["fid"], str, "fid")
        
        return CreateResponseDTO(fid=data["fid"])

    def to_api_json(self) -> Dict[str, Any]:
        return {"fid": self.fid}
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        return True
    
    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["CreateResponseDTO"]:
        return [CreateResponseDTO.from_api_json(item) for item in data_list]
