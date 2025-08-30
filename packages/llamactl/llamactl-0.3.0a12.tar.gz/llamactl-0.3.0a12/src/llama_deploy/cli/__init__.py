from llama_deploy.cli.commands.deployment import deployments
from llama_deploy.cli.commands.init import init
from llama_deploy.cli.commands.profile import profiles
from llama_deploy.cli.commands.serve import serve

from .app import app


# Main entry point function (called by the script)
def main() -> None:
    app()


__all__ = ["app", "deployments", "profiles", "serve", "init"]


if __name__ == "__main__":
    app()
