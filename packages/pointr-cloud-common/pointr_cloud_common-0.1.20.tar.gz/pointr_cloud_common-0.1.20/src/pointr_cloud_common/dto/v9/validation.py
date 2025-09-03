from typing import TypedDict, Any, Dict, List, Optional, TypeVar, cast, Protocol, runtime_checkable, Union, Literal, overload, get_type_hints
import json
from dataclasses import is_dataclass

T = TypeVar('T')

class ValidationError(Exception):
    """Exception raised for validation errors in DTOs."""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(f"{message}: {field}={value}" if field else message)

@runtime_checkable
class Validatable(Protocol):
    """Protocol for objects that can validate themselves."""
    def validate(self) -> bool: ...

def validate_required_field(data: Dict[str, Any], field: str) -> None:
    """Validate that a required field exists and is not None."""
    if field not in data or data[field] is None:
        raise ValidationError(f"Required field missing", field, None)

def validate_type(value: Any, expected_type: Any, field: str) -> None:
    """Validate that a value is of the expected type."""
    if not isinstance(value, expected_type):
        raise ValidationError(f"Invalid type, expected {expected_type.__name__}", field, value)

class FeaturePropertiesDict(TypedDict, total=False):
    """TypedDict for GeoJSON feature properties."""
    fid: str
    name: str
    typeCode: str
    extra: Dict[str, Any]
    sid: Optional[str]
    bid: Optional[str]
    eid: Optional[str]
    shortName: Optional[str]
    lvl: Optional[int]

class GeometryDict(TypedDict):
    """TypedDict for GeoJSON geometry."""
    type: str
    coordinates: Any

class FeatureDict(TypedDict):
    """TypedDict for GeoJSON feature."""
    type: Literal["Feature"]
    properties: FeaturePropertiesDict
    geometry: GeometryDict

class FeatureCollectionDict(TypedDict):
    """TypedDict for GeoJSON feature collection."""
    type: Literal["FeatureCollection"]
    features: List[FeatureDict]

def validate_feature_collection(data: Any) -> FeatureCollectionDict:
    """Validate that data is a valid GeoJSON feature collection."""
    if not isinstance(data, dict):
        raise ValidationError("Expected a dictionary for feature collection")
    
    if data.get("type") != "FeatureCollection":
        raise ValidationError("Expected type 'FeatureCollection'", "type", data.get("type"))
    
    if "features" not in data or not isinstance(data["features"], list):
        raise ValidationError("Expected 'features' to be a list", "features", data.get("features"))
    
    return cast(FeatureCollectionDict, data)

def validate_dto_list(data_list: List[Dict[str, Any]], dto_class: Any) -> List[T]:
    """Validate a list of dictionaries against a DTO class."""
    if not isinstance(data_list, list):
        raise ValidationError(f"Expected a list for {dto_class.__name__} list")
    
    result = []
    for i, item in enumerate(data_list):
        try:
            dto = dto_class.from_api_json(item)
            if hasattr(dto, 'validate'):
                dto.validate()
            result.append(dto)
        except ValidationError as e:
            raise ValidationError(f"Validation error at index {i}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error creating {dto_class.__name__} at index {i}: {str(e)}")
    
    return result

def ensure_dict(value: Any, field_name: str) -> Dict[str, Any]:
    """
    Ensure a value is a dictionary, converting None to an empty dict.
    
    Args:
        value: The value to check
        field_name: The name of the field (for error messages)
        
    Returns:
        A dictionary (either the original value or an empty dict if None)
        
    Raises:
        ValidationError: If the value is not None and not a dictionary
    """
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"Expected dictionary for {field_name}", field_name, value)
    return value
