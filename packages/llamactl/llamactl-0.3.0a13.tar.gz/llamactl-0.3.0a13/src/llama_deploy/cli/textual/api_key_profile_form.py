"""Textual-based forms for CLI interactions"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from llama_deploy.core.client.manage_client import ClientError, ControlPlaneClient
from llama_deploy.core.schema.projects import ProjectSummary
from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalGroup, Widget
from textual.content import Content
from textual.reactive import reactive
from textual.validation import Length
from textual.widgets import Button, Input, Label, Select, Static

from ..config import Profile, config_manager

logger = logging.getLogger(__name__)


class ValidationState(Enum):
    """States for API validation"""

    IDLE = "idle"
    VALIDATING = "validating"
    VALID = "valid"
    NETWORK_ERROR = "network_error"
    AUTH_REQUIRED = "auth_required"
    AUTH_INVALID = "auth_invalid"
    ERROR = "error"


@dataclass
class APIKeyProfileForm:
    """Form data for profile editing/creation"""

    name: str = ""
    api_url: str = ""
    project_id: str = ""
    api_key_auth_token: str = ""
    existing_name: str | None = None

    @classmethod
    def from_profile(cls, profile: Profile) -> "APIKeyProfileForm":
        """Create form from existing profile"""
        return cls(
            name=profile.name,
            api_url=profile.api_url,
            project_id=profile.project_id,
            api_key_auth_token=profile.api_key_auth_token or "",
        )

    def to_profile(self) -> Profile:
        """Create profile from form data"""
        return Profile(
            name=self.name,
            api_url=self.api_url,
            project_id=self.project_id,
            api_key_auth_token=self.api_key_auth_token,
        )


def validate_api_connection(
    api_url: str, api_key: str | None = None
) -> tuple[ValidationState, List[ProjectSummary], str]:
    """Validate API connection and return projects if successful"""
    try:
        # Create ControlPlaneClient with optional auth
        client = ControlPlaneClient(api_url, api_key)

        # Try to list projects (async client)
        projects = asyncio.run(client.list_projects())

        return ValidationState.VALID, projects, "Connected successfully"

    except ClientError as e:
        if e.status_code == 401:
            return ValidationState.AUTH_INVALID, [], "API key is not valid"
        elif e.status_code == 403:
            return ValidationState.AUTH_REQUIRED, [], "API requires an API key"
        elif e.status_code and 400 <= e.status_code < 500:
            return ValidationState.NETWORK_ERROR, [], "Invalid API URL"
        else:
            return ValidationState.ERROR, [], f"Server error: {str(e)}"
    except Exception as e:
        error_msg = str(e).lower()
        if (
            "connection" in error_msg
            or "timeout" in error_msg
            or "resolve" in error_msg
        ):
            return ValidationState.NETWORK_ERROR, [], "Cannot connect to API URL"
        else:
            return ValidationState.ERROR, [], f"Connection error: {str(e)}"


class APIKeyProfileEditApp(App[APIKeyProfileForm | None]):
    """Textual app for editing profiles"""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    name: reactive[str] = reactive("")
    api_url: reactive[str] = reactive("")
    project_id: reactive[str] = reactive("")
    api_key_auth_token: reactive[str] = reactive("")

    validation_state: reactive[ValidationState] = reactive(ValidationState.IDLE)
    validation_message: reactive[str] = reactive("")

    # Structural toggles → recompose when these change
    available_projects: reactive[List[ProjectSummary]] = reactive([], recompose=True)
    manual_project_mode: reactive[bool] = reactive(False, recompose=True)
    api_key_required: reactive[bool] = reactive(False, recompose=True)

    # Error banner content
    form_error_message: reactive[str] = reactive("", recompose=True)

    def __init__(
        self, initial_data: APIKeyProfileForm, prompt_message: str | None = None
    ):
        super().__init__()
        self.form_data = initial_data
        self.prompt_message = prompt_message
        # Track last validated values to prevent redundant validation
        self._last_validated_api_url = ""
        self._last_validated_api_key = ""
        # Initialize fields from provided data
        self.name = self.form_data.name
        self.api_url = self.form_data.api_url
        self.project_id = self.form_data.project_id
        self.api_key_auth_token = self.form_data.api_key_auth_token or ""

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        # Initialize tracked values from form data to prevent unnecessary initial validation
        # Force initial validation by resetting last validated sentinels
        self._last_validated_api_url = ""
        self._last_validated_api_key = ""

        # Trigger initial validation if we have API URL
        if self.api_url:
            self._trigger_validation()

    # ----- Reactive watchers (targeted updates to avoid focus loss) -----
    def watch_validation_message(self, old: str, new: str) -> None:
        try:
            message_widget = self.query_one("#validation-message", Static)
            message_widget.update(new)
            # Toggle visibility
            message_widget.display = bool(new)
            # Update style based on state
            css_class = (
                "success-message"
                if self.validation_state == ValidationState.VALID
                else "warning-message"
            )
            message_widget.set_classes(f"{css_class} full-width")
        except Exception:
            pass

    def watch_validation_state(
        self, old: ValidationState, new: ValidationState
    ) -> None:
        # Re-use same updater for message to refresh styling
        self.watch_validation_message(self.validation_message, self.validation_message)

    def on_key(self, event: events.Key) -> None:
        """Handle key events, including Ctrl+C"""
        if event.key == "ctrl+c":
            self.exit(None)

    @work(exclusive=True, thread=True)
    async def _validate_api_worker(self) -> None:
        """Worker to validate API connection"""
        # Use the latest state rather than querying widgets (avoids race conditions)
        api_url = self.api_url.strip()
        api_key_value = self.api_key_auth_token.strip()
        api_key = api_key_value or None

        # Check if values have actually changed since last validation
        if (
            api_url == self._last_validated_api_url
            and api_key == self._last_validated_api_key
        ):
            logger.debug(
                f"Skipping validation - no changes detected (URL: {api_url}, Key: {'***' if api_key else 'None'})"
            )
            return

        if not api_url:
            self.validation_state = ValidationState.IDLE
            self.validation_message = ""
            self.available_projects = []
            self.api_key_required = False
            # Reset tracked values when empty
            self._last_validated_api_url = ""
            self._last_validated_api_key = ""
            return

        # Update tracked values before validation
        self._last_validated_api_url = api_url
        self._last_validated_api_key = api_key

        self.validation_state = ValidationState.VALIDATING
        self.validation_message = "Validating connection..."
        logger.debug(
            f"Validating connection to {api_url} with API key {'***' if api_key else 'None'}"
        )
        state, projects, message = validate_api_connection(api_url, api_key)
        logger.debug(
            f"Validation result: {state}, {len(projects)} projects, '{message}'"
        )

        # Commit validation results
        self.validation_state = state
        self.validation_message = message
        self.available_projects = projects
        self.api_key_required = state == ValidationState.AUTH_REQUIRED

        # If we got projects but user is in manual mode and project is empty, suggest switching
        if state == ValidationState.VALID and projects and self.manual_project_mode:
            try:
                project_input = self.query_one("#project_id", Input)
                if not project_input.value.strip():
                    self.validation_message = f"Connected successfully. Found {len(projects)} projects - consider using project selector."
            except Exception:
                # Project input might not exist in selector mode
                pass

    def _trigger_validation(self) -> None:
        """Trigger validation worker"""
        self._validate_api_worker()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input enter/tab to trigger validation"""
        if event.input.id == "api_url":
            self.api_url = event.input.value.strip()
            self._trigger_validation()
        elif event.input.id == "api_key_auth_token":
            self.api_key_auth_token = event.input.value.strip()
            self._trigger_validation()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes with debouncing to avoid excessive validation"""
        if event.input.id in ("api_url", "api_key_auth_token", "name", "project_id"):
            # Cancel any existing validation timer
            if hasattr(self, "_validation_timer") and self._validation_timer:
                self._validation_timer.stop()

            # Update state from input immediately
            if event.input.id == "api_url":
                self.api_url = event.value.strip()
            elif event.input.id == "api_key_auth_token":
                self.api_key_auth_token = event.value.strip()
            elif event.input.id == "name":
                self.name = event.value.strip()
            elif event.input.id == "project_id":
                self.project_id = event.value.strip()

            # Set a new timer to validate after 1 second of no typing (only for api fields)
            if event.input.id in ("api_url", "api_key_auth_token"):
                self._validation_timer = self.set_timer(1.0, self._trigger_validation)

    def compose(self) -> ComposeResult:
        with Container(classes="form-container"):
            title = (
                "Edit Profile"
                if self.form_data.existing_name
                else "Create API Key Profile"
            )
            yield Static(title, classes="primary-message")
            yield Static(
                Content.from_markup(
                    "Configure a new API key profile to authenticate with the LlamaCloud control plane. This is stored locally in your OS's config directory."
                ),
                classes="info-message mb-1",
            )
            yield Static(
                self.form_error_message,
                id="error-message",
                classes=f"error-message {'hidden visible' if self.form_error_message else 'hidden'}",
            )

            # Validation status message (always present but hidden when empty)
            css_class = (
                "success-message"
                if self.validation_state == ValidationState.VALID
                else "warning-message"
            )
            yield Static(
                self.validation_message,
                id="validation-message",
                classes=f"{css_class} full-width {'hidden' if not self.validation_message else ''}",
            )

            with Static(classes="two-column-form-grid mb-1"):
                yield Label(
                    Content.from_markup("Profile Name[red]*[/]"),
                    classes="required form-label",
                    shrink=True,
                )
                yield Input(
                    value=self.name,
                    placeholder="A memorable name for this API key",
                    validators=[Length(minimum=1)],
                    id="name",
                    compact=True,
                )
                yield Label(
                    Content.from_markup("API URL[red]*[/]"),
                    classes="required form-label",
                    shrink=True,
                )
                yield Input(
                    value=self.api_url,
                    placeholder="https://api.cloud.llamaindex.ai",
                    validators=[Length(minimum=1)],
                    id="api_url",
                    compact=True,
                )

                # API Key field - make required if auth is required
                api_key_label = (
                    "API Key[red]*[/]" if self.api_key_required else "API Key"
                )
                yield Label(
                    Content.from_markup(api_key_label),
                    id="api-key-label",
                    classes="form-label",
                    shrink=True,
                )
                yield Input(
                    value=self.api_key_auth_token,
                    placeholder="API key auth token. Only required if control plane is authenticated",
                    id="api_key_auth_token",
                    validators=[Length(minimum=1)] if self.api_key_required else [],
                    compact=True,
                )
                # Project selection area
                yield Label(
                    Content.from_markup("Project ID[red]*[/]"),
                    classes="required form-label",
                    shrink=True,
                )

                # Project input area with toggle
                with Widget(id="project-input-area"):
                    if not self.manual_project_mode and self.available_projects:
                        # Show project selector
                        options = [
                            (
                                f"{p.project_name} ({p.deployment_count} deployments)",
                                p.project_id,
                            )
                            for p in self.available_projects
                        ]
                        # Find a valid initial value
                        project_ids = [p.project_id for p in self.available_projects]
                        initial_value = (
                            self.project_id
                            if self.project_id in project_ids
                            else project_ids[0]
                            if project_ids
                            else None
                        )

                        if initial_value is not None:
                            yield Select(
                                options=options,
                                value=initial_value,
                                id="project_select",
                                allow_blank=False,
                                compact=True,
                            )
                        else:
                            # Fallback to manual input if no projects available
                            yield Input(
                                value=self.project_id,
                                placeholder="Enter project ID manually",
                                validators=[Length(minimum=1)],
                                id="project_id",
                                compact=True,
                            )
                    else:
                        # Show manual input
                        yield Input(
                            value=self.project_id,
                            placeholder="Enter project ID manually",
                            validators=[Length(minimum=1)],
                            id="project_id",
                            compact=True,
                        )

                yield Static()
                # Mode toggle button
                if self.available_projects:
                    toggle_text = (
                        "Enter Project ID Manually"
                        if not self.manual_project_mode
                        else "Select Existing Project"
                    )
                    yield Button(
                        toggle_text,
                        id="toggle_project_mode",
                        classes="align-right",
                        variant="default",
                        compact=True,
                    )
                else:
                    yield Static()

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
                        result.project_id,
                        result.api_key_auth_token,
                    )
                    self.exit(profile)
                except Exception as e:
                    self._handle_error(e)

        elif event.button.id == "cancel":
            self.exit(None)

        elif event.button.id == "toggle_project_mode":
            # Keep current project ID when switching modes
            current_project_id = self._get_current_project_id()
            self.manual_project_mode = not self.manual_project_mode
            self.project_id = current_project_id

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle project selection changes"""
        if event.select.id == "project_select" and event.value:
            # Update state when project is selected
            self.project_id = event.value
            logger.debug(f"Project selected: {event.value}")

    def _handle_error(self, error: Exception) -> None:
        self.form_error_message = f"Error creating profile: {error}"

    def _validate_form(self) -> bool:
        """Validate required fields"""
        name_input = self.query_one("#name", Input)
        api_url_input = self.query_one("#api_url", Input)
        api_key_input = self.query_one("#api_key_auth_token", Input)
        errors = []

        # Clear previous error state
        name_input.remove_class("error")
        api_url_input.remove_class("error")
        api_key_input.remove_class("error")

        if not name_input.value.strip():
            name_input.add_class("error")
            errors.append("Profile name is required")

        if not api_url_input.value.strip():
            api_url_input.add_class("error")
            errors.append("API URL is required")

        # Validate API key if required
        if self.api_key_required and not api_key_input.value.strip():
            api_key_input.add_class("error")
            errors.append("API key is required")

        # Validate project ID
        project_id = self._get_current_project_id()
        if not project_id:
            # Add error class to appropriate element
            if self.manual_project_mode or not self.available_projects:
                try:
                    project_input = self.query_one("#project_id", Input)
                    project_input.add_class("error")
                except Exception:
                    pass
            else:
                try:
                    project_select = self.query_one("#project_select", Select)
                    project_select.add_class("error")
                except Exception:
                    pass
            errors.append("Project ID is required")

        if errors:
            self.form_error_message = "; ".join(errors)
            return False
        else:
            self.form_error_message = ""
            return True

    def _get_current_project_id(self) -> str:
        """Get the current project ID from either selector or input"""
        if self.manual_project_mode or not self.available_projects:
            try:
                project_input = self.query_one("#project_id", Input)
                return project_input.value.strip()
            except Exception:
                return ""
        else:
            try:
                project_select = self.query_one("#project_select", Select)
                return project_select.value or ""
            except Exception:
                return ""

    def _get_form_data(self) -> APIKeyProfileForm:
        """Extract form data from inputs"""
        name_input = self.query_one("#name", Input)
        api_url_input = self.query_one("#api_url", Input)
        api_key_input = self.query_one("#api_key_auth_token", Input)

        return APIKeyProfileForm(
            name=name_input.value.strip(),
            api_url=api_url_input.value.strip(),
            project_id=self._get_current_project_id(),
            api_key_auth_token=api_key_input.value.strip(),
            existing_name=self.form_data.existing_name,
        )


def edit_api_key_profile_form(
    profile: Profile,
    prompt_message: str | None = None,
) -> APIKeyProfileForm | None:
    """Launch profile edit form and return result"""
    initial_data = APIKeyProfileForm.from_profile(profile)
    initial_data.existing_name = profile.name or None
    app = APIKeyProfileEditApp(initial_data, prompt_message)
    return app.run()


def create_api_key_profile_form(
    api_url: str = "https://api.cloud.llamaindex.ai",
    name: str | None = None,
    project_id: str | None = None,
    api_key_auth_token: str | None = None,
    prompt_message: str | None = None,
) -> APIKeyProfileForm | None:
    """Launch profile creation form and return result"""
    return edit_api_key_profile_form(
        Profile(
            name=name or "",
            api_url=api_url,
            project_id=project_id or "",
            api_key_auth_token=api_key_auth_token or "",
        ),
        prompt_message,
    )
