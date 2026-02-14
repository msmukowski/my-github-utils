import sys

import click

from gh_utils import config, github_client
from gh_utils.exceptions import GhUtilsError


@click.group()
def cli():
    """GitHub utilities CLI."""


def _resolve_project_id(token: str, owner: str, project_id: str | None, project_title: str | None) -> str:
    if project_id and project_title:
        raise click.UsageError("Provide --project-id or --project-title, not both.")
    if project_id:
        return project_id
    if project_title:
        return github_client.find_project_id_by_title(token, owner, project_title)
    return config.get_project_id()


@cli.command()
@click.option("--title", "-t", required=True, help="Issue title.")
@click.option(
    "--body-file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to markdown file with issue body.",
)
@click.option("--label", "-l", multiple=True, help="Label to add (repeatable).")
def create_issue(title: str, body_file: str, label: tuple[str, ...]):
    """Create a GitHub issue from a markdown file."""
    token = config.get_github_token()
    owner = config.get_repo_owner()
    repo = config.get_repo_name()
    body = click.open_file(body_file).read()

    result = github_client.create_issue(
        token=token,
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        labels=list(label) if label else None,
    )

    click.echo(f"Created issue #{result['number']}: {result['html_url']}")
    click.echo(f"Node ID: {result['node_id']}")


@cli.command()
@click.option("--issue-node-id", "-i", required=True, help="Issue node ID.")
@click.option(
    "--project-id",
    "-p",
    default=None,
    help="Project V2 node ID (fallback: GITHUB_PROJECT_ID env var).",
)
@click.option(
    "--project-title",
    "-T",
    default=None,
    help="Project V2 title (looked up via GraphQL).",
)
def add_to_project(issue_node_id: str, project_id: str | None, project_title: str | None):
    """Add an existing issue to a GitHub Project V2."""
    token = config.get_github_token()
    owner = config.get_repo_owner()
    project_id = _resolve_project_id(token, owner, project_id, project_title)

    result = github_client.add_to_project(
        token=token, project_id=project_id, issue_node_id=issue_node_id
    )

    item_id = result["data"]["addProjectV2ItemById"]["item"]["id"]
    click.echo(f"Added to project. Item ID: {item_id}")


@cli.command()
@click.option("--title", "-t", required=True, help="Issue title.")
@click.option(
    "--body-file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to markdown file with issue body.",
)
@click.option("--label", "-l", multiple=True, help="Label to add (repeatable).")
@click.option(
    "--project-id",
    "-p",
    default=None,
    help="Project V2 node ID (fallback: GITHUB_PROJECT_ID env var).",
)
@click.option(
    "--project-title",
    "-T",
    default=None,
    help="Project V2 title (looked up via GraphQL).",
)
def create_and_add(
    title: str, body_file: str, label: tuple[str, ...], project_id: str | None, project_title: str | None
):
    """Create an issue and add it to a GitHub Project V2."""
    token = config.get_github_token()
    owner = config.get_repo_owner()
    repo = config.get_repo_name()
    project_id = _resolve_project_id(token, owner, project_id, project_title)

    body = click.open_file(body_file).read()

    issue = github_client.create_issue(
        token=token,
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        labels=list(label) if label else None,
    )

    click.echo(f"Created issue #{issue['number']}: {issue['html_url']}")

    result = github_client.add_to_project(
        token=token, project_id=project_id, issue_node_id=issue["node_id"]
    )

    item_id = result["data"]["addProjectV2ItemById"]["item"]["id"]
    click.echo(f"Added to project. Item ID: {item_id}")


def main():
    try:
        cli()
    except GhUtilsError as e:
        click.echo(f"Error: {e}", err=True)
        if hasattr(e, "response_body") and e.response_body:
            click.echo(f"Response: {e.response_body}", err=True)
        sys.exit(1)
