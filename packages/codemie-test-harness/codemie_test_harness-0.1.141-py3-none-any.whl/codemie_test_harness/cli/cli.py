"""Main CLI entry point for CodeMie Test Harness.

Thin entry point: registers commands and wires common options.
"""

from __future__ import annotations

import os
from typing import Optional

import click

from .constants import (
    CONTEXT_SETTINGS,
    KEY_MARKS,
    KEY_XDIST_N,
    KEY_RERUNS,
    KEY_AUTH_SERVER_URL,
    KEY_AUTH_CLIENT_ID,
    KEY_AUTH_CLIENT_SECRET,
    KEY_AUTH_REALM_NAME,
    KEY_CODEMIE_API_DOMAIN,
    # integrations
    KEY_GIT_ENV,
    KEY_GITLAB_URL,
    KEY_GITLAB_TOKEN,
    KEY_GITLAB_PROJECT,
    KEY_GITLAB_PROJECT_ID,
    KEY_GITHUB_URL,
    KEY_GITHUB_TOKEN,
    KEY_GITHUB_PROJECT,
    KEY_JIRA_URL,
    KEY_JIRA_TOKEN,
    KEY_JQL,
    KEY_CONFLUENCE_URL,
    KEY_CONFLUENCE_TOKEN,
    KEY_CQL,
    DEFAULT_MARKS,
    DEFAULT_XDIST_N,
    DEFAULT_RERUNS,
    AUTH_KEYS,
    INTEGRATION_KEYS,
)
from .utils import get_config_value, ensure_env_from_config
from .runner import run_pytest
from .commands.config_cmd import config_cmd
from .commands.run_cmd import run_cmd


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--marks",
    envvar=KEY_MARKS,
    help="Pytest -m expression, default from config or 'smoke'",
)
@click.option(
    "-n", "workers", envvar=KEY_XDIST_N, type=int, help="Number of xdist workers (-n)"
)
@click.option(
    "--reruns", envvar=KEY_RERUNS, type=int, help="Number of reruns for flaky tests"
)
@click.option("--auth-server-url", envvar=KEY_AUTH_SERVER_URL, help="Auth server url")
@click.option("--auth-client-id", envvar=KEY_AUTH_CLIENT_ID, help="Auth client id")
@click.option(
    "--auth-client-secret", envvar=KEY_AUTH_CLIENT_SECRET, help="Auth client secret"
)
@click.option("--auth-realm-name", envvar=KEY_AUTH_REALM_NAME, help="Auth realm name")
@click.option(
    "--api-domain", envvar=KEY_CODEMIE_API_DOMAIN, help="CodeMie API domain URL"
)
# Integrations
@click.option(
    "--git-env",
    envvar=KEY_GIT_ENV,
    type=click.Choice(["gitlab", "github"], case_sensitive=False),
    help="Git provider env: gitlab or github",
)
# GitLab
@click.option("--gitlab-url", envvar=KEY_GITLAB_URL, help="GitLab base URL")
@click.option("--gitlab-token", envvar=KEY_GITLAB_TOKEN, help="GitLab access token")
@click.option("--gitlab-project", envvar=KEY_GITLAB_PROJECT, help="GitLab project URL")
@click.option(
    "--gitlab-project-id",
    envvar=KEY_GITLAB_PROJECT_ID,
    help="GitLab project id",
    type=str,
)
# GitHub
@click.option("--github-url", envvar=KEY_GITHUB_URL, help="GitHub base URL")
@click.option("--github-token", envvar=KEY_GITHUB_TOKEN, help="GitHub access token")
@click.option("--github-project", envvar=KEY_GITHUB_PROJECT, help="GitHub project URL")
# JIRA
@click.option("--jira-url", envvar=KEY_JIRA_URL, help="Jira base URL")
@click.option("--jira-token", envvar=KEY_JIRA_TOKEN, help="Jira token")
@click.option("--jql", envvar=KEY_JQL, help="JQL query string")
# Confluence
@click.option("--confluence-url", envvar=KEY_CONFLUENCE_URL, help="Confluence base URL")
@click.option(
    "--confluence-token", envvar=KEY_CONFLUENCE_TOKEN, help="Confluence token"
)
@click.option("--cql", envvar=KEY_CQL, help="CQL query string")
@click.pass_context
def cli(
    ctx: click.Context,
    marks: Optional[str],
    workers: Optional[int],
    reruns: Optional[int],
    auth_server_url: Optional[str],
    auth_client_id: Optional[str],
    auth_client_secret: Optional[str],
    auth_realm_name: Optional[str],
    api_domain: Optional[str],
    git_env: Optional[str],
    gitlab_url: Optional[str],
    gitlab_token: Optional[str],
    gitlab_project: Optional[str],
    gitlab_project_id: Optional[str],
    github_url: Optional[str],
    github_token: Optional[str],
    github_project: Optional[str],
    jira_url: Optional[str],
    jira_token: Optional[str],
    jql: Optional[str],
    confluence_url: Optional[str],
    confluence_token: Optional[str],
    cql: Optional[str],
):
    """CodeMie Test Harness CLI.

    Without subcommand it will run pytest using configured defaults.
    """
    ctx.ensure_object(dict)

    # Resolve options using env -> config -> defaults
    resolved_marks = marks or get_config_value(KEY_MARKS, DEFAULT_MARKS)
    resolved_workers = (
        workers
        if workers is not None
        else int(get_config_value(KEY_XDIST_N, str(DEFAULT_XDIST_N)))
    )
    resolved_reruns = (
        reruns
        if reruns is not None
        else int(get_config_value(KEY_RERUNS, str(DEFAULT_RERUNS)))
    )

    # Ensure env vars. CLI args override env/config.
    provided = {
        # auth/api
        KEY_AUTH_SERVER_URL: auth_server_url,
        KEY_AUTH_CLIENT_ID: auth_client_id,
        KEY_AUTH_CLIENT_SECRET: auth_client_secret,
        KEY_AUTH_REALM_NAME: auth_realm_name,
        KEY_CODEMIE_API_DOMAIN: api_domain,
        # integrations
        KEY_GIT_ENV: git_env,
        KEY_GITLAB_URL: gitlab_url,
        KEY_GITLAB_TOKEN: gitlab_token,
        KEY_GITLAB_PROJECT: gitlab_project,
        KEY_GITLAB_PROJECT_ID: gitlab_project_id,
        KEY_GITHUB_URL: github_url,
        KEY_GITHUB_TOKEN: github_token,
        KEY_GITHUB_PROJECT: github_project,
        KEY_JIRA_URL: jira_url,
        KEY_JIRA_TOKEN: jira_token,
        KEY_JQL: jql,
        KEY_CONFLUENCE_URL: confluence_url,
        KEY_CONFLUENCE_TOKEN: confluence_token,
        KEY_CQL: cql,
    }
    for k, v in provided.items():
        if v is not None and v != "":
            os.environ[k] = str(v)
    # populate any missing values from saved config
    ensure_env_from_config(AUTH_KEYS + INTEGRATION_KEYS)

    ctx.obj.update(
        dict(marks=resolved_marks, workers=resolved_workers, reruns=resolved_reruns)
    )

    # default behavior
    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        run_pytest(resolved_workers, resolved_marks, resolved_reruns)


# Register subcommands
cli.add_command(config_cmd)
cli.add_command(run_cmd)


if __name__ == "__main__":  # pragma: no cover
    cli()
