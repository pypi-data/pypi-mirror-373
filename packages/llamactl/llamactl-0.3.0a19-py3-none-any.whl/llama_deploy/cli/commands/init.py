import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import click
import copier
import questionary
from click.exceptions import Exit
from llama_deploy.cli.app import app
from llama_deploy.cli.options import global_options
from rich import print as rprint


@dataclass
class TemplateOption:
    id: str
    name: str
    description: str
    git_url: str


options = [
    TemplateOption(
        id="basic-ui",
        name="Basic UI",
        description="A basic starter workflow with a React Vite UI",
        git_url="https://github.com/run-llama/template-workflow-basic-ui",
    ),
    TemplateOption(
        id="extraction-review",
        name="Extraction Agent with Review UI",
        description="Extract data from documents using a custom schema and Llama Cloud. Includes a UI to review and correct the results",
        git_url="https://github.com/run-llama/template-workflow-data-extraction",
    ),
]


@app.command()
@click.option(
    "--update",
    is_flag=True,
    help="Instead of creating a new app, update the current app to the latest version. Other options will be ignored.",
)
@click.option(
    "--template",
    type=click.Choice([o.id for o in options]),
    help="The template to use for the new app",
)
@click.option(
    "--dir",
    help="The directory to create the new app in",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, resolve_path=True, path_type=Path
    ),
)
@click.option(
    "--force",
    is_flag=True,
    help="Force overwrite the directory if it exists",
)
@global_options
def init(
    update: bool,
    template: str | None,
    dir: Path | None,
    force: bool,
) -> None:
    """Create a new app repository from a template"""
    if update:
        _update()
    else:
        _create(template, dir, force)


def _create(template: str | None, dir: Path | None, force: bool) -> None:
    if template is None:
        template = questionary.select(
            "Choose a template",
            choices=[
                questionary.Choice(title=o.name, value=o.id, description=o.description)
                for o in options
            ],
        ).ask()
    if template is None:
        rprint("No template selected")
        raise Exit(1)
    if dir is None:
        dir_str = questionary.text(
            "Enter the directory to create the new app in", default=template
        ).ask()
        if not dir_str:
            rprint("No directory provided")
            raise Exit(1)
        dir = Path(dir_str)
    resolved_template = next((o for o in options if o.id == template), None)
    if resolved_template is None:
        rprint(f"Template {template} not found")
        raise Exit(1)
    if dir.exists():
        is_ok = (
            force
            or questionary.confirm("Directory exists. Overwrite?", default=False).ask()
        )
        if not is_ok:
            raise Exit(1)
        else:
            shutil.rmtree(dir, ignore_errors=True)
    copier.run_copy(
        resolved_template.git_url,
        dir,
        quiet=True,
    )
    # Initialize git repository if git is available
    is_git_initialized = False
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)

        # Change to the new directory and initialize git repo
        original_cwd = Path.cwd()
        os.chdir(dir)

        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                check=True,
                capture_output=True,
            )
            is_git_initialized = True
        finally:
            os.chdir(original_cwd)

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or failed - continue without git initialization
        pass

    rprint(
        f"Successfully created [blue]{dir}[/] using the [blue]{resolved_template.name}[/] template! 🎉 🦙 💾"
    )
    rprint("")
    rprint("[bold]To run locally:[/]")
    rprint(f"    [orange3]cd[/] {dir}")
    rprint("    [orange3]uvx[/] llamactl serve")
    rprint("")
    rprint("[bold]To deploy:[/]")
    if not is_git_initialized:
        rprint("    [orange3]git[/] init")
        rprint("    [orange3]git[/] add .")
        rprint("    [orange3]git[/] commit -m 'Initial commit'")
        rprint("")
    rprint("[dim](Create a new repo and add it as a remote)[/]")
    rprint("")
    rprint("    [orange3]git[/] remote add origin <your-repo-url>")
    rprint("    [orange3]git[/] push -u origin main")
    rprint("")
    # rprint("  [orange3]uvx[/] llamactl login")
    rprint("    [orange3]uvx[/] llamactl deploy")
    rprint("")


def _update():
    """Update the app to the latest version"""
    try:
        copier.run_update(
            overwrite=True,
            skip_answered=True,
            quiet=True,
        )
    except copier.UserMessageError as e:
        rprint(f"{e}")
        raise Exit(1)

    # Check git status and warn about conflicts
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            conflicted_files = []
            modified_files = []

            for line in result.stdout.strip().split("\n"):
                status = line[:2]
                filename = line[3:]

                if "UU" in status or "AA" in status or "DD" in status:
                    conflicted_files.append(filename)
                elif status.strip():
                    modified_files.append(filename)

            if conflicted_files:
                rprint("")
                rprint("⚠️  [bold]Files with conflicts detected:[/]")
                for file in conflicted_files:
                    rprint(f"    {file}")
                rprint("")
                rprint(
                    "Please manually resolve conflicts with a merge editor before proceeding."
                )

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or not in a git repo - continue silently
        pass
