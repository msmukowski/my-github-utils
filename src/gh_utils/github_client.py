import requests

from gh_utils.exceptions import GitHubAPIError

GITHUB_API_URL = "https://api.github.com"
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _handle_response(response: requests.Response) -> dict:
    if not response.ok:
        raise GitHubAPIError(
            f"GitHub API error: {response.status_code} {response.reason}",
            status_code=response.status_code,
            response_body=response.text,
        )
    return response.json()


def create_issue(
    token: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
    labels: list[str] | None = None,
) -> dict:
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues"
    payload: dict = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    response = requests.post(url, json=payload, headers=_auth_headers(token))
    return _handle_response(response)


def find_project_id_by_title(token: str, owner: str, title: str) -> str:
    query = """
    query($owner: String!, $cursor: String) {
      organization(login: $owner) {
        projectsV2(first: 100, after: $cursor) {
          nodes { id title }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
    """
    cursor = None
    while True:
        payload = {
            "query": query,
            "variables": {"owner": owner, "cursor": cursor},
        }
        response = requests.post(
            GITHUB_GRAPHQL_URL, json=payload, headers=_auth_headers(token)
        )
        data = _handle_response(response)

        if "errors" in data:
            error_messages = "; ".join(e["message"] for e in data["errors"])
            raise GitHubAPIError(f"GraphQL error: {error_messages}")

        projects = data["data"]["organization"]["projectsV2"]
        for node in projects["nodes"]:
            if node["title"] == title:
                return node["id"]

        if not projects["pageInfo"]["hasNextPage"]:
            break
        cursor = projects["pageInfo"]["endCursor"]

    raise GitHubAPIError(f"Project with title '{title}' not found in org '{owner}'")


def add_to_project(token: str, project_id: str, issue_node_id: str) -> dict:
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    payload = {
        "query": query,
        "variables": {
            "projectId": project_id,
            "contentId": issue_node_id,
        },
    }

    response = requests.post(
        GITHUB_GRAPHQL_URL, json=payload, headers=_auth_headers(token)
    )
    data = _handle_response(response)

    if "errors" in data:
        error_messages = "; ".join(e["message"] for e in data["errors"])
        raise GitHubAPIError(f"GraphQL error: {error_messages}")

    return data
