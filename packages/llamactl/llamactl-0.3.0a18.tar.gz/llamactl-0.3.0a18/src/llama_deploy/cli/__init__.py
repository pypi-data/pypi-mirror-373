from llama_deploy.cli.commands.auth import auth
from llama_deploy.cli.commands.deployment import deployments
from llama_deploy.cli.commands.env import env_group
from llama_deploy.cli.commands.init import init
from llama_deploy.cli.commands.serve import serve

from .app import app


# Main entry point function (called by the script)
def main() -> None:
    app()


__all__ = ["app", "deployments", "auth", "serve", "init", "env_group"]


if __name__ == "__main__":
    app()
