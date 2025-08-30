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
    active_project_id: str | None = None


class ConfigManager:
    """Manages profiles and configuration using SQLite"""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.db_path = self.config_dir / "profiles.db"
        self._ensure_config_dir()
        self._init_database()

    def _get_config_dir(self) -> Path:
        """Get the configuration directory path based on OS"""
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

            if "project_id" in columns and "active_project_id" not in columns:
                # Migrate old schema to new schema
                conn.execute("""
                    ALTER TABLE profiles RENAME COLUMN project_id TO active_project_id
                """)

            # Create tables with new schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    name TEXT PRIMARY KEY,
                    api_url TEXT NOT NULL,
                    active_project_id TEXT
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
        self, name: str, api_url: str, active_project_id: str | None = None
    ) -> Profile:
        """Create a new profile"""
        profile = Profile(
            name=name, api_url=api_url, active_project_id=active_project_id
        )

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO profiles (name, api_url, active_project_id) VALUES (?, ?, ?)",
                    (profile.name, profile.api_url, profile.active_project_id),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"Profile '{name}' already exists")

        return profile

    def get_profile(self, name: str) -> Profile | None:
        """Get a profile by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, api_url, active_project_id FROM profiles WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            if row:
                return Profile(name=row[0], api_url=row[1], active_project_id=row[2])
        return None

    def list_profiles(self) -> List[Profile]:
        """List all profiles"""
        profiles = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, api_url, active_project_id FROM profiles ORDER BY name"
            )
            for row in cursor.fetchall():
                profiles.append(
                    Profile(name=row[0], api_url=row[1], active_project_id=row[2])
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
        return None

    def set_active_project(self, profile_name: str, project_id: str | None) -> bool:
        """Set the active project for a profile. Returns True if profile exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE profiles SET active_project_id = ? WHERE name = ?",
                (project_id, profile_name),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_active_project(self, profile_name: str) -> str | None:
        """Get the active project for a profile"""
        profile = self.get_profile(profile_name)
        return profile.active_project_id if profile else None


# Global config manager instance
config_manager = ConfigManager()
