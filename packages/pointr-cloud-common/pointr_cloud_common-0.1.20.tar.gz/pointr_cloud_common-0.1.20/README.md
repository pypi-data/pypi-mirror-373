# pointr_cloud_common

Shared Python library containing API clients and utilities for Pointr Cloud services.

## Installation

```bash
uv pip install pointr-cloud-common
```

## Modules

### pointr_cloud_common.api.v9.v9_api_service.V9ApiService

High level client for the Mapscale V9 API. Create an instance with a configuration dictionary containing:

```python
{
    "api_url": "https://mras.example.com",
    "client_identifier": "my-client",
    "username": "user",
    "password": "pass",
}
```

Alternatively, you can authenticate using existing tokens:

```
# Using an access token
config = {"api_url": "https://..-api.pointr.cloud", "client_identifier": "my-client"}
service = V9ApiService(config, token="your_access_token")

# Using a refresh token
service = V9ApiService(config, refresh_token="your_refresh_token")

# With user email for logging
service = V9ApiService(config, token="your_access_token", user_email="user@example.com")
```

The service authenticates and exposes helpers via sub services (`site_service`, `building_service`, `level_service`, `sdk_service`, `client_service`, and `poi_service`).

#### Methods

```python
get_sites() -> List[SiteDTO]
create_site(site: SiteDTO, source_api_service=None) -> str
update_site(site_id: str, site: SiteDTO, source_api_service=None) -> str
update_site_extra_data(site_fid: str, extra_data: dict) -> bool
get_site_by_fid(site_fid: str) -> SiteDTO
get_buildings(site_fid: str) -> List[BuildingDTO]
get_building_by_fid(site_fid: str, building_fid: str) -> BuildingDTO
create_building(site_fid: str, building: BuildingDTO, source_api_service=None) -> str
update_building(site_fid: str, building_fid: str, building: BuildingDTO, source_api_service=None) -> str
update_building_extra_data(site_fid: str, building_fid: str, extra_data: dict) -> bool
get_levels(site_fid: str, building_fid: str) -> List[LevelDTO]
get_level_by_id(site_fid: str, building_fid: str, level_id: str) -> LevelDTO
create_level(site_fid: str, building_fid: str, level: dict) -> str
update_level(site_fid: str, building_fid: str, level_id: str, level: dict) -> str
delete_level(site_fid: str, building_fid: str, level_id: str) -> bool
get_client_metadata() -> ClientMetadataDTO
update_client(client_id: str, client_data: dict) -> bool
create_client(client_data: dict) -> str
get_client_sdk_config() -> List[SdkConfigurationDTO]
get_site_sdk_config(site_fid: str) -> List[SdkConfigurationDTO]
get_building_sdk_config(site_fid: str, building_fid: str) -> List[SdkConfigurationDTO]
get_client_gps_geofences() -> list[dict]
put_global_sdk_configurations(configs: List[SdkConfigurationDTO]) -> bool
put_site_sdk_configurations(site_fid: str, configs: List[SdkConfigurationDTO]) -> bool
put_building_sdk_configurations(site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]) -> bool
get_site_pois(site_fid: str, published: bool = False) -> Dict[str, Any]
create_site_pois(site_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]
delete_site_pois(site_fid: str) -> bool
get_building_pois(site_fid: str, building_fid: str) -> Dict[str, Any]
create_building_pois(site_fid: str, building_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]
delete_building_pois(site_fid: str, building_fid: str) -> bool
get_level_pois(site_fid: str, building_fid: str, level_fid: str) -> Dict[str, Any]
create_level_pois(site_fid: str, building_fid: str, level_fid: str, pois: Dict[str, Any]) -> Dict[str, Any]
delete_level_pois(site_fid: str, building_fid: str, level_fid: str) -> bool
get_site_pois_excel(site_fid: str, published: bool = False) -> str
get_building_pois_excel(site_fid: str, building_fid: str) -> str
```

### pointr_cloud_common.api.mapscale_v9_service.MapscaleV9ApiService

Wrapper for Mapscale specific endpoints. Notable methods include:

```python
get_health() -> dict
create_user(user_data: dict) -> dict
update_user(user_identifier: str, user_data: dict) -> dict
get_client_configurations() -> dict
get_client_configuration(client_identifier: str) -> dict
create_client_configuration(config_data: dict) -> dict
update_client_configuration(client_identifier: str, config_data: dict) -> dict
delete_client_configuration(client_identifier: str) -> dict
get_engine_configurations() -> dict
create_engine_configuration(config_data: dict) -> dict
update_engine_configuration(configuration_id: str, config_data: dict) -> dict
delete_engine_configuration(configuration_id: str) -> dict
create_floor_plan_job(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_data: dict) -> dict
get_floor_plan_job(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str) -> dict
list_level_floor_plan_jobs(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, skip=None, take=None) -> dict
list_building_floor_plan_jobs(client_identifier: str, site_identifier: str, building_identifier: str, skip=None, take=None) -> dict
list_site_floor_plan_jobs(client_identifier: str, site_identifier: str, skip=None, take=None) -> dict
list_client_floor_plan_jobs(client_identifier: str, skip=None, take=None) -> dict
list_floor_plan_jobs(skip=None, take=None) -> dict
approve_floor_plan_job(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, data=None) -> dict
cancel_floor_plan_job(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, data=None) -> dict
decline_floor_plan_job(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, data=None) -> dict
download_original_floor_plan(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str) -> dict
update_floor_plan_job_content(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, data: dict) -> dict
upload_cad_file(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, file_data: dict) -> dict
upload_geojson(client_identifier: str, site_identifier: str, building_identifier: str, level_index: int, job_identifier: str, geojson_data: dict) -> dict
create_webhook_configuration(client_identifier: str, webhook_data: dict) -> dict
list_webhook_configurations(client_identifier: str) -> dict
get_webhook_configuration(client_identifier: str, identifier: str) -> dict
update_webhook_configuration(client_identifier: str, identifier: str, webhook_data: dict) -> dict
delete_webhook_configuration(client_identifier: str, identifier: str) -> dict
list_webhooks(client_identifier: str, skip=None, take=None) -> dict
resend_webhook(client_identifier: str, webhook_log_id: str) -> dict
```

Each method wraps the corresponding HTTP endpoint and returns the decoded JSON response.

### pointr_cloud_common.api.mapscale_token_service

```python
get_access_token(api_url: str, username: str, password: str) -> dict
refresh_access_token(api_url: str, client_id: str, refresh_token: str) -> dict
```

Helpers for acquiring and refreshing Mapscale authentication tokens.

### pointr_cloud_common.api.v9.environment_token_service

```python
get_access_token(client_id: str, api_url: str, username: str, password: str) -> dict
refresh_access_token(client_id: str, api_url: str, refresh_token: str) -> dict
is_token_valid(token_data: dict) -> bool
```

Helpers for acquiring and validating V9 tokens.

### pointr_cloud_common.api.v8.v8_api_service.V8ApiService

Entry point for interacting with the V8 API. Create an instance with a configuration dictionary containing:

```python
{
    "api_url": "https://api.example.com",
    "client_identifier": "my-client",
    "username": "user",
    "password": "pass",
}
```

Alternatively, you can authenticate using existing tokens:

```python
# Using an access token
config = {"api_url": "https://api.example.com", "client_identifier": "my-client"}
service = V8ApiService(config, token="your_access_token")

# Using a refresh token
service = V8ApiService(config, refresh_token="your_refresh_token")

# With user email for logging
service = V8ApiService(config, token="your_access_token", user_email="user@example.com")
```

The service authenticates and exposes helpers via sub services (`site_service`, `building_service`, `level_service`, `sdk_service`, `client_service`, `feature_service`, and `poi_service`).

#### Methods

```python
get_sites() -> List[SiteDTO]
get_site_by_fid(site_fid: str) -> SiteDTO
create_site(site: SiteDTO, source_api_service: Optional[Any] = None) -> str
update_site(site_id: str, site: SiteDTO, source_api_service: Optional[Any] = None) -> str
update_site_extra_data(site_fid: str, extra_data: dict) -> bool
get_buildings(site_fid: str) -> List[BuildingDTO]
get_building_by_fid(site_fid: str, building_fid: str) -> BuildingDTO
create_building(site_fid: str, building: BuildingDTO, source_api_service: Optional[Any] = None) -> str
update_building(site_fid: str, building_fid: str, building: BuildingDTO, source_api_service: Optional[Any] = None) -> str
update_building_extra_data(site_fid: str, building_fid: str, extra_data: dict) -> bool
get_levels(site_fid: str, building_fid: str) -> List[LevelDTO]
get_level_by_id(site_fid: str, building_fid: str, level_id: str) -> LevelDTO
create_level(site_fid: str, building_fid: str, level: dict) -> str
update_level(site_fid: str, building_fid: str, level_id: str, level: dict) -> str
delete_level(site_fid: str, building_fid: str, level_id: str) -> bool
get_client_metadata() -> ClientMetadataDTO
update_client(client_id: str, client_data: dict) -> bool
create_client(client_data: dict) -> str
get_client_gps_geofences() -> List[Dict[str, Any]]
get_client_sdk_config() -> List[SdkConfigurationDTO]
get_site_sdk_config(site_fid: str) -> List[SdkConfigurationDTO]
get_building_sdk_config(site_fid: str, building_fid: str) -> List[SdkConfigurationDTO]
put_global_sdk_configurations(configs: List[SdkConfigurationDTO]) -> bool
put_site_sdk_configurations(site_fid: str, configs: List[SdkConfigurationDTO]) -> bool
put_building_sdk_configurations(site_fid: str, building_fid: str, configs: List[SdkConfigurationDTO]) -> bool
get_building_features(building_id: str) -> Dict[str, Any]
get_building_features_by_type(building_id: str, type_code: str) -> Dict[str, Any]
get_level_features(building_id: str, level_index: str) -> Dict[str, Any]
get_level_features_by_type(building_id: str, level_index: str, type_code: str) -> Dict[str, Any]
get_site_features(site_id: str) -> Dict[str, Any]
get_site_features_by_type(site_id: str, type_code: str) -> Dict[str, Any]
create_or_update_building_features(site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]
create_or_update_level_features(building_id: str, level_index: str, features: Dict[str, Any]) -> Dict[str, Any]
create_or_update_site_features(site_id: str, features: Dict[str, Any]) -> Dict[str, Any]
delete_building_features(site_id: str, building_id: str) -> bool
delete_building_features_by_type(building_id: str, type_code: str) -> bool
delete_level_features(building_id: str, level_index: str) -> bool
delete_level_features_by_type(building_id: str, level_index: str, type_code: str) -> bool
delete_site_features(site_id: str) -> bool
delete_site_features_by_type(site_id: str, type_code: str) -> bool
get_feature_by_id(feature_id: str) -> Dict[str, Any]
create_or_update_feature(feature: Dict[str, Any]) -> Dict[str, Any]
delete_feature(feature_id: str) -> bool
get_all_building_features_by_level(site_id: str, building_id: str) -> Dict[str, Any]
migrate_building_features(source_site_id: str, source_building_id: str, target_site_id: str, target_building_id: str, feature_types: Optional[List[str]] = None) -> Dict[str, Any]
get_level_pois(building_fid: str, level_index: str) -> Dict[str, Any]
delete_level_pois(building_fid: str, level_index: str) -> bool
get_site_pois(site_fid: str) -> Dict[str, Any]
delete_site_pois(site_fid: str) -> bool
get_site_pois_draft(site_fid: str) -> Dict[str, Any]
get_level_pois_draft(building_fid: str, level_index: str) -> Dict[str, Any]
delete_building_pois(building_fid: str) -> bool
get_site_pois_excel(site_fid: str) -> None
get_building_pois_excel(building_fid: str) -> None
```

### pointr_cloud_common.api.v8.environment_token_service

```python
get_access_token(api_url: str, username: str, password: str) -> dict
refresh_access_token(api_url: str, refresh_token: str) -> dict
```

Helpers for acquiring V8 tokens.

### Utilities

#### pointr_cloud_common.utils.google_auth

```python
authenticate(config: Dict[str, str], env: str = "Prod") -> dict
exchange_code_for_token(config: Dict[str, str], auth_code: str) -> dict
get_user_info(access_token: str) -> dict
```

#### pointr_cloud_common.utils.jira_service

```python
class JiraService:
    create_issue(payload: Dict[str, Any]) -> str
    search_issues(jql: str) -> list[Dict[str, Any]]
    get_user_account_id(email: str) -> str | None

create_jira_issue(service: JiraService, payload: Dict[str, Any]) -> str
search_issues(config: Dict[str, str], jql: str) -> list[Dict[str, Any]]
```

#### pointr_cloud_common.utils.pointr_git_helper

```python
class PointrGitHelper:
    clone_repo(repo_url: str, local_folder: str) -> None
    pull_repo(local_folder: str) -> None
    sync_repo(repo_name: str, data_folder: str = "data/") -> None

cloneRepo(config: Dict[str, str], repo_url: str, local_folder: str) -> None
pullRepo(config: Dict[str, str], local_folder: str) -> None
syncRepo(config: Dict[str, str], repo_name: str) -> None
```

#### pointr_cloud_common.utils.pointr_access_right_helper

```python
class PointrAccessRightHelper:
    get_app_access_rights(app_name: str, email_address: str) -> Dict[str, Any]

get_app_access_rights(config: Dict[str, str], app_name: str, email_address: str) -> Dict[str, Any]
```

#### pointr_cloud_common.utils.pointr_jira_helper

```python
searchJiraIssues(jql: str, fields: str = "key,summary,description", loadComments: bool = False) -> list
extract_text_from_json(json_obj) -> str
createJiraFiles(issues: list) -> None
getJiraWorklogs(issue) -> list
getJiraComments(key: str) -> list
```

#### pointr_cloud_common.helpers.poi_excel_service_base

```python
class PoiExcelServiceBase:
    _get_excel_headers() -> list
    _process_poi_to_row(feature: Dict[str, Any]) -> list
    _convert_to_excel_csv(poi_data: Dict[str, Any]) -> str
```

#### Other helpers

```python
extract_client_fromJiraSummary(title, jiraProject) -> str
generate_timelog_report(jql, columns, employeeList) -> list
convertJiraDateToGMTTimeZone(inputDate: str, dateformat: str = date_format) -> datetime | None
get_connection(connectionString: str) -> pyodbc.Connection
get_smartsheet_as_dataframe(token: str, sheet_id: str) -> pandas.DataFrame
filter_environments(df: pandas.DataFrame, version_value: str, version_column: str, is_active_column: str, dashboard_version_column: str, client_name_column: str, environment_name_column: str, api_endpoint_column: str, client_id_column: str, client_secret_column: str, min_dashboard_version: str = None, version_compare_func=_version_gte) -> list[dict]
```
