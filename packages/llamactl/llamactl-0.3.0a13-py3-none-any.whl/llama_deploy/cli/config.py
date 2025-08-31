"""Configuration and profile management for llamactl"""

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Profile:
    """Profile configuration"""

    name: str
    api_url: str
    project_id: str
    api_key_auth_token: str | None = None


class ConfigManager:
    """Manages profiles and configuration using SQLite"""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.db_path = self.config_dir / "profiles.db"
        self._ensure_config_dir()
        self._init_database()
        self.default_control_plane_url = "https://api.llamacloud.com"

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

                # Add api_key_auth_token column if not already present
                mig_cursor = conn.execute("PRAGMA table_info(profiles)")
                mig_columns = [row[1] for row in mig_cursor.fetchall()]
                if "api_key_auth_token" not in mig_columns:
                    conn.execute(
                        "ALTER TABLE profiles ADD COLUMN api_key_auth_token TEXT"
                    )

            # Create tables with new schema (this will only create if they don't exist)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    name TEXT PRIMARY KEY,
                    api_url TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    api_key_auth_token TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            conn.commit()

    def create_profile(
        self,
        name: str,
        api_url: str,
        project_id: str,
        api_key_auth_token: str | None = None,
    ) -> Profile:
        """Create a new profile"""
        if not project_id.strip():
            raise ValueError("Project ID is required")
        profile = Profile(
            name=name,
            api_url=api_url,
            project_id=project_id,
            api_key_auth_token=api_key_auth_token,
        )

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO profiles (name, api_url, project_id, api_key_auth_token) VALUES (?, ?, ?, ?)",
                    (
                        profile.name,
                        profile.api_url,
                        profile.project_id,
                        profile.api_key_auth_token,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"Profile '{name}' already exists")

        return profile

    def get_profile(self, name: str) -> Profile | None:
        """Get a profile by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, api_url, project_id, api_key_auth_token FROM profiles WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            if row:
                return Profile(
                    name=row[0],
                    api_url=row[1],
                    project_id=row[2],
                    api_key_auth_token=row[3],
                )
        return None

    def list_profiles(self) -> List[Profile]:
        """List all profiles"""
        profiles = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, api_url, project_id, api_key_auth_token FROM profiles ORDER BY name"
            )
            for row in cursor.fetchall():
                profiles.append(
                    Profile(
                        name=row[0],
                        api_url=row[1],
                        project_id=row[2],
                        api_key_auth_token=row[3],
                    )
                )
        return profiles

    def delete_profile(self, name: str) -> bool:
        """Delete a profile by name. Returns True if deleted, False if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM profiles WHERE name = ?", (name,))
            conn.commit()

            # If this was the active profile, clear it
            if self.get_current_profile_name() == name:
                self.set_current_profile(None)

            return cursor.rowcount > 0

    def set_current_profile(self, name: str | None):
        """Set the current active profile"""
        with sqlite3.connect(self.db_path) as conn:
            if name is None:
                conn.execute("DELETE FROM settings WHERE key = 'current_profile'")
            else:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('current_profile', ?)",
                    (name,),
                )
            conn.commit()

    def get_current_profile_name(self) -> str | None:
        """Get the name of the current active profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM settings WHERE key = 'current_profile'"
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def get_current_profile(self) -> Profile | None:
        """Get the current active profile"""
        current_name = self.get_current_profile_name()
        if current_name:
            return self.get_profile(current_name)
        profiles = self.list_profiles()
        if len(profiles) == 1:
            return profiles[0]
        return None

    def set_project(self, profile_name: str, project_id: str) -> bool:
        """Set the project for a profile. Returns True if profile exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE profiles SET project_id = ? WHERE name = ?",
                (project_id, profile_name),
            )
            conn.commit()
            return cursor.rowcount > 0

    def set_default_control_plane_url(self, url: str) -> None:
        """Set the default control plane URL for the current session"""
        self.default_control_plane_url = url

    def get_project(self, profile_name: str) -> str | None:
        """Get the project for a profile"""
        profile = self.get_profile(profile_name)
        return profile.project_id if profile else None

    def set_api_key_auth_token(
        self, profile_name: str, api_key_auth_token: str | None
    ) -> bool:
        """Set the API key auth token for a profile. Returns True if profile exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE profiles SET api_key_auth_token = ? WHERE name = ?",
                (api_key_auth_token, profile_name),
            )
            conn.commit()
            return cursor.rowcount > 0


# Global config manager instance
config_manager = ConfigManager()
