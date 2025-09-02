import threading
import traceback
from suggestionManager import CodeSuggestionManager
from commandHistory import CommandHistory
from styledTextbox import StyledTextWindow

import tkinter as tk

class InteractiveConsoleText(StyledTextWindow):
    """TBD"""
    
    PROMPT = ">>> "
    PROMPT_LENGTH = 4
    
    def __init__(self, master, helpTab, userLocals=None, userGlobals=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Initialize components
        self.suggestionManager = CodeSuggestionManager(self, userLocals=userLocals, userGlobals=userGlobals)
        self.helpTab = helpTab
        
        self.navigatingHistory = False
        self.history = CommandHistory()
        
        self.inputVar = tk.StringVar()
        self.waitingForInput = False

        # Track current command
        self.currentCommandLine = 1
        self.isExecuting = False
        
        # Setup bindings
        self._setupBindings()
        
        # Initialize with first prompt
        self.addPrompt()

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
        return(int(self.index("end-1c").split(".")[0]))
    
    def getCommandStartPosition(self):
        """Get the starting position of the current command."""
        return(f"{self.currentCommandLine}.0")
    
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
            return(False)
        
        cursorLine = int(self.index("insert").split(".")[0])
        cursorCol = int(self.index("insert").split(".")[1])
        
        return((cursorLine >= self.currentCommandLine and 
                (cursorLine > self.currentCommandLine or cursorCol >= self.PROMPT_LENGTH)))

    def onEnter(self, event):
        """Handle Enter key - execute command."""
        self.suggestionManager.hideSuggestions()
        
        if self.waitingForInput:
            line = self.get("insert linestart", "insert lineend").strip()
            self.insert("end", "\n")  # move to next line like normal console
            self.inputVar.set(line)
            self.waitingForInput = False
            return("break")
        
        if self.isExecuting:
            return("break")
        
        command = self.getCurrentCommand()
        
        if not command.strip():
            return("break")
        
        # Check if statement is incomplete
        if self.isIncompleteStatement(command):
            return(self.onShiftEnter(event))
        
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
        
        return("break")

    def readInput(self):
        """Return the last entered line when input() is called."""
        self.waitingForInput = True
        self.wait_variable(self.inputVar)  #< waits until Enter is pressed
        line = self.inputVar.get()
        self.inputVar.set("")  #< reset
        return(line)

    def onShiftEnter(self, event):
        """Handle Shift+Enter - new line with auto-indent."""
        self.suggestionManager.hideSuggestions()
        
        if self.isExecuting:
            return("break")
        
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
        
        return("break")
    
    def onTab(self, event):
        """Handle Tab key for autocompletion."""
        if self.isExecuting:
            return("break")
        
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            self.suggestionManager.applySuggestion()
        else:
            self.suggestionManager.showSuggestions()
        
        return("break")
    
    def onBackspace(self, event):
        """Prevent backspace from deleting the prompt."""
        if not self.isCursorInEditableArea():
            return("break")
        
        # Check if we're at the prompt boundary
        cursorPos = self.index("insert")
        promptPos = self.getPromptPosition()
        
        if self.compare(cursorPos, "<=", promptPos):
            return("break")

    def onClick(self, event):
        """Handle mouse clicks - Ctrl+Click opens help for the clicked word."""
        self.suggestionManager.hideSuggestions()

        if event.state & 0x4:  #< Ctrl pressed
            clickIndex = self.index(f"@{event.x},{event.y}")  # mouse index

            # Get the full line
            i = int(clickIndex.split('.')[1])
            lineNum = clickIndex.split('.')[0]
            lineStart = f"{lineNum}.0"
            lineEnd = f"{lineNum}.end"
            lineText = self.get(lineStart, lineEnd)
            
            wordEndIndex = self.index(f"{clickIndex} wordend")
            # obj = self.get(f"{clickIndex} wordstart", f"{clickIndex} wordend").strip() #< Get the word at that index
            obj = ""
            for i in range (i-1,2, -1):
                letter = lineText[i]
                if (not (letter.isalnum() or letter == "_" or letter == ".")): #<  or (letter in " \n\t\r")
                    obj = lineText[i+1: int(wordEndIndex.split('.')[1])]
                    break
            
            
            if obj:
                self.helpTab.updateHelp(obj)
                self.helpTab.open()
            
            return("break")  #< Prevent default cursor behavior

        return(None)   #< Normal click behavior

    def onKeyPress(self, event):
        """Handle key press events."""
        # print(event.keysym)
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            if event.keysym == "Escape":
                self.suggestionManager.hideSuggestions()
                return("break")

        # Prevent editing outside command area
        if not event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R"]:
            self.navigatingHistory = False
            if not self.isCursorInEditableArea():
                self.mark_set("insert", "end")

        if event.keysym in ["Left", "Right"]:
            if self.index("insert") == self.getPromptPosition():
                self.mark_set("insert", "1.4")
                return("break")

    def onKeyRelease(self, event):
        """Handle key release events."""
        if event.keysym in ["Return", "Escape", "Left", "Right", "Home", "End"]:
            self.suggestionManager.hideSuggestions()
        elif event.keysym not in ["Up", "Down", "Shift_L", "Shift_R", "Control_L", "Control_R"]:
            if not self.isExecuting:
                self.after_idle(self.suggestionManager.showSuggestions)
                if not self.isExecuting:
                    self.after_idle(lambda: self.updateStyling(start=self.getPromptPosition()))

    def cancel(self, event):
        self.history.add(self.getCurrentCommand())
        self.replaceCurrentCommand("")

    def historyReplace(self, command):
        if self.getCurrentCommand() == "" or self.navigatingHistory:
            if self.isExecuting:
                return("break")

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
                return("break")
        command = self.history.navigateUp()
        return(self.historyReplace(command))
        # self.mark_set("insert", "insert -1 line")

    def onDown(self, event):
        if self.suggestionManager.suggestionWindow and \
           self.suggestionManager.suggestionWindow.winfo_viewable():
            if event.keysym == "Down":
                self.suggestionManager.handleNavigation("down")
                return("break")
        command = self.history.navigateDown()
        return(self.historyReplace(command))

    def isIncompleteStatement(self, code):
        """Check if the code is an incomplete statement."""
        lines = code.split("\n")
        if not lines[-1].strip():
            return(False)
        
        # Check for line ending with colon
        for line in lines:
            if line.strip().endswith(":"):
                return(True)
        
        return(False)
    
    def calculateIndent(self, line):
        """Calculate the indentation level for the next line."""
        currentIndent = len(line) - len(line.lstrip())
        
        # If line ends with colon, increase indent
        if line.strip().endswith(":"):
            return(currentIndent + 4)
        
        return(currentIndent)

    def writeOutput(self, text, tag="output"):
        """Write output to the console (thread-safe)."""
        def _write():
            self.insert("end", text + "\n", tag)
            self.see("end")
        
        self.after(0, _write)

    def getPromptPosition(self):
        """Get the position right after the prompt on current command line."""
        return(f"{self.currentCommandLine}.{self.PROMPT_LENGTH}")

    def getCurrentCommand(self):
        """Extract the current command text (without prompt)."""
        start = self.getPromptPosition()
        end = "end-1c"
        return(self.get(start, end))

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
