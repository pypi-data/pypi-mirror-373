import asyncio

import click
import questionary
from llama_deploy.cli.client import get_control_plane_client
from llama_deploy.cli.interactive_prompts.session_utils import is_interactive_session
from rich import print as rprint
from rich.table import Table

from ..app import app, console
from ..config import Profile, config_manager
from ..interactive_prompts.utils import (
    select_profile,
)
from ..options import global_options, interactive_option
from ..textual.api_key_profile_form import (
    create_api_key_profile_form,
    edit_api_key_profile_form,
)


# Create sub-applications for organizing commands
@app.group(
    help="Login to llama cloud control plane to manage deployments",
    no_args_is_help=True,
)
@global_options
def auth() -> None:
    """Login to llama cloud control plane"""
    pass


# Profile commands
@auth.command("login")
@global_options
@click.option(
    "--api-url",
    help="Specify a custom control plane API URL to log into",
    default="https://api.cloud.llamaindex.ai",
)
@click.option(
    "--name",
    help="Specify a memorable name for the API key login when creating non-interactively",
)
@click.option(
    "--project-id",
    help="Project ID to use for the login when creating non-interactively",
)
@click.option(
    "--api-key",
    help="Advanced: Control plane/Llama Cloud Bearer API key. Only needed if control plane is authenticated",
)
@click.option(
    "--login-url", help="Advanced: Custom login URL for initiating OpenID Connect flow"
)
@interactive_option
def create_login_profile(
    name: str | None,
    api_url: str,
    project_id: str | None,
    api_key: str | None,
    login_url: str | None,
    interactive: bool,
) -> None:
    """Login to llama cloud control plane as a new profile. May specify name, project ID, and API URL when creating non-interactively"""
    try:
        # If all required args are provided via CLI, skip interactive mode
        if name and project_id:
            # Use CLI args directly
            profile = config_manager.create_profile(name, api_url, project_id, api_key)
            rprint(f"[green]Manually created profile '{profile.name}'[/green]")

            # Automatically switch to the new profile
            config_manager.set_current_profile(name)
            rprint(f"[green]Switched to profile '{name}'[/green]")
            return
        elif not interactive:
            raise click.ClickException(
                "No --name or --project-id provided. Run `llamactl auth login --help` for more information."
            )

        # Use interactive creation
        profile = create_api_key_profile_form(
            api_url=api_url,
            project_id=project_id,
            api_key_auth_token=api_key,
        )
        if profile is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        try:
            rprint(f"[green]Logged in as '{profile.name}'[/green]")

            # Automatically switch to the new profile
            config_manager.set_current_profile(profile.name)
            rprint(f"[green]Switched to profile '{profile.name}'[/green]")
        except Exception as e:
            rprint(f"[red]Error creating profile: {e}[/red]")
            raise click.Abort()

    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@auth.command("token")
@global_options
@click.option(
    "--api-url",
    help="Specify a custom control plane API URL to log into",
    default="https://api.cloud.llamaindex.ai",
)
@click.option(
    "--name",
    help="Specify a memorable name for the API key login when creating non-interactively",
)
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
    api_url: str,
    name: str | None,
    project_id: str | None,
    api_key: str | None,
    interactive: bool,
) -> None:
    """Authenticate with an API key rather than logging in"""
    if not interactive:
        if not name or not project_id:
            raise click.ClickException(
                "No --name or --project-id provided. Run `llamactl auth create-token --help` for more information."
            )
        profile = config_manager.create_profile(name, api_url, project_id, api_key)
        rprint(f"[green]Created API key profile '{profile.name}'[/green]")

    else:
        profile = create_api_key_profile_form(
            name=name,
            api_url=api_url,
            project_id=project_id,
            api_key_auth_token=api_key,
        )
        if profile is None:
            rprint("[yellow]Cancelled[/yellow]")
            return
        rprint(f"[green]Created API key profile '{profile.name}'[/green]")
    config_manager.set_current_profile(profile.name)


@auth.command("list")
@global_options
def list_profiles() -> None:
    """List all logged in profiles"""
    try:
        profiles = config_manager.list_profiles()
        current_name = config_manager.get_current_profile_name()

        if not profiles:
            rprint("[yellow]No profiles found[/yellow]")
            rprint("Create one with: [cyan]llamactl profile create[/cyan]")
            return

        table = Table(title="Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("API URL", style="green")
        table.add_column("Active Project", style="yellow")
        table.add_column("Current", style="magenta")

        for profile in profiles:
            is_current = "✓" if profile.name == current_name else ""
            active_project = profile.project_id or "-"
            table.add_row(profile.name, profile.api_url, active_project, is_current)

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
    try:
        name = select_profile(name) if interactive else name
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        profile = config_manager.get_profile(name)
        if not profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()

        config_manager.set_current_profile(name)
        rprint(f"[green]Switched to profile '{name}'[/green]")

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
        name = select_profile(name) if interactive else name
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        profile = config_manager.get_profile(name)
        if not profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()

        if config_manager.delete_profile(name):
            rprint(f"[green]Logged out from '{name}'[/green]")
        else:
            rprint(f"[red]Profile '{name}' not found[/red]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@auth.command("edit-token")
@global_options
@click.argument("name", required=False)
def edit_api_key_profile(name: str | None) -> None:
    """Edit an API key profile"""
    if is_interactive_session():
        raise click.ClickException(
            "Interactive editing of API key profiles is not supported. You can instead delete and `llamactl auth create-token` to create a new profile."
        )
    try:
        name = select_profile(name)
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        # Get current profile
        maybe_profile = config_manager.get_profile(name)
        if not maybe_profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()
        profile = maybe_profile

        # Use the interactive edit menu
        updated = edit_api_key_profile_form(profile)
        if updated is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        try:
            current_profile = config_manager.get_current_profile()
            if not current_profile or current_profile.name != updated.name:
                config_manager.set_current_profile(updated.name)
                rprint(f"[green]Updated profile '{profile.name}'[/green]")
        except Exception as e:
            rprint(f"[red]Error updating profile: {e}[/red]")
            raise click.Abort()

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
    if project_id:
        config_manager.set_project(profile.name, project_id)
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
            ],
        ).ask()
        if result:
            config_manager.set_project(profile.name, result)
            rprint(f"[green]Set active project to '{result}'[/green]")
        else:
            rprint("[yellow]No project selected[/yellow]")
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


def validate_authenticated_profile(interactive: bool) -> Profile:
    """Validate that the user is authenticated"""

    profile = config_manager.get_current_profile()
    if profile:
        return profile
    elif not interactive:
        raise click.ClickException(
            "No profile configured. Run `llamactl profile create` to create a profile."
        )
    else:
        profiles = config_manager.list_profiles()
        if len(profiles) > 1:
            selected_profile = select_profile()
            if not selected_profile:
                raise click.ClickException("No profile selected")
            config_manager.set_current_profile(selected_profile)
            found_profile = config_manager.get_profile(selected_profile)
            if found_profile is None:
                raise RuntimeError(
                    f"Unexpected error: Profile '{selected_profile}' not found"
                )
            return found_profile
        else:
            selected_profile_obj = create_profile_interactive()
            if selected_profile_obj is None:
                raise click.ClickException("No profile selected")
            return selected_profile_obj


def create_profile_interactive(
    api_url: str = "https://api.cloud.llamaindex.ai",
    project_id: str | None = None,
    api_key_auth_token: str | None = None,
) -> Profile | None:
    should_continue = questionary.select(
        "This action requires you to authenticate with LlamaCloud. Continue?",
        choices=[
            questionary.Choice(title="Add API Key", value="add_api_key"),
            questionary.Choice(title="Cancel", value="cancel"),
        ],
    ).ask()
    if should_continue == "add_api_key":
        profile_form = create_api_key_profile_form(
            api_url=api_url,
            project_id=project_id,
            api_key_auth_token=api_key_auth_token,
        )
        if profile_form is None:
            raise click.ClickException("No profile selected")
        profile = profile_form.to_profile()
        config_manager.set_current_profile(profile.name)
        return profile

    return None
