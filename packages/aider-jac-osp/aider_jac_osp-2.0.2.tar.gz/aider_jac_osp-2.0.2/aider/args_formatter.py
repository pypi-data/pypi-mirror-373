"""Argument formatters for aider."""

import argparse

class MarkdownHelpFormatter(argparse.HelpFormatter):
    """Markdown formatter for help text"""
    
    def _format_action(self, action):
        """Format an action in markdown"""
        return super()._format_action(action)


class YamlHelpFormatter(argparse.HelpFormatter):
    """YAML formatter for help text"""
    
    def _format_action(self, action):
        """Format an action in YAML"""
        return super()._format_action(action)
