# ==========================================
# file_nodes.jac  
# Core OSP module: Defines file and code-level nodes
# ==========================================

node CodeFile {}
node FunctionNode {}
node ClassNode {}
node ImportNode {}

# ========================
# Relationships  
# ========================

edge contains {}   # CodeFile -> FunctionNode, ClassNode, ImportNode
edge imports {}    # CodeFile -> CodeFile (dependency)

# ========================
# Example usage behaviors
# ========================

walker file_logger {
    def log_files() -> str {
        return "Logging files";
    }
}
