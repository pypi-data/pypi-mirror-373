from pathlib import Path

import click
from llama_deploy.appserver.app import (
    prepare_server,
    start_server_in_target_venv,
)
from llama_deploy.core.config import DEFAULT_DEPLOYMENT_FILE_PATH
from rich import print as rprint

from ..app import app


@app.command(
    "serve",
    help="Serve a LlamaDeploy app locally for development and testing",
)
@click.argument(
    "deployment_file",
    required=False,
    default=DEFAULT_DEPLOYMENT_FILE_PATH,
    type=click.Path(dir_okay=True, resolve_path=True, path_type=Path),
)
@click.option(
    "--no-install", is_flag=True, help="Skip installing python and js dependencies"
)
@click.option(
    "--no-reload", is_flag=True, help="Skip reloading the API server on code changes"
)
@click.option("--no-open-browser", is_flag=True, help="Skip opening the browser")
@click.option(
    "--preview",
    is_flag=True,
    help="Preview mode pre-builds the UI to static files, like a production build",
)
@click.option("--port", type=int, help="The port to run the API server on")
@click.option("--ui-port", type=int, help="The port to run the UI proxy server on")
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="The log level to run the API server at",
)
@click.option(
    "--log-format",
    type=click.Choice(["console", "json"], case_sensitive=False),
    help="The format to use for logging",
)
def serve(
    deployment_file: Path,
    no_install: bool,
    no_reload: bool,
    no_open_browser: bool,
    preview: bool,
    port: int | None = None,
    ui_port: int | None = None,
    log_level: str | None = None,
    log_format: str | None = None,
) -> None:
    """Run llama_deploy API Server in the foreground. Reads the deployment configuration from the current directory. Can optionally specify a deployment file path."""
    if not deployment_file.exists():
        rprint(f"[red]Deployment file '{deployment_file}' not found[/red]")
        raise click.Abort()

    try:
        prepare_server(
            install=not no_install,
            build=preview,
        )
        start_server_in_target_venv(
            cwd=Path.cwd(),
            deployment_file=deployment_file,
            proxy_ui=not preview,
            reload=not no_reload,
            open_browser=not no_open_browser,
            port=port,
            ui_port=ui_port,
            log_level=log_level.upper() if log_level else None,
            log_format=log_format.lower() if log_format else None,
        )

    except KeyboardInterrupt:
        print("Shutting down...")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
