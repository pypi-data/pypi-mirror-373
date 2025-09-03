import pytest
from unittest.mock import MagicMock, patch
from pointr_cloud_common.api.v9.client_service import ClientApiService
from pointr_cloud_common.dto.v9.client_metadata_dto import ClientMetadataDTO
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestClientApiService:
    """Tests for the ClientApiService class."""
    
    def test_get_client_metadata(self, mock_api_service, mock_client_data):
        """Test get_client_metadata method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_client_data
        
        # Create the service
        client_service = ClientApiService(mock_api_service)
        
        # Call the method
        client_metadata = client_service.get_client_metadata()
        
        # Verify the result
        assert isinstance(client_metadata, ClientMetadataDTO)
        assert client_metadata.identifier == "test-client-id"
        assert client_metadata.name == "Test Client"
        assert "industry" in client_metadata.extraData
        assert client_metadata.extraData["industry"] == "Technology"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}"
        )
        
    def test_update_client(self, mock_api_service):
        """Test update_client method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {}
        
        # Create the service
        client_service = ClientApiService(mock_api_service)
        
        # Create client data
        client_data = {
            "identifier": "test-client-id",
            "name": "Updated Client",
            "extra": {
                "industry": "Healthcare",
                "region": "Europe"
            }
        }
        
        # Call the method
        result = client_service.update_client("test-client-id", client_data)
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "PUT", 
            "api/v9/content/draft/clients/test-client-id", 
            client_data
        )
        
    def test_create_client(self, mock_api_service):
        """Test create_client method."""
        # Set up the mock
        mock_api_service._make_request.return_value = {"identifier": "new-client-123"}
        
        # Create the service
        client_service = ClientApiService(mock_api_service)
        
        # Create client data
        client_data = {
            "identifier": "new-client-123",
            "name": "New Client",
            "extra": {
                "industry": "Retail",
                "region": "Asia"
            }
        }
        
        # Call the method
        result = client_service.create_client(client_data)
        
        # Verify the result
        assert result == "new-client-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "POST", 
            "api/v9/content/draft/clients", 
            client_data
        )
        
    def test_get_client_gps_geofences(self, mock_api_service):
        """Test get_client_gps_geofences method."""
        # Set up the mock
        mock_geofences = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "fid": "geofence-123",
                        "name": "Test Geofence",
                        "typeCode": "gps-geofence"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [0, 0],
                                [0, 1],
                                [1, 1],
                                [1, 0],
                                [0, 0]
                            ]
                        ]
                    }
                }
            ]
        }
        mock_api_service._make_request.return_value = mock_geofences
        
        # Create the service
        client_service = ClientApiService(mock_api_service)
        
        # Call the method
        geofences = client_service.get_client_gps_geofences()
        
        # Verify the result
        assert len(geofences) == 1
        assert geofences[0]["properties"]["fid"] == "geofence-123"
        assert geofences[0]["properties"]["name"] == "Test Geofence"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/gps-geofences"
        )
