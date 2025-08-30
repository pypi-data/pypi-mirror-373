"""Tool for executing kubectl commands."""
import subprocess
from typing import Optional, Tuple

READ_ONLY_COMMANDS = ["get", "describe", "explain", "logs", "top", "api-resources", "api-versions", "cluster-info"]
BLOCKING_COMMANDS = ["edit", "--watch", "-w"]

class KubectlTool:
    """A tool for executing kubectl commands safely."""

    def __init__(self, read_only: bool = True):
        """Initialize the KubectlTool.
        
        Args:
            read_only: If True, only read-only commands are allowed.
        """
        self.read_only = read_only

    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a kubectl command.
        
        Args:
            command: The kubectl command to execute (without the 'kubectl' prefix)
            
        Returns:
            A tuple of (success, output) where success is a boolean indicating
            if the command was successful, and output is the command's output.
        """
        command = command.strip()
        
        # Check if the command is a kubectl command
        if not command.startswith("kubectl"):
            return False, "Error: Command must start with 'kubectl'"
        
        # Remove 'kubectl' prefix and split into parts
        parts = command.split()
        if len(parts) < 2:
            return False, "Error: Invalid kubectl command"
            
        action = parts[1]
        
        # Check for blocking commands
        if any(blocking in command for blocking in BLOCKING_COMMANDS):
            return False, f"Error: Blocking commands ({BLOCKING_COMMANDS}) are not allowed"
            
        # Check for write operations in read-only mode
        if self.read_only and not any(cmd in action for cmd in READ_ONLY_COMMANDS):
            return False, f"Error: Write operations are not allowed in read-only mode. Allowed commands: {READ_ONLY_COMMANDS}"
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            return True, result.stdout
            
        except subprocess.CalledProcessError as e:
            return False, f"Error executing command: {e.stderr or e.stdout}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
