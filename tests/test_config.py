import pytest

from gh_utils.config import (
    get_github_token,
    get_project_id,
    get_repo_name,
    get_repo_owner,
)
from gh_utils.exceptions import ConfigError


@pytest.fixture
def clear_env(monkeypatch):
    """Remove all GH config env vars so tests start clean."""
    for var in ("GITHUB_TOKEN", "GITHUB_REPO_OWNER", "GITHUB_REPO_NAME", "GITHUB_PROJECT_ID"):
        monkeypatch.delenv(var, raising=False)


def test_get_github_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")
    assert get_github_token() == "ghp_test123"


def test_get_github_token_missing(clear_env):
    with pytest.raises(ConfigError, match="GITHUB_TOKEN"):
        get_github_token()


def test_get_repo_owner(monkeypatch):
    monkeypatch.setenv("GITHUB_REPO_OWNER", "myorg")
    assert get_repo_owner() == "myorg"


def test_get_repo_owner_missing(clear_env):
    with pytest.raises(ConfigError, match="GITHUB_REPO_OWNER"):
        get_repo_owner()


def test_get_repo_name(monkeypatch):
    monkeypatch.setenv("GITHUB_REPO_NAME", "my-repo")
    assert get_repo_name() == "my-repo"


def test_get_repo_name_missing(clear_env):
    with pytest.raises(ConfigError, match="GITHUB_REPO_NAME"):
        get_repo_name()


def test_get_project_id(monkeypatch):
    monkeypatch.setenv("GITHUB_PROJECT_ID", "PVT_123")
    assert get_project_id() == "PVT_123"


def test_get_project_id_missing(clear_env):
    with pytest.raises(ConfigError, match="GITHUB_PROJECT_ID"):
        get_project_id()
