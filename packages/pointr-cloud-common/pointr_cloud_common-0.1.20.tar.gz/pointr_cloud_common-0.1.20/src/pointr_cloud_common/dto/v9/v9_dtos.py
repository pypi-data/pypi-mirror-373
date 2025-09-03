from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, cast, ClassVar, Type, TypeVar

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import (
    ValidationError, validate_required_field, validate_type, 
    validate_feature_collection, FeatureDict, FeatureCollectionDict,
    ensure_dict
)

# Import the refactored DTOs
from pointr_cloud_common.dto.v9.response_dtos import CreateResponseDTO
from pointr_cloud_common.dto.v9.client_dtos import ClientMetadataDTO, ClientDTO, GpsGeofenceDTO
from pointr_cloud_common.dto.v9.sdk_dtos import SdkConfigurationDTO
from pointr_cloud_common.dto.v9.building_dtos import BuildingDTO
from pointr_cloud_common.dto.v9.site_dtos import SiteDTO
from pointr_cloud_common.dto.v9.level_dtos import LevelDTO
from pointr_cloud_common.dto.v9.migration_dtos import MigrationTreeDTO

# Re-export all DTOs for backward compatibility
__all__ = [
    'CreateResponseDTO',
    'ClientMetadataDTO',
    'ClientDTO',
    'GpsGeofenceDTO',
    'SdkConfigurationDTO',
    'BuildingDTO',
    'SiteDTO',
    'LevelDTO',
    'MigrationTreeDTO'
]
