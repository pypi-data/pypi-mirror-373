"""Markdown stream for aider."""

class MarkdownStream:
    """Placeholder markdown stream class"""
    
    def __init__(self, stream=None):
        self.stream = stream
    
    def write(self, text):
        """Write text to stream"""
        if self.stream:
            self.stream.write(text)
    
    def flush(self):
        """Flush the stream"""
        if self.stream:
            self.stream.flush()
    
    def close(self):
        """Close the stream"""
        if self.stream:
            self.stream.close()
