import customtkinter as ctk
import tkinter as tk
import traceback
import inspect
import threading
import sys
import io
import pygments
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
import keyword
import builtins


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


class CodeSuggestionManager:
    """Manages code suggestions and autocomplete functionality."""
    
    def __init__(self, textWidget, userLocals, userGlobals):
        self.userLocals = userLocals
        self.userGlobals = userGlobals
        self.textWidget = textWidget
        self.suggestionWindow = None
        self.suggestionListbox = None
        self.suggestions = []
        self.selectedSuggestion = 0
        
        # Build suggestion sources
        self.keywords = keyword.kwlist
        self.builtins = [name for name in dir(builtins) if not name.startswith('_')]
    
    def getCurrentWord(self):
        """Extract the word being typed at cursor position and suggest dir() if applicable."""
        suggestions = []
        cursorPos = self.textWidget.index(tk.INSERT)
        lineStart = self.textWidget.index(f"{cursorPos} linestart")
        currentLine = self.textWidget.get(lineStart, cursorPos)

        # Find the current word
        words = currentLine.split()
        if not words:
            return "", suggestions

        currentWord = words[-1]


        # If the word contains a dot, try to evaluate the base and get its dir()
        if '.' in currentWord:
            try:
                base_expr = '.'.join(currentWord.split('.')[:-1])
                obj = eval(base_expr, self.userLocals, self.userGlobals)
                suggestions = dir(obj)
            except:
                pass
        for char in "([{,.":
            if char in currentWord:
                currentWord = currentWord.split(char)[-1]

        return currentWord, suggestions
    
    def getSuggestions(self, partialWord, suggestions=[]):
        """Get code suggestions for partial word."""
        if len(partialWord) < 2:
            return suggestions
        
        # print(partialWord)
        if suggestions != []:
            suggestions = [suggestion for suggestion in suggestions if suggestion.lower().startswith(partialWord.lower())]
        else:
            # Add matching keywords
            for kw in self.keywords:
                if kw.startswith(partialWord.lower()):
                    suggestions.append(kw)
            
            # Add matching builtins
            for builtin in self.builtins:
                if builtin.startswith(partialWord):
                    suggestions.append(builtin)
            
            # Add matching variables from namespace
            master = self.textWidget.master
            if hasattr(master, 'userLocals'):
                for var in master.userLocals:
                    if var.startswith(partialWord) and not var.startswith('_'):
                        suggestions.append(var)
            
            if hasattr(master, 'userGlobals'):
                for var in master.userGlobals:
                    if var.startswith(partialWord) and not var.startswith('_'):
                        suggestions.append(var)
        
        # Remove duplicates and sort
        return sorted(list(set(suggestions)))
    
    def showSuggestions(self):
        """Display the suggestions popup."""
        currentWord, extraSuggestions = self.getCurrentWord()
        suggestions = self.getSuggestions(currentWord, extraSuggestions)
        
        if not suggestions:
            self.hideSuggestions()
            return
        
        self.suggestions = suggestions
        self.selectedSuggestion = 0
        
        # Create suggestion window if needed
        if not self.suggestionWindow:
            self._createSuggestionWindow()
        
        # Update listbox content
        self.suggestionListbox.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestionListbox.insert(tk.END, suggestion)
        
        self.suggestionListbox.selection_set(0)
        
        # Position window near cursor
        self._positionSuggestionWindow()
        self.suggestionWindow.deiconify()
    
    def _createSuggestionWindow(self):
        """Create the suggestion popup window."""
        self.suggestionWindow = tk.Toplevel(self.textWidget)
        self.suggestionWindow.wm_overrideredirect(True)
        self.suggestionWindow.configure(bg="#2d2d2d")
        
        self.suggestionListbox = tk.Listbox(
            self.suggestionWindow,
            bg="#2d2d2d",
            fg="white",
            selectbackground="#0066cc",
            font=("Consolas", 10),
            height=8
        )
        self.suggestionListbox.pack()
    
    def _positionSuggestionWindow(self):
        """Position the suggestion window near the cursor."""
        cursorPos = self.textWidget.index(tk.INSERT)
        x, y, _, _ = self.textWidget.bbox(cursorPos)
        x += self.textWidget.winfo_rootx()
        y += self.textWidget.winfo_rooty() + 20
        self.suggestionWindow.geometry(f"+{x}+{y}")
    
    def hideSuggestions(self):
        """Hide the suggestions popup."""
        if self.suggestionWindow:
            self.suggestionWindow.withdraw()
    
    def applySuggestion(self, suggestion=None):
        """Apply the selected suggestion at cursor position."""
        if not suggestion and self.suggestions:
            suggestion = self.suggestions[self.selectedSuggestion]
        if not suggestion:
            return
        
        currentWord, _ = self.getCurrentWord()
        # Only insert the missing part
        missingPart = suggestion[len(currentWord):]
        cursorPos = self.textWidget.index(tk.INSERT)
        self.textWidget.insert(cursorPos, missingPart)
        
        self.hideSuggestions()
    
    def handleNavigation(self, direction):
        """Handle up/down navigation in suggestions."""
        if not self.suggestions:
            return
            
        if direction == "down":
            self.selectedSuggestion = min(self.selectedSuggestion + 1, len(self.suggestions) - 1)
        else:  # up
            self.selectedSuggestion = max(self.selectedSuggestion - 1, 0)
        
        self.suggestionListbox.selection_clear(0, tk.END)
        self.suggestionListbox.selection_set(self.selectedSuggestion)


class CommandHistory:
    """Manages command history and navigation."""
    
    def __init__(self):
        self.history = []
        self.index = -1
        self.tempCommand = ""
    
    def add(self, command):
        """Add a command to history."""
        if command.strip():
            self.history.append(command)
            self.index = len(self.history)
    
    def navigateUp(self):
        """Get previous command from history."""
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        return None
    
    def navigateDown(self):
        """Get next command from history."""
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        elif self.index == len(self.history) - 1:
            self.index = len(self.history)
            return self.tempCommand
        return None
    
    def setTemp(self, command):
        """Store temporary command while navigating history."""
        self.tempCommand = command


class InteractiveConsoleText(tk.Text):
    """A tk.Text widget with Python syntax highlighting for interactive console."""
    
    PROMPT = ">>> "
    PROMPT_LENGTH = 4
    
    def __init__(self, master, userLocals=None, userGlobals=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Initialize components
        self.suggestionManager = CodeSuggestionManager(self, userLocals=userLocals, userGlobals=userGlobals)
        
        self.navigatingHistory = False
        self.history = CommandHistory()
        
        # Syntax highlighting setup
        self.lexer = PythonLexer()
        self.style = get_style_by_name("monokai")
        
        # Track current command
        self.currentCommandLine = 1
        self.isExecuting = False
        
        # Setup tags and bindings
        self._setupTags()
        self._setupBindings()
        
        # Initialize with first prompt
        self.addPrompt()
    
    def _setupTags(self):
        """Configure text tags for different output types."""
        self.tag_configure("prompt", foreground="#00ff00", font=("Consolas", 12, "bold"))
        self.tag_configure("output", foreground="#ffffff", font=("Consolas", 12))
        self.tag_configure("error", foreground="#ff6666", font=("Consolas", 12))
        self.tag_configure("result", foreground="#66ccff", font=("Consolas", 12))
        
        # Configure syntax highlighting tags
        for token, style in self.style:
            if style["color"]:
                fg = f"#{style['color']}"
                font = ("Consolas", 12, "bold" if style["bold"] else "normal")
                self.tag_configure(str(token), foreground=fg, font=font)
    
    def _setupBindings(self):
        """Setup all key and mouse bindings."""
        self.bind("<Return>", self.onEnter)
        self.bind("<Shift-Return>", self.onShiftEnter)
        self.bind("<Control-c>", self.cancel)
        self.bind("<Tab>", self.onTab)
        self.bind("<BackSpace>", self.onBackspace)
        self.bind("<KeyRelease>", self.onKeyRelease)
        self.bind("<KeyPress>", self.onKeyPress)
        self.bind("<Button-1>", self.onClick)
        self.bind("<Up>", self.onUp)
        self.bind("<Down>", self.onDown)

    def getCurrentLineNumber(self):
        """Get the line number where current command starts."""
        return int(self.index("end-1c").split(".")[0])
    
    def getPromptPosition(self):
        """Get the position right after the prompt on current command line."""
        return f"{self.currentCommandLine}.{self.PROMPT_LENGTH}"
    
    def getCommandStartPosition(self):
        """Get the starting position of the current command."""
        return f"{self.currentCommandLine}.0"
    
    def getCurrentCommand(self):
        """Extract the current command text (without prompt)."""
        if self.isExecuting:
            return ""
        
        start = self.getPromptPosition()
        end = "end-1c"
        return self.get(start, end)
    
    def replaceCurrentCommand(self, newCommand):
        """Replace the current command with new text."""
        if self.isExecuting:
            return
        
        start = self.getPromptPosition()
        end = "end-1c"
        
        self.delete(start, end)
        self.insert(start, newCommand)
        self.see("end")
    
    def isCursorInEditableArea(self):
        """Check if cursor is in the editable command area."""
        if self.isExecuting:
            return False
        
        cursorLine = int(self.index("insert").split(".")[0])
        cursorCol = int(self.index("insert").split(".")[1])
        
        return (cursorLine >= self.currentCommandLine and 
                (cursorLine > self.currentCommandLine or cursorCol >= self.PROMPT_LENGTH))

    def onEnter(self, event):
        """Handle Enter key - execute command."""
        self.suggestionManager.hideSuggestions()
        
        if self.isExecuting:
            return "break"
        
        command = self.getCurrentCommand()
        
        if not command.strip():
            return "break"
        
        # Check if statement is incomplete
        if self.isIncompleteStatement(command):
            return self.onShiftEnter(event)
        
        # Execute the command
        self.history.add(command)
        self.mark_set("insert", "end")
        self.insert("end", "\n")
        self.see("end")
        
        # Execute in thread
        self.isExecuting = True
        threading.Thread(
            target=self.executeCommandThreaded,
            args=(command,),
            daemon=True
        ).start()
        
        return "break"
    
    def onShiftEnter(self, event):
        """Handle Shift+Enter - new line with auto-indent."""
        self.suggestionManager.hideSuggestions()
        
        if self.isExecuting:
            return "break"
        
        # Get current line for indent calculation
        cursorPos = self.index("insert")
        lineStart = self.index(f"{cursorPos} linestart")
        lineEnd = self.index(f"{cursorPos} lineend")
        currentLine = self.get(lineStart, lineEnd)
        
        # Calculate indentation
        indent = self.calculateIndent(currentLine)
        
        # Insert newline with indent
        self.insert("insert", "\n" + " " * indent)
        self.see("end")
        
        return "break"
    
    def onTab(self, event):
        """Handle Tab key for autocompletion."""
        if self.isExecuting:
            return "break"
        
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            self.suggestionManager.applySuggestion()
        else:
            self.suggestionManager.showSuggestions()
        
        return "break"
    
    def onBackspace(self, event):
        """Prevent backspace from deleting the prompt."""
        if not self.isCursorInEditableArea():
            return "break"
        
        # Check if we're at the prompt boundary
        cursorPos = self.index("insert")
        promptPos = self.getPromptPosition()
        
        if self.compare(cursorPos, "<=", promptPos):
            return "break"
    
    def onClick(self, event):
        """Handle mouse clicks - prevent clicking before prompt."""
        self.suggestionManager.hideSuggestions()
        return None

    def onKeyPress(self, event):
        """Handle key press events."""
        # print(event.keysym)
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            if event.keysym == "Escape":
                self.suggestionManager.hideSuggestions()
                return "break"

        # Prevent editing outside command area
        if not event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R"]:
            self.navigatingHistory = False
            if not self.isCursorInEditableArea():
                self.mark_set("insert", "end")

        if event.keysym in ["Left", "Right"]:
            if self.index("insert") == self.getPromptPosition():
                self.mark_set("insert", "1.4")
                return "break"

    def onKeyRelease(self, event):
        """Handle key release events."""
        if event.keysym in ["Return", "Escape", "Left", "Right", "Home", "End"]:
            self.suggestionManager.hideSuggestions()
        elif event.keysym not in ["Up", "Down", "Shift_L", "Shift_R", "Control_L", "Control_R"]:
            if not self.isExecuting:
                self.after_idle(self.suggestionManager.showSuggestions)
                self.after_idle(self.highlightCurrentCommand)

    def cancel(self, event):
        self.history.add(self.getCurrentCommand())
        self.replaceCurrentCommand("")

    def historyReplace(self, command):
        if self.getCurrentCommand() == "" or self.navigatingHistory:
            if self.isExecuting:
                return "break"

            if self.history.index == len(self.history.history):
                self.history.setTemp(self.getCurrentCommand())

            if command is not None:
                self.replaceCurrentCommand(command)
                self.navigatingHistory = True
            return("break")

    def onUp(self, event):
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            if event.keysym == "Up":
                self.suggestionManager.handleNavigation("up")
                return "break"
        command = self.history.navigateUp()
        return(self.historyReplace(command))
        # self.mark_set("insert", "insert -1 line")

    def onDown(self, event):
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            if event.keysym == "Down":
                self.suggestionManager.handleNavigation("down")
                return "break"
        command = self.history.navigateDown()
        return(self.historyReplace(command))

    def isIncompleteStatement(self, code):
        """Check if the code is an incomplete statement."""
        lines = code.split("\n")
        if not lines[-1].strip():
            return False
        
        # Check for line ending with colon
        for line in lines:
            if line.strip().endswith(":"):
                return True
        
        return False
    
    def calculateIndent(self, line):
        """Calculate the indentation level for the next line."""
        currentIndent = len(line) - len(line.lstrip())
        
        # If line ends with colon, increase indent
        if line.strip().endswith(":"):
            return currentIndent + 4
        
        return currentIndent
    
    def highlightCurrentCommand(self):
        """Apply syntax highlighting to the current command."""
        if self.isExecuting:
            return
        
        # Clear existing highlighting
        start = self.getPromptPosition()
        end = "end-1c"
        
        for token, _ in self.style:
            self.tag_remove(str(token), start, end)
        
        # Get and highlight the command
        command = self.getCurrentCommand()
        if not command:
            return

        self.mark_set("highlight_pos", start)
        
        for token, content in pygments.lex(command, self.lexer):
            if content:
                endPos = f"highlight_pos + {len(content)}c"
                if content.strip():  # Only highlight non-whitespace
                    self.tag_add(str(token), "highlight_pos", endPos)
                self.mark_set("highlight_pos", endPos)

    def writeOutput(self, text, tag="output"):
        """Write output to the console (thread-safe)."""
        def _write():
            self.insert("end", text + "\n", tag)
            self.see("end")
        
        self.after(0, _write)
    
    def addPrompt(self):
        """Add a new command prompt."""
        def _add():
            # Store the line number for the new command
            self.currentCommandLine = self.getCurrentLineNumber()
            
            # Insert prompt
            self.insert("end", self.PROMPT)
            promptStart = f"{self.currentCommandLine}.0"
            promptEnd = f"{self.currentCommandLine}.{self.PROMPT_LENGTH}"
            self.tag_add("prompt", promptStart, promptEnd)
            
            self.mark_set("insert", "end")
            self.see("end")
            self.isExecuting = False
        
        if self.isExecuting:
            self.after(0, _add)
        else:
            _add()
    
    def executeCommandThreaded(self, command):
        """Execute a command in a separate thread."""
        try:
            # Try eval first for expressions
            result = eval(command, self.master.userGlobals, self.master.userLocals)
            if result is not None:
                self.writeOutput(str(result), "result")
                self.master.userLocals["_"] = result
        except SyntaxError:
            try:
                # Try exec for statements
                exec(command, self.master.userGlobals, self.master.userLocals)
            except Exception:
                self.writeOutput(traceback.format_exc(), "error")
        except Exception:
            self.writeOutput(traceback.format_exc(), "error")
        
        # Add new prompt after execution
        self.addPrompt()


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
    
    def _createUi(self):
        """Create the user interface."""
        # Main frame
        frame = ctk.CTkFrame(self)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Console text widget
        self.console = InteractiveConsoleText(
            frame,
            userGlobals=self.userGlobals,
            userLocals=self.userLocals,
            wrap="word",
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            font=("Consolas", 12)
        )
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Give console access to namespace
        self.console.master = self
    
    def _setupOutputRedirect(self):
        """Setup stdout/stderr redirection to console."""
        sys.stdout = StdoutRedirect(self.console.writeOutput)
        sys.stderr = StdoutRedirect(
            lambda text, tag: self.console.writeOutput(text, "error")
        )
    
    def probe(self, *args, **kwargs):
        """Start the console main loop."""
        self.mainloop(*args, **kwargs)


# Example usage
if __name__ == "__main__":
    # Example variables and functions for testing
    foo = 42
    
    def greet(name):
        print(f"Hello {name}!")
        return f"Greeted {name}"
    
    # Create the list for testing autocomplete
    exampleList = [1, 2, 3, 4, 5]
    
    # Start the console
    InteractiveConsole().probe()