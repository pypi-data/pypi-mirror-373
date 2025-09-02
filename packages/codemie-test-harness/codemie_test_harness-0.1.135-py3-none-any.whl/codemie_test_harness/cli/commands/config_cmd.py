from __future__ import annotations
import click
from ..constants import CONSOLE
from ..utils import load_config, get_config_value, set_config_value


@click.group(name="config")
def config_cmd():
    """Manage configuration for test harness.

    Keys:
      - AUTH_SERVER_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, AUTH_REALM_NAME, CODEMIE_API_DOMAIN
      - PYTEST_MARKS, PYTEST_N, PYTEST_RERUNS
      - GIT_ENV
        GitLab: GITLAB_URL, GITLAB_TOKEN, GITLAB_PROJECT, GITLAB_PROJECT_ID
        GitHub: GITHUB_URL, GITHUB_TOKEN, GITHUB_PROJECT
        Jira: JIRA_URL, JIRA_TOKEN, JQL
        Confluence: CONFLUENCE_URL, CONFLUENCE_TOKEN, CQL
    """
    pass


@config_cmd.command(name="list")
def config_list():
    cfg = load_config()
    if not cfg:
        CONSOLE.print("[yellow]No config set yet[/]")
    else:
        for k, v in cfg.items():
            CONSOLE.print(f"[cyan]{k}[/] = [green]{v}[/]")


@config_cmd.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    set_config_value(key, value)
    CONSOLE.print(f"[green]Saved[/] {key} = {value}")


@config_cmd.command(name="get")
@click.argument("key")
def config_get(key: str):
    val = get_config_value(key)
    if val is None:
        CONSOLE.print(f"[yellow]{key} not set[/]")
    else:
        CONSOLE.print(f"{key} = {val}")
