import asyncio

import click
import questionary
from llama_deploy.cli.client import get_control_plane_client
from llama_deploy.cli.config.auth_service import AuthService
from llama_deploy.cli.config.env_service import service
from llama_deploy.core.client.manage_client import ClientError, ControlPlaneClient
from llama_deploy.core.schema.projects import ProjectSummary
from rich import print as rprint
from rich.table import Table
from rich.text import Text

from ..app import app, console
from ..config.schema import Auth
from ..options import global_options, interactive_option


# Create sub-applications for organizing commands
@app.group(
    help="Login to llama cloud control plane to manage deployments",
    no_args_is_help=True,
)
@global_options
def auth() -> None:
    """Login to llama cloud control plane"""
    pass


@auth.command("token")
@global_options
@click.option(
    "--project-id",
    help="Project ID to use for the login when creating non-interactively",
)
@click.option(
    "--api-key",
    help="API key to use for the login when creating non-interactively",
)
@interactive_option
def create_api_key_profile(
    project_id: str | None,
    api_key: str | None,
    interactive: bool,
) -> None:
    """Authenticate with an API key and create a profile in the current environment."""
    try:
        auth_svc = service.current_auth_service()

        # Non-interactive mode: require both api-key and project-id
        if not interactive:
            if not api_key or not project_id:
                raise click.ClickException(
                    "--api-key and --project-id are required in non-interactive mode"
                )
            created = auth_svc.create_profile_from_token(project_id, api_key)
            rprint(
                f"[green]Created API key profile '{created.name}' and set as current[/green]"
            )
            return

        # Interactive mode: prompt for token (masked) and validate
        token_value = api_key or _prompt_for_api_key()
        projects = _validate_token_and_list_projects(auth_svc, token_value)

        # Select or enter project ID
        selected_project_id = project_id or _select_or_enter_project(
            projects, auth_svc.env.requires_auth
        )
        if not selected_project_id:
            rprint("[yellow]No project selected[/yellow]")
            return

        # Create and set profile
        created = auth_svc.create_profile_from_token(selected_project_id, token_value)
        rprint(
            f"[green]Created API key profile '{created.name}' and set as current[/green]"
        )
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@auth.command("list")
@global_options
def list_profiles() -> None:
    """List all logged in profiles"""
    try:
        auth_svc = service.current_auth_service()
        profiles = auth_svc.list_profiles()
        current = auth_svc.get_current_profile()

        if not profiles:
            rprint("[yellow]No profiles found[/yellow]")
            rprint("Create one with: [cyan]llamactl auth token[/cyan]")
            return

        table = Table(show_edge=False, box=None, header_style="bold cornflower_blue")
        table.add_column("  Name")
        table.add_column("Active Project", style="grey46")

        for profile in profiles:
            text = Text()
            if profile == current:
                text.append("* ", style="magenta")
            else:
                text.append("  ")
            text.append(profile.name)
            active_project = profile.project_id or "-"
            table.add_row(
                text,
                active_project,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@auth.command("switch")
@global_options
@click.argument("name", required=False)
@interactive_option
def switch_profile(name: str | None, interactive: bool) -> None:
    """Switch to a different profile"""
    auth_svc = service.current_auth_service()
    try:
        selected_auth = _select_profile(auth_svc, name, interactive)
        if not selected_auth:
            rprint("[yellow]No profile selected[/yellow]")
            return

        auth_svc.set_current_profile(selected_auth.name)
        rprint(f"[green]Switched to profile '{selected_auth.name}'[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@auth.command("logout")
@global_options
@click.argument("name", required=False)
@interactive_option
def delete_profile(name: str | None, interactive: bool) -> None:
    """Logout from a profile and wipe all associated data"""
    try:
        auth_svc = service.current_auth_service()
        auth = _select_profile(auth_svc, name, interactive)
        if not auth:
            rprint("[yellow]No profile selected[/yellow]")
            return

        if auth_svc.delete_profile(auth.name):
            rprint(f"[green]Logged out from '{auth.name}'[/green]")
        else:
            rprint(f"[red]Profile '{auth.name}' not found[/red]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


# Projects commands
@auth.command("project")
@click.argument("project_id", required=False)
@interactive_option
@global_options
def change_project(project_id: str | None, interactive: bool) -> None:
    """Change the active project for the current profile"""
    profile = validate_authenticated_profile(interactive)
    if project_id and profile.project_id == project_id:
        return
    auth_svc = service.current_auth_service()
    if project_id:
        auth_svc.set_project(profile.name, project_id)
        rprint(f"[green]Set active project to '{project_id}'[/green]")
        return
    if not interactive:
        raise click.ClickException(
            "No --project-id provided. Run `llamactl auth project --help` for more information."
        )
    try:
        client = get_control_plane_client()
        projects = asyncio.run(client.list_projects())

        if not projects:
            rprint("[yellow]No projects found[/yellow]")
            return
        result = questionary.select(
            "Select a project",
            choices=[
                questionary.Choice(
                    title=f"{project.project_name} ({project.deployment_count} deployments)",
                    value=project.project_id,
                )
                for project in projects
            ]
            + (
                [questionary.Choice(title="Create new project", value="__CREATE__")]
                if not auth_svc.env.requires_auth
                else []
            ),
        ).ask()
        if result == "__CREATE__":
            project_id = questionary.text("Enter project ID").ask()
            result = project_id
        if result:
            auth_svc.set_project(profile.name, result)
            rprint(f"[green]Set active project to '{result}'[/green]")
        else:
            rprint("[yellow]No project selected[/yellow]")
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


def validate_authenticated_profile(interactive: bool) -> Auth:
    """Validate that the user is authenticated within the current environment.

    - If there is a current profile, return it.
    - If multiple profiles exist in the current environment, prompt to select in interactive mode.
    - If none exist:
      - If environment requires_auth: run token flow inline.
      - Else: create profile without token after selecting a project.
    """

    auth_svc = service.current_auth_service()
    existing = auth_svc.get_current_profile()
    if existing:
        return existing

    if not interactive:
        raise click.ClickException(
            "No profile configured. Run `llamactl auth token` to create a profile."
        )

    # Filter profiles by current environment
    env_profiles = auth_svc.list_profiles()
    current_env = auth_svc.env

    if len(env_profiles) > 1:
        # Prompt to select
        choice: Auth | None = questionary.select(
            "Select profile",
            choices=[questionary.Choice(title=p.name, value=p) for p in env_profiles],
        ).ask()
        if not choice:
            raise click.ClickException("No profile selected")
        auth_svc.set_current_profile(choice.name)
        return choice
    if len(env_profiles) == 1:
        only = env_profiles[0]
        auth_svc.set_current_profile(only.name)
        return only

    # No profiles exist for this env
    if current_env.requires_auth:
        # Inline token flow
        created = _token_flow_for_env(auth_svc)
        return created
    else:
        # No auth required: select project and create a default profile without token
        project_id: str | None = questionary.text("Enter project ID").ask()
        if not project_id:
            raise click.ClickException("No project ID provided")
        created = auth_svc.create_profile_from_token(project_id, None)
        return created


# -----------------------------
# Helpers for token/profile flow
# -----------------------------


def _prompt_for_api_key() -> str:
    while True:
        entered = questionary.password("Enter API key token").ask()
        if entered:
            return entered.strip()
        rprint("[yellow]API key is required[/yellow]")


def _validate_token_and_list_projects(
    auth_svc: AuthService, api_key: str
) -> list[ProjectSummary]:
    async def _run():
        async with ControlPlaneClient.ctx(auth_svc.env.api_url, api_key) as client:
            return await client.list_projects()

    try:
        return asyncio.run(_run())
    except ClientError as e:
        if getattr(e, "status_code", None) == 401:
            rprint("[red]Invalid API key. Please try again.[/red]")
            return _validate_token_and_list_projects(auth_svc, _prompt_for_api_key())
        if getattr(e, "status_code", None) == 403:
            rprint("[red]This environment requires a valid API key.[/red]")
            return _validate_token_and_list_projects(auth_svc, _prompt_for_api_key())
        raise
    except Exception as e:
        raise click.ClickException(f"Failed to validate API key: {e}")


def _select_or_enter_project(
    projects: list[ProjectSummary], requires_auth: bool
) -> str | None:
    if not projects:
        return None
    # select the only authorized project if there is only one
    elif len(projects) == 1 and requires_auth:
        return projects[0].project_id
    else:
        choice = questionary.select(
            "Select a project",
            choices=[
                questionary.Choice(
                    title=f"{p.project_name} ({p.deployment_count} deployments)",
                    value=p.project_id,
                )
                for p in projects
            ],
        ).ask()
        return choice


def _token_flow_for_env(auth_service: AuthService) -> Auth:
    token_value = _prompt_for_api_key()
    projects = _validate_token_and_list_projects(auth_service, token_value)
    project_id = _select_or_enter_project(projects, auth_service.env.requires_auth)
    if not project_id:
        raise click.ClickException("No project selected")
    created = auth_service.create_profile_from_token(project_id, token_value)
    return created


def _select_profile(
    auth_svc: AuthService, profile_name: str | None, is_interactive: bool
) -> Auth | None:
    """
    Select a profile interactively if name not provided.
    Returns the selected profile name or None if cancelled.

    In non-interactive sessions, returns None if profile_name is not provided.
    """
    if profile_name:
        profile = auth_svc.get_profile(profile_name)
        if profile:
            return profile

    # Don't attempt interactive selection in non-interactive sessions
    if not is_interactive:
        return None

    try:
        profiles = auth_svc.list_profiles()

        if not profiles:
            rprint("[yellow]No profiles found[/yellow]")
            return None

        choices = []
        current = auth_svc.get_current_profile()

        for profile in profiles:
            title = f"{profile.name} ({profile.api_url})"
            if profile == current:
                title += " [current]"
            choices.append(questionary.Choice(title=title, value=profile))

        return questionary.select("Select profile:", choices=choices).ask()

    except Exception as e:
        rprint(f"[red]Error loading profiles: {e}[/red]")
        return None
