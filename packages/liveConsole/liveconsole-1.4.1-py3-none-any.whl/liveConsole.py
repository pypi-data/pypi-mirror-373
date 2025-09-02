import customtkinter as ctk
import inspect
import sys
import io

from helpTab import HelpTab
from mainConsole import InteractiveConsoleText


class StdoutRedirect(io.StringIO):
    """Redirects stdout/stderr to a callback function."""
    
    def __init__(self, writeCallback):
        super().__init__()
        self.writeCallback = writeCallback

    def write(self, s):
        if s.strip():
            self.writeCallback(s, "output")

    def flush(self):
        pass

class StdinRedirect(io.StringIO):
    """Redirects stdin to capture input() from the console."""
    def __init__(self, readCallback):
        super().__init__()
        self.readCallback = readCallback

    def readline(self, *args, **kwargs):
        return(self.readCallback())


class InteractiveConsole(ctk.CTk):
    """Main console window application."""
    
    def __init__(self, userGlobals=None, userLocals=None):
        super().__init__()
        
        # Window setup
        self.title("Live Interactive Console")
        self.geometry("900x600")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Get namespace from caller if not provided
        if userGlobals is None or userLocals is None:
            callerFrame = inspect.currentframe().f_back
            if userGlobals is None:
                userGlobals = callerFrame.f_globals
            if userLocals is None:
                userLocals = callerFrame.f_locals
        
        self.userGlobals = userGlobals
        self.userLocals = userLocals
        
        # Create UI
        self._createUi()
        
        # Redirect stdout/stderr
        self._setupOutputRedirect()
        self._setupInputRedirect()
    
    def _createUi(self):
        """Create UI with console and help tab."""
        frame = ctk.CTkFrame(self)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Horizontal frame
        self.horizFrame = ctk.CTkFrame(frame)
        self.horizFrame.pack(fill="both", expand=True)

        # Right: Help Tab
        self.helpTab = HelpTab(self.horizFrame, width=500)

        # Left: Console
        self.consoleFrame = ctk.CTkFrame(self.horizFrame, width=600)
        self.consoleFrame.pack(side="left", fill="both", expand=True)
        self.consoleFrame.pack_propagate(False)  # prevent shrinking to fit contents

        self.console = InteractiveConsoleText(
            self.consoleFrame,
            self.helpTab,
            userGlobals=self.userGlobals,
            userLocals=self.userLocals,
            wrap="word",
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            font=("Consolas", 12)
        )
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        self.console.master = self

    
    def _setupOutputRedirect(self):
        """Setup stdout/stderr redirection to console."""
        sys.stdout = StdoutRedirect(self.console.writeOutput)
        sys.stderr = StdoutRedirect(
            lambda text, tag: self.console.writeOutput(text, "error")
        )

    def _setupInputRedirect(self):
        """Setup stdin redirection to console."""
        sys.stdin = StdinRedirect(self.console.readInput)
    
    def probe(self, *args, **kwargs):
        """Start the console main loop."""
        self.mainloop(*args, **kwargs)


# Example usage
if __name__ == "__main__":
    # Example variables and functions for testing
    foo = 42
    
    def greet(name):
        print(f"Hello {name}!")
        return(f"Greeted {name}")
    
    # Create the list for testing autocomplete
    exampleList = [1, 2, 3, 4, 5]
    
    # Start the console
    InteractiveConsole().probe()