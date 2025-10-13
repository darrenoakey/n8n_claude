import pytest
from n8n_client import N8nConfig, N8nClient, N8nWorkflows, N8nOutput


# ##################################################################
# test get api key
# verify api key retrieval from keyring fails when missing or succeeds
def test_get_api_key():
    # this will either succeed or fail naturally based on keyring state
    # we do not stub or fake keyring access
    try:
        api_key = N8nConfig.get_api_key()
        assert api_key is not None
        assert len(api_key) > 0
    except RuntimeError as err:
        # expected failure when key not in keyring
        assert "Missing secret" in str(err)


# ##################################################################
# test get headers
# verify headers contain required authentication and content type
def test_get_headers():
    try:
        headers = N8nClient.get_headers()
        assert "X-N8N-API-KEY" in headers
        assert "Accept" in headers
        assert "Content-Type" in headers
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"
    except RuntimeError:
        # expected failure when key not in keyring
        pytest.skip("API key not available in keyring")


# ##################################################################
# test list workflows
# real integration test to list workflows from n8n instance
def test_list_workflows():
    try:
        result = N8nWorkflows.list_workflows()
        assert result is not None
        assert "data" in result
        workflows = result["data"]
        assert isinstance(workflows, list)
    except RuntimeError as err:
        # expected failure when credentials missing or network unavailable
        pytest.skip(f"Cannot connect to n8n: {err}")


# ##################################################################
# test format workflow summary
# verify workflow summary formatting with sample data
def test_format_workflow_summary():
    workflow = {
        "id": "123",
        "name": "Test Workflow",
        "active": True
    }
    summary = N8nOutput.format_workflow_summary(workflow)
    assert "[123]" in summary
    assert "Test Workflow" in summary
    assert "active" in summary


# ##################################################################
# test format workflow list empty
# verify empty workflow list formatting
def test_format_workflow_list_empty():
    result = N8nOutput.format_workflow_list([])
    assert result == "No workflows found"


# ##################################################################
# test format workflow list with workflows
# verify workflow list formatting with sample data
def test_format_workflow_list_with_workflows():
    workflows = [
        {"id": "1", "name": "Flow One", "active": True},
        {"id": "2", "name": "Flow Two", "active": False}
    ]
    result = N8nOutput.format_workflow_list(workflows)
    assert "[1]" in result
    assert "Flow One" in result
    assert "[2]" in result
    assert "Flow Two" in result
