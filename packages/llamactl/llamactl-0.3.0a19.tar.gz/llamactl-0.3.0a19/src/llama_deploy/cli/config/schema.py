from dataclasses import dataclass


@dataclass
class Auth:
    """Auth Profile configuration"""

    name: str
    api_url: str
    project_id: str
    api_key: str | None = None


@dataclass
class Environment:
    """Environment configuration stored in SQLite.

    Note: `api_url`, `requires_auth`, and `min_llamactl_version` are persisted
    in the environments table.
    """

    api_url: str
    requires_auth: bool
    min_llamactl_version: str | None = None


DEFAULT_ENVIRONMENT = Environment(
    api_url="https://api.cloud.llamaindex.ai",
    requires_auth=True,
    min_llamactl_version=None,
)
