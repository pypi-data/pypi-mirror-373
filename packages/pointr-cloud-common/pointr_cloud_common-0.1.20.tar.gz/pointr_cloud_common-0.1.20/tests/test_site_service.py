import pytest
from unittest.mock import MagicMock, patch
from pointr_cloud_common.api.v9.site_service import SiteApiService
from pointr_cloud_common.dto.v9.site_dto import SiteDTO
from pointr_cloud_common.api.v9.base_service import V9ApiError

class TestSiteApiService:
    """Tests for the SiteApiService class."""
    
    def test_get_sites(self, mock_api_service, mock_site_data):
        """Test get_sites method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_site_data
        
        # Create the service
        site_service = SiteApiService(mock_api_service)
        
        # Call the method
        sites = site_service.get_sites()
        
        # Verify the result
        assert len(sites) == 1
        assert isinstance(sites[0], SiteDTO)
        assert sites[0].fid == "site-123"
        assert sites[0].name == "Test Site"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites"
        )
        
    def test_get_site_by_fid(self, mock_api_service, mock_site_data):
        """Test get_site_by_fid method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_site_data
        
        # Create the service
        site_service = SiteApiService(mock_api_service)
        
        # Call the method
        site = site_service.get_site_by_fid("site-123")
        
        # Verify the result
        assert isinstance(site, SiteDTO)
        assert site.fid == "site-123"
        assert site.name == "Test Site"
        assert site.typeCode == "site-outline"
        assert "description" in site.extraData
        assert site.extraData["description"] == "Test site description"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123"
        )
        
    def test_create_site(self, mock_api_service, mock_create_response):
        """Test create_site method."""
        # Set up the mock
        mock_api_service._make_request.return_value = mock_create_response
        
        # Create the service
        site_service = SiteApiService(mock_api_service)
        
        # Create a site DTO
        site = SiteDTO(
            fid="site-123",
            name="Test Site",
            typeCode="site-outline",
            extraData={"description": "Test site description"}
        )
        
        # Call the method
        result = site_service.create_site(site)
        
        # Verify the result
        assert result == "new-entity-123"
        
        # Verify the mock was called correctly
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "POST"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites"
        assert "features" in args[2]
        
    def test_update_site(self, mock_api_service, mock_site_data):
        """Test update_site method with source API service."""
        # Set up the mocks
        mock_source_api_service = MagicMock()
        mock_source_api_service._make_request.return_value = mock_site_data
        mock_source_api_service.client_id = "source-client-id"
        
        # Create the service
        site_service = SiteApiService(mock_api_service)
        
        # Create a site DTO
        site = SiteDTO(
            fid="site-123",
            name="Updated Site",
            typeCode="site-outline",
            extraData={"description": "Updated site description"}
        )
        
        # Call the method
        result = site_service.update_site("site-123", site, mock_source_api_service)
        
        # Verify the result
        assert result == "site-123"
        
        # Verify the mocks were called correctly
        mock_source_api_service._make_request.assert_called_once_with(
            "GET", 
            f"api/v9/content/draft/clients/source-client-id/sites/site-123"
        )
        
        mock_api_service._make_request.assert_called_once()
        args, kwargs = mock_api_service._make_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123"
        
    def test_update_site_extra_data(self, mock_api_service, mock_site_data):
        """Test update_site_extra_data method."""
        # Set up the mocks
        mock_api_service._make_request.side_effect = [
            mock_site_data,  # First call to get current site data
            {}  # Second call to update the site
        ]
        
        # Create the service
        site_service = SiteApiService(mock_api_service)
        
        # Call the method
        extra_data = {"description": "Updated description", "status": "active"}
        result = site_service.update_site_extra_data("site-123", extra_data)
        
        # Verify the result
        assert result is True
        
        # Verify the mocks were called correctly
        assert mock_api_service._make_request.call_count == 2
        
        # First call should be a GET to retrieve the current site data
        args1, kwargs1 = mock_api_service._make_request.call_args_list[0]
        assert args1[0] == "GET"
        assert args1[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123"
        
        # Second call should be a PUT to update the site with the new extra data
        args2, kwargs2 = mock_api_service._make_request.call_args_list[1]
        assert args2[0] == "PUT"
        assert args2[1] == f"api/v9/content/draft/clients/{mock_api_service.client_id}/sites/site-123"
        assert "features" in args2[2]
        assert args2[2]["features"][0]["properties"]["extra"] == extra_data
