import sys
import io
from pygments.styles import get_style_by_name
import customtkinter as ctk
from styledTextbox import StyledTextWindow

class HelpTab(ctk.CTkFrame):
    """A right-hand help tab with closable and updateable text content."""

    def __init__(self, parent, width=500, title="Help", **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.parent = parent
        self.visible = False

        # Ensure initial width is respected
        self.pack_propagate(False)

        # Header frame with title and close button
        headerFrame = ctk.CTkFrame(self, height=30)
        headerFrame.pack(fill="x")
        self.style = get_style_by_name("monokai")

        self.titleLabel = ctk.CTkLabel(headerFrame, text=title, font=("Consolas", 12, "bold"))
        self.titleLabel.pack(side="left", padx=5)

        self.closeButton = ctk.CTkButton(headerFrame, text="X", height=20, command=self.close)
        self.closeButton.pack(side="right", padx=5)

        # Scrollable text area
        self.textBox = StyledTextWindow(self, wrap="word", font=("Consolas", 11), bg="#2e2e2e")
        self.textBox.pack(fill="both", expand=True, padx=5, pady=5)
        self.textBox.configure(state="disabled")  # read-only

    def close(self):
        """Hide the help tab."""
        if self.visible:
            self.pack_forget()
            self.visible = False

    def open(self):
        """Show the help tab."""
        if not self.visible:
            self.pack(side="left", fill="y")
            # self.configure(width=self.minWidth)
            self.visible = True
            
    def _getHelp(self, obj):
        """Return the output of help(obj) as a string."""
        old_stdout = sys.stdout  # save current stdout
        sys.stdout = buffer = io.StringIO()  # redirect stdout to a string buffer
        try:
            help(obj)
            return(buffer.getvalue())
        finally:
            sys.stdout = old_stdout  # restore original stdout

    def updateHelp(self, obj):
        """Update the help tab content."""

        self.textBox.configure(state="normal")
        self.textBox.delete("1.0", "end")
        self.textBox.insert("1.0", self._getHelp(obj))
        self.textBox.updateStyling()
        self.textBox.configure(state="disabled")
