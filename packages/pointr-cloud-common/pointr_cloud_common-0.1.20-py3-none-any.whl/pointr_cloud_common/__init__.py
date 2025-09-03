"""
Pointr Cloud Commons - A Python package for interacting with Pointr Cloud APIs.

This package provides a set of tools for interacting with the Pointr Cloud APIs
(both V8 and V9), including services for managing sites, buildings, levels and
SDK configurations.
"""

import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import main classes for easy access
from pointr_cloud_common.api.v9.v9_api_service import V9ApiService
from pointr_cloud_common.api.v9.base_service import V9ApiError
from pointr_cloud_common.api.mapscale_v9_service import MapscaleV9ApiService

# Expose V8 API classes at the package level
from pointr_cloud_common.api.v8.v8_api_service import V8ApiService
from pointr_cloud_common.api.v8.base_service import V8ApiError

# Version information
__version__ = '0.1.0'

# Public exports for convenience
__all__ = [
    'V9ApiService',
    'V9ApiError',
    'V8ApiService',
    'V8ApiError',
    'MapscaleV9ApiService',
]
