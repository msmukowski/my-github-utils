import os

from gh_utils.exceptions import ConfigError


def get_github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ConfigError("GITHUB_TOKEN environment variable is not set")
    return token


def get_repo_owner() -> str:
    owner = os.environ.get("GITHUB_REPO_OWNER")
    if not owner:
        raise ConfigError("GITHUB_REPO_OWNER environment variable is not set")
    return owner


def get_repo_name() -> str:
    name = os.environ.get("GITHUB_REPO_NAME")
    if not name:
        raise ConfigError("GITHUB_REPO_NAME environment variable is not set")
    return name


def get_project_id() -> str:
    project_id = os.environ.get("GITHUB_PROJECT_ID")
    if not project_id:
        raise ConfigError("GITHUB_PROJECT_ID environment variable is not set")
    return project_id
