"""
Textual UI components for the terminal chat client
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Static, Button
from textual.binding import Binding


class MessageDisplay(Static):
    """Widget to display chat messages"""

    def __init__(self):
        super().__init__()
        self.messages = []

    def add_message(self, username: str, message: str, timestamp: str = ""):
        """Add a message to the display"""
        self.messages.append(f"[{timestamp}] {username}: {message}")
        self.update("\n".join(self.messages))


class ChatApp(App):
    """Main chat application"""

    CSS = """
    Screen {
        background: $surface;
    }

    #message-container {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        overflow-y: scroll;
    }

    #input-container {
        height: auto;
        dock: bottom;
        padding: 1;
    }

    Input {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the UI"""
        yield Header()
        yield Container(
            MessageDisplay(id="message-display"),
            id="message-container"
        )
        yield Container(
            Input(placeholder="Type a message...", id="message-input"),
            id="input-container"
        )
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission"""
        message = event.value
        if message.strip():
            # TODO: Send message to server via WebSocket
            message_display = self.query_one("#message-display", MessageDisplay)
            message_display.add_message("You", message)
            event.input.value = ""

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()
