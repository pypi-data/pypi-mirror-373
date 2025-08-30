"""Textual-based forms for CLI interactions"""

from dataclasses import dataclass
from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    HorizontalGroup,
)
from textual.validation import Length
from textual.widgets import Button, Input, Label, Static

from ..config import Profile, config_manager


@dataclass
class ProfileForm:
    """Form data for profile editing/creation"""

    name: str = ""
    api_url: str = ""
    active_project_id: str = ""
    existing_name: str | None = None

    @classmethod
    def from_profile(cls, profile: Profile) -> "ProfileForm":
        """Create form from existing profile"""
        return cls(
            name=profile.name,
            api_url=profile.api_url,
            active_project_id=profile.active_project_id or "",
        )


class ProfileEditApp(App[ProfileForm | None]):
    """Textual app for editing profiles"""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self, initial_data: ProfileForm):
        super().__init__()
        self.form_data = initial_data

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_key(self, event: events.Key) -> None:
        """Handle key events, including Ctrl+C"""
        if event.key == "ctrl+c":
            self.exit(None)

    def compose(self) -> ComposeResult:
        with Container(classes="form-container"):
            title = "Edit Profile" if self.form_data.existing_name else "Create Profile"
            yield Static(title, classes="primary-message")
            yield Static("", id="error-message", classes="error-message hidden")
            with Static(classes="two-column-form-grid"):
                yield Label(
                    "Profile Name: *", classes="required form-label", shrink=True
                )
                yield Input(
                    value=self.form_data.name,
                    placeholder="Enter profile name",
                    validators=[Length(minimum=1)],
                    id="name",
                    compact=True,
                )
                yield Label("API URL: *", classes="required form-label", shrink=True)
                yield Input(
                    value=self.form_data.api_url,
                    placeholder="http://prod-cloud-llama-deploy",
                    validators=[Length(minimum=1)],
                    id="api_url",
                    compact=True,
                )
                yield Label("Project ID:", classes="form-label", shrink=True)
                yield Input(
                    value=self.form_data.active_project_id,
                    placeholder="Optional project ID",
                    id="project_id",
                    compact=True,
                )
            with HorizontalGroup(classes="button-row"):
                yield Button("Save", variant="primary", id="save", compact=True)
                yield Button("Cancel", variant="default", id="cancel", compact=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            if self._validate_form():
                result = self._get_form_data()
                try:
                    if result.existing_name:
                        config_manager.delete_profile(result.existing_name)
                    profile = config_manager.create_profile(
                        result.name,
                        result.api_url,
                        result.active_project_id,
                    )
                    self.exit(profile)
                except Exception as e:
                    self._handle_error(e)

        elif event.button.id == "cancel":
            self.exit(None)

    def _handle_error(self, error: Exception) -> None:
        error_message = self.query_one("#error-message", Static)
        error_message.update(f"Error creating profile: {error}")
        error_message.add_class("visible")

    def _validate_form(self) -> bool:
        """Validate required fields"""
        name_input = self.query_one("#name", Input)
        api_url_input = self.query_one("#api_url", Input)
        error_message = self.query_one("#error-message", Static)

        errors = []

        # Clear previous error state
        name_input.remove_class("error")
        api_url_input.remove_class("error")

        if not name_input.value.strip():
            name_input.add_class("error")
            errors.append("Profile name is required")

        if not api_url_input.value.strip():
            api_url_input.add_class("error")
            errors.append("API URL is required")

        if errors:
            error_message.update("; ".join(errors))
            error_message.add_class("visible")
            return False
        else:
            error_message.update("")
            error_message.remove_class("visible")
            return True

    def _get_form_data(self) -> ProfileForm:
        """Extract form data from inputs"""
        name_input = self.query_one("#name", Input)
        api_url_input = self.query_one("#api_url", Input)
        project_id_input = self.query_one("#project_id", Input)

        return ProfileForm(
            name=name_input.value.strip(),
            api_url=api_url_input.value.strip(),
            active_project_id=project_id_input.value.strip(),
            existing_name=self.form_data.existing_name,
        )


def edit_profile_form(profile: Profile) -> ProfileForm | None:
    """Launch profile edit form and return result"""
    initial_data = ProfileForm.from_profile(profile)
    initial_data.existing_name = profile.name or None
    app = ProfileEditApp(initial_data)
    return app.run()


def create_profile_form() -> ProfileForm | None:
    """Launch profile creation form and return result"""
    return edit_profile_form(
        Profile(
            name="", api_url="http://prod-cloud-llama-deploy", active_project_id=None
        )
    )
