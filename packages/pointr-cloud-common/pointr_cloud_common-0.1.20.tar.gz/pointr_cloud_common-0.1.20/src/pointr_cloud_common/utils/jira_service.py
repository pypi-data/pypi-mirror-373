import logging
from typing import Dict, Any
import requests
from requests.auth import HTTPBasicAuth


class JiraService:
    """Minimal Jira REST service."""

    def __init__(self, config: Dict[str, str]) -> None:
        self.base_url = config["jira_url"].rstrip("/")
        self.user = config["user"]
        self.token = config["token"]
        self.auth = HTTPBasicAuth(self.user, self.token)
        self.logger = logging.getLogger(__name__)

    def create_issue(
        self,
        summary: str,
        description: str = "",
        project: str = "MAP",
        issue_type: str = "Task",
        fields: Dict[str, Any] | None = None,
    ) -> str:
        """Create a Jira issue and return its key."""
        issue_fields = {
            "summary": summary or "No summary",
            "project": {"key": project or "DEMO"},
            "issuetype": {"name": issue_type},
            "description": description or "",
        }
        if fields:
            issue_fields.update(fields)

        issue_data = {"fields": issue_fields}
        


        headers = {"Accept": "application/json"}
        response = requests.post(
            f"{self.base_url}/rest/api/2/issue",
            json=issue_data,
            auth=self.auth,
            headers=headers,
        )
        if response.status_code not in (200, 201):
            self.logger.error(f"Jira API error: {response.text}")
            raise Exception(f"Jira API error: {response.text}")
        
        data: Dict[str, Any] = response.json()
        return data.get("key", "")

    def search_issues(self, jql: str) -> list[Dict[str, Any]]:
        """Search Jira issues using JQL and return the list of matching issues."""
        headers = {"Accept": "application/json"}
        response = requests.get(
            f"{self.base_url}/rest/api/2/search",
            params={"jql": jql},
            auth=self.auth,
            headers=headers,
        )
        if response.status_code != 200:
            raise Exception(f"Jira API error: {response.text}")
        data: Dict[str, Any] = response.json()
        return data.get("issues", [])

    def get_user_account_id(self, email: str) -> str | None:
        """Return the Jira accountId for the given email address."""
        headers = {"Accept": "application/json"}
        response = requests.get(
            f"{self.base_url}/rest/api/3/user/search",
            params={"query": email},
            auth=self.auth,
            headers=headers,
        )
        if response.status_code != 200:
            self.logger.error("Jira API error: %s", response.text)
            return None
        try:
            users = response.json()
        except Exception as exc:  # pragma: no cover - unexpected JSON
            self.logger.error("Failed to parse Jira response: %s", exc)
            return None
        if isinstance(users, list) and users:
            return users[0].get("accountId")
        return None


def create_jira_issue(service: JiraService, payload: Dict[str, Any]) -> str:
    """Create a Jira issue describing a floorplan job webhook event."""
    job_id = payload.get("floorPlanJobId", "")
    summary = f"Floorplan job {payload.get('status', '')} {job_id}".strip()
    parts = [
        f"Operation: {payload.get('operationType')}",
        f"Status: {payload.get('status')}",
    ]
    result_url = payload.get("floorPlanJobResultUrl")
    if result_url:
        parts.append(f"Result: {result_url}")
    description = "\n".join(parts)
    return service.create_issue(
        summary=summary,
        description=description,
        project="MAP",
        issue_type="Task"
    )


def search_issues(config: Dict[str, str], jql: str) -> list[Dict[str, Any]]:
    """Legacy helper to search Jira issues using configuration."""
    service = JiraService(config)
    return service.search_issues(jql)
