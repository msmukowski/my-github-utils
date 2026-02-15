<p align="center">
  <img src="assets/banner.webp" alt="GH Utils banner" />
</p>

---

CLI tool for GitHub automation — create issues from markdown files and add them to GitHub Projects V2.

## Setup

Requires Python 3.12+.

```bash
pyenv virtualenv 3.12.9 my-github-utils
pyenv local my-github-utils
pip install -e ".[dev]"
```

## Configuration

Set these environment variables:

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Always | Personal access token (fine-grained: `issues: write`, `projects: write`) |
| `GITHUB_REPO_OWNER` | Always | Repository owner (org or user) |
| `GITHUB_REPO_NAME` | Always | Repository name |
| `GITHUB_PROJECT_ID` | Fallback | Project V2 node ID (used when `--project-id` / `--project-title` not provided) |

## Commands

### `create-issue`

Create a GitHub issue from a markdown file.

```bash
gh-utils create-issue -t "Bug: login broken" -f issue-body.md
gh-utils create-issue -t "Feature request" -f body.md -l enhancement -l frontend
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--title` | `-t` | Yes | Issue title |
| `--body-file` | `-f` | Yes | Path to markdown file with issue body |
| `--label` | `-l` | No | Label (repeatable) |

### `add-to-project`

Add an existing issue to a GitHub Project V2.

```bash
gh-utils add-to-project -i I_kwDOABC123 -T "Sprint Board"
gh-utils add-to-project -i I_kwDOABC123 -p PVT_kwHOB123
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--issue-node-id` | `-i` | Yes | Issue node ID (printed by `create-issue`) |
| `--project-id` | `-p` | No* | Project V2 node ID |
| `--project-title` | `-T` | No* | Project V2 title (resolved via GraphQL) |

*Provide `--project-id` or `--project-title`. If neither is given, falls back to `GITHUB_PROJECT_ID` env var.

### `create-and-add`

Create an issue and add it to a project in one step.

```bash
gh-utils create-and-add -t "New task" -f body.md -T "Backlog"
gh-utils create-and-add -t "Bug" -f body.md -l bug -p PVT_kwHOB123
```

Accepts all options from both `create-issue` and `add-to-project` (except `--issue-node-id`).

## Running tests

```bash
pytest tests/ -v
```
