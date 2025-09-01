from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

import click
from llama_deploy.cli.commands.aliased_group import AliasedGroup
from llama_deploy.cli.config.env_service import service
from llama_deploy.cli.options import global_options
from rich import print as rprint
from rich.console import Console
from rich.text import Text

console = Console(highlight=False)


def print_version(ctx: click.Context, param: click.Option, value: bool) -> None:
    """Print the version of llama_deploy"""
    if not value or ctx.resilient_parsing:
        return
    try:
        ver = pkg_version("llamactl")
        console.print(Text.assemble("client version: ", (ver, "green")))

        # If there is an active profile, attempt to query server version
        auth_service = service.current_auth_service()
        if auth_service:
            try:
                data = auth_service.fetch_server_version()
                server_ver = data.version
                console.print(
                    Text.assemble(
                        "server version: ",
                        (
                            server_ver or "unknown",
                            "bright_yellow" if server_ver is None else "green",
                        ),
                    )
                )
            except Exception as e:
                console.print(
                    Text.assemble(
                        "server version: ",
                        ("unavailable", "bright_yellow"),
                        (f" - {e}", "dim"),
                    )
                )
    except PackageNotFoundError:
        rprint("[red]Package 'llamactl' not found[/red]")
        raise click.Abort()
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
    ctx.exit()


# Main CLI application
@click.group(
    help="Create, develop, and deploy LlamaIndex workflow based apps", cls=AliasedGroup
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print client and server versions of LlamaDeploy",
)
@global_options
def app():
    pass
