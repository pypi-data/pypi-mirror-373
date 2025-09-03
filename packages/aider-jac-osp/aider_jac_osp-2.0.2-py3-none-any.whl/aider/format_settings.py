"""Format settings for aider."""

def format_settings(settings):
    """
    Format settings placeholder function
    
    Args:
        settings: Settings dictionary to format
        
    Returns:
        Formatted settings string
    """
    if not settings:
        return ""
    
    formatted = []
    for key, value in settings.items():
        formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)


def scrub_sensitive_info(text):
    """
    Scrub sensitive information from text
    
    Args:
        text: Text to scrub
        
    Returns:
        Scrubbed text
    """
    if not text:
        return ""
    
    # Basic scrubbing - replace common sensitive patterns
    import re
    
    # Replace API keys
    text = re.sub(r'(api.?key["\s]*[:=]["\s]*)[a-zA-Z0-9_-]+', r'\1***', text, flags=re.IGNORECASE)
    # Replace tokens
    text = re.sub(r'(token["\s]*[:=]["\s]*)[a-zA-Z0-9_-]+', r'\1***', text, flags=re.IGNORECASE)
    
    return text
