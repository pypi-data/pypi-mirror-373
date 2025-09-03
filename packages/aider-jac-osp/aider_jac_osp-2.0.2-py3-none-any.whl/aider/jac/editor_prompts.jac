# editor_prompts.jac
# Jac module for code editor prompt templates
# Focused on code editing, refactoring, bug fixing, and suggestions

walker editor_prompts {

    # Code improvement prompt
    def code_improvement_prompt(file_name: str, issues: list = [], context: str = "") -> str {
        issues_str = "; ".join(issues) if issues else "No specific issues provided.";
        context_str = context if context else "No additional context provided.";
        
        prompt = """
        CODE IMPROVEMENT TASK: {file_name}

        KNOWN ISSUES:
        {issues_str}

        CONTEXT:
        {context_str}

        INSTRUCTIONS:
        - Suggest improvements to code readability and maintainability
        - Optimize function or class structure
        - Ensure proper variable naming and commenting
        """.format(file_name=file_name, issues_str=issues_str, context_str=context_str);
        return prompt.strip();
    }

    # Bug fixing prompt
    def bug_fix_prompt(file_name: str, bug_description: str, related_code: str = "") -> str {
        related_code_str = related_code if related_code else "No specific code snippet provided.";
        
        prompt = """
        BUG FIX TASK: {file_name}

        BUG DESCRIPTION:
        {bug_description}

        RELATED CODE:
        {related_code_str}

        INSTRUCTIONS:
        - Identify root cause of the bug
        - Suggest corrected code or refactoring
        - Ensure no new bugs are introduced
        """.format(file_name=file_name, bug_description=bug_description, related_code_str=related_code_str);
        return prompt.strip();
    }

    # Refactoring suggestion prompt
    def refactoring_prompt(file_name: str, functions: list = [], context: str = "") -> str {
        functions_str = "; ".join(functions) if functions else "All functions and classes";
        context_str = context if context else "No additional context provided.";
        
        prompt = """
        REFACTORING TASK: {file_name}

        FUNCTIONS/CLASSES TO REVIEW:
        {functions_str}

        CONTEXT:
        {context_str}

        INSTRUCTIONS:
        - Improve code modularity and reuse
        - Reduce duplication
        - Follow language-specific best practices
        """.format(file_name=file_name, functions_str=functions_str, context_str=context_str);
        return prompt.strip();
    }

    # Code review prompt
    def code_review_prompt(file_name: str, reviewer: str = "assistant", focus_areas: list = []) -> str {
        focus_areas_str = "; ".join(focus_areas) if focus_areas else "General code quality, readability, and correctness";
        
        prompt = """
        CODE REVIEW TASK: {file_name}

        REVIEWER: {reviewer}

        FOCUS AREAS:
        {focus_areas_str}

        INSTRUCTIONS:
        - Highlight potential issues or bugs
        - Suggest improvements in code style and structure
        - Check for maintainability and performance optimizations
        """.format(file_name=file_name, reviewer=reviewer, focus_areas_str=focus_areas_str);
        return prompt.strip();
    }

    # Add comments prompt
    def add_comments_prompt(file_name: str, code_snippet: str, context: str = "") -> str {
        context_str = context if context else "No additional context provided.";
        
        prompt = """
        ADD COMMENTS TASK: {file_name}

        CODE SNIPPET:
        {code_snippet}

        CONTEXT:
        {context_str}

        INSTRUCTIONS:
        - Add meaningful and concise comments
        - Explain logic for complex blocks
        - Maintain readability and clarity
        """.format(file_name=file_name, code_snippet=code_snippet, context_str=context_str);
        return prompt.strip();
    }

    # Automated suggestion prompt
    def automated_suggestion_prompt(file_name: str, task_summary: str) -> str {
        prompt = """
        AUTOMATED EDITOR SUGGESTION: {file_name}

        TASK SUMMARY:
        {task_summary}

        INSTRUCTIONS:
        - Provide quick and actionable suggestions
        - Focus on immediate improvements
        """.format(file_name=file_name, task_summary=task_summary);
        return prompt.strip();
    }

}

# End of editor_prompts.jac
