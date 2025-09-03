from typing import Dict, Any, List, Optional
import logging
import json

from pointr_cloud_common.dto.v9 import SiteDTO, BuildingDTO, LevelDTO
from pointr_cloud_common.dto.v9.validation import ensure_dict, ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


DEFAULT_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[0.0, 0.0], [0.0, 0.001], [0.001, 0.001], [0.001, 0.0], [0.0, 0.0]]],
}


class SiteApiService(BaseApiService):
    """Service for site-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _fetch_source_geometry(self, fid: str, source_api_service: Any) -> Optional[Dict[str, Any]]:
        """Fetch geometry for the given site fid from the source API service."""
        try:
            data = source_api_service._make_request("GET", f"api/v8/sites/{fid}/draft")
            result = data.get("result", data)
            geometry = result.get("geometry")
            if geometry:
                self.logger.info(f"Successfully retrieved geometry for site {fid} from source API")
                return geometry
            self.logger.warning(f"No geometry found for site {fid} in source API")
        except Exception as e:
            self.logger.error(f"Failed to retrieve geometry for site {fid} from source API: {str(e)}")
        return None

    def _to_site_dto(self, data: Dict[str, Any]) -> SiteDTO:
        """Convert a raw V8 API site object into a SiteDTO."""

        # Parse nested buildings if present.  The `/clients/{id}/sites` endpoint
        # may include a ``buildings`` array with level information.  We mirror
        # the logic from ``BuildingApiService._building_from_v8`` here instead
        # of importing the service to keep this method self-contained.

        site_fid = str(data.get("siteInternalIdentifier"))
        buildings: List[BuildingDTO] = []
        for b in data.get("buildings", []):
            levels: List[LevelDTO] = []
            for l in b.get("levels", []):
                try:
                    level_dto = LevelDTO(
                        fid=str(l.get("levelIndex")),
                        name=l.get("levelLongTitle", ""),
                        shortName=l.get("levelShortTitle"),
                        levelNumber=l.get("levelIndex"),
                        typeCode="level-outline",
                        sid=site_fid,
                        bid=str(b.get("buildingInternalIdentifier")),
                    )
                    levels.append(level_dto)
                except ValidationError as e:
                    self.logger.error(f"Failed to parse level: {str(e)}")
                    raise V8ApiError(f"Failed to parse level: {str(e)}")

            try:
                building_dto = BuildingDTO(
                    fid=str(b.get("buildingInternalIdentifier")),
                    name=b.get("buildingTitle", ""),
                    typeCode="building-outline",
                    sid=site_fid,
                    bid=b.get("buildingExternalIdentifier"),
                    extraData=ensure_dict(b.get("buildingExtraData"), "buildingExtraData"),
                    levels=levels,
                )
                buildings.append(building_dto)
            except ValidationError as e:
                self.logger.error(f"Failed to parse building: {str(e)}")
                raise V8ApiError(f"Failed to parse building: {str(e)}")

        try:
            return SiteDTO(
                fid=site_fid,
                name=data.get("siteTitle", ""),
                typeCode="site-outline",
                sid=data.get("siteExternalIdentifier"),
                extraData=ensure_dict(data.get("siteExtraData"), "siteExtraData"),
                buildings=buildings,
            )
        except ValidationError as e:
            self.logger.error(f"Failed to parse site: {str(e)}")
            raise V8ApiError(f"Failed to parse site: {str(e)}")

    def get_sites(self) -> List[SiteDTO]:
        endpoint = f"api/v8/clients/{self.client_id}/sites/draft"
        self.logger.info(f"Making V8 API call to get sites: {endpoint}")
        data = self._make_request("GET", endpoint)
        self.logger.info(f"Raw V8 API response for sites: {data}")
        
        results = data.get("result", {}).get("sites", []) if isinstance(data, dict) else []
        self.logger.info(f"Found {len(results)} sites in V8 API response")
        
        sites = [self._to_site_dto(item) for item in results]
        self.logger.info(f"Converted {len(sites)} sites to DTOs")

        for site in sites:
            try:
                buildings = self.api_service.building_service.get_buildings(site.fid)
                site.buildings = buildings
                self.logger.info(
                    f"Attached {len(buildings)} buildings to site {site.fid}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to fetch buildings for site {site.fid}: {str(e)}"
                )

        return sites

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        endpoint = f"api/v8/sites/{site_fid}/draft"
        data = self._make_request("GET", endpoint)
        site_data = data.get("result", data)
        try:
            site = self._to_site_dto(site_data)
            return site
        except Exception as e:
            raise

    def create_site(self, site: SiteDTO, source_api_service: Optional[Any] = None) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(site.fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "siteTitle": site.name,
            "siteExternalIdentifier": site.sid,
            "siteExtraData": site.extraData,
            "geometry": geometry,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        endpoint = f"api/v8/clients/{self.client_id}/sites"
        data = self._make_request("POST", endpoint, payload)
        return str(data.get("result", {}).get("siteInternalIdentifier", ""))

    def update_site(self, site_id: str, site: SiteDTO, source_api_service: Optional[Any] = None) -> str:
        endpoint = f"api/v8/sites/{site_id}"
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(site.fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "siteTitle": site.name,
            "siteExternalIdentifier": site.sid,
            "siteExtraData": site.extraData,
            "geometry": geometry,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            self._make_request("PATCH", endpoint, payload)
        except Exception as e:
            raise
        return site_id

    def update_site_extra_data(self, site_fid: str, extra_data: Dict[str, Any]) -> bool:
        try:
            # Get the current site to retrieve the title
            current_site = self.get_site_by_fid(site_fid)
            payload = {
                "siteTitle": current_site.name,
                "siteExtraData": extra_data
            }
            endpoint = f"api/v8/sites/{site_fid}"
            self._make_request("PATCH", endpoint, payload)
            return True
        except Exception as e:
            self.logger.error(f"Error updating site extra data for {site_fid}: {str(e)}")
            raise
