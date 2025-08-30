import click
from llama_deploy.cli.client import get_control_plane_client
from rich import print as rprint
from rich.table import Table

from ..app import app, console
from ..config import config_manager
from ..interactive_prompts.utils import (
    select_profile,
)
from ..options import global_options
from ..textual.profile_form import create_profile_form, edit_profile_form


# Create sub-applications for organizing commands
@app.group(
    help="Login to manage deployments and switch between projects",
    no_args_is_help=True,
)
@global_options
def profiles() -> None:
    """Manage profiles"""
    pass


# Profile commands
@profiles.command("create")
@global_options
@click.option("--name", help="Profile name")
@click.option("--api-url", help="API server URL")
@click.option("--project-id", help="Default project ID")
def create_profile(
    name: str | None, api_url: str | None, project_id: str | None
) -> None:
    """Create a new profile"""
    try:
        # If all required args are provided via CLI, skip interactive mode
        if name and api_url:
            # Use CLI args directly
            profile = config_manager.create_profile(name, api_url, project_id)
            rprint(f"[green]Created profile '{profile.name}'[/green]")

            # Automatically switch to the new profile
            config_manager.set_current_profile(name)
            rprint(f"[green]Switched to profile '{name}'[/green]")
            return

        # Use interactive creation
        profile = create_profile_form()
        if profile is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        try:
            rprint(f"[green]Created profile '{profile.name}'[/green]")

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


@profiles.command("list")
@global_options
def list_profiles() -> None:
    """List all profiles"""
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
            active_project = profile.active_project_id or "-"
            table.add_row(profile.name, profile.api_url, active_project, is_current)

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profiles.command("switch")
@global_options
@click.argument("name", required=False)
def switch_profile(name: str | None) -> None:
    """Switch to a different profile"""
    try:
        name = select_profile(name)
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


@profiles.command("delete")
@global_options
@click.argument("name", required=False)
def delete_profile(name: str | None) -> None:
    """Delete a profile"""
    try:
        name = select_profile(name)
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        profile = config_manager.get_profile(name)
        if not profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()

        if config_manager.delete_profile(name):
            rprint(f"[green]Deleted profile '{name}'[/green]")
        else:
            rprint(f"[red]Profile '{name}' not found[/red]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profiles.command("edit")
@global_options
@click.argument("name", required=False)
def edit_profile(name: str | None) -> None:
    """Edit a profile"""
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
        updated = edit_profile_form(profile)
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
@profiles.command("list-projects")
@global_options
def list_projects() -> None:
    """List all projects with deployment counts"""
    try:
        client = get_control_plane_client()
        projects = client.list_projects()

        if not projects:
            rprint("[yellow]No projects found[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("Project ID", style="cyan")
        table.add_column("Deployments", style="green")

        for project in projects:
            project_id = project.project_id
            deployment_count = project.deployment_count
            table.add_row(project_id, str(deployment_count))

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
