"""Configuration and profile management for llamactl"""

import os
import sqlite3
from pathlib import Path
from typing import Any

from .schema import DEFAULT_ENVIRONMENT, Auth, Environment


def _to_auth(row: Any) -> Auth:
    return Auth(
        name=row[0],
        api_url=row[1],
        project_id=row[2],
        api_key=row[3],
    )


def _to_environment(row: Any) -> Environment:
    return Environment(
        api_url=row[0],
        requires_auth=bool(row[1]),
        min_llamactl_version=row[2],
    )


class ConfigManager:
    """Manages profiles and configuration using SQLite"""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.db_path = self.config_dir / "profiles.db"
        self._ensure_config_dir()
        self._init_database()

    def _get_config_dir(self) -> Path:
        """Get the configuration directory path based on OS.

        Honors LLAMACTL_CONFIG_DIR when set. This helps tests isolate state.
        """
        override = os.environ.get("LLAMACTL_CONFIG_DIR")
        if override:
            return Path(override).expanduser()
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", "~")) / "llamactl"
        else:  # Unix-like (Linux, macOS)
            config_dir = Path.home() / ".config" / "llamactl"
        return config_dir.expanduser()

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if we need to migrate from old schema
            cursor = conn.execute("PRAGMA table_info(profiles)")
            columns = [row[1] for row in cursor.fetchall()]

            # Migration: handle old active_project_id -> project_id and make it required
            if "active_project_id" in columns and "project_id" not in columns:
                # Delete any profiles that have no active_project_id since project_id is now required
                conn.execute(
                    "DELETE FROM profiles WHERE active_project_id IS NULL OR active_project_id = ''"
                )

                # Rename active_project_id to project_id
                # Note: SQLite doesn't allow changing column constraints easily, but we enforce
                # the NOT NULL constraint in our application code and new table creation
                conn.execute(
                    "ALTER TABLE profiles RENAME COLUMN active_project_id TO project_id"
                )

                # Add api_key column if not already present
                mig_cursor = conn.execute("PRAGMA table_info(profiles)")
                mig_columns = [row[1] for row in mig_cursor.fetchall()]
                if "api_key" not in mig_columns:
                    conn.execute("ALTER TABLE profiles ADD COLUMN api_key TEXT")

            # Create tables with new schema (this will only create if they don't exist)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    name TEXT PRIMARY KEY,
                    api_url TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    api_key TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Environments: first-class environments table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS environments (
                    api_url TEXT PRIMARY KEY,
                    requires_auth INTEGER NOT NULL,
                    min_llamactl_version TEXT
                )
                """
            )

            # Ensure there is a current environment setting. If missing, set to default.
            setting_cursor = conn.execute(
                "SELECT value FROM settings WHERE key = 'current_environment_api_url'"
            )
            setting_row = setting_cursor.fetchone()
            if not setting_row:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_environment_api_url', ?)",
                    (DEFAULT_ENVIRONMENT.api_url,),
                )

            # Seed environments from existing profiles if environments is empty
            env_count_cur = conn.execute("SELECT COUNT(*) FROM environments")
            env_count = env_count_cur.fetchone()[0]
            if env_count == 0:
                # Insert distinct api_url values from profiles with requires_auth = 0 (False)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO environments (api_url, requires_auth)
                    SELECT DISTINCT api_url, 0 FROM profiles
                    """
                )

                # Also ensure the current environment exists as a row
                cur_env_cursor = conn.execute(
                    "SELECT value FROM settings WHERE key = 'current_environment_api_url'"
                )
                cur_env_row = cur_env_cursor.fetchone()
                if cur_env_row:
                    conn.execute(
                        "INSERT OR IGNORE INTO environments (api_url, requires_auth, min_llamactl_version) VALUES (?, ?, ?)",
                        (
                            cur_env_row[0],
                            1 if DEFAULT_ENVIRONMENT.requires_auth else 0,
                            DEFAULT_ENVIRONMENT.min_llamactl_version,
                        ),
                    )

            conn.commit()

    def create_profile(
        self,
        name: str,
        api_url: str,
        project_id: str,
        api_key: str | None = None,
    ) -> Auth:
        """Create a new auth profile"""
        if not project_id.strip():
            raise ValueError("Project ID is required")
        profile = Auth(
            name=name,
            api_url=api_url,
            project_id=project_id,
            api_key=api_key,
        )

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO profiles (name, api_url, project_id, api_key) VALUES (?, ?, ?, ?)",
                    (
                        profile.name,
                        profile.api_url,
                        profile.project_id,
                        profile.api_key,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"Profile '{name}' already exists")

        return profile

    def get_profile(self, name: str, env_url: str) -> Auth | None:
        """Get a profile by name"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT name, api_url, project_id, api_key FROM profiles WHERE name = ? AND api_url = ?",
                (name, env_url),
            ).fetchone()
            if row:
                return _to_auth(row)
        return None

    def list_profiles(self, env_url: str) -> list[Auth]:
        """List all profiles"""
        with sqlite3.connect(self.db_path) as conn:
            return [
                _to_auth(row)
                for row in conn.execute(
                    "SELECT name, api_url, project_id, api_key FROM profiles WHERE api_url = ? ORDER BY name",
                    (env_url,),
                ).fetchall()
            ]

    def delete_profile(self, name: str, env_url: str) -> bool:
        """Delete a profile by name. Returns True if deleted, False if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM profiles WHERE name = ? AND api_url = ?", (name, env_url)
            )
            conn.commit()

            # If this was the active profile, clear it
            if self.get_settings_current_profile_name() == name:
                self.set_settings_current_profile(None)

            return cursor.rowcount > 0

    def set_settings_current_profile(self, name: str | None):
        """Set or clear the current active profile.

        If name is None, the setting is removed.
        """
        with sqlite3.connect(self.db_path) as conn:
            if name is None:
                conn.execute("DELETE FROM settings WHERE key = 'current_profile'")
            else:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_profile', ?)",
                    (name,),
                )
            conn.commit()

    def get_settings_current_profile_name(self) -> str | None:
        """Get the name of the current active profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM settings WHERE key = 'current_profile'"
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def get_current_profile(self, env_url: str) -> Auth | None:
        """Get the current active profile"""
        current_name = self.get_settings_current_profile_name()
        if current_name:
            return self.get_profile(current_name, env_url)
        return None

    def set_project(self, profile_name: str, env_url: str, project_id: str) -> bool:
        """Set the project for a profile. Returns True if profile exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE profiles SET project_id = ? WHERE name = ? AND api_url = ?",
                (project_id, profile_name, env_url),
            )
            conn.commit()
            return cursor.rowcount > 0

    # Environment management APIs
    def create_or_update_environment(
        self, api_url: str, requires_auth: bool, min_llamactl_version: str | None = None
    ) -> None:
        """Create or update an environment row."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO environments (api_url, requires_auth, min_llamactl_version) VALUES (?, ?, ?)",
                (api_url, 1 if requires_auth else 0, min_llamactl_version),
            )
            conn.commit()

    def get_environment(self, api_url: str) -> Environment | None:
        """Retrieve an environment by URL."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT api_url, requires_auth, min_llamactl_version FROM environments WHERE api_url = ?",
                (api_url,),
            ).fetchone()
            if row:
                return _to_environment(row)
        return None

    def list_environments(self) -> list[Environment]:
        """List all environments."""
        with sqlite3.connect(self.db_path) as conn:
            envs = [
                _to_environment(row)
                for row in conn.execute(
                    "SELECT api_url, requires_auth, min_llamactl_version FROM environments ORDER BY api_url"
                ).fetchall()
            ]
            if not envs:
                envs = [DEFAULT_ENVIRONMENT]
            return envs

    def set_settings_current_environment(self, api_url: str) -> None:
        """Set the current environment by URL.

        Requires the environment row to already exist (validated elsewhere, e.g. via
        a probe before creation). Raises ValueError if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_environment_api_url', ?)",
                (api_url,),
            )
            conn.commit()

    def get_current_environment(self) -> Environment:
        """Get the current environment.

        Ensures there is a settings entry and a corresponding row in `environments`.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM settings WHERE key = 'current_environment_api_url'"
            )
            row = cursor.fetchone()
            api_url = row[0] if row else DEFAULT_ENVIRONMENT.api_url
            if not row:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_environment_api_url', ?)",
                    (api_url,),
                )

            # Ensure environment exists
            conn.execute(
                "INSERT OR IGNORE INTO environments (api_url, requires_auth, min_llamactl_version) VALUES (?, ?, ?)",
                (
                    api_url,
                    1 if DEFAULT_ENVIRONMENT.requires_auth else 0,
                    DEFAULT_ENVIRONMENT.min_llamactl_version,
                ),
            )

            # Read the environment
            env_row = conn.execute(
                "SELECT api_url, requires_auth, min_llamactl_version FROM environments WHERE api_url = ?",
                (api_url,),
            ).fetchone()
            if env_row:
                return _to_environment(env_row)

        # If we somehow got here without returning, raise an error
        raise RuntimeError("Failed to load current environment")

    def delete_environment(self, api_url: str) -> bool:
        """Delete an environment and all associated profiles.

        Returns True if the environment existed and was deleted, False otherwise.
        If the deleted environment was current, switch current to the default URL.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Check existence
            exists_cursor = conn.execute(
                "SELECT 1 FROM environments WHERE api_url = ?",
                (api_url,),
            )
            if exists_cursor.fetchone() is None:
                return False

            # Delete profiles tied to this environment
            conn.execute("DELETE FROM profiles WHERE api_url = ?", (api_url,))

            # Delete environment row
            conn.execute("DELETE FROM environments WHERE api_url = ?", (api_url,))

            # If current environment is this one, reset to default
            setting_cursor = conn.execute(
                "SELECT value FROM settings WHERE key = 'current_environment_api_url'"
            )
            row = setting_cursor.fetchone()
            if row and row[0] == api_url:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_environment_api_url', ?)",
                    (DEFAULT_ENVIRONMENT.api_url,),
                )

            conn.commit()
            return True


# Global config manager instance
config_manager = ConfigManager()
