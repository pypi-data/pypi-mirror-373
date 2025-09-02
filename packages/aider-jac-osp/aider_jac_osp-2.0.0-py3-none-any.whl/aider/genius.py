"""
genius.py
Genius Mode implementation using Jac Object-Spatial Programming for autonomous operations.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from .jac_integration import JacIntegration, JacIntegrationError

class GeniusConfigError(Exception):
    """Exception raised for Genius configuration errors."""
    pass

class GeniusMode:
    """
    Genius Mode for autonomous code editing using Jac OSP/MTP.
    Provides autonomous planning, execution, and validation capabilities.
    """

    def __init__(self, io, repo, llm_config: Optional[Dict] = None):
        """
        Initialize Genius Mode.

        Args:
            io: Aider IO instance for user interaction
            repo: Repository instance
            llm_config: LLM configuration settings
        """
        self.io = io
        self.repo = repo
        self.llm_config = llm_config or {}
        
        # Initialize Jac integration
        try:
            self.jac = JacIntegration()
        except Exception as e:
            raise GeniusConfigError(f"Failed to initialize Jac integration: {str(e)}")

        # Genius Mode settings
        self.max_iterations = self.llm_config.get('genius_max_iterations', 10)
        self.confidence_threshold = self.llm_config.get('genius_confidence_threshold', 0.8)
        self.validation_enabled = self.llm_config.get('genius_validation', True)

    def is_available(self) -> bool:
        """Check if Genius Mode is available and properly configured."""
        try:
            # Test Jac integration
            test_result = self.jac.bridge.test_connection()
            return test_result.get('success', False)
        except Exception:
            return False

    def enable(self, task_description: str = "") -> Dict[str, Any]:
        """
        Enable Genius Mode for autonomous operation.

        Args:
            task_description: Description of task for autonomous execution

        Returns:
            Dict containing enablement status and configuration
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Genius Mode unavailable - Jac integration not working"
            }

        self.io.tool_output("Genius Mode enabled - Autonomous operation starting")
        
        try:
            # Initialize planning
            if task_description:
                plan = self.jac.plan_autonomous_task(task_description)
                self.io.tool_output(f"Generated autonomous plan: {plan.get('summary', 'Plan created')}")
                
            return {
                "success": True,
                "mode": "genius",
                "task": task_description,
                "config": {
                    "max_iterations": self.max_iterations,
                    "confidence_threshold": self.confidence_threshold,
                    "validation_enabled": self.validation_enabled
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to enable Genius Mode: {str(e)}"
            }

    def execute_autonomous_task(self, task: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task autonomously using Jac OSP/MTP.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            Dict containing execution results
        """
        try:
            self.io.tool_output(f"🔮 Genius Mode executing: {task}")
            
            # Step 1: Plan using MTP
            plan = self.jac.plan_autonomous_task(task, context)
            self.io.tool_output(f"Plan: {plan.get('summary', 'Generated')}")

            # Step 2: Rank files using OSP
            if self.repo.get_tracked_files():
                rankings = self.jac.get_repo_ranking(self.repo.get_tracked_files(), task)
                top_files = sorted(rankings.items(), key=lambda x: x[1], reverse=True)[:5]
                self.io.tool_output(f"Top relevant files: {[f[0] for f in top_files]}")

            # Step 3: Execute plan steps
            results = []
            for step in plan.get('steps', []):
                step_result = self._execute_plan_step(step)
                results.append(step_result)
                
                # Validate after each step if enabled
                if self.validation_enabled and step_result.get('success'):
                    validation = self._validate_step(step, step_result)
                    if not validation.get('success'):
                        self.io.tool_output(f"⚠️ Validation failed for step: {step}")
                        break

            return {
                "success": True,
                "task": task,
                "plan": plan,
                "results": results,
                "files_modified": self._get_modified_files(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Autonomous execution failed: {str(e)}"
            }

    def _execute_plan_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single plan step."""
        try:
            step_type = step.get('type', 'unknown')
            
            if step_type == 'file_edit':
                return self._execute_file_edit(step)
            elif step_type == 'analysis':
                return self._execute_analysis(step)
            elif step_type == 'validation':
                return self._execute_validation(step)
            else:
                return {"success": False, "error": f"Unknown step type: {step_type}"}
                
        except Exception as e:
            return {"success": False, "error": f"Step execution failed: {str(e)}"}

    def _execute_file_edit(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file editing step."""
        # This would integrate with Aider's existing file editing mechanisms
        # For now, return a placeholder result
        return {
            "success": True,
            "type": "file_edit",
            "file": step.get('file'),
            "message": "File edit executed (placeholder)"
        }

    def _execute_analysis(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an analysis step using Jac components."""
        try:
            analysis_result = self.jac.bridge.execute_script("context_gatherer.jac", step)
            return {
                "success": True,
                "type": "analysis",
                "result": analysis_result
            }
        except Exception as e:
            return {"success": False, "error": f"Analysis failed: {str(e)}"}

    def _execute_validation(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a validation step."""
        try:
            files = step.get('files', [])
            validation_result = self.jac.validate_code_changes(files)
            return {
                "success": True,
                "type": "validation",
                "result": validation_result
            }
        except Exception as e:
            return {"success": False, "error": f"Validation failed: {str(e)}"}

    def _validate_step(self, step: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a completed step."""
        if not self.validation_enabled:
            return {"success": True, "message": "Validation disabled"}

        try:
            validation = self.jac.mtp.validate_changes()
            return validation
        except Exception as e:
            return {"success": False, "error": f"Step validation failed: {str(e)}"}

    def _get_modified_files(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract list of modified files from results."""
        modified_files = []
        for result in results:
            if result.get('success') and result.get('type') == 'file_edit':
                file_path = result.get('file')
                if file_path:
                    modified_files.append(file_path)
        return modified_files

    def get_status(self) -> Dict[str, Any]:
        """Get current Genius Mode status."""
        return {
            "available": self.is_available(),
            "jac_workspace": self.jac_workspace,
            "cache_dir": self.cache_dir,
            "config": {
                "max_iterations": self.max_iterations,
                "confidence_threshold": self.confidence_threshold,
                "validation_enabled": self.validation_enabled
            }
        }


class GeniusConfig:
    """Configuration management for Genius Mode."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize Genius configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or os.path.expanduser("~/.aider/genius.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        import json
        
        default_config = {
            "max_iterations": 10,
            "confidence_threshold": 0.8,
            "validation_enabled": True,
            "jac_workspace": None,
            "cache_dir": None,
            "autonomous_mode": False
        }

        if not os.path.exists(self.config_file):
            return default_config

        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
                return default_config
        except Exception as e:
            print(f"Warning: Failed to load Genius config: {e}")
            return default_config

    def save_config(self) -> bool:
        """Save current configuration to file."""
        import json
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Failed to save Genius config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)
