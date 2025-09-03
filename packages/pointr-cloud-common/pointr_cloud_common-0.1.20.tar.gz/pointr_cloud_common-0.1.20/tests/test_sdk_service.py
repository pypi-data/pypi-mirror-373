import pytest
from unittest.mock import MagicMock, patch
from pointr_cloud_common.api.v9.sdk_service import SdkApiService
from pointr_cloud_common.dto.v9.sdk_configuration_dto import SdkConfigurationDTO
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestSdkApiService:
    """Tests for the SdkApiService class."""
    
    def test_get_client_sdk_config(self, mock_api_service, mock_sdk_config_data):
        """Test get_client_sdk_config method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_sdk_config_data
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Call the method
        configs = sdk_service.get_client_sdk_config()
        
        # Verify the result
        assert len(configs) == 3
        assert all(isinstance(config, SdkConfigurationDTO) for config in configs)
        assert configs[0].key == "config1"
        assert configs[0].value == "value1"
        assert configs[0].scope == "global"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sdk-configurations"
        )
        
    def test_get_site_sdk_config(self, mock_api_service, mock_sdk_config_data):
        """Test get_site_sdk_config method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_sdk_config_data
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Call the method
        configs = sdk_service.get_site_sdk_config("site-123")
        
        # Verify the result
        assert len(configs) == 3
        assert all(isinstance(config, SdkConfigurationDTO) for config in configs)
        assert configs[0].key == "config1"
        assert configs[0].value == "value1"
        assert configs[0].scope == "site"
        assert configs[0].scopeId == "site-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/sdk-configurations"
        )
        
    def test_get_building_sdk_config(self, mock_api_service, mock_sdk_config_data):
        """Test get_building_sdk_config method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_sdk_config_data
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Call the method
        configs = sdk_service.get_building_sdk_config("site-123", "building-123")
        
        # Verify the result
        assert len(configs) == 3
        assert all(isinstance(config, SdkConfigurationDTO) for config in configs)
        assert configs[0].key == "config1"
        assert configs[0].value == "value1"
        assert configs[0].scope == "building"
        assert configs[0].scopeId == "building-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/sdk-configurations"
        )
        
    def test_put_global_sdk_configurations(self, mock_api_service):
        """Test put_global_sdk_configurations method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {}
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Create SDK configurations
        configs = [
            SdkConfigurationDTO(key="config1", value="value1"),
            SdkConfigurationDTO(key="config2", value=True)
        ]
        
        # Call the method
        result = sdk_service.put_global_sdk_configurations(configs)
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sdk-configurations"
        assert len(args[2]) == 2
        assert args[2][0]["key"] == "config1"
        assert args[2][0]["value"] == "value1"
        assert args[2][1]["key"] == "config2"
        assert args[2][1]["value"] is True
        
    def test_put_site_sdk_configurations(self, mock_api_service):
        """Test put_site_sdk_configurations method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {}
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Create SDK configurations
        configs = [
            SdkConfigurationDTO(key="config1", value="value1", scope="site", scopeId="site-123"),
            SdkConfigurationDTO(key="config2", value=True, scope="site", scopeId="site-123")
        ]
        
        # Call the method
        result = sdk_service.put_site_sdk_configurations("site-123", configs)
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/sdk-configurations"
        assert len(args[2]) == 2
        
    def test_put_building_sdk_configurations(self, mock_api_service):
        """Test put_building_sdk_configurations method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {}
        
        # Create the service
        sdk_service = SdkApiService(mock_api_service)
        
        # Create SDK configurations
        configs = [
            SdkConfigurationDTO(key="config1", value="value1", scope="building", scopeId="building-123"),
            SdkConfigurationDTO(key="config2", value=True, scope="building", scopeId="building-123")
        ]
        
        # Call the method
        result = sdk_service.put_building_sdk_configurations("site-123", "building-123", configs)
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/sdk-configurations"
        assert len(args[2]) == 2
