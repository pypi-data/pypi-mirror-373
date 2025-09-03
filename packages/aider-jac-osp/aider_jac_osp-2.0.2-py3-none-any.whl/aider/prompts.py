# flake8: noqa: E501
"""
Enhanced prompts module with support for /genius command and multi-modal prompt templates.

This module provides:
- System prompts for various AI assistant modes
- Template functions for dynamic prompt generation
- Integration hooks for editor.py and sendchat.py
- Configurable prompt personalization
"""

from typing import Dict, Any, Optional
import json


def get_optimized_prompt(prompt: str, **kwargs) -> str:
    """
    Optimize a prompt for token efficiency and effectiveness
    
    Args:
        prompt: The original prompt to optimize
        **kwargs: Additional parameters for optimization
        
    Returns:
        str: Optimized prompt
    """
    # Basic optimization - remove extra whitespace and normalize
    optimized = ' '.join(prompt.split())
    return optimized


def get_genius_template(template_name: str = "default") -> str:
    """
    Get a genius mode template by name
    
    Args:
        template_name: Name of the template to retrieve
        
    Returns:
        str: The genius template content
    """
    templates = {
        "default": """You are an AI coding assistant with advanced capabilities. 
Analyze the request carefully and provide comprehensive, well-structured responses.""",
        "analysis": """You are a code analysis expert. Examine the code thoroughly 
and provide detailed insights, potential improvements, and architectural recommendations.""",
        "optimization": """You are a performance optimization specialist. Focus on 
efficiency, scalability, and best practices in your code suggestions."""
    }
    return templates.get(template_name, templates["default"])


# COMMIT PROMPTS
# Conventional Commits text adapted from:
# https://www.conventionalcommits.org/en/v1.0.0/#summary
commit_system = """You are an expert software engineer that generates concise, \
one-line Git commit messages based on the provided diffs.
Review the provided context and diffs which are about to be committed to a git repo.
Review the diffs carefully.
Generate a one-line commit message for those changes.
The commit message should be structured as follows: <type>: <description>
Use these for <type>: fix, feat, build, chore, ci, docs, style, refactor, perf, test
Ensure the commit message:{language_instruction}
- Starts with the appropriate prefix.
- Is in the imperative mood (e.g., \"add feature\" not \"added feature\" or \"adding feature\").
- Does not exceed 72 characters.
Reply only with the one-line commit message, without any additional text, explanations, or line breaks.
"""

# GENIUS COMMAND PROMPTS
genius_system_base = """You are a brilliant creative problem-solving assistant with exceptional analytical capabilities. 
Your role is to provide innovative, insightful, and comprehensive solutions to complex programming and technical challenges.

Core capabilities:
- Deep technical analysis and pattern recognition
- Creative problem-solving with unconventional approaches  
- Multi-perspective thinking and lateral problem-solving
- Code optimization and architectural insights
- Debugging with root-cause analysis
- Performance and scalability considerations

When responding:
- Think creatively and explore multiple solution paths
- Provide detailed reasoning for your recommendations
- Consider edge cases and potential pitfalls
- Suggest best practices and optimization opportunities
- Break down complex problems into manageable components
- Offer both immediate fixes and long-term improvements

Your responses should be thorough, insightful, and demonstrate deep understanding of the technical context."""

genius_code_analysis = """You are an expert code analyst and architect specializing in deep code understanding and optimization.

Focus areas:
- Code quality assessment and improvement suggestions
- Performance bottlenecks identification and solutions  
- Security vulnerability analysis and mitigation
- Design pattern recommendations and refactoring opportunities
- Scalability and maintainability enhancements
- Cross-module dependency analysis and optimization

Analyze the provided code with exceptional attention to:
- Logic flow and algorithmic efficiency
- Memory usage and resource management
- Error handling and edge cases
- Code organization and structure
- Documentation and readability
- Testing and validation needs

Provide actionable insights that go beyond surface-level observations."""

genius_debugging = """You are a master debugger with exceptional skills in root-cause analysis and systematic problem resolution.

Debugging approach:
- Systematic analysis of symptoms and error patterns
- Trace execution flow and data transformation
- Identify logical inconsistencies and runtime issues  
- Analyze dependencies and integration points
- Consider environmental and configuration factors
- Evaluate concurrency and timing issues

Investigation methodology:
- Gather comprehensive context and reproduction steps
- Hypothesize potential causes based on evidence
- Recommend targeted debugging strategies
- Suggest logging and monitoring improvements
- Provide prevention strategies for similar issues

Focus on finding the true root cause, not just fixing symptoms."""

genius_architecture = """You are a senior software architect with expertise in system design and technical leadership.

Architectural considerations:
- System design patterns and best practices
- Scalability and performance architecture
- Integration patterns and API design
- Data flow and storage optimization
- Security architecture and threat modeling
- Deployment and operational considerations

Design philosophy:
- Balance complexity with maintainability
- Consider future growth and evolution
- Optimize for team productivity and code quality
- Ensure robust error handling and recovery
- Design for testability and observability
- Plan for monitoring and troubleshooting

Provide strategic technical guidance that considers both immediate needs and long-term sustainability."""

# GENIUS PROMPT MODES
GENIUS_MODES = {
    "default": genius_system_base,
    "code_analysis": genius_code_analysis,
    "debugging": genius_debugging,
    "architecture": genius_architecture,
    "creative": genius_system_base + "\n\nEmphasize creative and unconventional solutions. Think outside the box and propose innovative approaches that others might not consider.",
    "performance": genius_code_analysis + "\n\nFocus heavily on performance optimization, efficiency improvements, and resource utilization. Prioritize speed and scalability in your recommendations.",
    "security": genius_code_analysis + "\n\nPrioritize security considerations, vulnerability assessment, and secure coding practices. Analyze for potential security risks and provide hardening recommendations."
}

# COMMANDS
undo_command_reply = (
    "I did `git reset --hard HEAD~1` to discard the last edits. Please wait for further"
    " instructions before attempting that change again. Feel free to ask relevant questions about"
    " why the changes were reverted."
)

added_files = (
    "I added these files to the chat: {fnames}\nLet me know if there are others we should add."
)

run_output = """I ran this command:
{command}
And got this output:
{output}
"""

genius_activation = """🧠 **Genius Mode Activated** 🧠
Mode: {mode}
Focus: {focus_area}

I'm now operating in enhanced analytical mode with deep problem-solving capabilities. Please describe your challenge or question, and I'll provide comprehensive, innovative solutions.
"""

# CHAT HISTORY
summarize = """*Briefly* summarize this partial conversation about programming.
Include less detail about older parts and more detail about the most recent messages.
Start a new paragraph every time the topic changes!
This is only part of a longer conversation so *DO NOT* conclude the summary with language like "Finally, ...". Because the conversation continues after the summary.
The summary *MUST* include the function names, libraries, packages that are being discussed.
The summary *MUST* include the filenames that are being referenced by the assistant inside the ```...``` fenced code blocks!
The summaries *MUST NOT* include ```...``` fenced code blocks!
Phrase the summary with the USER in first person, telling the ASSISTANT about the conversation.
Write *as* the user.
The user should refer to the assistant as *you*.
Start the summary with "I asked you...".
"""

summary_prefix = "I spoke to you previously about a number of things.\n"

# UNIFIED PROMPT SYSTEM
PROMPTS = {
    "commit": commit_system,
    "genius": genius_system_base,
    "genius_code": genius_code_analysis,
    "genius_debug": genius_debugging,
    "genius_arch": genius_architecture,
    "summarize": summarize,
    "undo": undo_command_reply,
    "added_files": added_files,
    "run_output": run_output,
    "genius_activation": genius_activation
}

# PROMPT CONFIGURATIONS
class PromptConfig:
    """Configuration class for prompt personalization and settings."""
    
    def __init__(self):
        self.creativity_level = "balanced"  # low, balanced, high
        self.detail_level = "comprehensive"  # brief, standard, comprehensive
        self.code_style = "pythonic"  # pythonic, functional, oop, minimal
        self.focus_areas = []  # performance, security, maintainability, etc.
        
        # LLM parameters that can be influenced by prompts
        self.temperature = 0.7
        self.max_tokens = 4000
        self.top_p = 0.9
    
    def update_from_args(self, args):
        """Update configuration from command line arguments or config."""
        if hasattr(args, 'creativity_level'):
            self.creativity_level = args.creativity_level
        if hasattr(args, 'detail_level'):
            self.detail_level = args.detail_level
        if hasattr(args, 'code_style'):
            self.code_style = args.code_style
        if hasattr(args, 'focus_areas'):
            self.focus_areas = args.focus_areas or []
        
        # Adjust LLM parameters based on settings
        if self.creativity_level == "high":
            self.temperature = 0.9
        elif self.creativity_level == "low":
            self.temperature = 0.3
        
        if self.detail_level == "comprehensive":
            self.max_tokens = 6000
        elif self.detail_level == "brief":
            self.max_tokens = 2000

# Global prompt configuration instance
_prompt_config = PromptConfig()

def get_prompt_config() -> PromptConfig:
    """Get the global prompt configuration."""
    return _prompt_config

def update_prompt_config(args=None, **kwargs):
    """Update the global prompt configuration."""
    if args:
        _prompt_config.update_from_args(args)
    
    for key, value in kwargs.items():
        if hasattr(_prompt_config, key):
            setattr(_prompt_config, key, value)

# GENIUS COMMAND INTEGRATION FUNCTIONS
def get_genius_prompt(user_input: str, mode: str = "default", context: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a genius mode prompt based on user input and context.
    
    Args:
        user_input: The user's question or problem description
        mode: The genius mode to use (default, debugging, architecture, etc.)
        context: Additional context like file contents, error messages, etc.
    
    Returns:
        Formatted prompt string for the LLM
    """
    config = get_prompt_config()
    
    # Get base prompt for the mode
    base_prompt = GENIUS_MODES.get(mode, genius_system_base)
    
    # Add personalization based on config
    personalization = _build_personalization_prompt(config)
    
    # Add context if provided
    context_section = _build_context_section(context) if context else ""
    
    # Combine all sections
    full_prompt = f"""{base_prompt}

{personalization}

{context_section}

User Query: {user_input}

Please provide a comprehensive, insightful response that demonstrates deep technical understanding and creative problem-solving."""
    
    return full_prompt

def get_genius_activation_message(mode: str = "default") -> str:
    """Get the activation message for genius mode."""
    mode_descriptions = {
        "default": "General problem-solving with creative insights",
        "code_analysis": "Deep code review and optimization",
        "debugging": "Systematic root-cause analysis",
        "architecture": "System design and technical strategy",
        "creative": "Innovative and unconventional solutions",
        "performance": "Speed and efficiency optimization",
        "security": "Security analysis and hardening"
    }
    
    focus_area = mode_descriptions.get(mode, "Enhanced analytical problem-solving")
    
    return PROMPTS["genius_activation"].format(
        mode=mode.title(),
        focus_area=focus_area
    )

def get_genius_modes() -> Dict[str, str]:
    """Get available genius modes and their descriptions."""
    return {
        "default": "Balanced creative problem-solving",
        "code": "Deep code analysis and optimization", 
        "debug": "Systematic debugging and root-cause analysis",
        "arch": "Software architecture and system design",
        "creative": "Innovative and unconventional approaches",
        "performance": "Performance optimization focus",
        "security": "Security-first analysis and recommendations"
    }

def _build_personalization_prompt(config: PromptConfig) -> str:
    """Build personalization section based on configuration."""
    personalizations = []
    
    if config.creativity_level == "high":
        personalizations.append("Emphasize highly creative and innovative solutions.")
    elif config.creativity_level == "low":
        personalizations.append("Focus on proven, conservative approaches.")
    
    if config.detail_level == "comprehensive":
        personalizations.append("Provide detailed explanations with thorough analysis.")
    elif config.detail_level == "brief":
        personalizations.append("Keep responses concise while maintaining insight.")
    
    if config.code_style == "pythonic":
        personalizations.append("Follow Pythonic conventions and best practices.")
    elif config.code_style == "functional":
        personalizations.append("Prefer functional programming approaches when applicable.")
    elif config.code_style == "oop":
        personalizations.append("Emphasize object-oriented design patterns.")
    
    if config.focus_areas:
        focus_list = ", ".join(config.focus_areas)
        personalizations.append(f"Pay special attention to: {focus_list}")
    
    if personalizations:
        return "Personalization guidelines:\n" + "\n".join(f"- {p}" for p in personalizations)
    return ""

def _build_context_section(context: Dict[str, Any]) -> str:
    """Build context section from provided context data."""
    sections = []
    
    if "files" in context:
        files_info = []
        for filename, content in context["files"].items():
            files_info.append(f"**{filename}**:\n```\n{content}\n```")
        sections.append("Files in context:\n" + "\n\n".join(files_info))
    
    if "error_message" in context:
        sections.append(f"Error message:\n```\n{context['error_message']}\n```")
    
    if "environment" in context:
        sections.append(f"Environment: {context['environment']}")
    
    if "additional_info" in context:
        sections.append(f"Additional information: {context['additional_info']}")
    
    if sections:
        return "Context:\n" + "\n\n".join(sections)
    return ""

# INTEGRATION HOOKS FOR OTHER MODULES
def get_prompt(prompt_key: str, **format_kwargs) -> str:
    """
    Get a prompt by key with optional formatting.
    
    Args:
        prompt_key: Key from PROMPTS dictionary
        **format_kwargs: Arguments for string formatting
    
    Returns:
        Formatted prompt string
    """
    if prompt_key not in PROMPTS:
        raise ValueError(f"Unknown prompt key: {prompt_key}")
    
    prompt = PROMPTS[prompt_key]
    
    if format_kwargs:
        try:
            return prompt.format(**format_kwargs)
        except KeyError as e:
            raise ValueError(f"Missing format argument for prompt '{prompt_key}': {e}")
    
    return prompt

def register_custom_prompt(key: str, prompt: str):
    """Register a custom prompt template."""
    PROMPTS[key] = prompt

def get_available_prompts() -> Dict[str, str]:
    """Get all available prompt keys and their first lines for reference."""
    return {key: prompt.split('\n')[0][:100] + "..." if len(prompt.split('\n')[0]) > 100 
            else prompt.split('\n')[0] for key, prompt in PROMPTS.items()}

# EDITOR.PY AND SENDCHAT.PY INTEGRATION HELPERS
def format_commit_prompt(language_instruction: str = "") -> str:
    """Format commit prompt with language instruction."""
    return PROMPTS["commit"].format(language_instruction=language_instruction)

def format_file_addition_message(filenames: list) -> str:
    """Format file addition message."""
    fnames = ", ".join(filenames)
    return PROMPTS["added_files"].format(fnames=fnames)

def format_command_output(command: str, output: str) -> str:
    """Format command execution output."""
    return PROMPTS["run_output"].format(command=command, output=output)

# BATCH PROMPT OPERATIONS
def get_multiple_prompts(prompt_keys: list, format_kwargs: Optional[Dict[str, Dict]] = None) -> Dict[str, str]:
    """
    Get multiple prompts at once.
    
    Args:
        prompt_keys: List of prompt keys
        format_kwargs: Optional dict of {prompt_key: {format_args}} for formatting
    
    Returns:
        Dictionary of {prompt_key: formatted_prompt}
    """
    results = {}
    format_kwargs = format_kwargs or {}
    
    for key in prompt_keys:
        kwargs = format_kwargs.get(key, {})
        results[key] = get_prompt(key, **kwargs)
    
    return results

# VALIDATION AND TESTING HELPERS
def validate_prompt_formatting(prompt_key: str, test_kwargs: Dict[str, Any]) -> bool:
    """Test if a prompt can be formatted with given arguments."""
    try:
        get_prompt(prompt_key, **test_kwargs)
        return True
    except (KeyError, ValueError):
        return False

def get_prompt_variables(prompt_key: str) -> list:
    """Extract format variables from a prompt template."""
    import re
    if prompt_key not in PROMPTS:
        return []
    
    prompt = PROMPTS[prompt_key]
    # Find all {variable_name} patterns
    variables = re.findall(r'\{(\w+)\}', prompt)
    return list(set(variables))  # Remove duplicates