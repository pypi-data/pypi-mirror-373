from typing import Dict, Any, Optional
import logging
import requests
import json
import time


class V9ApiError(Exception):
    """Exception raised for V9 API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class BaseApiService:
    """Base class for all V9 API services."""
    
    def __init__(self, api_service):
        """
        Initialize the base API service.
        
        Args:
            api_service: The parent V9ApiService instance
        """
        self.api_service = api_service
        self.base_url = api_service.base_url
        self.client_id = api_service.client_id
        self.user_email = api_service.user_email
        self.token = api_service.token
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the API."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        start_time = time.time()
        operation_name = f"{method} {endpoint}"
        
        try:
            self.logger.info(f"Making {operation_name} request to {url}")
            
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
            self.logger.info(f"API operation {operation_name} completed in {duration:.2f}s")
            
            # Log the full response for debugging
            self.logger.info(f"Raw API response for {operation_name}: {response.text}")
            
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
                except:
                    error_msg += f", response: {response.text[:200]}"
                
                self.logger.error(f"{error_msg} for {operation_name}")
                raise V9ApiError(
                    error_msg, 
                    status_code=response.status_code, 
                    response_text=response.text
                )
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # If the response is not JSON, return an empty dict
                if response.text.strip():
                    self.logger.warning(f"Non-JSON response from API: {response.text[:200]}")
                return {}
            
        except requests.RequestException as e:
            # Log the operation failure
            duration = time.time() - start_time
            self.logger.error(f"API operation {operation_name} failed after {duration:.2f}s: {str(e)}")
            raise V9ApiError(f"Request error: {str(e)}")
