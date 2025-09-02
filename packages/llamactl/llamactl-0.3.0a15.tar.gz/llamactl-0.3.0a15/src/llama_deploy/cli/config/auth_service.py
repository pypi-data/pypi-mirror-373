import asyncio

from llama_deploy.cli.config._config import Auth, ConfigManager, Environment
from llama_deploy.core.client.manage_client import ControlPlaneClient
from llama_deploy.core.schema import VersionResponse
from llama_deploy.core.schema.projects import ProjectSummary


class AuthService:
    def __init__(self, config_manager: ConfigManager, env: Environment):
        self.config_manager = config_manager
        self.env = env

    def list_profiles(self) -> list[Auth]:
        return self.config_manager.list_profiles(self.env.api_url)

    def get_profile(self, name: str) -> Auth | None:
        return self.config_manager.get_profile(name, self.env.api_url)

    def set_current_profile(self, name: str) -> None:
        self.config_manager.set_settings_current_profile(name)

    def select_any_profile(self) -> None:
        # best effort to select a profile within the environment
        profiles = self.list_profiles()
        if profiles:
            self.set_current_profile(profiles[0].name)

    def get_current_profile(self) -> Auth | None:
        return self.config_manager.get_current_profile(self.env.api_url)

    def create_profile_from_token(self, project_id: str, api_key: str | None) -> Auth:
        base = _auto_profile_name_from_token(api_key or "") if api_key else "default"
        auth = self.config_manager.create_profile(
            base, self.env.api_url, project_id, api_key
        )
        self.config_manager.set_settings_current_profile(auth.name)
        return auth

    def delete_profile(self, name: str) -> bool:
        return self.config_manager.delete_profile(name, self.env.api_url)

    def set_project(self, name: str, project_id: str) -> None:
        self.config_manager.set_project(name, self.env.api_url, project_id)

    def fetch_server_version(self) -> VersionResponse:
        async def _fetch_server_version() -> VersionResponse:
            async with ControlPlaneClient.ctx(self.env.api_url) as client:
                version = await client.server_version()
                return version

        return asyncio.run(_fetch_server_version())

    def _validate_token_and_list_projects(self, api_key: str) -> list[ProjectSummary]:
        async def _run():
            async with ControlPlaneClient.ctx(self.env.api_url, api_key) as client:
                return await client.list_projects()

        return asyncio.run(_run())


def _auto_profile_name_from_token(api_key: str) -> str:
    token = api_key or "token"
    cleaned = token.replace(" ", "")
    first = cleaned[:6]
    last = cleaned[-4:] if len(cleaned) > 10 else cleaned[-2:]
    base = f"token-{first}-{last}"
    return base
