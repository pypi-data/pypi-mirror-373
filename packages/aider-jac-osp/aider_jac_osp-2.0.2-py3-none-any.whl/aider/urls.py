"""
URL handling utilities for web scraping and content retrieval
"""

import re
import requests
from urllib.parse import urlparse, urljoin
from typing import List, Optional, Dict, Any


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text using regex"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)


def fetch_url_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch content from a URL
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Content as string or None if failed
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def clean_url(url: str) -> str:
    """Clean and normalize a URL"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def get_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


class URLProcessor:
    """Process and manage URLs for content extraction"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        
    def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a URL and extract relevant information
        
        Returns:
            Dict with url, title, content, domain, etc.
        """
        result = {
            'url': url,
            'domain': get_domain(url),
            'title': None,
            'content': None,
            'error': None
        }
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            content = response.text
            result['content'] = content
            
            # Try to extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            if title_match:
                result['title'] = title_match.group(1).strip()
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
