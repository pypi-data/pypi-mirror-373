try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import Input, Static, RichLog, Header, Footer
    from textual.reactive import reactive
    from textual.binding import Binding
    from textual.suggester import Suggester

    from rich.console import RenderableType
    from rich.text import Text
    from rich.markup import escape
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

import asyncio
import os
from typing import Optional, Any, Callable, List
import builtins
import sys
import logging
from pathlib import Path

logger = logging.getLogger("SplitConsole")

class SessionSuggester(Suggester):
    """Custom suggester that gets completions from the session object"""
    
    def __init__(self, session):
        self.session = session
        super().__init__()
    
    async def get_suggestion(self, value: str) -> str | None:
        """Get completion suggestion from session"""
        if not value:
            return None
            
        try:
            completions = []
            
            # Try different methods to get completions from session
            if hasattr(self.session, 'get_completions'):
                completions = self.session.get_completions(value)
            elif hasattr(self.session, 'complete'):
                # Some sessions might have a complete method
                result = self.session.complete(value)
                if result:
                    completions = result if isinstance(result, list) else [result]
            elif hasattr(self.session, 'completer') and hasattr(self.session.completer, 'get_completions'):
                # Check if there's a completer object
                completer_result = self.session.completer.get_completions(None, value)
                if completer_result:
                    completions = [c.text for c in completer_result if hasattr(c, 'text')]
            
            if completions and len(completions) > 0:
                # Return the first completion that starts with the current value
                for completion in completions:
                    completion_text = str(completion)
                    if completion_text.startswith(value) and len(completion_text) > len(value):
                        return completion_text[len(value):]
                        
        except Exception as e:
            logger.debug(f"Error getting completions: {e}")
        
        return None

class SplitConsole(App):
    """A split console application using Textual"""
    
    CSS = """
    Screen {
        layers: base overlay;
    }
    
    #banner {
        dock: top;
        height: 3;
        background: $surface;
        border: solid green;
    }
    
    #banner-left {
        color: green;
        text-style: bold;
    }
    
    #banner-right {
        color: red;
        text-align: right;
    }
    
    #output {
        border: solid green;
        scrollbar-background: $surface;
        scrollbar-color: green;
    }
    
    #input-container {
        dock: bottom;
        height: 3;
        background: $surface;
    }
    
    #prompt {
        width: 3;
        color: green;
        text-style: bold;
        content-align: center middle;
    }
    
    #input {
        border: solid green;
    }
    
    .status {
        color: blue;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+l", "clear", "Clear", show=False),
    ]
    
    status_text = reactive("")
    
    def __init__(self, 
                 session: Any,
                 banner_text: str,
                 history_file: Optional[str] = None,
                 route_print: bool = True,
                 route_logs: bool = True,
                 route_stdout: bool = True,
                 route_stderr: bool = True,
                 log_level: str = "INFO",
                 exit_callback: Optional[Callable] = None,
                 title: str = None,
                 **kwargs):
        """
        Initialize a split console with customizable components
        
        Args:
            session: Session object that handles command parsing and execution
            banner_text: Text to display in the banner
            history_file: Optional path to history file for command history
            route_print: Whether to route print() calls to the console
            route_logs: Whether to route logging to the console  
            route_stdout: Whether to route stdout to the console
            route_stderr: Whether to route stderr to the console
            log_level: Logging level
            exit_callback: Optional callback to call on exit
            title: Optional window title
        """
        super().__init__(**kwargs)
        
        self.session = session
        self.banner_text = banner_text
        self.history_file = history_file
        self.exit_callback = exit_callback
        self.command_history: List[str] = []
        self.history_index = -1
        
        # Create suggester for autocompletion
        self.suggester = SessionSuggester(session)
        
        # Load command history
        self._load_history()
        
        if title:
            self.title = title
        
        # Set up output routing
        if route_print:
            self.original_print = builtins.print
            builtins.print = self.print_redirect
            
        if route_logs:
            self._configure_logging(log_level)

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        with Container(id="banner"):
            with Horizontal():
                yield Static(self.banner_text, id="banner-left")
                yield Static("", id="banner-right")
        
        yield RichLog(id="output", highlight=True, markup=True)
        
        with Container(id="input-container"):
            with Horizontal():
                yield Static("$>", id="prompt")
                yield Input(
                    placeholder="Enter command...", 
                    id="input",
                    suggester=self.suggester
                )

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self.query_one("#input").focus()
        
    def _load_history(self):
        """Load command history from file"""
        if self.history_file:
            history_path = Path(os.path.expanduser(self.history_file))
            if history_path.exists():
                try:
                    with open(history_path, 'r') as f:
                        self.command_history = [line.strip() for line in f.readlines()]
                except Exception as e:
                    logger.error(f"Failed to load history: {e}")

    def _save_history(self):
        """Save command history to file"""
        if self.history_file:
            history_path = Path(os.path.expanduser(self.history_file))
            try:
                history_path.parent.mkdir(parents=True, exist_ok=True)
                with open(history_path, 'w') as f:
                    for cmd in self.command_history[-1000:]:  # Keep last 1000 commands
                        f.write(f"{cmd}\n")
            except Exception as e:
                logger.error(f"Failed to save history: {e}")

    def _configure_logging(self, log_level: str):
        """Configure logging to route to the console"""
        class TextualLogHandler(logging.Handler):
            def __init__(self, console_app):
                super().__init__()
                self.console_app = console_app
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.console_app.print_ansi(msg)
                except Exception:
                    pass
        
        # Set up logging
        handler = TextualLogHandler(self)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, log_level.upper()))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        # Only handle events from our input widget
        if event.input.id != "input":
            return
            
        command = event.value.strip()
        input_widget = self.query_one("#input")
        
        if not command:
            self.print_ansi("")
            input_widget.clear()
            return
            
        # Add to history
        if command not in self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
            self._save_history()
        
        self.history_index = len(self.command_history)
        
        # Display the command
        self.print_ansi(f"$> {command}")
        
        # Execute the command
        if hasattr(self.session, 'parseCommand'):
            try:
                self.session.parseCommand(command)
            except Exception as e:
                logger.error(f"Failed to execute command ({command}): {e}")
        
        input_widget.clear()

    def on_key(self, event) -> None:
        """Handle key events for history navigation and completion"""
        input_widget = self.query_one("#input")
        
        if not input_widget.has_focus:
            return
        
        if event.key == "up":
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                input_widget.value = self.command_history[self.history_index]
                input_widget.cursor_position = len(input_widget.value)
                event.prevent_default()
                
        elif event.key == "down":
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                input_widget.value = self.command_history[self.history_index]
                input_widget.cursor_position = len(input_widget.value)
                event.prevent_default()
            elif self.history_index >= len(self.command_history) - 1:
                input_widget.clear()
                self.history_index = len(self.command_history)
                event.prevent_default()
                
        elif event.key == "tab":
            # Handle tab completion
            current_value = input_widget.value
            if current_value:
                self._handle_tab_completion(input_widget, current_value)
                event.prevent_default()

    def _handle_tab_completion(self, input_widget, current_value: str):
        """Handle tab completion by getting all possible completions"""
        try:
            completions = []
            
            # Get completions using the same logic as the suggester
            if hasattr(self.session, 'get_completions'):
                completions = self.session.get_completions(current_value)
            elif hasattr(self.session, 'complete'):
                result = self.session.complete(current_value)
                if result:
                    completions = result if isinstance(result, list) else [result]
            elif hasattr(self.session, 'completer') and hasattr(self.session.completer, 'get_completions'):
                completer_result = self.session.completer.get_completions(None, current_value)
                if completer_result:
                    completions = [c.text for c in completer_result if hasattr(c, 'text')]
            
            if completions:
                # Find completions that start with current value
                matching_completions = [c for c in completions if str(c).startswith(current_value)]
                
                if len(matching_completions) == 1:
                    # Only one match, complete it
                    input_widget.value = str(matching_completions[0])
                    input_widget.cursor_position = len(input_widget.value)
                elif len(matching_completions) > 1:
                    # Multiple matches, show them
                    self.print_ansi(f"Completions: {', '.join(map(str, matching_completions))}")
                    
        except Exception as e:
            logger.debug(f"Error in tab completion: {e}")

    def print_redirect(self, *args, **kwargs):
        """Redirect print calls to the console"""
        text = " ".join(map(str, args))
        self.print_ansi(text)

    def print_ansi(self, text: str) -> None:
        """Print text to the output window"""
        output = self.query_one("#output", RichLog)
        
        # Handle ANSI color codes and markup
        try:
            # Convert simple ANSI codes to Rich markup
            rich_text = Text.from_ansi(text)
            output.write(rich_text)
        except Exception:
            # Fallback to plain text if ANSI parsing fails
            output.write(escape(text))

    def action_clear(self) -> None:
        """Clear the console output"""
        output = self.query_one("#output", RichLog)
        output.clear()

    def action_quit(self) -> None:
        """Quit the application"""
        if self.exit_callback:
            self.exit_callback()
        self.exit()

    def update_status(self, status: str) -> None:
        """Update the status display in the banner"""
        self.status_text = status
        banner_right = self.query_one("#banner-right")
        banner_right.update(status)

    def clear_console(self) -> None:
        """Clear the console output (alias for action_clear)"""
        self.action_clear()

    async def run_async(self, *args, **kwargs):
        """Run the console application asynchronously"""
        return await super().run_async(*args, **kwargs)
    
    def start(self) -> None:
        """Start the console application"""
        self.run()


# Example usage:
if __name__ == '__main__':
    class DummySession:
        def parseCommand(self, cmd):
            print(f"Executing command: {cmd}")
            
            # Example of different command responses
            if cmd.lower() == "help":
                print("Available commands:")
                print("  help - Show this help")
                print("  clear - Clear the console")
                print("  status <text> - Update status")
                print("  test - Run a test")
            elif cmd.lower().startswith("status "):
                status_text = cmd[7:]  # Remove "status " prefix
                app.update_status(status_text)
            elif cmd.lower() == "test":
                print("[bold green]Test passed![/bold green]")
                print("[red]This is red text[/red]")
                print("[blue]This is blue text[/blue]")
            elif cmd.lower() == "error":
                raise Exception("This is a test error")
            else:
                print(f"Unknown command: {cmd}")
    
    app = SplitConsole(
        session=DummySession(),
        banner_text="Test Console v2.0 (Textual)",
        history_file="~/.test-history",
        title="Split Console Demo"
    )
    
    app.start()