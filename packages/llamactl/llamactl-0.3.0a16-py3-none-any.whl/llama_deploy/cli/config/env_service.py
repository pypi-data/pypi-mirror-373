from dataclasses import replace

from llama_deploy.cli.config.schema import Environment

from ._config import ConfigManager, config_manager
from .auth_service import AuthService


class EnvService:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def list_environments(self) -> list[Environment]:
        return self.config_manager.list_environments()

    def get_current_environment(self) -> Environment:
        return self.config_manager.get_current_environment()

    def switch_environment(self, api_url: str) -> Environment:
        env = self.config_manager.get_environment(api_url)
        if not env:
            raise ValueError(
                f"Environment '{api_url}' not found. Add it with 'llamactl auth env add <API_URL>'"
            )
        self.config_manager.set_settings_current_environment(api_url)
        self.config_manager.set_settings_current_profile(None)
        return env

    def create_or_update_environment(self, env: Environment) -> None:
        self.config_manager.create_or_update_environment(
            env.api_url, env.requires_auth, env.min_llamactl_version
        )

    def delete_environment(self, api_url: str) -> bool:
        return self.config_manager.delete_environment(api_url)

    def current_auth_service(self) -> AuthService:
        return AuthService(self.config_manager, self.get_current_environment())

    def auto_update_env(self, env: Environment) -> Environment:
        svc = AuthService(self.config_manager, env)
        version = svc.fetch_server_version()
        update = replace(env)
        update.requires_auth = version.requires_auth
        update.min_llamactl_version = version.min_llamactl_version
        if update != env:
            self.config_manager.create_or_update_environment(
                update.api_url, update.requires_auth, update.min_llamactl_version
            )
        return update

    def probe_environment(self, api_url: str) -> Environment:
        clean = api_url.rstrip("/")
        base_env = Environment(
            api_url=clean, requires_auth=False, min_llamactl_version=None
        )
        svc = AuthService(self.config_manager, base_env)
        version = svc.fetch_server_version()
        base_env.requires_auth = version.requires_auth
        base_env.min_llamactl_version = version.min_llamactl_version
        return base_env


service = EnvService(config_manager)
