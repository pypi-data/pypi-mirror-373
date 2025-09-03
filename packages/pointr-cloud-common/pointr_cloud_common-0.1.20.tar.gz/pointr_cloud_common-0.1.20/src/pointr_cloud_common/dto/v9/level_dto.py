from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_required_field, validate_type

@dataclass
class LevelDTO(BaseDTO):
    fid: str
    name: str
    typeCode: str = "level-outline"  # Default typeCode
    shortName: Optional[str] = None
    levelNumber: Optional[int] = None
    sid: Optional[str] = None  # Site ID
    bid: Optional[str] = None  # Building ID

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "LevelDTO":
        """
        Convert API JSON to LevelDTO.
        
        Args:
            data: The data to convert
        
        Returns:
            A LevelDTO instance
        
        Raises:
            ValidationError: If the data is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dictionary for LevelDTO, got {type(data).__name__}")
        
        # Handle both direct properties and nested properties
        properties = data.get("properties", data)
        if not isinstance(properties, dict):
            raise ValidationError("Expected dictionary for properties", "properties", properties)
        
        # Extract required fields with defaults if missing
        fid = properties.get("fid", "")
        if not fid:
            raise ValidationError("Missing required field 'fid'", "fid", None)
        
        name = properties.get("name", f"Level {fid}")
        
        # Extract typeCode with default
        typeCode = properties.get("typeCode", "level-outline")
        
        # Extract optional fields
        short_name = properties.get("shortName")
        if short_name is not None:
            validate_type(short_name, str, "shortName")
        
        level_number = properties.get("lvl")
        if level_number is not None:
            try:
                level_number = int(level_number)
            except (ValueError, TypeError):
                raise ValidationError("levelNumber must be convertible to int", "lvl", level_number)
        
        # Extract site ID and building ID
        sid = properties.get("sid")
        bid = properties.get("bid")
        
        return LevelDTO(
            fid=fid,
            name=name,
            typeCode=typeCode,
            shortName=short_name,
            levelNumber=level_number,
            sid=sid,
            bid=bid
        )

    def to_api_json(self) -> Dict[str, Any]:
        result = {
            "fid": self.fid,
            "name": self.name,
            "typeCode": self.typeCode,
            "shortName": self.shortName,
            "lvl": self.levelNumber
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
        return True

    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["LevelDTO"]:
        return [LevelDTO.from_api_json(item) for item in data_list]
