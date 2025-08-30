"""Textual component to monitor a deployment and stream its logs."""

from __future__ import annotations

import asyncio
import hashlib
import threading
import time
from pathlib import Path
from typing import Iterator

from llama_deploy.cli.client import get_project_client as get_client
from llama_deploy.core.client.manage_client import Closer
from llama_deploy.core.schema.base import LogEvent
from llama_deploy.core.schema.deployments import DeploymentResponse
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalGroup, Widget
from textual.content import Content
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, RichLog, Static


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


	"""

    deployment_id: str
    deployment = reactive[DeploymentResponse | None](None, recompose=False)
    error_message = reactive("", recompose=False)
    wrap_enabled = reactive(False, recompose=False)
    autoscroll_enabled = reactive(True, recompose=False)
    stream_closer: Closer | None = None

    def __init__(self, deployment_id: str) -> None:
        super().__init__()
        self.deployment_id = deployment_id
        self._stop_stream = threading.Event()
        # Persist content written to the RichLog across recomposes
        self._log_buffer: list[Text] = []

    def on_mount(self) -> None:
        # Kick off initial fetch and start logs stream in background
        self.run_worker(self._fetch_deployment(), exclusive=True)
        self.run_worker(self._stream_logs, exclusive=False, thread=True)
        # Start periodic polling of deployment status
        self.run_worker(self._poll_deployment_status(), exclusive=False)

    def compose(self) -> ComposeResult:
        yield Static("Deployment Status", classes="primary-message")
        yield Static("", classes="error-message", id="error_message")

        # Single-line status bar with colored icon and deployment ID
        with HorizontalGroup(classes="status-line"):
            yield Static(
                self._render_status_line(), classes="status-main", id="status_line"
            )
            yield Static("", classes="status-right", id="last_event_status")
        yield Static("", classes="last-event mb-1", id="last_event_details")

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
            auto_label = (
                "Auto-scroll: On" if self.autoscroll_enabled else "Auto-scroll: Off"
            )
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

    async def _fetch_deployment(self) -> None:
        try:
            client = get_client()
            self.deployment = client.get_deployment(
                self.deployment_id, include_events=True
            )
            # Clear any previous error on success
            self.error_message = ""
        except Exception as e:  # pragma: no cover - network errors
            self.error_message = f"Failed to fetch deployment: {e}"

    def _stream_logs(self) -> None:
        """Consume the blocking log iterator in a single worker thread.

        Cooperative cancellation uses `self._stop_stream` to exit cleanly.
        """
        client = get_client()

        def _sleep_with_cancel(total_seconds: float) -> None:
            step = 0.2
            remaining = total_seconds
            while remaining > 0 and not self._stop_stream.is_set():
                time.sleep(min(step, remaining))
                remaining -= step

        base_backoff_seconds = 0.2
        backoff_seconds = base_backoff_seconds
        max_backoff_seconds = 30.0

        while not self._stop_stream.is_set():
            try:
                connect_started_at = time.monotonic()
                closer, stream = client.stream_deployment_logs(
                    self.deployment_id,
                    include_init_containers=True,
                )
                # On any (re)connect, clear existing content
                self.app.call_from_thread(self._reset_log_view_for_reconnect)

                buffered_stream = _buffer_log_lines(stream)

                def close_stream():
                    try:
                        closer()
                    except Exception:
                        pass

                self.stream_closer = close_stream
                # Stream connected; consume until end
                for events in buffered_stream:
                    if self._stop_stream.is_set():
                        break
                    # Marshal UI updates back to the main thread via the App
                    self.app.call_from_thread(self._handle_log_events, events)
                if self._stop_stream.is_set():
                    break
                # Stream ended without explicit error; attempt reconnect
                self.app.call_from_thread(
                    self._set_error_message, "Log stream disconnected. Reconnecting..."
                )
            except Exception as e:
                if self._stop_stream.is_set():
                    break
                # Surface the error to the UI and attempt reconnect with backoff
                self.app.call_from_thread(
                    self._set_error_message, f"Log stream failed: {e}. Reconnecting..."
                )

            # Duration-aware backoff: subtract how long the last connection lived
            connection_lifetime = 0.0
            try:
                connection_lifetime = max(0.0, time.monotonic() - connect_started_at)
            except Exception:
                connection_lifetime = 0.0

            # If the connection lived longer than the current backoff window,
            # reset to base so the next reconnect is immediate.
            if connection_lifetime >= backoff_seconds:
                backoff_seconds = base_backoff_seconds
            else:
                backoff_seconds = min(backoff_seconds * 2.0, max_backoff_seconds)

            delay = max(0.0, backoff_seconds - connection_lifetime)
            if delay > 0:
                _sleep_with_cancel(delay)

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
        if self.stream_closer is not None:
            self.stream_closer()
            self.stream_closer = None

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

        widget.update(self._render_status_line())
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
            btn.label = "Auto-scroll: On" if enabled else "Auto-scroll: Off"
        except Exception:
            pass

    async def _poll_deployment_status(self) -> None:
        """Periodically refresh deployment status to reflect updates in the UI."""
        client = get_client()
        while not self._stop_stream.is_set():
            try:
                self.deployment = client.get_deployment(
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


def _buffer_log_lines(iter: Iterator[LogEvent]) -> Iterator[list[LogEvent]]:
    """Batch log events into small lists using a background reader.

    This reduces UI churn while still reacting quickly. On shutdown we
    absorb stream read errors that are expected when the connection is
    closed from another thread.
    """
    buffer: list[LogEvent] = []
    bg_error: Exception | None = None
    done = threading.Event()

    def pump() -> None:
        nonlocal bg_error
        try:
            for event in iter:
                buffer.append(event)
        except Exception as e:
            bg_error = e
        finally:
            done.set()

    t = threading.Thread(target=pump, daemon=True)
    t.start()
    try:
        while not done.is_set():
            if buffer:
                # Yield a snapshot and clear in-place to avoid reallocating list
                yield list(buffer)
                buffer.clear()
            time.sleep(0.5)
        if bg_error is not None:
            raise bg_error
    finally:
        try:
            t.join(timeout=0.1)
        except Exception:
            pass
