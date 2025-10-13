import json
import keyring
import requests
from typing import Any


# ##################################################################
# n8n configuration
# centralized configuration for n8n instance and api access
class N8nConfig:
    API_PATH = "/api/v1"
    KEYRING_SERVICE = "n8n"
    KEYRING_API_KEY = "api_key"
    KEYRING_URL_KEY = "url"

    # ##################################################################
    # get api key
    # retrieve api key from system keyring with explicit failure
    @staticmethod
    def get_api_key() -> str:
        key = keyring.get_password(N8nConfig.KEYRING_SERVICE, N8nConfig.KEYRING_API_KEY)
        if not key:
            raise RuntimeError(f"Missing secret for {N8nConfig.KEYRING_SERVICE}/{N8nConfig.KEYRING_API_KEY}")
        return key

    # ##################################################################
    # get url
    # retrieve n8n instance url from system keyring with explicit failure
    @staticmethod
    def get_url() -> str:
        url = keyring.get_password(N8nConfig.KEYRING_SERVICE, N8nConfig.KEYRING_URL_KEY)
        if not url:
            raise RuntimeError(f"Missing secret for {N8nConfig.KEYRING_SERVICE}/{N8nConfig.KEYRING_URL_KEY}")
        return url

    # ##################################################################
    # get base url
    # construct full api base url
    @staticmethod
    def get_base_url() -> str:
        return f"{N8nConfig.get_url()}{N8nConfig.API_PATH}"


# ##################################################################
# n8n client
# stateless http operations for n8n api with standard headers
class N8nClient:

    # ##################################################################
    # get headers
    # construct authentication headers for n8n api requests
    @staticmethod
    def get_headers() -> dict[str, str]:
        return {
            "X-N8N-API-KEY": N8nConfig.get_api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    # ##################################################################
    # make request
    # centralized http request handler with error context
    @staticmethod
    def make_request(method: str, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{N8nConfig.get_base_url()}{endpoint}"
        headers = N8nClient.get_headers()

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, verify=False)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, verify=False)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, verify=False)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, verify=False)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, verify=False)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.text else {}

        except requests.exceptions.RequestException as err:
            error_detail = ""
            if hasattr(err, 'response') and err.response is not None:
                try:
                    error_detail = f" response_body={err.response.text}"
                except:
                    pass
            raise RuntimeError(f"API request failed method={method} url={url} err={err}{error_detail}")


# ##################################################################
# n8n workflows
# workflow management operations via n8n api
class N8nWorkflows:

    # ##################################################################
    # list workflows
    # retrieve all workflows from n8n instance
    @staticmethod
    def list_workflows() -> dict[str, Any]:
        return N8nClient.make_request("GET", "/workflows")

    # ##################################################################
    # get workflow
    # retrieve specific workflow by id
    @staticmethod
    def get_workflow(workflow_id: str) -> dict[str, Any]:
        return N8nClient.make_request("GET", f"/workflows/{workflow_id}")

    # ##################################################################
    # create workflow
    # create new workflow with provided definition
    @staticmethod
    def create_workflow(workflow_data: dict[str, Any]) -> dict[str, Any]:
        return N8nClient.make_request("POST", "/workflows", workflow_data)

    # ##################################################################
    # update workflow
    # update existing workflow by id with new definition
    @staticmethod
    def update_workflow(workflow_id: str, workflow_data: dict[str, Any]) -> dict[str, Any]:
        return N8nClient.make_request("PUT", f"/workflows/{workflow_id}", workflow_data)

    # ##################################################################
    # delete workflow
    # remove workflow by id
    @staticmethod
    def delete_workflow(workflow_id: str) -> dict[str, Any]:
        return N8nClient.make_request("DELETE", f"/workflows/{workflow_id}")


# ##################################################################
# n8n output
# formatting and display helpers for workflow data
class N8nOutput:

    # ##################################################################
    # format workflow summary
    # extract key fields for readable workflow list display
    @staticmethod
    def format_workflow_summary(workflow: dict[str, Any]) -> str:
        wf_id = workflow.get("id", "unknown")
        name = workflow.get("name", "unnamed")
        active = workflow.get("active", False)
        status = "active" if active else "inactive"
        return f"[{wf_id}] {name} ({status})"

    # ##################################################################
    # format workflow list
    # convert workflow list to readable summary lines
    @staticmethod
    def format_workflow_list(workflows: list[dict[str, Any]]) -> str:
        if not workflows:
            return "No workflows found"
        lines = [N8nOutput.format_workflow_summary(wf) for wf in workflows]
        return "\n".join(lines)

    # ##################################################################
    # format workflow detail
    # convert workflow to pretty printed json
    @staticmethod
    def format_workflow_detail(workflow: dict[str, Any]) -> str:
        return json.dumps(workflow, indent=2)
