import logging
import json
import time
from typing import Dict, Any, Optional
import requests

from pointr_cloud_common.api.mapscale_token_service import (
    get_access_token,
    refresh_access_token,
)
from pointr_cloud_common.api.v9.base_service import V9ApiError


class MapscaleV9ApiService:
    """Service for interacting with Mapscale V9 API."""

    def __init__(
        self,
        config: Dict[str, str],
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        self.base_url = config["api_url"]
        self.client_id = config["client_identifier"]
        self.config = config
        self.logger = logging.getLogger(__name__)

        if token:
            self.token = token
        elif refresh_token:
            token_data = refresh_access_token(
                api_url=self.base_url,
                client_id=self.client_id,
                refresh_token=refresh_token,
            )
            self.token = token_data["access_token"]
        else:
            token_data = get_access_token(
                api_url=self.base_url,
                username=config["username"],
                password=config["password"],
            )
            self.token = token_data["access_token"]

    def _make_request(
        self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        start_time = time.time()
        operation_name = f"{method} {endpoint}"

        try:
            method_upper = method.upper()
            if method_upper == "GET":
                response = requests.get(url, headers=headers)
            elif method_upper in {"POST", "PUT", "PATCH"}:
                request_fn = {
                    "POST": requests.post,
                    "PUT": requests.put,
                    "PATCH": requests.patch,
                }[method_upper]
                response = request_fn(url, headers=headers, json=json_data)
            elif method_upper == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            duration = time.time() - start_time
            self.logger.debug(
                f"Mapscale API {operation_name} completed in {duration:.2f}s"
            )

            if not response.ok:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_details = response.json()
                    if isinstance(error_details, dict):
                        if "message" in error_details:
                            error_msg += f", message: {error_details['message']}"
                        elif "error" in error_details:
                            error_msg += f", error: {error_details['error']}"
                        else:
                            error_msg += f", details: {error_details}"
                    else:
                        error_msg += f", details: {error_details}"
                except Exception:
                    error_msg += f", response: {response.text[:200]}"
                raise V9ApiError(
                    error_msg,
                    status_code=response.status_code,
                    response_text=response.text,
                )

            try:
                return response.json()
            except json.JSONDecodeError:
                if response.text.strip():
                    self.logger.warning(
                        f"Non-JSON response from Mapscale API: {response.text[:200]}"
                    )
                return {}

        except requests.RequestException as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Mapscale API {operation_name} failed after {duration:.2f}s: {str(e)}"
            )
            raise V9ApiError(f"Request error: {str(e)}")

    # Example helper methods
    def get_health(self) -> Dict[str, Any]:
        return self._make_request("GET", "api/v9/mapscale/health")

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "api/v9/mapscale/auth/users", user_data)

    def update_user(self, user_identifier: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/auth/users/{user_identifier}"
        return self._make_request("PUT", endpoint, user_data)

    def get_client_configurations(self) -> Dict[str, Any]:
        return self._make_request("GET", "api/v9/mapscale/client-configurations")

    def get_client_configuration(self, client_identifier: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/client-configurations/{client_identifier}"
        return self._make_request("GET", endpoint)

    def create_client_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "api/v9/mapscale/client-configurations", config_data)

    def update_client_configuration(self, client_identifier: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/client-configurations/{client_identifier}"
        return self._make_request("PUT", endpoint, config_data)

    def delete_client_configuration(self, client_identifier: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/client-configurations/{client_identifier}"
        return self._make_request("DELETE", endpoint)

    def get_engine_configurations(self) -> Dict[str, Any]:
        return self._make_request("GET", "api/v9/mapscale/engine-configurations")

    def create_engine_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "api/v9/mapscale/engine-configurations", config_data)

    def update_engine_configuration(self, configuration_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/engine-configurations/{configuration_id}"
        return self._make_request("PUT", endpoint, config_data)

    def delete_engine_configuration(self, configuration_id: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/engine-configurations/{configuration_id}"
        return self._make_request("DELETE", endpoint)

    def create_floor_plan_job(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs"
        )
        return self._make_request("POST", endpoint, job_data)

    def get_floor_plan_job(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}"
        )
        return self._make_request("GET", endpoint)

    def list_level_floor_plan_jobs(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        skip: Optional[int] = None,
        take: Optional[int] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs"
        )
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def list_building_floor_plan_jobs(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        skip: Optional[int] = None,
        take: Optional[int] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/floor-plan-jobs"
        )
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def list_site_floor_plan_jobs(
        self,
        client_identifier: str,
        site_identifier: str,
        skip: Optional[int] = None,
        take: Optional[int] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/floor-plan-jobs"
        )
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def list_client_floor_plan_jobs(
        self,
        client_identifier: str,
        skip: Optional[int] = None,
        take: Optional[int] = None,
    ) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs"
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def list_floor_plan_jobs(self, skip: Optional[int] = None, take: Optional[int] = None) -> Dict[str, Any]:
        endpoint = "api/v9/mapscale/floor-plan-jobs"
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def approve_floor_plan_job(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/approve"
        )
        return self._make_request("POST", endpoint, data)

    def cancel_floor_plan_job(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/cancel"
        )
        return self._make_request("POST", endpoint, data)

    def decline_floor_plan_job(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/decline"
        )
        return self._make_request("POST", endpoint, data)

    def download_original_floor_plan(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/original-floor-plan"
        )
        return self._make_request("GET", endpoint)

    def update_floor_plan_job_content(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/update-content"
        )
        return self._make_request("POST", endpoint, data)

    def upload_cad_file(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        file_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/upload-cad-file"
        )
        return self._make_request("POST", endpoint, file_data)

    def upload_geojson(
        self,
        client_identifier: str,
        site_identifier: str,
        building_identifier: str,
        level_index: int,
        job_identifier: str,
        geojson_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        endpoint = (
            f"api/v9/mapscale/clients/{client_identifier}/sites/{site_identifier}/"
            f"buildings/{building_identifier}/levels/{level_index}/floor-plan-jobs/{job_identifier}/upload-geojson"
        )
        return self._make_request("POST", endpoint, geojson_data)

    def create_webhook_configuration(self, client_identifier: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/configurations/webhooks"
        return self._make_request("POST", endpoint, webhook_data)

    def list_webhook_configurations(self, client_identifier: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/configurations/webhooks"
        return self._make_request("GET", endpoint)

    def get_webhook_configuration(self, client_identifier: str, identifier: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/configurations/webhooks/{identifier}"
        return self._make_request("GET", endpoint)

    def update_webhook_configuration(self, client_identifier: str, identifier: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/configurations/webhooks/{identifier}"
        return self._make_request("PUT", endpoint, webhook_data)

    def delete_webhook_configuration(self, client_identifier: str, identifier: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/configurations/webhooks/{identifier}"
        return self._make_request("DELETE", endpoint)

    def list_webhooks(self, client_identifier: str, skip: Optional[int] = None, take: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/webhooks"
        params = []
        if skip is not None:
            params.append(f"skip={skip}")
        if take is not None:
            params.append(f"take={take}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._make_request("GET", endpoint)

    def resend_webhook(self, client_identifier: str, webhook_log_id: str) -> Dict[str, Any]:
        endpoint = f"api/v9/mapscale/clients/{client_identifier}/floor-plan-jobs/webhooks/resend/{webhook_log_id}"
        return self._make_request("POST", endpoint)