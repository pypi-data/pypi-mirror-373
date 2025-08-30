from llama_deploy.cli.config import config_manager
from llama_deploy.core.client.manage_client import ControlPlaneClient, ProjectClient
from rich import print as rprint


def get_control_plane_client(base_url: str | None = None) -> ControlPlaneClient:
    profile = config_manager.get_current_profile()
    if not profile and not base_url:
        rprint("\n[bold red]No profile configured![/bold red]")
        rprint("\nTo get started, create a profile with:")
        rprint("[cyan]llamactl profile create[/cyan]")
        raise SystemExit(1)
    resolved_base_url = (base_url or (profile.api_url if profile else "")).rstrip("/")
    if not resolved_base_url:
        raise ValueError("API URL is required")
    return ControlPlaneClient(resolved_base_url)


def get_project_client(
    base_url: str | None = None, project_id: str | None = None
) -> ProjectClient:
    profile = config_manager.get_current_profile()
    if not profile:
        rprint("\n[bold red]No profile configured![/bold red]")
        rprint("\nTo get started, create a profile with:")
        rprint("[cyan]llamactl profile create[/cyan]")
        raise SystemExit(1)
    resolved_base_url = (base_url or profile.api_url or "").rstrip("/")
    if not resolved_base_url:
        raise ValueError("API URL is required")
    resolved_project_id = project_id or profile.active_project_id
    if not resolved_project_id:
        raise ValueError("Project ID is required")
    return ProjectClient(resolved_base_url, resolved_project_id)
