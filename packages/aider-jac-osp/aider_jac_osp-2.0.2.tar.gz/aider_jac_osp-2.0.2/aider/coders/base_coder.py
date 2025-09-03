"""
Base Coder - Main coding assistant functionality
"""

class UnknownEditFormat(Exception):
    """Exception raised when edit format is unknown"""
    pass


class Coder:
    """Main coder class that handles autonomous code editing"""
    
    def __init__(self, *args, **kwargs):
        """Initialize coder with basic setup"""
        self.repo = None
        self.genius_mode = None
        self.jac_integration = None
        self.sendchat_manager = None
        self.llm_manager = None
        self.lint_cmds = None
        self.verbose = False
    
    def get_repo_map(self):
        """Get repository map"""
        return "Repository map not available"
    
    def show_prompts(self):
        """Show available prompts"""
        print("Prompts not available")
    
    def resume_chat_history(self):
        """Resume chat history"""
        pass
    
    def run(self):
        """Run the main coder loop"""
        pass
