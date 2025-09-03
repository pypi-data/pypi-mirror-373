"""V8 API package."""

from pointr_cloud_common.api.v8.errors import V8ApiError
from pointr_cloud_common.api.v8.v8_api_service import V8ApiService
from pointr_cloud_common.api.v8.base_service import BaseApiService
from pointr_cloud_common.api.v8.poi_service import PoiApiService

__all__ = ['V8ApiError', 'V8ApiService', 'BaseApiService', 'PoiApiService']
