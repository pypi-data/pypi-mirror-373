"""
Simple spinner utility for terminal operations
"""
import time
import threading
import sys


class Spinner:
    """Simple terminal spinner for showing progress"""
    
    def __init__(self, message="Loading...", chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        self.message = message
        self.chars = chars
        self.running = False
        self.thread = None
        
    def _spin(self):
        """Internal spinning method"""
        i = 0
        while self.running:
            char = self.chars[i % len(self.chars)]
            sys.stdout.write(f'\r{char} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()
        
    def start(self):
        """Start the spinner"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin)
            self.thread.daemon = True
            self.thread.start()
        
    def stop(self):
        """Stop the spinner"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
                
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
                
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Alias for compatibility
WaitingSpinner = Spinner