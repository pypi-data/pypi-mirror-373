"""Dump utilities for debugging and inspection."""

def dump(*args, **kwargs):
    """Simple dump function for debugging"""
    print("Debug dump:", args, kwargs)
    return args[0] if args else None
