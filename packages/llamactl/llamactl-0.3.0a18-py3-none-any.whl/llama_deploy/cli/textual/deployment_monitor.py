"""Textual component to monitor a deployment and stream its logs."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import threading
import time
import webbrowser
from pathlib import Path

from llama_deploy.cli.client import (
    project_client_context,
)
from llama_deploy.core.schema import LogEvent
from llama_deploy.core.schema.deployments import DeploymentResponse
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalGroup, Widget
from textual.content import Content
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, RichLog, Static

logger = logging.getLogger(__name__)


class DeploymentMonitorWidget(Widget):
    """Widget that fetches deployment details once and streams logs.

    Notes:
    - Status is polled periodically
    - Log stream is started with init container logs included on first connect
    - If the stream ends or hangs, we reconnect with duration-aware backoff
    """

    DEFAULT_CSS = """
	DeploymentMonitorWidget {
		layout: vertical;
		width: 1fr;
		height: 1fr;
	}

	.monitor-container {
		width: 1fr;
		height: 1fr;
		padding: 0;
		margin: 0;
	}

	.details-grid {
		layout: grid;
		grid-size: 2;
		grid-columns: auto 1fr;
		grid-gutter: 0 1;
		grid-rows: auto;
		height: auto;
		width: 1fr;
	}

	.log-header {
		margin-top: 1;
	}

    .status-line .status-main {
        width: auto;
    }

    .status-line .status-right {
        width: 1fr;
        text-align: right;
        min-width: 12;
    }

    .deployment-link-label {
        width: auto;
    }

    .deployment-link {
        width: 1fr;
        min-width: 16;
        height: auto;
        align: left middle;
        text-align: left;
        content-align: left middle;
    }


	"""

    deployment_id: str
    deployment = reactive[DeploymentResponse | None](None, recompose=False)
    error_message = reactive("", recompose=False)
    wrap_enabled = reactive(False, recompose=False)
    autoscroll_enabled = reactive(True, recompose=False)

    def __init__(self, deployment_id: str) -> None:
        super().__init__()
        self.deployment_id = deployment_id
        self._stop_stream = threading.Event()
        # Persist content written to the RichLog across recomposes
        self._log_buffer: list[Text] = []

    async def on_mount(self) -> None:
        # Kick off initial fetch and start logs stream in background
        self.run_worker(self._fetch_deployment())
        self.run_worker(self._stream_logs())
        # Start periodic polling of deployment status
        self.run_worker(self._poll_deployment_status())

    def compose(self) -> ComposeResult:
        yield Static("Deployment Status", classes="primary-message")

        with HorizontalGroup(classes=""):
            yield Static("  URL:    ", classes="deployment-link-label")
            yield Button(
                "",
                id="deployment_link_button",
                classes="deployment-link",
                compact=True,
                variant="default",
            )
        yield Static("", classes="error-message", id="error_message")

        # Single-line status bar with colored icon and deployment ID
        with HorizontalGroup(classes="status-line"):
            yield Static(
                self._render_status_line(), classes="status-main", id="status_line"
            )
            yield Static("", classes="status-right", id="last_event_status")
        yield Static("", classes="last-event", id="last_event_details")
        yield Static("")  # just a spacer

        yield Static("Logs", classes="secondary-message log-header")
        yield RichLog(
            id="log_view",
            classes="log-view mb-1",
            auto_scroll=self.autoscroll_enabled,
            wrap=self.wrap_enabled,
            highlight=True,
        )

        with HorizontalGroup(classes="button-row"):
            wrap_label = "Wrap: On" if self.wrap_enabled else "Wrap: Off"
            auto_label = "Scroll: Auto" if self.autoscroll_enabled else "Scroll: Off"
            yield Button(wrap_label, id="toggle_wrap", variant="default", compact=True)
            yield Button(
                auto_label, id="toggle_autoscroll", variant="default", compact=True
            )
            yield Button("Copy", id="copy_log", variant="default", compact=True)
            yield Button("Close", id="close", variant="default", compact=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            # Signal parent app to close
            self.post_message(MonitorCloseMessage())
        elif event.button.id == "toggle_wrap":
            self.wrap_enabled = not self.wrap_enabled
        elif event.button.id == "toggle_autoscroll":
            self.autoscroll_enabled = not self.autoscroll_enabled
        elif event.button.id == "copy_log":
            txt = "\n".join([str(x) for x in self._log_buffer])
            self.app.copy_to_clipboard(txt)
        elif event.button.id == "deployment_link_button":
            self.action_open_url()

    async def _fetch_deployment(self) -> None:
        try:
            async with project_client_context() as client:
                self.deployment = await client.get_deployment(
                    self.deployment_id, include_events=True
                )
            # Clear any previous error on success
            self.error_message = ""
        except Exception as e:  # pragma: no cover - network errors
            self.error_message = f"Failed to fetch deployment: {e}"

    async def _stream_logs(self) -> None:
        """Consume the async log iterator, batch updates, and reconnect with backoff."""

        async def _sleep_with_cancel(total_seconds: float) -> None:
            step = 0.2
            remaining = total_seconds
            while remaining > 0 and not self._stop_stream.is_set():
                await asyncio.sleep(min(step, remaining))
                remaining -= step

        # Batching configuration: small latency to reduce UI churn while staying responsive
        batch_max_latency_seconds = 0.1
        batch_max_items = 200

        base_backoff_seconds = 0.2
        backoff_seconds = base_backoff_seconds
        max_backoff_seconds = 30.0

        while not self._stop_stream.is_set():
            connect_started_at = time.monotonic()
            # On any (re)connect, clear existing content
            self._reset_log_view_for_reconnect()

            queue: asyncio.Queue[LogEvent] = asyncio.Queue(maxsize=10000)
            producer_done = asyncio.Event()

            async def _producer() -> None:
                try:
                    async with project_client_context() as client:
                        async for event in client.stream_deployment_logs(
                            self.deployment_id,
                            include_init_containers=True,
                            tail_lines=10000,
                        ):
                            if self._stop_stream.is_set():
                                break
                            try:
                                await queue.put(event)
                            except Exception:
                                # If queue put fails due to cancellation/shutdown, stop
                                break
                except Exception as e:
                    # Surface error via error message and rely on reconnect loop
                    if not self._stop_stream.is_set():
                        self._set_error_message(
                            f"Log stream failed: {e}. Reconnecting..."
                        )
                finally:
                    producer_done.set()

            async def _consumer() -> None:
                batch: list[LogEvent] = []
                next_deadline = time.monotonic() + batch_max_latency_seconds
                while not self._stop_stream.is_set():
                    # Stop once producer finished and queue drained
                    if producer_done.is_set() and queue.empty():
                        if batch:
                            self._handle_log_events(batch)
                            batch = []
                        break
                    timeout = max(0.0, next_deadline - time.monotonic())
                    try:
                        item = await asyncio.wait_for(queue.get(), timeout=timeout)
                        batch.append(item)
                        if len(batch) >= batch_max_items:
                            self._handle_log_events(batch)
                            batch = []
                            next_deadline = time.monotonic() + batch_max_latency_seconds
                    except asyncio.TimeoutError:
                        if batch:
                            self._handle_log_events(batch)
                            batch = []
                        next_deadline = time.monotonic() + batch_max_latency_seconds
                    except Exception:
                        # On any unexpected error, flush and exit, reconnect will handle
                        if batch:
                            self._handle_log_events(batch)
                        break

            producer_task = asyncio.create_task(_producer())
            try:
                await _consumer()
            finally:
                # Ensure producer is not left running
                try:
                    producer_task.cancel()
                except Exception:
                    pass

            if self._stop_stream.is_set():
                break

            # If we reached here, the stream ended or failed; attempt reconnect with backoff
            self._set_error_message("Log stream disconnected. Reconnecting...")

            # Duration-aware backoff (smaller when the previous connection lived longer)
            connection_lifetime = 0.0
            try:
                connection_lifetime = max(0.0, time.monotonic() - connect_started_at)
            except Exception:
                connection_lifetime = 0.0

            if connection_lifetime >= backoff_seconds:
                backoff_seconds = base_backoff_seconds
            else:
                backoff_seconds = min(backoff_seconds * 2.0, max_backoff_seconds)

            delay = max(0.0, backoff_seconds - connection_lifetime)
            if delay > 0:
                await _sleep_with_cancel(delay)

    def _reset_log_view_for_reconnect(self) -> None:
        """Clear UI and buffers so new stream replaces previous content."""
        try:
            log_widget = self.query_one("#log_view", RichLog)
        except Exception:
            log_widget = None
        if log_widget is not None:
            log_widget.clear()

    def _set_error_message(self, message: str) -> None:
        self.error_message = message

    def _handle_log_events(self, events: list[LogEvent]) -> None:
        def to_text(event: LogEvent) -> Text:
            txt = Text()
            txt.append(
                f"[{event.container}] ", style=self._container_style(event.container)
            )
            txt.append(event.text)
            return txt

        texts = [to_text(event) for event in events]
        if not texts:
            return

        log_widget = self.query_one("#log_view", RichLog)
        for text in texts:
            log_widget.write(text)
            self._log_buffer.append(text)
        # Clear any previous error once we successfully receive logs
        if self.error_message:
            self.error_message = ""

    def _container_style(self, container_name: str) -> str:
        palette = [
            "bold magenta",
            "bold cyan",
            "bold blue",
            "bold green",
            "bold red",
            "bold bright_blue",
        ]
        # Stable hash to pick a color per container name
        h = int(hashlib.sha256(container_name.encode()).hexdigest(), 16)
        return palette[h % len(palette)]

    def _status_icon_and_style(self, phase: str) -> tuple[str, str]:
        # Map deployment phase to a colored icon
        phase = phase or "-"
        green = "bold green"
        yellow = "bold yellow"
        red = "bold red"
        gray = "grey50"
        if phase in {"Running", "Succeeded"}:
            return "●", green
        if phase in {"Pending", "Syncing", "RollingOut"}:
            return "●", yellow
        if phase in {"Failed", "RolloutFailed"}:
            return "●", red
        return "●", gray

    def action_open_url(self) -> None:
        if not self.deployment or not self.deployment.apiserver_url:
            return
        logger.debug(f"Opening URL: {self.deployment.apiserver_url}")
        webbrowser.open(str(self.deployment.apiserver_url))

    def _render_status_line(self) -> Text:
        phase = self.deployment.status if self.deployment else "Unknown"
        icon, style = self._status_icon_and_style(phase)
        line = Text()
        line.append(icon, style=style)
        line.append(" ")
        line.append(f"Status: {phase} — Deployment ID: {self.deployment_id or '-'}")
        return line

    def _render_last_event_details(self) -> Content:
        if not self.deployment or not self.deployment.events:
            return Content()
        latest = self.deployment.events[-1]
        txt = Text(f"  {latest.message}", style="dim")
        return Content.from_rich_text(txt)

    def _render_last_event_status(self) -> Content:
        if not self.deployment or not self.deployment.events:
            return Content()
        txt = Text()
        # Pick the most recent by last_timestamp
        latest = self.deployment.events[-1]
        ts = None
        ts = (latest.last_timestamp or latest.first_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        parts: list[str] = []
        if latest.type:
            parts.append(latest.type)
        if latest.reason:
            parts.append(latest.reason)
        kind = "/".join(parts) if parts else None
        if kind:
            txt.append(f"{kind} ", style="medium_purple3")
        txt.append(f"{ts}", style="dim")
        return Content.from_rich_text(txt)

    def on_unmount(self) -> None:
        # Attempt to stop the streaming loop
        self._stop_stream.set()

    # Reactive watchers to update widgets in place instead of recomposing
    def watch_error_message(self, message: str) -> None:
        try:
            widget = self.query_one("#error_message", Static)
        except Exception:
            return
        widget.update(message)
        widget.display = bool(message)

    def watch_deployment(self, deployment: DeploymentResponse | None) -> None:
        if deployment is None:
            return

        widget = self.query_one("#status_line", Static)
        ev_widget = self.query_one("#last_event_status", Static)
        ev_details_widget = self.query_one("#last_event_details", Static)
        deployment_link_button = self.query_one("#deployment_link_button", Button)
        widget.update(self._render_status_line())
        deployment_link_button.label = f"{str(self.deployment.apiserver_url or '')}"
        # Update last event line
        ev_widget.update(self._render_last_event_status())
        ev_details_widget.update(self._render_last_event_details())
        ev_details_widget.display = bool(self.deployment and self.deployment.events)

    def watch_wrap_enabled(self, enabled: bool) -> None:
        try:
            log_widget = self.query_one("#log_view", RichLog)
            log_widget.wrap = enabled
            # Clear existing lines; new wrap mode will apply to subsequent events
            log_widget.clear()
            for text in self._log_buffer:
                log_widget.write(text)
        except Exception:
            pass
        try:
            btn = self.query_one("#toggle_wrap", Button)
            btn.label = "Wrap: On" if enabled else "Wrap: Off"
        except Exception:
            pass

    def watch_autoscroll_enabled(self, enabled: bool) -> None:
        try:
            log_widget = self.query_one("#log_view", RichLog)
            log_widget.auto_scroll = enabled
        except Exception:
            pass
        try:
            btn = self.query_one("#toggle_autoscroll", Button)
            btn.label = "Scroll: Auto" if enabled else "Scroll: Off"
        except Exception:
            pass

    async def _poll_deployment_status(self) -> None:
        """Periodically refresh deployment status to reflect updates in the UI."""
        while not self._stop_stream.is_set():
            try:
                async with project_client_context() as client:
                    self.deployment = await client.get_deployment(
                        self.deployment_id, include_events=True
                    )
                # Clear any previous error on success
                if self.error_message:
                    self.error_message = ""
            except Exception as e:  # pragma: no cover - network errors
                # Non-fatal; will try again on next interval
                self.error_message = f"Failed to refresh status: {e}"
            await asyncio.sleep(5)


class MonitorCloseMessage(Message):
    pass


class DeploymentMonitorApp(App[None]):
    """Standalone app wrapper around the monitor widget.

    This allows easy reuse in other flows by embedding the widget.
    """

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self, deployment_id: str) -> None:
        super().__init__()
        self.deployment_id = deployment_id

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        with Container():
            yield DeploymentMonitorWidget(self.deployment_id)

    def on_monitor_close_message(self, _: MonitorCloseMessage) -> None:
        self.exit(None)

    def on_key(self, event: events.Key) -> None:
        # Support Ctrl+C to exit, consistent with other screens and terminals
        if event.key == "ctrl+c":
            self.exit(None)


def monitor_deployment_screen(deployment_id: str) -> None:
    """Launch the standalone deployment monitor screen."""
    app = DeploymentMonitorApp(deployment_id)
    app.run()
