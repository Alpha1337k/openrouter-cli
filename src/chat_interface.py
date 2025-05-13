import prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
import os
import sys


class NoTTYInterface:
    def __init__(self):
        pass

    def run(self) -> str | None:
        """Run the chat interface"""

        user_input = sys.stdin.read().strip()

        if user_input is None or len(user_input) == 0:
            print("Error: no / empty data provided")
            return None

        return user_input


class ChatInterface:
    def __init__(self):
        os.makedirs(os.path.expanduser("~/.openrouter-cli"), exist_ok=True)

        history_path = os.path.expanduser("~/.openrouter-cli/history")

        # Create a history object to store previous commands.
        self.history = FileHistory(history_path)

        # Create key bindings
        self.kb = KeyBindings()

        # Create a prompt session with history and key bindings
        self.session = PromptSession(history=self.history, key_bindings=self.kb)

        # Add custom key bindings
        @self.kb.add("c-c")
        def _(event):
            """Ctrl-C to exit the chat"""
            event.app.exit()

    def run(self) -> str | None:
        """Run the chat interface"""

        try:
            # Get user input with arrow key history navigation
            user_input = self.session.prompt(">>> ")

            if user_input is None:
                return None

            # Simple echo bot - replace with your chat logic
            if user_input.lower() in ["/exit", "/quit"]:
                return None

        except KeyboardInterrupt:
            return ""
        except EOFError:
            return None

        return user_input.strip()
