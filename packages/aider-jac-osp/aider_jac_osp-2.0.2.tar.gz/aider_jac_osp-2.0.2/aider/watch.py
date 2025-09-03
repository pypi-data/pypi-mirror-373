"""File watching functionality for Aider"""

import time
import threading
from pathlib import Path
from typing import List, Callable, Optional


class FileWatcher:
    """Watches files for changes and triggers callbacks"""
    
    def __init__(self, paths: List[str], callback: Optional[Callable] = None):
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.watching = False
        self.thread = None
        self.last_modified = {}
        
    def start(self):
        """Start watching files"""
        if self.watching:
            return
            
        self.watching = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop watching files"""
        self.watching = False
        if self.thread:
            self.thread.join()
            
    def _watch_loop(self):
        """Main watching loop"""
        while self.watching:
            for path in self.paths:
                if path.exists():
                    mtime = path.stat().st_mtime
                    if path not in self.last_modified:
                        self.last_modified[path] = mtime
                    elif self.last_modified[path] != mtime:
                        self.last_modified[path] = mtime
                        if self.callback:
                            self.callback(str(path))
            time.sleep(0.1)
