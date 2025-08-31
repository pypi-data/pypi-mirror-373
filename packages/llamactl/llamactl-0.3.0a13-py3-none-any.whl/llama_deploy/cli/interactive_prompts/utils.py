"""Shared utilities for CLI operations"""

import questionary
from rich import print as rprint
from rich.console import Console

from ..config import config_manager
from .session_utils import is_interactive_session

console = Console()


def select_profile(profile_name: str | None = None) -> str | None:
    """
    Select a profile interactively if name not provided.
    Returns the selected profile name or None if cancelled.

    In non-interactive sessions, returns None if profile_name is not provided.
    """
    if profile_name:
        return profile_name

    # Don't attempt interactive selection in non-interactive sessions
    if not is_interactive_session():
        return None

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

    In non-interactive sessions, returns the default value without prompting.
    """
    if not is_interactive_session():
        return default

    return questionary.confirm(message, default=default).ask() or False
