import pytest
from unittest.mock import MagicMock, patch
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError

class TestBaseApiService:
    """Tests for the BaseApiService class."""
    
    def test_init(self, mock_api_service):
        """Test initialization of BaseApiService."""
        base_service = BaseApiService(mock_api_service)
        
        assert base_service.api_service == mock_api_service
        assert base_service.base_url == mock_api_service.base_url
        assert base_service.client_id == mock_api_service.client_id
        assert base_service.user_email == mock_api_service.user_email
        assert base_service.token == mock_api_service.token
        
    def test_make_request(self, mock_api_service):
        """Test _make_request method."""
        base_service = BaseApiService(mock_api_service)
        
        # Set up the mock
        expected_result = {"key": "value"}
        mock_api_service._make_request.return_value = expected_result
        
        # Call the method
        result = base_service._make_request("GET", "test/endpoint", {"param": "value"})
        
        # Verify the result
        assert result == expected_result
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with("GET", "test/endpoint", {"param": "value"})

class TestV9ApiError:
    """Tests for the V9ApiError class."""
    
    def test_init(self):
        """Test initialization of V9ApiError."""
        error = V9ApiError("Test error", 400, "Bad request")
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_text == "Bad request"
        
    def test_init_without_optional_args(self):
        """Test initialization of V9ApiError without optional arguments."""
        error = V9ApiError("Test error")
        
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_text is None
