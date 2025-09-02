from contextlib import asynccontextmanager
from typing import AsyncGenerator

from llama_deploy.cli.config.env_service import service
from llama_deploy.core.client.manage_client import ControlPlaneClient, ProjectClient
from rich import print as rprint


def get_control_plane_client() -> ControlPlaneClient:
    profile = service.current_auth_service().get_current_profile()
    if profile:
        resolved_base_url = profile.api_url.rstrip("/")
        resolved_api_key = profile.api_key
        return ControlPlaneClient(resolved_base_url, resolved_api_key)

    # Fallback: allow env-scoped client construction for env operations
    env = service.get_current_environment()
    resolved_base_url = env.api_url.rstrip("/")
    return ControlPlaneClient(resolved_base_url, None)


def get_project_client() -> ProjectClient:
    profile = service.current_auth_service().get_current_profile()
    if not profile:
        rprint("\n[bold red]No profile configured![/bold red]")
        rprint("\nTo get started, create a profile with:")
        rprint("[cyan]llamactl auth token[/cyan]")
        raise SystemExit(1)
    return ProjectClient(profile.api_url, profile.project_id, profile.api_key)


@asynccontextmanager
async def project_client_context() -> AsyncGenerator[ProjectClient, None]:
    client = get_project_client()
    try:
        yield client
    finally:
        try:
            await client.aclose()
        except Exception:
            pass
