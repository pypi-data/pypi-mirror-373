"""Chat history functionality for aider."""

class ChatSummary:
    """Placeholder chat summary class"""
    
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        """Add a message to the summary"""
        self.messages.append({"role": role, "content": content})
    
    def get_summary(self):
        """Get the chat summary"""
        return self.messages
    
    def clear(self):
        """Clear the summary"""
        self.messages = []
