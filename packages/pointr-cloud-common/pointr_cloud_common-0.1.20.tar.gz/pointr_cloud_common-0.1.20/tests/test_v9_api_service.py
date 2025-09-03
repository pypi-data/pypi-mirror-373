import pytest
from unittest.mock import MagicMock, patch, call
import requests
import json
from pointr_cloud_common.api.v9.v9_api_service import V9ApiService
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestV9ApiService:
    """Tests for the V9ApiService class."""
    
    def test_init_with_token(self, mock_config, mock_token):
        """Test initialization with token."""
        # Create the service with a token
        api_service = V9ApiService(mock_config, user_email="test@example.com", token=mock_token)
        
        # Verify the service properties
        assert api_service.base_url == mock_config["api_url"]
        assert api_service.client_id == mock_config["client_identifier"]
        assert api_service.user_email == "test@example.com"
        assert api_service.token == mock_token
        
        # Verify the sub-services were initialized
        assert api_service.site_service is not None
        assert api_service.building_service is not None
        assert api_service.level_service is not None
        assert api_service.sdk_service is not None
        assert api_service.client_service is not None
        
    def test_init_with_credentials(self, mock_config):
        """Test initialization with credentials."""
        # Mock the _get_token method
        with patch('pointr_cloud_common.api.v9.v9_api_service.V9ApiService._get_token', return_value="test-token") as mock_get_token:
            # Create the service with credentials
            api_service = V9ApiService(mock_config)
            
            # Verify the service properties
            assert api_service.base_url == mock_config["api_url"]
            assert api_service.client_id == mock_config["client_identifier"]
            assert api_service.token == "test-token"
            
            # Verify _get_token was called
            mock_get_token.assert_called_once()
            
    def test_get_token(self, mock_config):
        """Test _get_token method."""
        # Mock the requests.post method
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"access_token": "test-token"}
            mock_post.return_value = mock_response
            
            # Create the service
            api_service = V9ApiService.__new__(V9ApiService)
            api_service.base_url = mock_config["api_url"]
            api_service.client_id = mock_config["client_identifier"]
            api_service.username = mock_config["username"]
            api_service.password = mock_config["password"]
            api_service.logger = MagicMock()
            
            # Call the method
            token = api_service._get_token()
            
            # Verify the result
            assert token == "test-token"
            
            # Verify the mock was called correctly
            mock_post.assert_called_once_with(
                f"{mock_config['api_url']}/api/v9/identity/clients/{mock_config['client_identifier']}/auth/token",
                json={
                    "username": mock_config["username"],
                    "password": mock_config["password"],
                    "grant_type": "password"
                }
            )
            
    def test_get_token_error(self, mock_config):
        """Test _get_token method with error."""
        # Mock the requests.post method
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.json.side_effect = ValueError("No JSON")
            mock_post.return_value = mock_response
            
            # Create the service
            api_service = V9ApiService.__new__(V9ApiService)
            api_service.base_url = mock_config["api_url"]
            api_service.client_id = mock_config["client_identifier"]
            api_service.username = mock_config["username"]
            api_service.password = mock_config["password"]
            api_service.logger = MagicMock()
            
            # Call the method and expect an exception
            with pytest.raises(V9ApiError) as excinfo:
                api_service._get_token()
            
            # Verify the exception message
            assert "Failed to get token: 401" in str(excinfo.value)
            assert "response: Unauthorized" in str(excinfo.value)
            
    def test_make_request(self):
        """Test _make_request method."""
        # Create a new instance of V9ApiService
        api_service = V9ApiService.__new__(V9ApiService)
        api_service.base_url = "https://api.example.com"
        api_service.token = "test-token"
        api_service.logger = MagicMock()
        
        # Mock the requests.get method
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"key": "value"}
            mock_get.return_value = mock_response
            
            # Call the method
            result = api_service._make_request("GET", "test/endpoint")
            
            # Verify the result
            assert result == {"key": "value"}
            
            # Verify the mock was called correctly
            mock_get.assert_called_once_with(
                "https://api.example.com/test/endpoint",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json"
                }
            )
            
    def test_make_request_post(self):
        """Test _make_request method with POST."""
        # Create a new instance of V9ApiService
        api_service = V9ApiService.__new__(V9ApiService)
        api_service.base_url = "https://api.example.com"
        api_service.token = "test-token"
        api_service.logger = MagicMock()
        
        # Mock the requests.post method
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"key": "value"}
            mock_post.return_value = mock_response
            
            # Call the method
            result = api_service._make_request("POST", "test/endpoint", {"param": "value"})
            
            # Verify the result
            assert result == {"key": "value"}
            
            # Verify the mock was called correctly
            mock_post.assert_called_once_with(
                "https://api.example.com/test/endpoint",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json"
                },
                json={"param": "value"}
            )
            
    def test_make_request_error(self):
        """Test _make_request method with error."""
        # Create a new instance of V9ApiService
        api_service = V9ApiService.__new__(V9ApiService)
        api_service.base_url = "https://api.example.com"
        api_service.token = "test-token"
        api_service.logger = MagicMock()
        
        # Mock the requests.get method
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.json.return_value = {"message": "Resource not found"}
            mock_get.return_value = mock_response
            
            # Call the method and expect an exception
            with pytest.raises(V9ApiError) as excinfo:
                api_service._make_request("GET", "test/endpoint")
            
            # Verify the exception message
            assert "API request failed: 404" in str(excinfo.value)
            assert "message: Resource not found" in str(excinfo.value)
            
    def test_make_request_network_error(self):
        """Test _make_request method with network error."""
        # Create a new instance of V9ApiService
        api_service = V9ApiService.__new__(V9ApiService)
        api_service.base_url = "https://api.example.com"
        api_service.token = "test-token"
        api_service.logger = MagicMock()
        
        # Mock the requests.get method
        with patch('requests.get') as mock_get:
            # Set up the mock to raise an exception
            mock_get.side_effect = requests.RequestException("Connection error")
            
            # Call the method and expect an exception
            with pytest.raises(V9ApiError) as excinfo:
                api_service._make_request("GET", "test/endpoint")
            
            # Verify the exception message
            assert "Request error: Connection error" in str(excinfo.value)
            
    def test_delegation_methods(self, mock_api_service):
        """Test that delegation methods call the correct service methods."""
        # Mock the service methods
        mock_api_service.site_service.get_sites = MagicMock(return_value=["site1", "site2"])
        mock_api_service.building_service.get_buildings = MagicMock(return_value=["building1", "building2"])
        mock_api_service.level_service.get_levels = MagicMock(return_value=["level1", "level2"])
        mock_api_service.client_service.get_client_metadata = MagicMock(return_value={"name": "Test Client"})
        mock_api_service.sdk_service.get_client_sdk_config = MagicMock(return_value=["config1", "config2"])
        
        # Call the delegation methods
        sites = mock_api_service.get_sites()
        buildings = mock_api_service.get_buildings("site-123")
        levels = mock_api_service.get_levels("site-123", "building-123")
        client_metadata = mock_api_service.get_client_metadata()
        sdk_configs = mock_api_service.get_client_sdk_config()
        
        # Verify the results
        assert sites == ["site1", "site2"]
        assert buildings == ["building1", "building2"]
        assert levels == ["level1", "level2"]
        assert client_metadata == {"name": "Test Client"}
        assert sdk_configs == ["config1", "config2"]
        
        # Verify the mocks were called correctly
        mock_api_service.site_service.get_sites.assert_called_once()
        mock_api_service.building_service.get_buildings.assert_called_once_with("site-123")
        mock_api_service.level_service.get_levels.assert_called_once_with("site-123", "building-123")
        mock_api_service.client_service.get_client_metadata.assert_called_once()
        mock_api_service.sdk_service.get_client_sdk_config.assert_called_once()
