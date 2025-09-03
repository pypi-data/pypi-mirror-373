try:
    from prompt_toolkit.application import Application 
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout.containers import HSplit, Window, ScrollOffsets
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.shortcuts import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.layout.processors import BeforeInput
    from prompt_toolkit import print_formatted_text, ANSI
    from prompt_toolkit.shortcuts import set_title
    from prompt_toolkit.formatted_text import FormattedText
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

logger = logging.getLogger("InterpreterConsole")

class InterpreterConsole:
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
                 title: str = None,
                 prompt_prefix: str = ">>> ",
                 continuation_prefix: str = "... "
                 ):
        """
        Initialize an interpreter-style console similar to Python REPL
        
        Args:
            session: Session object that handles command parsing and execution
            banner_text: Text to display at startup
            history_file: Optional path to history file
            prompt_prefix: Primary prompt (default: ">>> ")
            continuation_prefix: Continuation prompt for multiline (default: "... ")
        """
        self.session = session
        self.banner_text = banner_text
        self.prompt_prefix = prompt_prefix
        self.continuation_prefix = continuation_prefix
        self.exitCallback = exitCallback
        self.multiline_buffer = []
        
        if title:
            set_title(title)
        
        # Initialize prompt session
        self._init_prompt_session(history_file)
        
        # Store original print function before redirecting
        self._original_print = builtins.print
        
        # Route print and logs
        if routePrint:
            builtins.print = self.printRedirect
            
        if routeLogs:
            configure_logging(self.print_ansi, logLevel)

    def _init_prompt_session(self, history_file: Optional[str]):
        """Initialize the prompt session with completion and history"""
        history = None
        if history_file:
            history = FileHistory(os.path.expanduser(history_file))
            
        # Set up key bindings
        kb = KeyBindings()
        
        @kb.add('c-c')
        def keyboard_interrupt(event):
            """Handle Ctrl+C - clear current input or exit"""
            if self.multiline_buffer:
                # Clear multiline buffer and reset to primary prompt
                self.multiline_buffer = []
                print_formatted_text(ANSI("\n\x1b[31mKeyboardInterrupt\x1b[0m"))
                event.app.exit(result='')
            else:
                if self.exitCallback:
                    self.exitCallback()
                event.app.exit(exception=KeyboardInterrupt)
        
        @kb.add('c-d')
        def eof(event):
            """Handle Ctrl+D - exit"""
            if self.exitCallback:
                self.exitCallback()
            event.app.exit(exception=EOFError)
            
        @kb.add('c-a')
        def select_all(event):
            """Handle Ctrl+A - select all in current buffer"""
            event.current_buffer.cursor_position = 0
            event.current_buffer.start_selection()
            event.current_buffer.cursor_position = len(event.current_buffer.text)
            
        @kb.add('c-x')
        def cut_text(event):
            """Handle Ctrl+X - cut selected text"""
            if event.current_buffer.selection_state:
                event.current_buffer.cut_selection()
                
        @kb.add('c-v')  
        def paste_text(event):
            """Handle Ctrl+V - paste from clipboard"""
            event.current_buffer.paste_clipboard_data(event.app.clipboard.get_data())
        
        # Enable text selection with mouse
        @kb.add('s-left')
        def select_left(event):
            """Extend selection to the left"""
            if not event.current_buffer.selection_state:
                event.current_buffer.start_selection()
            event.current_buffer.cursor_left()
            
        @kb.add('s-right') 
        def select_right(event):
            """Extend selection to the right"""
            if not event.current_buffer.selection_state:
                event.current_buffer.start_selection()
            event.current_buffer.cursor_right()
            
        @kb.add('s-up')
        def select_up(event):
            """Extend selection up"""
            if not event.current_buffer.selection_state:
                event.current_buffer.start_selection()
            event.current_buffer.cursor_up()
            
        @kb.add('s-down')
        def select_down(event): 
            """Extend selection down"""
            if not event.current_buffer.selection_state:
                event.current_buffer.start_selection()
            event.current_buffer.cursor_down()
            
        self.prompt_session = PromptSession(
            history=history,
            completer=CommandCompleter(self.session),
            complete_while_typing=True,
            key_bindings=kb,
            mouse_support=True,
            wrap_lines=True,
            multiline=False,  # We'll handle multiline manually
            enable_history_search=True,
            search_ignore_case=True,
        )

    def printRedirect(self, *args, **kwargs):
        """Redirect print calls to our ANSI printer"""
        text = " ".join(map(str, args))
        # Use the original print function to avoid recursion
        if kwargs.get('file') is None:  # Only redirect stdout prints
            self.print_ansi(text)
        else:
            # Use original print for stderr or other files
            self._original_print(*args, **kwargs)

    def print_ansi(self, text: str) -> None:
        """Print ANSI-formatted text with selection support"""
        # Use print_formatted_text which supports terminal selection
        print_formatted_text(ANSI(text))

    def _get_current_prompt(self) -> FormattedText:
        """Get the appropriate prompt based on state"""
        if self.multiline_buffer:
            return FormattedText([('ansigreen', self.continuation_prefix)])
        else:
            return FormattedText([('ansigreen', self.prompt_prefix)])

    def _is_complete_statement(self, text: str) -> bool:
        """
        Check if the current input forms a complete statement.
        This is a simplified version - you might want to enhance this
        based on your specific language/command syntax.
        """
        # Simple heuristic: check for unclosed brackets, quotes, etc.
        open_brackets = text.count('(') - text.count(')')
        open_squares = text.count('[') - text.count(']')
        open_braces = text.count('{') - text.count('}')
        
        # Count quotes (simplified - doesn't handle escaped quotes)
        single_quotes = text.count("'") % 2
        double_quotes = text.count('"') % 2
        
        # If any are unclosed, it's incomplete
        if (open_brackets > 0 or open_squares > 0 or open_braces > 0 or 
            single_quotes != 0 or double_quotes != 0):
            return False
            
        # Check for line continuation backslashes
        if text.rstrip().endswith('\\'):
            return False
            
        return True

    def _handle_input(self, user_input: str) -> bool:
        """
        Handle user input and return True if we should continue the REPL
        """
        user_input = user_input.rstrip()
        
        # Handle empty input
        if not user_input:
            if self.multiline_buffer:
                # Empty line in multiline mode - execute the buffer
                full_command = '\n'.join(self.multiline_buffer)
                self.multiline_buffer = []
                self._execute_command(full_command)
            return True
        
        # Add to multiline buffer
        self.multiline_buffer.append(user_input)
        
        # Check if this forms a complete statement
        full_text = '\n'.join(self.multiline_buffer)
        
        if self._is_complete_statement(full_text):
            # Execute the complete command
            self._execute_command(full_text)
            self.multiline_buffer = []
        
        return True

    def _execute_command(self, command: str):
        """Execute a command through the session"""
        if hasattr(self.session, 'parseCommand'):
            try:
                self.session.parseCommand(command)
            except Exception as e:
                logger.error(f"Failed to execute command ({command}): {e}")
                self.print_ansi(f"\x1b[31mError: {e}\x1b[0m")

    def _show_banner(self):
        """Display the startup banner"""
        if self.banner_text:
            self.print_ansi(f"\x1b[32m{self.banner_text}\x1b[0m")
            self.print_ansi("")

    async def run_async(self):
        """Run the console asynchronously"""
        self._show_banner()
        
        try:
            while True:
                try:
                    # Get input with appropriate prompt
                    prompt = self._get_current_prompt()
                    user_input = await self.prompt_session.prompt_async(
                        message=prompt,
                        multiline=False
                    )
                    
                    # Handle the input
                    if not self._handle_input(user_input):
                        break
                        
                except (EOFError, KeyboardInterrupt):
                    # Clean exit
                    if self.multiline_buffer:
                        self.multiline_buffer = []
                        self.print_ansi("")
                        continue
                    else:
                        break
                except Exception as e:
                    logger.error(f"Unexpected error in REPL: {e}")
                    self.print_ansi(f"\x1b[31mUnexpected error: {e}\x1b[0m")
                    
        except Exception as e:
            logger.error(f"Fatal error in console: {e}")
        finally:
            if self.exitCallback:
                self.exitCallback()

    def run(self):
        """Run the console synchronously"""
        asyncio.run(self.run_async())
        
    def start(self):
        """Start the console (alias for run)"""
        self.run()

# Example usage:
if __name__ == '__main__':
    class DummySession:
        def parseCommand(self, cmd):
            print(f"\x1b[36mExecuting command:\x1b[0m {cmd}")
            if cmd.strip().lower() == 'exit':
                raise EOFError("User requested exit")
    
    console = InterpreterConsole(
        session=DummySession(),
        banner_text="Python Interpreter Style Console v1.0\nType 'exit' to quit, Ctrl+C to interrupt, Ctrl+D to exit",
        history_file="~/.interpreter-history",
        title="Interpreter Console"
    )
    
    try:
        console.run()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")