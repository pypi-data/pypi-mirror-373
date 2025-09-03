import pytest
from unittest.mock import MagicMock, patch, ANY
from pointr_cloud_common.api.v9.building_service import BuildingApiService
from pointr_cloud_common.dto.v9.building_dto import BuildingDTO
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestBuildingApiService:
    """Tests for the BuildingApiService class."""
    
    def test_get_buildings(self, mock_api_service, mock_building_data):
        """Test get_buildings method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_building_data
        
        # Create the service
        building_service = BuildingApiService(mock_api_service)
        
        # Call the method
        buildings = building_service.get_buildings("site-123")
        
        # Verify the result
        assert len(buildings) == 1
        assert isinstance(buildings[0], BuildingDTO)
        assert buildings[0].fid == "building-123"
        assert buildings[0].name == "Test Building"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings"
        )
        
    def test_get_building_by_fid(self, mock_api_service, mock_building_data):
        """Test get_building_by_fid method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_building_data
        
        # Create the service
        building_service = BuildingApiService(mock_api_service)
        
        # Call the method
        building = building_service.get_building_by_fid("site-123", "building-123")
        
        # Verify the result
        assert isinstance(building, BuildingDTO)
        assert building.fid == "building-123"
        assert building.name == "Test Building"
        assert building.typeCode == "building-outline"
        assert building.sid == "site-123"
        assert "floors" in building.extraData
        assert building.extraData["floors"] == 5
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123"
        )
        
    def test_create_building(self, mock_api_service, mock_create_response):
        """Test create_building method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_create_response
        
        # Create the service
        building_service = BuildingApiService(mock_api_service)
        
        # Create a building DTO
        building = BuildingDTO(
            fid="building-123",
            name="Test Building",
            typeCode="building-outline",
            sid="site-123",
            extraData={"floors": 5}
        )
        
        # Call the method
        result = building_service.create_building("site-123", building)
        
        # Verify the result
        assert result == "new-entity-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "POST"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings"
        assert "features" in args[2]
        
    def test_update_building(self, mock_api_service, mock_building_data):
        """Test update_building method with source API service."""
        # Set up the mocks
        mock_source_api_service = MagicMock()
        mock_source_api_service._make_request.return_value = mock_building_data
        mock_source_api_service.client_id = "source-client-id"
        
        # Create the service
        building_service = BuildingApiService(mock_api_service)
        
        # Create a building DTO
        building = BuildingDTO(
            fid="building-123",
            name="Updated Building",
            typeCode="building-outline",
            sid="site-123",
            extraData={"floors": 6}
        )
        
        # Call the method
        result = building_service.update_building("site-123", "building-123", building, mock_source_api_service)
        
        # Verify the result
        assert result == "building-123"
        
        # Verify the mocks were called correctly
        mock_source_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/source-client-id/sites/site-123/buildings/building-123"
        )
        
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123"
        
    def test_update_building_extra_data(self, mock_api_service, mock_building_data):
        """Test update_building_extra_data method."""
        # Set up the mocks
        mock_api_service._make_request.side_effect = [
            mock_building_data,  # First call to get current building data
            {}  # Second call to update the building
        ]
        
        # Create the service
        building_service = BuildingApiService(mock_api_service)
        
        # Call the method
        extra_data = {"floors": 7, "renovated": True}
        result = building_service.update_building_extra_data("site-123", "building-123", extra_data)
        
        # Verify the result
        assert result is True
        
        # Verify the mocks were called correctly
        assert mock_api_service._make_request.call_count == 2
        
        # First call should be a GET to retrieve the current building data
        args1, kwargs1 = mock_api_service._make_request.call_args_list[0]
        assert args1[0] == "GET"
        assert args1[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123"
        
        # Second call should be a PUT to update the building with the new extra data
        args2, kwargs2 = mock_api_service._make_request.call_args_list[1]
        assert args2[0] == "PUT"
        assert args2[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123/buildings/building-123"
        assert "features" in args2[2]
        assert args2[2]["features"][0]["properties"]["extra"] == extra_data
