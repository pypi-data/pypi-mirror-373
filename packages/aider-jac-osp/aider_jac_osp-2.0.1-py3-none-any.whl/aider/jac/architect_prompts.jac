# architect_prompts.jac
# Jac module for architect-level prompt templates
# Focused on high-level system design, refactoring, and architecture guidance

walker architect_prompts {

    # System design analysis prompt
    def system_design_prompt(system_name: str, context: str, objectives: list) -> str {
        prompt = """
        ARCHITECTURE ANALYSIS: {system_name}

        CONTEXT:
        {context}

        OBJECTIVES:
        {objectives}

        INSTRUCTIONS:
        - Identify major components and dependencies
        - Suggest improvements for maintainability and scalability
        - Consider modularity and separation of concerns
        """.format(
            system_name=system_name,
            context=context if context else 'No context provided.',
            objectives="; ".join(objectives) if objectives else "Provide high-level architectural analysis."
        );
        return prompt.strip();
    }

    # Refactoring guidance prompt
    def refactoring_prompt(component_name: str, issues: list, suggestions: list) -> str {
        prompt = """
        REFACTORING TASK: {component_name}

        KNOWN ISSUES:
        {issues}

        SUGGESTED IMPROVEMENTS:
        {suggestions}

        INSTRUCTIONS:
        - Ensure backward compatibility
        - Optimize code structure and readability
        - Reduce redundancy and improve modularity
        """.format(
            component_name=component_name,
            issues="; ".join(issues) if issues else 'No known issues provided.',
            suggestions="; ".join(suggestions) if suggestions else 'Provide refactoring recommendations.'
        );
        return prompt.strip();
    }

    # Dependency review prompt
    def dependency_review_prompt(component_name: str, dependencies: list) -> str {
        prompt = """
        DEPENDENCY REVIEW: {component_name}

        DEPENDENCIES:
        {dependencies}

        OBJECTIVES:
        - Identify unnecessary or risky dependencies
        - Suggest replacement or optimization
        - Maintain overall system integrity
        """.format(
            component_name=component_name,
            dependencies="; ".join(dependencies) if dependencies else 'No dependencies listed.'
        );
        return prompt.strip();
    }

    # Architecture validation prompt
    def architecture_validation_prompt(system_name: str, files: list, checks: list) -> str {
        prompt = """
        ARCHITECTURE VALIDATION: {system_name}

        FILES TO CHECK:
        {files}

        CHECKS TO PERFORM:
        {checks}

        GOAL:
        - Ensure adherence to architecture principles
        - Detect potential design flaws
        - Maintain modular and scalable structure
        """.format(
            system_name=system_name,
            files=', '.join(files) if files else 'No files specified.',
            checks=', '.join(checks) if checks else 'Provide architectural consistency checks.'
        );
        return prompt.strip();
    }

    # High-level planning prompt
    def high_level_planning_prompt(task_name: str, goals: list, context: str) -> str {
        prompt = """
        HIGH-LEVEL PLAN: {task_name}

        GOALS:
        {goals}

        CONTEXT:
        {context}

        INSTRUCTIONS:
        - Break down tasks into sequential actions
        - Prioritize actions based on impact
        - Consider architectural implications of each step
        """.format(
            task_name=task_name,
            goals="; ".join(goals) if goals else 'Define goals for the task.',
            context=context if context else 'No context provided.'
        );
        return prompt.strip();
    }

    # Concise architect prompt generator
    def concise_architect_prompt(task_name: str, summary: str) -> str {
        prompt = """
        ARCHITECT TASK: {task_name}
        SUMMARY: {summary}
        """.format(task_name=task_name, summary=summary);
        return prompt.strip();
    }

}

# End of architect_prompts.jac