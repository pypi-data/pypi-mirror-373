"""
osp_interface.py
High-level OSP (Optimal Software Planning) interface.
Provides Python-friendly API to interact with Jac-based RepoMap.
"""

from typing import Any, Dict, List, Optional
from .jac_bridge import JacBridge, JacBridgeError

class OSPInterfaceError(Exception):
    """Custom exception for OSP interface errors."""
    pass

class OSPInterface:
    """
    High-level interface for OSP RepoMap operations.
    """

    def __init__(self, jac_workspace: Optional[str] = None):
        """
        Initialize OSP interface with optional Jac workspace.

        Args:
            jac_workspace: Path to the Jac project containing OSP modules
        """
        self.bridge = JacBridge(jac_workspace=jac_workspace)

    def list_files(self) -> List[str]:
        """
        List all files in the repository according to RepoMap.

        Returns:
            List of relative file paths
        """
        try:
            files = self.bridge.call_walker("repomap_osp", "list_all_files")
            return files or []
        except JacBridgeError as e:
            raise OSPInterfaceError(f"Failed to list files: {e}")

    def list_functions(self, file_path: str) -> List[str]:
        """
        List all functions in a specific file.

        Args:
            file_path: Path to the file relative to repo root

        Returns:
            List of function names
        """
        try:
            funcs = self.bridge.call_walker(
                "repomap_osp", "list_functions",
                args={"file_path": file_path, "action": "list_functions"}
            )
            return funcs or []
        except JacBridgeError as e:
            raise OSPInterfaceError(f"Failed to list functions for {file_path}: {e}")

    def rank_files(self, files: Optional[List[str]] = None, context: Optional[str] = None) -> Dict[str, float]:
        """
        Rank files in the repository based on OSP algorithms.

        Args:
            files: List of files to rank. If None, ranks all files.
            context: Optional context for ranking

        Returns:
            Dict mapping file paths to ranking scores
        """
        try:
            rankings = self.bridge.call_walker(
                "ranking_algorithms", "rank_files",
                args={"files": files or [], "context": context}
            )
            return rankings or {}
        except JacBridgeError as e:
            raise OSPInterfaceError(f"Failed to rank files: {e}")
        except Exception as e:
            raise OSPInterfaceError(f"Failed to rank files: {e}")

    def file_dependencies(self, file_path: str) -> List[str]:
        """
        Get direct dependencies of a file.

        Args:
            file_path: Relative file path

        Returns:
            List of dependent file paths
        """
        try:
            deps = self.bridge.call_walker(
                "impact_analyzer",
                "get_file_dependencies",
                args={"file_path": file_path}
            )
            return deps or []
        except JacBridgeError as e:
            raise OSPInterfaceError(f"Failed to get dependencies for {file_path}: {e}")

    def search_node(self, query: str, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search nodes in the RepoMap using query.

        Args:
            query: Search string
            node_type: Optional node type filter (e.g., "FunctionNode", "ClassNode")

        Returns:
            List of nodes with relevant metadata
        """
        try:
            results = self.bridge.call_walker(
                "context_gatherer",
                "search_nodes",
                args={"query": query, "node_type": node_type}
            )
            return results or []
        except JacBridgeError as e:
            raise OSPInterfaceError(f"Failed to search nodes: {e}")

# Example usage
if __name__ == "__main__":
    osp = OSPInterface(jac_workspace="./jac")

    print("All files in repo:", osp.list_files())
    test_file = osp.list_files()[0] if osp.list_files() else None
    if test_file:
        print(f"Functions in {test_file}:", osp.list_functions(test_file))
        print(f"Dependencies for {test_file}:", osp.file_dependencies(test_file))
        print("Top ranked files:", osp.rank_files(strategy="default"))
