from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type

@dataclass
class LevelDTO(BaseDTO):
    fid: str
    name: str
    shortName: Optional[str] = None
    levelNumber: Optional[int] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "LevelDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for LevelDTO")
        
        validate_required_field(data, "fid")
        validate_required_field(data, "name")
        validate_type(data["fid"], str, "fid")
        validate_type(data["name"], str, "name")
        
        short_name = data.get("shortName")
        if short_name is not None:
            validate_type(short_name, str, "shortName")
        
        level_number = data.get("lvl")
        if level_number is not None:
            try:
                level_number = int(level_number)
            except (ValueError, TypeError):
                raise ValidationError("levelNumber must be convertible to int", "lvl", level_number)
        
        return LevelDTO(
            fid=data["fid"],
            name=data["name"],
            shortName=short_name,
            levelNumber=level_number
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "fid": self.fid,
            "name": self.name,
            "shortName": self.shortName,
            "lvl": self.levelNumber
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        return True

    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["LevelDTO"]:
        return [LevelDTO.from_api_json(item) for item in data_list]
