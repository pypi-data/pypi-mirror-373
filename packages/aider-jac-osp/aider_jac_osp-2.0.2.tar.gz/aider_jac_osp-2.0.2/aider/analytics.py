"""
Analytics tracking and usage statistics for Aider-Jac-OSP
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class Analytics:
    """Simple analytics tracking for Aider usage"""
    
    def __init__(self, enabled: bool = False, log_file: Optional[str] = None):
        self.enabled = enabled
        self.log_file = log_file or os.path.join(os.path.expanduser("~"), ".aider_analytics.log")
        self.session_start = time.time()
        self.events = []
        
    def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """Track an analytics event"""
        if not self.enabled:
            return
            
        event = {
            'timestamp': datetime.now().isoformat(),
            'event': event_name,
            'properties': properties or {},
            'session_duration': time.time() - self.session_start
        }
        
        self.events.append(event)
        
        # Optionally write to log file
        if self.log_file:
            self._write_to_log(event)
    
    def track_model_usage(self, model_name: str, tokens_used: int = 0, cost: float = 0.0):
        """Track model usage statistics"""
        self.track_event('model_usage', {
            'model': model_name,
            'tokens': tokens_used,
            'cost': cost
        })
    
    def track_command(self, command: str, success: bool = True):
        """Track command execution"""
        self.track_event('command_executed', {
            'command': command,
            'success': success
        })
    
    def track_error(self, error_type: str, error_message: str):
        """Track errors for debugging"""
        self.track_event('error', {
            'type': error_type,
            'message': error_message
        })
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            'session_duration': time.time() - self.session_start,
            'events_tracked': len(self.events),
            'enabled': self.enabled
        }
    
    def _write_to_log(self, event: Dict[str, Any]):
        """Write event to log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception:
            pass  # Fail silently for analytics
    
    def flush(self):
        """Flush any pending analytics data"""
        if self.events:
            self.track_event('session_end', {
                'total_events': len(self.events),
                'session_duration': time.time() - self.session_start
            })
            
    def disable(self):
        """Disable analytics tracking"""
        self.enabled = False
        
    def enable(self):
        """Enable analytics tracking"""
        self.enabled = True
