"""CLI commands for managing LlamaDeploy deployments.

This command group lets you list, create, edit, refresh, and delete deployments.
A deployment points the control plane at your Git repository and deployment file
(e.g., `llama_deploy.yaml`). The control plane pulls your code at the selected
git ref, reads the config, and runs your app.
"""

import asyncio

import click
import questionary
from llama_deploy.cli.commands.auth import validate_authenticated_profile
from llama_deploy.core.schema.deployments import DeploymentUpdate
from rich import print as rprint
from rich.table import Table
from rich.text import Text

from ..app import app, console
from ..client import get_project_client
from ..interactive_prompts.session_utils import (
    is_interactive_session,
)
from ..interactive_prompts.utils import (
    confirm_action,
)
from ..options import global_options, interactive_option
from ..textual.deployment_form import create_deployment_form, edit_deployment_form
from ..textual.deployment_monitor import monitor_deployment_screen


@app.group(
    help="Deploy your app to the cloud.",
    no_args_is_help=True,
)
@global_options
def deployments() -> None:
    """Manage deployments"""
    pass


# Deployments commands
@deployments.command("list")
@global_options
@interactive_option
def list_deployments(interactive: bool) -> None:
    """List deployments for the configured project."""
    validate_authenticated_profile(interactive)
    try:
        client = get_project_client()
        deployments = asyncio.run(client.list_deployments())

        if not deployments:
            rprint(
                f"[yellow]No deployments found for project {client.project_id}[/yellow]"
            )
            return

        table = Table(show_edge=False, box=None, header_style="bold cornflower_blue")
        table.add_column("Name")
        table.add_column("Status", style="grey46")
        table.add_column("Repository", style="grey46")

        for deployment in deployments:
            name = deployment.id
            status = deployment.status
            repo_url = deployment.repo_url
            gh = "https://github.com/"
            if repo_url.startswith(gh):
                repo_url = "gh:" + repo_url.removeprefix(gh)

            table.add_row(
                name,
                status,
                repo_url,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("get")
@global_options
@click.argument("deployment_id", required=False)
@interactive_option
def get_deployment(deployment_id: str | None, interactive: bool) -> None:
    """Get details of a specific deployment"""
    validate_authenticated_profile(interactive)
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return
        if interactive:
            monitor_deployment_screen(deployment_id)
            return

        deployment = asyncio.run(client.get_deployment(deployment_id))

        table = Table(show_edge=False, box=None, header_style="bold cornflower_blue")
        table.add_column("Property", style="grey46", justify="right")
        table.add_column("Value")

        table.add_row("ID", Text(deployment.id))
        table.add_row("Project ID", Text(deployment.project_id))
        table.add_row("Status", Text(deployment.status))
        table.add_row("Repository", Text(deployment.repo_url))
        table.add_row("Deployment File", Text(deployment.deployment_file_path))
        table.add_row("Git Ref", Text(deployment.git_ref or "-"))

        apiserver_url = deployment.apiserver_url
        table.add_row(
            "API Server URL",
            Text(str(apiserver_url) if apiserver_url else "-"),
        )

        secret_names = deployment.secret_names or []
        table.add_row("Secrets", Text("\n".join(secret_names), style="italic"))

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("create")
@global_options
@interactive_option
def create_deployment(
    interactive: bool,
) -> None:
    """Interactively create a new deployment"""

    if not interactive:
        raise click.ClickException(
            "This command requires an interactive session. Run in a terminal or provide required arguments explicitly."
        )
    validate_authenticated_profile(interactive)

    # Use interactive creation
    deployment_form = create_deployment_form()
    if deployment_form is None:
        rprint("[yellow]Cancelled[/yellow]")
        return

    rprint(
        f"[green]Created deployment: {deployment_form.name} (id: {deployment_form.id})[/green]"
    )


@deployments.command("delete")
@global_options
@click.argument("deployment_id", required=False)
@interactive_option
def delete_deployment(deployment_id: str | None, interactive: bool) -> None:
    """Delete a deployment"""
    validate_authenticated_profile(interactive)
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id, interactive=interactive)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        if interactive:
            if not confirm_action(f"Delete deployment '{deployment_id}'?"):
                rprint("[yellow]Cancelled[/yellow]")
                return

        asyncio.run(client.delete_deployment(deployment_id))
        rprint(f"[green]Deleted deployment: {deployment_id}[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("edit")
@global_options
@click.argument("deployment_id", required=False)
@interactive_option
def edit_deployment(deployment_id: str | None, interactive: bool) -> None:
    """Interactively edit a deployment"""
    validate_authenticated_profile(interactive)
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id, interactive=interactive)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details
        current_deployment = asyncio.run(client.get_deployment(deployment_id))

        # Use the interactive edit form
        updated_deployment = edit_deployment_form(current_deployment)
        if updated_deployment is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        rprint(
            f"[green]Successfully updated deployment: {updated_deployment.name}[/green]"
        )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("update")
@global_options
@click.argument("deployment_id", required=False)
@interactive_option
def refresh_deployment(deployment_id: str | None, interactive: bool) -> None:
    """Update the deployment, pulling the latest code from it's branch"""
    validate_authenticated_profile(interactive)
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details to show what we're refreshing
        current_deployment = asyncio.run(client.get_deployment(deployment_id))
        deployment_name = current_deployment.name
        old_git_sha = current_deployment.git_sha or ""

        # Create an empty update to force git SHA refresh with spinner
        with console.status(f"Refreshing {deployment_name}..."):
            deployment_update = DeploymentUpdate()
            updated_deployment = asyncio.run(
                client.update_deployment(
                    deployment_id,
                    deployment_update,
                )
            )

        # Show the git SHA change with short SHAs
        new_git_sha = updated_deployment.git_sha or ""
        old_short = old_git_sha[:7] if old_git_sha else "none"
        new_short = new_git_sha[:7] if new_git_sha else "none"

        if old_git_sha == new_git_sha:
            rprint(f"No changes: already at {new_short}")
        else:
            rprint(f"Updated: {old_short} → {new_short}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


def select_deployment(
    deployment_id: str | None = None, interactive: bool = is_interactive_session()
) -> str | None:
    """
    Select a deployment interactively if ID not provided.
    Returns the selected deployment ID or None if cancelled.

    In non-interactive sessions, returns None if deployment_id is not provided.
    """
    if deployment_id:
        return deployment_id

    # Don't attempt interactive selection in non-interactive sessions
    if not interactive:
        return None

    try:
        client = get_project_client()
        deployments = asyncio.run(client.list_deployments())

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
