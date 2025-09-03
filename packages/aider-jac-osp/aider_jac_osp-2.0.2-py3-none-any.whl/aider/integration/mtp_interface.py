"""
mtp_interface.py
High-level interface for Genius/MTP autonomous agent.
Provides Python-friendly API to interact with Jac-based MTP agent.
"""

from typing import Any, Dict, List, Optional
from .jac_bridge import JacBridge, JacBridgeError

class MTPInterfaceError(Exception):
    """Custom exception for MTP interface errors."""
    pass

class MTPInterface:
    """
    High-level interface for Genius/MTP agent operations.
    """

    def __init__(self, jac_workspace: Optional[str] = None):
        """
        Initialize MTP interface with optional Jac workspace.

        Args:
            jac_workspace: Path to Jac project containing MTP modules
        """
        self.bridge = JacBridge(jac_workspace=jac_workspace)

    def plan_task(self, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a high-level plan for a given task.

        Args:
            task_description: Task description in natural language
            context: Optional repository context or additional instructions

        Returns:
            Plan dictionary with ordered steps and metadata
        """
        try:
            plan = self.bridge.call_walker(
                "planning_walker", "create_plan",
                args={"task": task_description, "context": context}
            )
            return plan or {"steps": [], "summary": "No plan generated"}
        except JacBridgeError as e:
            raise MTPInterfaceError(f"Failed to plan task: {e}")

    def edit_code(self, file_path: str, instructions: str) -> str:
        """
        Apply edits to a file according to MTP instructions.

        Args:
            file_path: Path to file relative to repo root
            instructions: Edit instructions in natural language

        Returns:
            Updated file content
        """
        try:
            updated_content = self.bridge.call_walker(
                "editing_walker", "edit_file",
                args={"file_path": file_path, "instructions": instructions}
            )
            return updated_content or ""
        except JacBridgeError as e:
            raise MTPInterfaceError(f"Failed to edit file {file_path}: {e}")

    def validate_code(self, file_path: str) -> Dict[str, Any]:
        """
        Run MTP validation on a file.

        Args:
            file_path: Path to file relative to repo root

        Returns:
            Validation results including warnings, errors, and recommendations
        """
        try:
            validation_result = self.bridge.call_walker(
                "validation_walker", "validate_file",
                args={"file_path": file_path}
            )
            return validation_result or {}
        except JacBridgeError as e:
            raise MTPInterfaceError(f"Failed to validate {file_path}: {e}")

    def validate_changes(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate recent changes using MTP validation walker.

        Args:
            files: Optional list of files to validate. If None, validates all changed files.

        Returns:
            Dict containing validation results
        """
        try:
            validation_result = self.bridge.call_walker(
                "validation_walker", "validate_changes",
                args={"files": files or []}
            )
            return validation_result or {"success": True, "message": "No validation issues found"}
        except JacBridgeError as e:
            raise MTPInterfaceError(f"Failed to validate changes: {e}")

    def full_autonomous_task(self, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the full Genius/MTP workflow: planning, editing, validation.

        Args:
            task_description: Task description in natural language
            context: Optional repository context

        Returns:
            Dictionary containing plan, edits, and validation results
        """
        result = {}

        try:
            # Step 1: Generate plan
            plan = self.plan_task(task_description, context)
            result["plan"] = plan

            # Step 2: Execute edits for each planned action
            edits = {}
            for step in plan.get("steps", []):
                file_path = step.get("file")
                instructions = step.get("instructions")
                if file_path and instructions:
                    edits[file_path] = self.edit_code(file_path, instructions)
            result["edits"] = edits

            # Step 3: Validate edited files
            validations = {}
            for file_path in edits.keys():
                validations[file_path] = self.validate_code(file_path)
            result["validations"] = validations

            return result

        except MTPInterfaceError as e:
            raise
        except Exception as e:
            raise MTPInterfaceError(f"Failed to execute full autonomous task: {e}")

# Example usage
if __name__ == "__main__":
    mtp = MTPInterface(jac_workspace="./jac")
    task = "Refactor all functions with inconsistent naming conventions."
    context = "Repository contains Python and Jac files."
    
    print("Planning task...")
    plan = mtp.plan_task(task, context)
    print("Plan:", plan)
    
    # If there are steps, perform full autonomous execution
    if plan.get("steps"):
        print("Executing full autonomous task...")
        result = mtp.full_autonomous_task(task, context)
        print("Autonomous Task Result:", result)
