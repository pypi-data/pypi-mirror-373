import pytest
from unittest.mock import MagicMock, patch
from pointr_cloud_common.api.v9.level_service import LevelApiService
from pointr_cloud_common.dto.v9.level_dto import LevelDTO
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestLevelApiService:
    """Tests for the LevelApiService class."""
    
    def test_get_levels(self, mock_api_service, mock_level_data):
        """Test get_levels method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_level_data
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Call the method
        levels = level_service.get_levels("site-123", "building-123")
        
        # Verify the result
        assert len(levels) == 1
        assert isinstance(levels[0], LevelDTO)
        assert levels[0].fid == "level-123"
        assert levels[0].name == "Floor 1"
        assert levels[0].floorNumber == 1
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels"
        )
        
    def test_get_level_by_id(self, mock_api_service, mock_level_data):
        """Test get_level_by_id method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_level_data
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Call the method
        level = level_service.get_level_by_id("site-123", "building-123", "level-123")
        
        # Verify the result
        assert isinstance(level, LevelDTO)
        assert level.fid == "level-123"
        assert level.name == "Floor 1"
        assert level.floorNumber == 1
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels"
        )
        
    def test_get_level_by_id_not_found(self, mock_api_service, mock_level_data):
        """Test get_level_by_id method when level is not found."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_level_data
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Call the method and expect an exception
        with pytest.raises(V9ApiError) as excinfo:
            level_service.get_level_by_id("site-123", "building-123", "non-existent-level")
        
        # Verify the exception message
        assert "No level found with ID" in str(excinfo.value)
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels"
        )
        
    def test_create_level(self, mock_api_service, mock_create_response):
        """Test create_level method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_create_response
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Create level data
        level_data = {
            "fid": "level-123",
            "name": "Floor 1",
            "typeCode": "level",
            "floorNumber": 1,
            "extra": {
                "height": 3.5
            }
        }
        
        # Call the method
        result = level_service.create_level("site-123", "building-123", level_data)
        
        # Verify the result
        assert result == "new-entity-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "POST", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels", 
            level_data
        )
        
    def test_update_level(self, mock_api_service, mock_create_response):
        """Test update_level method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_create_response
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Create level data
        level_data = {
            "fid": "level-123",
            "name": "Updated Floor 1",
            "typeCode": "level",
            "floorNumber": 1,
            "extra": {
                "height": 4.0
            }
        }
        
        # Call the method
        result = level_service.update_level("site-123", "building-123", "level-123", level_data)
        
        # Verify the result
        assert result == "new-entity-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "PUT", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels/level-123", 
            level_data
        )
        
    def test_delete_level(self, mock_api_service):
        """Test delete_level method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {}
        
        # Create the service
        level_service = LevelApiService(mock_api_service)
        
        # Call the method
        result = level_service.delete_level("site-123", "building-123", "level-123")
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "DELETE", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123/levels/level-123"
        )
