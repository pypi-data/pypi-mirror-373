"""Shared utilities for CLI operations"""

import questionary
from rich import print as rprint
from rich.console import Console

from ..client import get_project_client as get_client
from ..config import config_manager

console = Console()


def select_deployment(deployment_id: str | None = None) -> str | None:
    """
    Select a deployment interactively if ID not provided.
    Returns the selected deployment ID or None if cancelled.
    """
    if deployment_id:
        return deployment_id

    try:
        client = get_client()
        deployments = client.list_deployments()

        if not deployments:
            rprint(
                f"[yellow]No deployments found for project {client.project_id}[/yellow]"
            )
            return None

        choices = []
        for deployment in deployments:
            name = deployment.name
            deployment_id = deployment.id
            status = deployment.status
            choices.append(
                questionary.Choice(
                    title=f"{name} ({deployment_id}) - {status}", value=deployment_id
                )
            )

        return questionary.select("Select deployment:", choices=choices).ask()

    except Exception as e:
        rprint(f"[red]Error loading deployments: {e}[/red]")
        return None


def select_profile(profile_name: str | None = None) -> str | None:
    """
    Select a profile interactively if name not provided.
    Returns the selected profile name or None if cancelled.
    """
    if profile_name:
        return profile_name

    try:
        profiles = config_manager.list_profiles()

        if not profiles:
            rprint("[yellow]No profiles found[/yellow]")
            return None

        choices = []
        current_name = config_manager.get_current_profile_name()

        for profile in profiles:
            title = f"{profile.name} ({profile.api_url})"
            if profile.name == current_name:
                title += " [current]"
            choices.append(questionary.Choice(title=title, value=profile.name))

        return questionary.select("Select profile:", choices=choices).ask()

    except Exception as e:
        rprint(f"[red]Error loading profiles: {e}[/red]")
        return None


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask for confirmation with a consistent interface.
    """
    return questionary.confirm(message, default=default).ask() or False
