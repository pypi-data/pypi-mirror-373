"""
Chat message handling and validation utilities
"""

from typing import List, Dict, Any


def ensure_alternating_roles(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensure messages alternate between user and assistant roles
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        List of messages with alternating roles
    """
    if not messages:
        return messages
    
    cleaned_messages = []
    last_role = None
    
    for message in messages:
        current_role = message.get('role')
        
        # Skip consecutive messages from the same role
        if current_role == last_role:
            # Merge content if both are from the same role
            if cleaned_messages and current_role in ['user', 'assistant']:
                cleaned_messages[-1]['content'] += '\n' + message.get('content', '')
                continue
        
        cleaned_messages.append(message)
        last_role = current_role
    
    return cleaned_messages


def sanity_check_messages(messages: List[Dict[str, Any]]) -> bool:
    """
    Perform sanity checks on message format and content
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        bool: True if messages pass sanity checks
    """
    if not messages:
        return True
    
    for message in messages:
        # Check required keys
        if 'role' not in message or 'content' not in message:
            return False
            
        # Check valid roles
        if message['role'] not in ['system', 'user', 'assistant', 'function']:
            return False
            
        # Check content is not empty
        if not message.get('content', '').strip():
            return False
    
    return True


def format_messages_for_api(messages: List[Dict[str, Any]], model: str = None) -> List[Dict[str, Any]]:
    """
    Format messages for specific API requirements
    
    Args:
        messages: Raw messages
        model: Model name for specific formatting
        
    Returns:
        Formatted messages
    """
    formatted = []
    
    for message in messages:
        formatted_msg = {
            'role': message.get('role', 'user'),
            'content': str(message.get('content', ''))
        }
        
        # Add any additional fields
        for key in ['name', 'function_call', 'tool_calls']:
            if key in message:
                formatted_msg[key] = message[key]
                
        formatted.append(formatted_msg)
    
    return formatted


class SendChatManager:
    """Manages sending chat messages and handling responses"""
    
    def __init__(self):
        self.history = []
        
    def send_chat(self, message: str) -> str:
        """Send a chat message and get response"""
        self.history.append({"role": "user", "content": message})
        response = "Chat response"
        self.history.append({"role": "assistant", "content": response})
        return response
        
    def clear_history(self):
        """Clear chat history"""
        self.history.clear()


class AutonomousFlow:
    """Handles autonomous conversation flows"""
    
    def __init__(self):
        self.active = False
        
    def start(self):
        """Start autonomous flow"""
        self.active = True
        
    def stop(self):
        """Stop autonomous flow"""
        self.active = False
        
    def process(self, input_data):
        """Process autonomous flow"""
        if not self.active:
            return None
        return "Processed"
