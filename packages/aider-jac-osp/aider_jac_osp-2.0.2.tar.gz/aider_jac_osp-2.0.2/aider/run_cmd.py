"""Run command module for aider."""

import subprocess

def run_cmd(cmd, cwd=None):
    """
    Run a command placeholder function
    
    Args:
        cmd: Command to run
        cwd: Working directory
        
    Returns:
        Command result
    """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)
