"""Error reporting functionality for aider."""

import sys
import traceback

def report_uncaught_exceptions(func):
    """
    Decorator to report uncaught exceptions
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Uncaught exception: {e}", file=sys.stderr)
            traceback.print_exc()
            raise
    return wrapper
