"""Textual-based deployment forms for CLI interactions"""

import dataclasses
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from llama_deploy.cli.client import get_project_client as get_client
from llama_deploy.cli.env import load_env_secrets_from_string
from llama_deploy.cli.textual.deployment_help import (
    DeploymentHelpBackMessage,
    DeploymentHelpWidget,
)
from llama_deploy.cli.textual.deployment_monitor import (
    DeploymentMonitorWidget,
    MonitorCloseMessage,
)
from llama_deploy.cli.textual.git_validation import (
    GitValidationWidget,
    ValidationCancelMessage,
    ValidationResultMessage,
)
from llama_deploy.cli.textual.secrets_form import SecretsWidget
from llama_deploy.core.deployment_config import (
    DEFAULT_DEPLOYMENT_NAME,
    read_deployment_config,
)
from llama_deploy.core.git.git_util import (
    get_current_branch,
    get_git_root,
    is_git_repo,
    list_remotes,
)
from llama_deploy.core.schema.deployments import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentUpdate,
)
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalGroup, Widget
from textual.content import Content
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Length
from textual.widgets import Button, Input, Label, Static


@dataclass
class DeploymentForm:
    """Form data for deployment editing/creation"""

    name: str = ""
    # unique id, generated from the name
    id: str | None = None
    repo_url: str = ""
    git_ref: str = "main"
    deployment_file_path: str = ""
    personal_access_token: str = ""
    # indicates if the deployment has a personal access token (value is unknown)
    has_existing_pat: bool = False
    # secrets that have been added
    secrets: dict[str, str] = field(default_factory=dict)
    # initial secrets, values unknown
    initial_secrets: set[str] = field(default_factory=set)
    # initial secrets that have been removed
    removed_secrets: set[str] = field(default_factory=set)
    # if the deployment is being edited
    is_editing: bool = False

    @classmethod
    def from_deployment(cls, deployment: DeploymentResponse) -> "DeploymentForm":
        secret_names = deployment.secret_names or []

        return DeploymentForm(
            name=deployment.name,
            id=deployment.id,
            repo_url=deployment.repo_url,
            git_ref=deployment.git_ref or "main",
            deployment_file_path=deployment.deployment_file_path,
            personal_access_token="",  # Always start empty for security
            has_existing_pat=deployment.has_personal_access_token,
            secrets={},
            initial_secrets=set(secret_names),
            is_editing=True,
        )

    def to_update(self) -> DeploymentUpdate:
        """Convert form data to API format"""

        secrets: dict[str, str | None] = self.secrets.copy()
        for secret in self.removed_secrets:
            secrets[secret] = None

        data = DeploymentUpdate(
            repo_url=self.repo_url,
            git_ref=self.git_ref or "main",
            deployment_file_path=self.deployment_file_path or None,
            personal_access_token=(
                ""
                if self.personal_access_token is None and not self.has_existing_pat
                else self.personal_access_token
            ),
            secrets=secrets,
        )

        return data

    def to_create(self) -> DeploymentCreate:
        """Convert form data to API format"""

        return DeploymentCreate(
            name=self.name,
            repo_url=self.repo_url,
            deployment_file_path=self.deployment_file_path or None,
            git_ref=self.git_ref or "main",
            personal_access_token=self.personal_access_token,
            secrets=self.secrets,
        )


class DeploymentFormWidget(Widget):
    """Widget containing all deployment form logic and reactive state"""

    DEFAULT_CSS = """
    DeploymentFormWidget {
        layout: vertical;
        height: auto;
    }
    """

    form_data: reactive[DeploymentForm] = reactive(DeploymentForm(), recompose=True)
    error_message: reactive[str] = reactive("", recompose=True)

    def __init__(self, initial_data: DeploymentForm, save_error: str | None = None):
        super().__init__()
        self.form_data = initial_data
        self.original_form_data = initial_data
        self.error_message = save_error or ""

    def compose(self) -> ComposeResult:
        title = "Edit Deployment" if self.form_data.is_editing else "Create Deployment"

        yield Static(
            Content.from_markup(
                f"{title} [italic][@click=app.show_help()]More info[/][/italic]"
            ),
            classes="primary-message",
        )
        yield Static(
            self.error_message,
            id="error-message",
            classes="error-message " + ("visible" if self.error_message else "hidden"),
        )

        # Main deployment fields
        with Widget(classes="two-column-form-grid"):
            yield Label(
                "Deployment Name: *", classes="required form-label", shrink=True
            )
            yield Input(
                value=self.form_data.name,
                placeholder="Enter deployment name",
                validators=[Length(minimum=1)],
                id="name",
                disabled=self.form_data.is_editing,
                classes="disabled" if self.form_data.is_editing else "",
                compact=True,
            )

            yield Label("Repository URL: *", classes="required form-label", shrink=True)
            yield Input(
                value=self.form_data.repo_url,
                placeholder="https://github.com/user/repo",
                validators=[Length(minimum=1)],
                id="repo_url",
                compact=True,
            )

            yield Label("Git Reference:", classes="form-label", shrink=True)
            yield Input(
                value=self.form_data.git_ref,
                placeholder="main, develop, v1.0.0, etc.",
                id="git_ref",
                compact=True,
            )

            yield Label("Config File:", classes="form-label", shrink=True)
            yield Input(
                value=self.form_data.deployment_file_path,
                placeholder="Optional path to config dir/file",
                id="deployment_file_path",
                compact=True,
            )
            yield Label("Personal Access Token:", classes="form-label", shrink=True)
            if self.form_data.has_existing_pat:
                yield Button(
                    "Change / Delete",
                    variant="default",
                    id="change_pat",
                    compact=True,
                )
            else:
                yield Input(
                    value=self.form_data.personal_access_token,
                    placeholder="Leave blank to clear"
                    if self.form_data.has_existing_pat
                    else "Optional",
                    password=True,
                    id="personal_access_token",
                    compact=True,
                )

        # Secrets section
        yield SecretsWidget(
            initial_secrets=self.form_data.secrets,
            prior_secrets=self.form_data.initial_secrets,
        )

        with HorizontalGroup(classes="button-row"):
            yield Button("Save", variant="primary", id="save", compact=True)
            yield Button("Cancel", variant="default", id="cancel", compact=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._save()
        elif event.button.id == "change_pat":
            updated_form = dataclasses.replace(self.resolve_form_data())
            updated_form.has_existing_pat = False
            updated_form.personal_access_token = ""
            self.form_data = updated_form
        elif event.button.id == "cancel":
            # Post message to parent app to handle cancel
            self.post_message(CancelFormMessage())

    def _save(self) -> None:
        self.form_data = self.resolve_form_data()
        if self._validate_form():
            # Post message to parent app to start validation
            self.post_message(StartValidationMessage(self.form_data))

    def _validate_form(self) -> bool:
        """Validate required fields"""
        name_input = self.query_one("#name", Input)
        repo_url_input = self.query_one("#repo_url", Input)

        errors = []

        # Clear previous error state
        name_input.remove_class("error")
        repo_url_input.remove_class("error")

        if not name_input.value.strip():
            name_input.add_class("error")
            errors.append("Deployment name is required")

        if not repo_url_input.value.strip():
            repo_url_input.add_class("error")
            errors.append("Repository URL is required")

        if errors:
            self._show_error("; ".join(errors))
            return False
        else:
            self._show_error("")
            return True

    def _show_error(self, message: str) -> None:
        """Show an error message"""
        self.error_message = message

    def resolve_form_data(self) -> DeploymentForm:
        """Extract form data from inputs"""
        name_input = self.query_one("#name", Input)
        repo_url_input = self.query_one("#repo_url", Input)
        git_ref_input = self.query_one("#git_ref", Input)
        deployment_file_input = self.query_one("#deployment_file_path", Input)

        # PAT input might not exist if there's an existing PAT
        try:
            pat_input = self.query_one("#personal_access_token", Input)
            pat_value = pat_input.value.strip()
        except Exception:
            pat_value = self.form_data.personal_access_token or ""

        # Get updated secrets from the secrets widget
        secrets_widget = self.query_one(SecretsWidget)
        updated_secrets = secrets_widget.get_updated_secrets()
        updated_prior_secrets = secrets_widget.get_updated_prior_secrets()

        return DeploymentForm(
            name=name_input.value.strip(),
            id=self.form_data.id,
            repo_url=repo_url_input.value.strip(),
            git_ref=git_ref_input.value.strip() or "main",
            deployment_file_path=deployment_file_input.value.strip(),
            personal_access_token=pat_value,
            secrets=updated_secrets,
            initial_secrets=self.original_form_data.initial_secrets,
            is_editing=self.original_form_data.is_editing,
            has_existing_pat=self.form_data.has_existing_pat,
            removed_secrets=self.original_form_data.initial_secrets.difference(
                updated_prior_secrets
            ),
        )


# Messages for communication between form widget and app
class SaveFormMessage(Message):
    def __init__(self, deployment: DeploymentResponse):
        super().__init__()
        self.deployment = deployment


class CancelFormMessage(Message):
    pass


class StartValidationMessage(Message):
    def __init__(self, form_data: DeploymentForm):
        super().__init__()
        self.form_data = form_data


class ShowHelpMessage(Message):
    def __init__(self, form_data: DeploymentForm):
        super().__init__()
        self.form_data = form_data


class HelpBackMessage(Message):
    pass


class DeploymentEditApp(App[DeploymentResponse | None]):
    """Textual app for editing/creating deployments"""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    # App states: 'form', 'validation', 'help', or 'monitor'
    current_state: reactive[str] = reactive("form", recompose=True)
    form_data: reactive[DeploymentForm] = reactive(DeploymentForm())
    save_error: reactive[str] = reactive("", recompose=True)
    saved_deployment = reactive[DeploymentResponse | None](None, recompose=True)

    def __init__(self, initial_data: DeploymentForm):
        super().__init__()
        self.initial_data = initial_data
        self.form_data = initial_data

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_key(self, event: events.Key) -> None:
        """Handle key events, including Ctrl+C"""
        if event.key == "ctrl+c":
            if self.current_state == "monitor" and self.saved_deployment is not None:
                self.exit(self.saved_deployment)
            else:
                self.exit(None)

    def compose(self) -> ComposeResult:
        is_slim = self.current_state != "monitor"
        with Container(classes="form-container" if is_slim else ""):
            if self.current_state == "form":
                yield DeploymentFormWidget(self.form_data, self.save_error)
            elif self.current_state == "validation":
                yield GitValidationWidget(
                    repo_url=self.form_data.repo_url,
                    deployment_id=self.form_data.id
                    if self.form_data.is_editing
                    else None,
                    pat=self.form_data.personal_access_token
                    if self.form_data.personal_access_token
                    else None,
                )
            elif self.current_state == "help":
                yield DeploymentHelpWidget()
            elif self.current_state == "monitor":
                deployment_id = (
                    self.saved_deployment.id if self.saved_deployment else ""
                )
                yield DeploymentMonitorWidget(deployment_id)
            else:
                yield Static("Unknown state: " + self.current_state)

    def action_show_help(self) -> None:
        widget = self.query("DeploymentFormWidget")
        if widget:
            typed_widget: DeploymentFormWidget = widget[0]
            self.form_data = typed_widget.resolve_form_data()

        self.current_state = "help"

    def on_deployment_help_back_message(
        self, message: DeploymentHelpBackMessage
    ) -> None:
        self.current_state = "form"

    def on_start_validation_message(self, message: StartValidationMessage) -> None:
        """Handle validation start message from form widget"""
        self.form_data = message.form_data
        self.save_error = ""  # Clear any previous errors
        self.current_state = "validation"

    async def on_validation_result_message(
        self, message: ValidationResultMessage
    ) -> None:
        """Handle validation success from git validation widget"""
        logging.info("validation result message", message)
        # Update form data with validated PAT if provided
        if message.pat is not None:
            updated_form = dataclasses.replace(self.form_data)
            updated_form.personal_access_token = message.pat
            # If PAT is being cleared (empty string), also clear the has_existing_pat flag
            if message.pat == "":
                updated_form.has_existing_pat = False
            self.form_data = updated_form

        # Proceed with save (async)
        await self._perform_save()

    def on_validation_cancel_message(self, message: ValidationCancelMessage) -> None:
        """Handle validation cancellation from git validation widget"""
        # Return to form, clearing any save error
        self.save_error = ""
        self.current_state = "form"

    def on_show_help_message(self, message: ShowHelpMessage) -> None:
        """Navigate to help view, preserving current form state."""
        self.form_data = message.form_data
        self.current_state = "help"

    def on_help_back_message(self, message: HelpBackMessage) -> None:
        """Return from help to form, keeping form state intact."""
        self.current_state = "form"

    async def _perform_save(self) -> None:
        """Actually save the deployment after validation"""
        logging.info("saving form data", self.form_data)
        result = self.form_data
        client = get_client()
        try:
            update_deployment = (
                await client.update_deployment(result.id, result.to_update())
                if result.is_editing
                else await client.create_deployment(result.to_create())
            )
            # Save and navigate to embedded monitor screen
            self.saved_deployment = update_deployment
            # Ensure form_data carries the new ID for any subsequent operations
            if not result.is_editing and update_deployment.id:
                updated_form = dataclasses.replace(self.form_data)
                updated_form.id = update_deployment.id
                updated_form.is_editing = True
                self.form_data = updated_form
            self.current_state = "monitor"
        except Exception as e:
            # Return to form and show error
            self.save_error = f"Error saving deployment: {e}"
            self.current_state = "form"

    def on_save_form_message(self, message: SaveFormMessage) -> None:
        """Handle save message from form widget (shouldn't happen with new flow)"""
        self.exit(message.deployment)

    def on_cancel_form_message(self, message: CancelFormMessage) -> None:
        """Handle cancel message from form widget"""
        self.exit(None)

    def on_monitor_close_message(self, _: MonitorCloseMessage) -> None:
        """Handle close from embedded monitor by exiting with saved deployment."""
        self.exit(self.saved_deployment)


def edit_deployment_form(
    deployment: DeploymentResponse,
) -> DeploymentResponse | None:
    """Launch deployment edit form and return result"""
    initial_data = DeploymentForm.from_deployment(deployment)
    app = DeploymentEditApp(initial_data)
    return app.run()


def create_deployment_form() -> DeploymentResponse | None:
    """Launch deployment creation form and return result"""
    initial_data = _initialize_deployment_data()
    app = DeploymentEditApp(initial_data)
    return app.run()


def _initialize_deployment_data() -> DeploymentForm:
    """
    initialize the deployment form data from the current git repo and .env file
    """

    repo_url: str | None = None
    git_ref: str | None = None
    secrets: dict[str, str] = {}
    name: str | None = None
    config_file_path: str | None = None
    if is_git_repo():
        seen = set[str]()
        remotes = list_remotes()
        candidate_origins = []
        for remote in remotes:
            normalized_url = _normalize_to_http(remote)
            if normalized_url not in seen:
                candidate_origins.append(normalized_url)
                seen.add(normalized_url)
        preferred_origin = sorted(
            candidate_origins, key=lambda x: "github.com" in x, reverse=True
        )
        if preferred_origin:
            repo_url = preferred_origin[0]
        git_ref = get_current_branch()
        root = get_git_root()
        if root != Path.cwd():
            config_file_path = str(Path.cwd().relative_to(root))

    if Path(".env").exists():
        secrets = load_env_secrets_from_string(Path(".env").read_text())
    try:
        config = read_deployment_config(Path("."), Path("."))
        if config.name != DEFAULT_DEPLOYMENT_NAME:
            name = config.name
    except Exception:
        pass

    form = DeploymentForm(
        name=name or "",
        repo_url=repo_url or "",
        git_ref=git_ref or "main",
        secrets=secrets,
        deployment_file_path=config_file_path or "",
    )
    return form


def _normalize_to_http(url: str) -> str:
    """
    normalize a git url to a best guess for a corresponding http(s) url
    """
    candidate = (url or "").strip()

    # If no scheme, first try scp-like SSH syntax: [user@]host:path
    has_scheme = "://" in candidate
    if not has_scheme:
        scp_match = re.match(
            r"^(?:(?P<user>[^@]+)@)?(?P<host>[^:/\s]+):(?P<path>[^/].+)$",
            candidate,
        )
        if scp_match:
            host = scp_match.group("host")
            path = scp_match.group("path").lstrip("/")
            if path.endswith(".git"):
                path = path[:-4]
            return f"https://{host}/{path}"

    # If no scheme (and not scp), assume host/path and prepend https
    parsed = urlsplit(candidate if has_scheme else f"https://{candidate}")

    # Drop credentials from netloc
    netloc = parsed.netloc.split("@", 1)[-1]

    # Drop explicit port (common for SSH like :7999 which is wrong for https)
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]

    # Normalize path and strip .git
    path = parsed.path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]

    if path:
        return f"https://{netloc}/{path}"
    else:
        return f"https://{netloc}"
