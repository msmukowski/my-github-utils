from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gh_utils.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("GITHUB_REPO_OWNER", "owner")
    monkeypatch.setenv("GITHUB_REPO_NAME", "repo")
    monkeypatch.setenv("GITHUB_PROJECT_ID", "PVT_123")


@pytest.fixture
def body_file(tmp_path):
    path = tmp_path / "body.md"
    path.write_text("# Issue\nSome content")
    return path


########## Test HELP


def test_main_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "GitHub utilities CLI" in result.output


def test_create_issue_help(runner):
    result = runner.invoke(cli, ["create-issue", "--help"])
    assert result.exit_code == 0
    assert "--title" in result.output
    assert "--body-file" in result.output


def test_add_to_project_help(runner):
    result = runner.invoke(cli, ["add-to-project", "--help"])
    assert result.exit_code == 0
    assert "--issue-node-id" in result.output


def test_create_and_add_help(runner):
    result = runner.invoke(cli, ["create-and-add", "--help"])
    assert result.exit_code == 0
    assert "--title" in result.output
    assert "--project-id" in result.output


########## Test Create Issue

def test_create_issue(runner, body_file, env_vars):
    mock_result = {
        "number": 10,
        "html_url": "https://github.com/owner/repo/issues/10",
        "node_id": "I_abc",
    }

    with patch("gh_utils.cli.github_client.create_issue", return_value=mock_result) as mock_create:
        result = runner.invoke(cli, [
            "create-issue", "-t", "My Issue", "-f", str(body_file),
            "-l", "bug", "-l", "urgent",
        ])

    assert result.exit_code == 0
    assert "#10" in result.output
    assert "I_abc" in result.output
    mock_create.assert_called_once_with(
        token="ghp_test",
        owner="owner",
        repo="repo",
        title="My Issue",
        body="# Issue\nSome content",
        labels=["bug", "urgent"],
    )


def test_create_issue_missing_required_option(runner):
    result = runner.invoke(cli, ["create-issue", "-t", "Title"])
    assert result.exit_code != 0


########## Test Add To Project

def test_add_to_project(runner, env_vars):
    mock_result = {
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_999"}}}
    }

    with patch("gh_utils.cli.github_client.add_to_project", return_value=mock_result):
        result = runner.invoke(cli, ["add-to-project", "-i", "I_abc123"])

    assert result.exit_code == 0
    assert "PVTI_999" in result.output


def test_add_to_project_explicit_project_id(runner, env_vars):
    mock_result = {
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_1"}}}
    }

    with patch("gh_utils.cli.github_client.add_to_project", return_value=mock_result) as mock_add:
        result = runner.invoke(cli, ["add-to-project", "-i", "I_node", "-p", "PVT_explicit"])

    assert result.exit_code == 0
    mock_add.assert_called_once_with(
        token="ghp_test", project_id="PVT_explicit", issue_node_id="I_node"
    )


def test_add_to_project_by_title(runner, env_vars):
    mock_result = {
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_2"}}}
    }

    with patch("gh_utils.cli.github_client.find_project_id_by_title", return_value="PVT_resolved") as mock_find, \
         patch("gh_utils.cli.github_client.add_to_project", return_value=mock_result) as mock_add:
        result = runner.invoke(cli, ["add-to-project", "-i", "I_node", "-T", "My Board"])

    assert result.exit_code == 0
    mock_find.assert_called_once_with("ghp_test", "owner", "My Board")
    mock_add.assert_called_once_with(
        token="ghp_test", project_id="PVT_resolved", issue_node_id="I_node"
    )


def test_add_to_project_rejects_both_id_and_title(runner, env_vars):
    result = runner.invoke(cli, ["add-to-project", "-i", "I_node", "-p", "PVT_x", "-T", "Board"])
    assert result.exit_code != 0
    assert "not both" in result.output


########## Test Create and Add

def test_create_and_add(runner, body_file, env_vars):
    mock_issue = {
        "number": 5,
        "html_url": "https://github.com/owner/repo/issues/5",
        "node_id": "I_node5",
    }
    mock_project = {
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_5"}}}
    }

    with patch("gh_utils.cli.github_client.create_issue", return_value=mock_issue), \
         patch("gh_utils.cli.github_client.add_to_project", return_value=mock_project) as mock_add:
        result = runner.invoke(cli, [
            "create-and-add", "-t", "Title", "-f", str(body_file),
        ])

    assert result.exit_code == 0
    assert "#5" in result.output
    assert "PVTI_5" in result.output
    mock_add.assert_called_once_with(
        token="ghp_test", project_id="PVT_123", issue_node_id="I_node5"
    )


def test_create_and_add_by_title(runner, body_file, env_vars):
    mock_issue = {
        "number": 6,
        "html_url": "https://github.com/owner/repo/issues/6",
        "node_id": "I_node6",
    }
    mock_project = {
        "data": {"addProjectV2ItemById": {"item": {"id": "PVTI_6"}}}
    }

    with patch("gh_utils.cli.github_client.create_issue", return_value=mock_issue), \
         patch("gh_utils.cli.github_client.find_project_id_by_title", return_value="PVT_resolved"), \
         patch("gh_utils.cli.github_client.add_to_project", return_value=mock_project) as mock_add:
        result = runner.invoke(cli, [
            "create-and-add", "-t", "Title", "-f", str(body_file), "-T", "My Board",
        ])

    assert result.exit_code == 0
    assert "#6" in result.output
    mock_add.assert_called_once_with(
        token="ghp_test", project_id="PVT_resolved", issue_node_id="I_node6"
    )
