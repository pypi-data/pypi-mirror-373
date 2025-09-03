# mtp_prompts_syntax.jac
# MTP (Model Task Protocol) prompts - Syntax-corrected version
# Manages prompts for model task protocol interactions

walker MTPPrompts {

    # Generate task template for MTP protocol
    def task_template(task_name: str, details: str, files: list) -> str {
        template = "TASK: " + task_name + "\n";
        template = template + "DETAILS: " + details + "\n";
        template = template + "FILES INVOLVED: " + str(len(files)) + "\n";
        
        if len(files) > 0 {
            template = template + "File list:\n";
            i = 0;
            while i < len(files) {
                template = template + "- " + files[i] + "\n";
                i = i + 1;
            }
        }
        
        template = template + "\nINSTRUCTIONS:\n";
        template = template + "Please analyze the task and provide structured response.\n";
        
        return template;
    }

    # Generate code analysis prompt
    def code_analysis_prompt(file_path: str, analysis_type: str) -> str {
        prompt = "CODE ANALYSIS REQUEST\n";
        prompt = prompt + "=====================\n";
        prompt = prompt + "File: " + file_path + "\n";
        prompt = prompt + "Analysis Type: " + analysis_type + "\n\n";
        
        if analysis_type == "complexity" {
            prompt = prompt + "Please analyze the computational complexity of this code.\n";
            prompt = prompt + "Focus on: Time complexity, Space complexity, Algorithm efficiency\n";
        } elif analysis_type == "quality" {
            prompt = prompt + "Please analyze the code quality.\n";
            prompt = prompt + "Focus on: Readability, Maintainability, Best practices\n";
        } elif analysis_type == "security" {
            prompt = prompt + "Please analyze potential security issues.\n";
            prompt = prompt + "Focus on: Vulnerabilities, Input validation, Data handling\n";
        } else {
            prompt = prompt + "Please provide general code analysis.\n";
        }
        
        return prompt;
    }

    # Generate refactoring suggestion prompt
    def refactoring_prompt(target_file: str, issues: list, goals: list) -> str {
        prompt = "REFACTORING REQUEST\n";
        prompt = prompt + "==================\n";
        prompt = prompt + "Target File: " + target_file + "\n\n";
        
        if len(issues) > 0 {
            prompt = prompt + "Current Issues:\n";
            i = 0;
            while i < len(issues) {
                prompt = prompt + "- " + issues[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        if len(goals) > 0 {
            prompt = prompt + "Refactoring Goals:\n";
            j = 0;
            while j < len(goals) {
                prompt = prompt + "- " + goals[j] + "\n";
                j = j + 1;
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please provide specific refactoring recommendations.\n";
        return prompt;
    }

    # Generate debugging assistance prompt
    def debugging_prompt(error_description: str, context_files: list, error_trace: str) -> str {
        prompt = "DEBUGGING ASSISTANCE\n";
        prompt = prompt + "===================\n";
        prompt = prompt + "Error Description: " + error_description + "\n\n";
        
        if len(error_trace) > 0 {
            prompt = prompt + "Error Trace:\n";
            prompt = prompt + error_trace + "\n\n";
        }
        
        if len(context_files) > 0 {
            prompt = prompt + "Related Files (" + str(len(context_files)) + "):\n";
            i = 0;
            while i < len(context_files) {
                prompt = prompt + "- " + context_files[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please help identify the root cause and suggest fixes.\n";
        return prompt;
    }

    # Generate testing strategy prompt
    def testing_strategy_prompt(module_name: str, functions: list, complexity_level: str) -> str {
        prompt = "TESTING STRATEGY REQUEST\n";
        prompt = prompt + "=======================\n";
        prompt = prompt + "Module: " + module_name + "\n";
        prompt = prompt + "Complexity Level: " + complexity_level + "\n";
        prompt = prompt + "Functions to Test: " + str(len(functions)) + "\n\n";
        
        if len(functions) > 0 {
            prompt = prompt + "Function List:\n";
            i = 0;
            while i < len(functions) {
                prompt = prompt + "- " + functions[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please suggest a comprehensive testing strategy including:\n";
        prompt = prompt + "- Unit test cases\n";
        prompt = prompt + "- Integration test scenarios\n";
        prompt = prompt + "- Edge cases to consider\n";
        prompt = prompt + "- Test data requirements\n";
        
        return prompt;
    }

    # Generate documentation prompt
    def documentation_prompt(code_section: str, doc_type: str, audience: str) -> str {
        prompt = "DOCUMENTATION REQUEST\n";
        prompt = prompt + "====================\n";
        prompt = prompt + "Documentation Type: " + doc_type + "\n";
        prompt = prompt + "Target Audience: " + audience + "\n";
        prompt = prompt + "Code Section Length: " + str(len(code_section)) + " characters\n\n";
        
        if doc_type == "api" {
            prompt = prompt + "Please generate API documentation including:\n";
            prompt = prompt + "- Function signatures\n";
            prompt = prompt + "- Parameter descriptions\n";
            prompt = prompt + "- Return value documentation\n";
            prompt = prompt + "- Usage examples\n";
        } elif doc_type == "user_guide" {
            prompt = prompt + "Please generate user guide documentation including:\n";
            prompt = prompt + "- Step-by-step instructions\n";
            prompt = prompt + "- Common use cases\n";
            prompt = prompt + "- Troubleshooting tips\n";
        } elif doc_type == "technical" {
            prompt = prompt + "Please generate technical documentation including:\n";
            prompt = prompt + "- Architecture overview\n";
            prompt = prompt + "- Implementation details\n";
            prompt = prompt + "- Design decisions\n";
        } else {
            prompt = prompt + "Please generate appropriate documentation.\n";
        }
        
        return prompt;
    }

    # Generate performance optimization prompt
    def performance_optimization_prompt(bottleneck_areas: list, performance_metrics: dict) -> str {
        prompt = "PERFORMANCE OPTIMIZATION REQUEST\n";
        prompt = prompt + "================================\n";
        
        if len(bottleneck_areas) > 0 {
            prompt = prompt + "Identified Bottlenecks:\n";
            i = 0;
            while i < len(bottleneck_areas) {
                prompt = prompt + "- " + bottleneck_areas[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        if performance_metrics.get("execution_time") {
            prompt = prompt + "Current Performance Metrics:\n";
            prompt = prompt + "- Execution Time: " + str(performance_metrics["execution_time"]) + "\n";
            if performance_metrics.get("memory_usage") {
                prompt = prompt + "- Memory Usage: " + str(performance_metrics["memory_usage"]) + "\n";
            }
            if performance_metrics.get("cpu_usage") {
                prompt = prompt + "- CPU Usage: " + str(performance_metrics["cpu_usage"]) + "\n";
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please suggest optimization strategies including:\n";
        prompt = prompt + "- Algorithm improvements\n";
        prompt = prompt + "- Data structure optimizations\n";
        prompt = prompt + "- Caching strategies\n";
        prompt = prompt + "- Resource usage optimizations\n";
        
        return prompt;
    }

    # Generate code review prompt
    def code_review_prompt(files_to_review: list, review_criteria: list, priority_level: str) -> str {
        prompt = "CODE REVIEW REQUEST\n";
        prompt = prompt + "==================\n";
        prompt = prompt + "Priority Level: " + priority_level + "\n";
        prompt = prompt + "Files to Review: " + str(len(files_to_review)) + "\n\n";
        
        if len(files_to_review) > 0 {
            prompt = prompt + "File List:\n";
            i = 0;
            while i < len(files_to_review) {
                prompt = prompt + "- " + files_to_review[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        if len(review_criteria) > 0 {
            prompt = prompt + "Review Criteria:\n";
            j = 0;
            while j < len(review_criteria) {
                prompt = prompt + "- " + review_criteria[j] + "\n";
                j = j + 1;
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please provide a thorough code review covering:\n";
        prompt = prompt + "- Code quality and standards\n";
        prompt = prompt + "- Potential bugs or issues\n";
        prompt = prompt + "- Performance considerations\n";
        prompt = prompt + "- Security implications\n";
        prompt = prompt + "- Suggestions for improvement\n";
        
        return prompt;
    }

    # Generate architectural guidance prompt
    def architectural_guidance_prompt(system_description: str, requirements: list, constraints: list) -> str {
        prompt = "ARCHITECTURAL GUIDANCE REQUEST\n";
        prompt = prompt + "=============================\n";
        prompt = prompt + "System Description: " + system_description + "\n\n";
        
        if len(requirements) > 0 {
            prompt = prompt + "Requirements:\n";
            i = 0;
            while i < len(requirements) {
                prompt = prompt + "- " + requirements[i] + "\n";
                i = i + 1;
            }
            prompt = prompt + "\n";
        }
        
        if len(constraints) > 0 {
            prompt = prompt + "Constraints:\n";
            j = 0;
            while j < len(constraints) {
                prompt = prompt + "- " + constraints[j] + "\n";
                j = j + 1;
            }
            prompt = prompt + "\n";
        }
        
        prompt = prompt + "Please provide architectural guidance including:\n";
        prompt = prompt + "- Recommended system architecture\n";
        prompt = prompt + "- Component design suggestions\n";
        prompt = prompt + "- Technology stack recommendations\n";
        prompt = prompt + "- Scalability considerations\n";
        prompt = prompt + "- Risk assessment\n";
        
        return prompt;
    }

}
