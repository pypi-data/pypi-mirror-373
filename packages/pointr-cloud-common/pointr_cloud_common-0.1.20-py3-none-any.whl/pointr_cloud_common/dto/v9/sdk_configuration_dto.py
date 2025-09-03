from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Set, ClassVar
import logging

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError, validate_type

# Use standard logger instead of app-specific logger
logger = logging.getLogger(__name__)

@dataclass
class SdkConfigurationDTO(BaseDTO):
    key: str
    value: str
    valueType: str
    
    # Class variables (not dataclass fields)
    VALID_VALUE_TYPES: ClassVar[Set[str]] = {"Float", "Double", "Integer", "Boolean", "String"}

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SdkConfigurationDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SdkConfigurationDTO")
        
        key = data.get("key") or data.get("configurationKey")
        value = data.get("value") or data.get("configurationValue")
        value_type = data.get("valueType") or data.get("ValueType") or data.get("configurationValueType")
        
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
        """
        Convert the DTO to a dictionary for API requests.
        
        Returns:
            A dictionary representation of the DTO
        """
        return {
            "configurationKey": self.key,
            "configurationValue": self.value,
            "configurationValueType": self.valueType
        }
    
    def validate(self) -> bool:
        """
        Validate the DTO according to API requirements.
        
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not self.key:
            raise ValidationError("configurationKey cannot be empty", "key", self.key)
            
        if self.value is None:  # Allow empty string but not None
            raise ValidationError("configurationValue cannot be None", "value", self.value)
            
            
        if not self.valueType:
            raise ValidationError("configurationValueType cannot be empty", "valueType", self.valueType)
            
        if self.valueType not in self.VALID_VALUE_TYPES:
            raise ValidationError(
                f"configurationValueType must be one of {', '.join(self.VALID_VALUE_TYPES)}", 
                "valueType", 
                self.valueType
            )
            
        return True

    @staticmethod
    def list_from_api_json(data_list: List[Dict[str, Any]]) -> List["SdkConfigurationDTO"]:
        return [SdkConfigurationDTO.from_api_json(item) for item in data_list]
        
    @staticmethod
    def list_from_client_api_json(data: Any) -> List["SdkConfigurationDTO"]:
        """
        Convert client API JSON to a list of SdkConfigurationDTO objects.
        
        The API returns a structure like:
        {
            "client": [
                {"key": "...", "value": "...", "valueType": "..."},
                ...
            ],
            "sites": [...]
        }
        
        Args:
            data: The data from the API
            
        Returns:
            A list of SdkConfigurationDTO objects
        """
        if data is None:
            logger.warning("Client SDK configuration is None, returning empty list")
            return []
        
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for client SDK configuration, got {type(data).__name__}, returning empty list")
            return []
        
        # Extract the "client" array from the response
        client_configs = data.get("client", [])
        if not isinstance(client_configs, list):
            logger.warning(f"Expected list for client.client, got {type(client_configs).__name__}, returning empty list")
            return []
        
        logger.info(f"Processing {len(client_configs)} client SDK configurations")
        
        result = []
        for i, item in enumerate(client_configs):
            try:
                if not isinstance(item, dict):
                    logger.warning(f"SDK configuration at index {i} is not a dictionary, skipping")
                    continue
                result.append(SdkConfigurationDTO.from_api_json(item))
            except ValidationError as e:
                logger.warning(f"Failed to parse SDK configuration at index {i}: {str(e)}")
        
        return result
        
    @staticmethod
    def list_from_site_api_json(data: Any, site_fid: Optional[str] = None) -> List["SdkConfigurationDTO"]:
        """
        Convert site API JSON to a list of SdkConfigurationDTO objects.
        
        The API returns a structure like:
        {
            "sites": [
                {
                    "siteIdentifier": "...",
                    "configurations": [
                        {"key": "...", "value": "...", "ValueType": "..."},
                        ...
                    ],
                    "buildings": [...]
                },
                ...
            ]
        }
        
        Args:
            data: The data from the API
            site_fid: Site FID to match against siteIdentifier
            
        Returns:
            A list of SdkConfigurationDTO objects
        """
        if data is None:
            logger.warning(f"Site SDK configuration for site {site_fid or 'unknown'} is None, returning empty list")
            return []
        
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for site SDK configuration for site {site_fid or 'unknown'}, got {type(data).__name__}, returning empty list")
            return []
        
        # Extract the "sites" array from the response
        sites = data.get("sites", [])
        if not isinstance(sites, list):
            logger.warning(f"Expected list for sites, got {type(sites).__name__}, returning empty list")
            return []
        
        # Find the site with matching siteIdentifier
        site_configs = []
        for site in sites:
            if not isinstance(site, dict):
                continue
                
            site_identifier = site.get("siteIdentifier")
            if site_identifier == site_fid:
                site_configs = site.get("configurations", [])
                break
        
        if not isinstance(site_configs, list):
            logger.warning(f"Expected list for site configurations, got {type(site_configs).__name__}, returning empty list")
            return []
        
        logger.info(f"Processing {len(site_configs)} site SDK configurations for site {site_fid}")
        
        result = []
        for i, item in enumerate(site_configs):
            try:
                if not isinstance(item, dict):
                    logger.warning(f"SDK configuration at index {i} for site {site_fid or 'unknown'} is not a dictionary, skipping")
                    continue
                result.append(SdkConfigurationDTO.from_api_json(item))
            except ValidationError as e:
                logger.warning(f"Failed to parse SDK configuration at index {i} for site {site_fid or 'unknown'}: {str(e)}")
        
        return result
        
    @staticmethod
    def list_from_building_api_json(data: Any, building_fid: Optional[str] = None) -> List["SdkConfigurationDTO"]:
        """
        Convert building API JSON to a list of SdkConfigurationDTO objects.
        
        The API returns a structure like:
        {
            "buildings": [
                {
                    "buildingIdentifier": "...",
                    "configurations": [
                        {"key": "...", "value": "...", "ValueType": "..."},
                        ...
                    ]
                },
                ...
            ]
        }
        
        Or it might be nested within a site:
        {
            "sites": [
                {
                    "siteIdentifier": "...",
                    "buildings": [
                        {
                            "buildingIdentifier": "...",
                            "configurations": [...]
                        },
                        ...
                    ]
                }
            ]
        }
        
        Args:
            data: The data from the API
            building_fid: Building FID to match against buildingIdentifier
            
        Returns:
            A list of SdkConfigurationDTO objects
        """
        if data is None:
            logger.warning(f"Building SDK configuration for building {building_fid or 'unknown'} is None, returning empty list")
            return []
        
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for building SDK configuration for building {building_fid or 'unknown'}, got {type(data).__name__}, returning empty list")
            return []
        
        # Try to find the building in the direct "buildings" array
        buildings = data.get("buildings", [])
        if not isinstance(buildings, list):
            # Try to find the building in the nested "sites" array
            sites = data.get("sites", [])
            if isinstance(sites, list):
                for site in sites:
                    if not isinstance(site, dict):
                        continue
                    
                    site_buildings = site.get("buildings", [])
                    if isinstance(site_buildings, list):
                        buildings.extend(site_buildings)
        
        # Find the building with matching buildingIdentifier
        building_configs = []
        for building in buildings:
            if not isinstance(building, dict):
                continue
                
            building_identifier = building.get("buildingIdentifier")
            if building_identifier == building_fid:
                building_configs = building.get("configurations", [])
                break
        
        if not isinstance(building_configs, list):
            logger.warning(f"Expected list for building configurations, got {type(building_configs).__name__}, returning empty list")
            return []
        
        logger.info(f"Processing {len(building_configs)} building SDK configurations for building {building_fid}")
        
        result = []
        for i, item in enumerate(building_configs):
            try:
                if not isinstance(item, dict):
                    logger.warning(f"SDK configuration at index {i} for building {building_fid or 'unknown'} is not a dictionary, skipping")
                    continue
                result.append(SdkConfigurationDTO.from_api_json(item))
            except ValidationError as e:
                logger.warning(f"Failed to parse SDK configuration at index {i} for building {building_fid or 'unknown'}: {str(e)}")
        
        return result
