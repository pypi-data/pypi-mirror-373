"""CLI commands for managing LlamaDeploy deployments.

This command group lets you list, create, edit, refresh, and delete deployments.
A deployment points the control plane at your Git repository and deployment file
(e.g., `llama_deploy.yaml`). The control plane pulls your code at the selected
git ref, reads the config, and runs your app.
"""

import click
from llama_deploy.core.schema.deployments import DeploymentUpdate
from rich import print as rprint
from rich.table import Table

from ..app import app, console
from ..client import get_project_client
from ..interactive_prompts.utils import (
    confirm_action,
    select_deployment,
)
from ..options import global_options
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
def list_deployments() -> None:
    """List deployments for the configured project."""
    try:
        client = get_project_client()
        deployments = client.list_deployments()

        if not deployments:
            rprint(
                f"[yellow]No deployments found for project {client.project_id}[/yellow]"
            )
            return

        table = Table(title=f"Deployments for project {client.project_id}")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Repository", style="blue")
        table.add_column("Deployment File", style="magenta")
        table.add_column("Git Ref", style="white")
        table.add_column("PAT", style="red")
        table.add_column("Secrets", style="bright_green")

        for deployment in deployments:
            name = deployment.name
            deployment_id = deployment.id
            status = deployment.status
            repo_url = deployment.repo_url
            deployment_file_path = deployment.deployment_file_path
            git_ref = deployment.git_ref
            has_pat = "✓" if deployment.has_personal_access_token else "-"
            secret_names = deployment.secret_names
            secrets_display = str(len(secret_names)) if secret_names else "-"

            table.add_row(
                name,
                deployment_id,
                status,
                repo_url,
                deployment_file_path,
                git_ref,
                has_pat,
                secrets_display,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("get")
@global_options
@click.argument("deployment_id", required=False)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Do not open a live monitor screen showing status and streaming logs",
)
def get_deployment(deployment_id: str | None, non_interactive: bool) -> None:
    """Get details of a specific deployment"""
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        if not non_interactive:
            monitor_deployment_screen(deployment_id)
            return

        deployment = client.get_deployment(deployment_id)

        table = Table(title=f"Deployment: {deployment.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("ID", deployment.id)
        table.add_row("Project ID", deployment.project_id)
        table.add_row("Status", deployment.status)
        table.add_row("Repository", deployment.repo_url)
        table.add_row("Deployment File", deployment.deployment_file_path)
        table.add_row("Git Ref", deployment.git_ref)
        table.add_row("Has PAT", str(deployment.has_personal_access_token))

        apiserver_url = deployment.apiserver_url
        if apiserver_url:
            table.add_row("API Server URL", str(apiserver_url))

        secret_names = deployment.secret_names
        if secret_names:
            table.add_row("Secrets", ", ".join(secret_names))

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("create")
@global_options
@click.option("--repo-url", help="HTTP(S) Git Repository URL")
@click.option("--name", help="Deployment name")
@click.option("--deployment-file-path", help="Path to deployment file")
@click.option("--git-ref", help="Git reference (branch, tag, or commit)")
@click.option(
    "--personal-access-token", help="Git Personal Access Token (HTTP Basic Auth)"
)
def create_deployment(
    repo_url: str | None,
    name: str | None,
    deployment_file_path: str | None,
    git_ref: str | None,
    personal_access_token: str | None,
) -> None:
    """Interactively create a new deployment"""

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
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_deployment(deployment_id: str | None, confirm: bool) -> None:
    """Delete a deployment"""
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        if not confirm:
            if not confirm_action(f"Delete deployment '{deployment_id}'?"):
                rprint("[yellow]Cancelled[/yellow]")
                return

        client.delete_deployment(deployment_id)
        rprint(f"[green]Deleted deployment: {deployment_id}[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("edit")
@global_options
@click.argument("deployment_id", required=False)
def edit_deployment(deployment_id: str | None) -> None:
    """Interactively edit a deployment"""
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details
        current_deployment = client.get_deployment(deployment_id)

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
def refresh_deployment(deployment_id: str | None) -> None:
    """Update the deployment, pulling the latest code from it's branch"""
    try:
        client = get_project_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details to show what we're refreshing
        current_deployment = client.get_deployment(deployment_id)
        deployment_name = current_deployment.name
        old_git_sha = current_deployment.git_sha or ""

        # Create an empty update to force git SHA refresh with spinner
        with console.status(f"Refreshing {deployment_name}..."):
            deployment_update = DeploymentUpdate()
            updated_deployment = client.update_deployment(
                deployment_id,
                deployment_update,
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
