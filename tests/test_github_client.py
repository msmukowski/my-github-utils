from unittest.mock import patch, MagicMock

import pytest

from gh_utils.exceptions import GitHubAPIError
from gh_utils.github_client import create_issue, add_to_project, find_project_id_by_title


@pytest.fixture
def ok_response():
    """Factory for a successful API response."""
    def _make(json_data):
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = json_data
        return resp
    return _make


@pytest.fixture
def error_response():
    """Factory for a failed API response."""
    def _make(status_code, reason="Error", text=""):
        resp = MagicMock()
        resp.ok = False
        resp.status_code = status_code
        resp.reason = reason
        resp.text = text
        return resp
    return _make


########## Test Create Issue


def test_create_issue_successfully(ok_response):
    response = ok_response({
        "number": 42,
        "html_url": "https://github.com/owner/repo/issues/42",
        "node_id": "I_abc123",
    })

    with patch("gh_utils.github_client.requests.post", return_value=response) as mock_post:
        result = create_issue(
            token="ghp_test", owner="owner", repo="repo",
            title="Test issue", body="Issue body", labels=["bug"],
        )

    mock_post.assert_called_once()
    payload = mock_post.call_args.kwargs["json"]
    assert payload["title"] == "Test issue"
    assert payload["body"] == "Issue body"
    assert payload["labels"] == ["bug"]
    assert result["number"] == 42


def test_create_issue_without_labels(ok_response):
    response = ok_response({"number": 1, "html_url": "url", "node_id": "id"})

    with patch("gh_utils.github_client.requests.post", return_value=response) as mock_post:
        create_issue(token="ghp_test", owner="o", repo="r", title="T", body="B")

    payload = mock_post.call_args.kwargs["json"]
    assert "labels" not in payload


def test_create_issue_raises_on_api_error(error_response):
    response = error_response(422, "Unprocessable Entity", '{"message": "Validation Failed"}')

    with patch("gh_utils.github_client.requests.post", return_value=response):
        with pytest.raises(GitHubAPIError, match="422") as exc_info:
            create_issue(token="t", owner="o", repo="r", title="T", body="B")

    assert exc_info.value.status_code == 422


########## Test Find Project ID by Title


def test_find_project_id_by_title(ok_response):
    response = ok_response({
        "data": {
            "organization": {
                "projectsV2": {
                    "nodes": [
                        {"id": "PVT_aaa", "title": "Other Board"},
                        {"id": "PVT_bbb", "title": "My Board"},
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
    })

    with patch("gh_utils.github_client.requests.post", return_value=response):
        result = find_project_id_by_title(token="ghp_test", owner="myorg", title="My Board")

    assert result == "PVT_bbb"


def test_find_project_id_by_title_not_found(ok_response):
    response = ok_response({
        "data": {
            "organization": {
                "projectsV2": {
                    "nodes": [{"id": "PVT_aaa", "title": "Other Board"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
    })

    with patch("gh_utils.github_client.requests.post", return_value=response):
        with pytest.raises(GitHubAPIError, match="not found"):
            find_project_id_by_title(token="ghp_test", owner="myorg", title="Nope")


########## Test Add to project


def test_add_to_project_successfully(ok_response):
    response = ok_response({
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_123"}}}
    })

    with patch("gh_utils.github_client.requests.post", return_value=response) as mock_post:
        result = add_to_project(token="ghp_test", project_id="PVT_abc", issue_node_id="I_xyz")

    mock_post.assert_called_once()
    payload = mock_post.call_args.kwargs["json"]
    assert payload["variables"]["projectId"] == "PVT_abc"
    assert payload["variables"]["contentId"] == "I_xyz"
    assert result["data"]["addProjectV2ItemById"]["item"]["id"] == "PVTI_123"


def test_add_to_project_raises_on_graphql_error(ok_response):
    response = ok_response({
        "errors": [{"message": "Could not resolve to a ProjectV2"}]
    })

    with patch("gh_utils.github_client.requests.post", return_value=response):
        with pytest.raises(GitHubAPIError, match="GraphQL error"):
            add_to_project(token="t", project_id="bad", issue_node_id="I_x")


def test_add_to_project_raises_on_http_error(error_response):
    response = error_response(401, "Unauthorized", "Bad credentials")

    with patch("gh_utils.github_client.requests.post", return_value=response):
        with pytest.raises(GitHubAPIError, match="401"):
            add_to_project(token="bad", project_id="p", issue_node_id="i")
