import tkinter as tk
import pygments
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name

class StyledTextWindow(tk.Text):
    def __init__(self, master,  **kwargs):
        super().__init__(master, **kwargs)
       
        # Syntax highlighting setup
        self.lexer = PythonLexer()
        self.style = get_style_by_name("monokai")
        
        # Setup tags
        self._setupTags()

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


    def updateStyling(self, start="1.0"):
        """Apply syntax highlighting to the current command."""
        end = "end-1c"
        
        for token, _ in self.style:
            self.tag_remove(str(token), start, end)
        
        # Get and highlight the command
        command = self.get(start, "end-1c")
        if not command:
            return(-1)

        self.mark_set("highlight_pos", start)
        
        for token, content in pygments.lex(command, self.lexer):
            if content:
                endPos = f"highlight_pos + {len(content)}c"
                if content.strip():  # Only highlight non-whitespace
                    self.tag_add(str(token), "highlight_pos", endPos)
                self.mark_set("highlight_pos", endPos)
