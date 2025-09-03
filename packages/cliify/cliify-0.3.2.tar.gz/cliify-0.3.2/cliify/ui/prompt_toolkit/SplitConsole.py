try:
    from prompt_toolkit.application import Application 
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout.containers import HSplit, VSplit, Window, ScrollOffsets, FloatContainer, Float
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
    from prompt_toolkit.widgets import TextArea, Frame, Label, HorizontalLine
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.layout.menus import CompletionsMenu
    from prompt_toolkit import print_formatted_text, ANSI
    from prompt_toolkit.data_structures import Point
    from prompt_toolkit.shortcuts import set_title
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

import asyncio
import os
from typing import Optional, Any, Callable
import builtins
import sys

from cliify.completers.prompt_toolkit import CommandCompleter
from cliify.ui.LogRouter import configure_logging

import logging 

logger = logging.getLogger("SplitConsole")

class SplitConsole:
    def __init__(self, 
                 session: Any,
                 banner_text: str,
                 history_file: Optional[str] = None,
                 routePrint: bool = True,
                 routeLogs: bool = True,
                 routeStdout: bool = True,
                 routeStderr: bool = True,
                 logLevel: str = "INFO",
                 exitCallback: Optional[Callable] = None,
                 title: str = None
                 ):
        """
        Initialize a split console with customizable components
        
        Args:
            session: Session object that handles command parsing and execution
            banner_text: Text to display in the banner
            command_completer: Optional command completer for input
            history_file: Optional path to history file
        """
        self.session = session
        self.banner_text = banner_text
        self._line_count = 0
        self.full_output = ""
        self.exitCallback = exitCallback

        if title:
            set_title(title)
        
        # Set up key bindings
        self.kb = KeyBindings()
        self._setup_key_bindings()
        
        # Initialize UI components
        self._init_banner()
        self._init_output_window()
        self._init_input_field(command_completer=CommandCompleter(session), history_file=history_file)
        self._init_layout()
        
        # Create application
        self.application = Application(
            layout=Layout(self.layout, focused_element=self.input_field),
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True
        )

        # Route print and logs
        if routePrint:
            builtins.print = self.printRedirect

        if routeLogs:
            configure_logging(self.print_ansi, logLevel)

        # if routeStdout:
        #     sys.stdout = self.printRedirect

        # if routeStderr:
        #     sys.stderr = self.printRedirect


    def _setup_key_bindings(self):
        """Set up default key bindings"""
        
        @self.kb.add('c-c')
        def exit_app(event):
            if self.exitCallback:
                self.exitCallback()
            event.app.exit(0)
            

    def printRedirect(self, *args, **kwargs):
        self.print_ansi(" ".join(map(str, args)))

    def _init_banner(self):
        """Initialize the banner component"""
        self.banner_left = Label(self.banner_text, style="fg:ansigreen")
        self.top_info = Label("", style="fg:ansired")
        self.util_info = Label("", style="fg:ansiblue")
        banner_right = HSplit([self.top_info])
        self.banner_content = VSplit([self.banner_left, banner_right])
        self.divider = HorizontalLine()
        self.divider.window.style = "fg:ansigreen"

    def _init_output_window(self):
        """Initialize the output window"""
        self.output_control = FormattedTextControl(
            text=[('ansigreen', '')],
            get_cursor_position=self._get_cursor_pos,
            focusable=True
        )
        self.output_window = Window(
            content=self.output_control,
            style="class:main-content",
            wrap_lines=False,
            allow_scroll_beyond_bottom=True,
            scroll_offsets=ScrollOffsets(top=-100000, bottom=-100000)
        )

    def _init_input_field(self, command_completer: Optional[Any], history_file: Optional[str]):
        """Initialize the input field"""
        history = None
        if history_file:
            history = FileHistory(os.path.expanduser(history_file))
            
        self.input_field = Buffer(
            multiline=False,
            complete_while_typing=True,
            history=history,
            completer=command_completer
        )
        self.input_field.accept_handler = self._handle_input
        
        self.input_window = Window(
            BufferControl(buffer=self.input_field),
            height=2,
            style='class:input-win'
        )
        self.prompt_window = Window(
            FormattedTextControl(text="$>"),
            height=1,
            style='fg:ansigreen',
            width=3
        )

    def _init_layout(self):
        """Initialize the main layout"""
        self.layout = FloatContainer(
            content=HSplit([
                self.banner_content,
                self.divider,
                self.output_window,
                self.divider,
                VSplit([self.prompt_window, self.input_window])
            ]),
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1)
                )
            ]
        )

    def _get_cursor_pos(self) -> Point:
        """Get the current cursor position"""
        # Safely get the line count based on actual content
        try:
            actual_lines = len(self.full_output.splitlines()) if self.full_output else 0
            # Use the smaller of the two to prevent index out of range
            safe_line_count = min(self._line_count, actual_lines)
            return Point(x=0, y=max(0, safe_line_count - 1))
        except:
            return Point(x=0, y=0)

    def _handle_input(self, buff: Buffer) -> None:
        """Handle input from the buffer"""
        line = buff.text
        if line.strip() == "":
            self.print_ansi("")
            return
        if hasattr(self.session, 'parseCommand'):
            try:
                self.session.parseCommand(line)
            except Exception as e:
                logger.error(f"Failed to execute command ({line}): {e}")


    def print_ansi(self, text: str) -> None:
        """Print ANSI-formatted text to the output window"""
        try:
            self.full_output += "\n" + text 
            ansi = ANSI(self.full_output)
            self.output_control.text = ansi

            # Update line count based on actual content
            self._line_count = len(self.full_output.splitlines())
            newLines = text.count("\n") + 1

            # If screen is full, only scroll by the new lines
            if (self.output_window.render_info and 
                self._line_count > self.output_window.render_info.window_height):
                self.output_window.vertical_scroll += newLines

            # Invalidate the application to force a redraw
            self.application.invalidate()
        except Exception as e:
            # Fallback to basic behavior if there's an issue
            logger.error(f"Error in print_ansi: {e}")
            try:
                self.application.invalidate()
            except:
                pass

    def clear_console(self) -> None:
        """Clear the console output"""
        self._line_count = 0
        self.full_output = ""
        self.output_control.text = [('ansigreen', '')]
        self.application.invalidate()

    def update_status(self, status: str) -> None:
        """Update the status display in the banner"""
        self.top_info.text = status
        self.application.invalidate()

    async def run(self) -> None:
        """Run the console application"""
        return await self.application.run_async()
    
    def start(self) -> None:
        """Start the console application"""
        asyncio.run(self.run())

# Example usage:
if __name__ == '__main__':
    class DummySession:
        def parseCommand(self, cmd):
            print(f"Executing command: {cmd}")
    
    console = SplitConsole(
        session=DummySession(),
        banner_text="Test Console v1.0",
        history_file="~/.test-history"
    )
    
    asyncio.run(console.run())