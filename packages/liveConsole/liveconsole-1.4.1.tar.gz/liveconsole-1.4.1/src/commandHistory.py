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
            return(self.history[self.index])
        return(None)
    
    def navigateDown(self):
        """Get next command from history."""
        if self.index < len(self.history) - 1:
            self.index += 1
            return(self.history[self.index])
        elif self.index == len(self.history) - 1:
            self.index = len(self.history)
            return(self.tempCommand)
        return(None)
    
    def setTemp(self, command):
        """Store temporary command while navigating history."""
        self.tempCommand = command