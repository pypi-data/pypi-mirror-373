import keyword
import builtins
import tkinter as tk

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
            return("", suggestions)

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

        return(currentWord, suggestions)
    
    def getSuggestions(self, partialWord, suggestions=[]):
        """Get code suggestions for partial word."""
        if len(partialWord) < 2:
            return(suggestions)

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
        return(sorted(list(set(suggestions))))
    
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
