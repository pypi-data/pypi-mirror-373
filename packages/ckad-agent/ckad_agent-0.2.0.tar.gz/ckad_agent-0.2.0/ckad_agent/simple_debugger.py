"""Simple Kubernetes debugger using pydantic-ai."""
from typing import Optional, Dict, Any, List, Tuple, Callable, Awaitable
from dataclasses import dataclass
import re
import asyncio

from pydantic_ai import Agent, Tool, RunContext
from .kubectl_tool import KubectlTool

@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    output: str

class KubernetesDebugger:
    """Simple Kubernetes debugger that runs commands and analyzes output."""
    
    def __init__(self, read_only: bool = True, callback: Optional[Callable[[str], Awaitable[None]]] = None):
        """Initialize the debugger.
        
        Args:
            read_only: If True, only read-only commands are allowed.
            callback: Optional callback function for streaming output
        """
        self.kubectl = KubectlTool(read_only=read_only)
        self.callback = callback or (lambda x: asyncio.get_event_loop().run_until_complete(asyncio.sleep(0)))
        self.command_history: List[Dict[str, Any]] = []
        
        # Create a wrapper function that matches the expected signature
        async def kubectl_command_wrapper(ctx: RunContext, command: str) -> str:
            return await self._execute_kubectl_command(command, ctx)
            
        # Create the kubectl command tool
        self.kubectl_tool = Tool(
            name="kubectl_command",
            description="Execute a kubectl command to interact with the Kubernetes cluster.",
            function=kubectl_command_wrapper
        )
        
        # Create the LLM agent
        self.agent = Agent(
            model="gpt-4",
            system_prompt=self._get_system_prompt(read_only),
            tools=[self.kubectl_tool]
        )
    
    def _get_system_prompt(self, read_only: bool) -> str:
        """Generate the system prompt for the LLM."""
        if read_only:
            read_only_clause = """
You only have read only permissions to the cluster. You cannot create, update or delete
resources on the cluster, but you can use the following commands; 'get', 'describe', 'logs', 'top', 'events'.
You can propose changes for the end user to run to fix the command afterwards.
"""
        else:
            read_only_clause = ""
            
        return f"""# Your Role
You are an expert Kubernetes administrator and your job is to resolve issues relating to
Kubernetes deployments using kubectl. Do not try and debug the issue with the containers themselves
and only focus on issues relating to kubernetes itself. You are already logged in to the cluster.

# How to present code
You must only provide one command to execute at a time. Never put placeholders like <pod-name> or
<service-name> in your code. Make sure you limit the output when running 'kubectl logs' using the
--tail or --since flags; if using --tail limit logs to the last 10 records.
Do not use the 'kubectl edit' command.

{read_only_clause}

# Useful kubectl command
kubectl get: Get resources deployed to the cluster.
kubectl get events: Lists all warning events.
kubectl describe: Provides details about resources deployed on the cluster.
kubectl logs: Get Pod logs.
kubectl top: Show CPU and memory metrics.
kubectl apply: Declaratively create resources on the cluster.
kubectl create: Imperatively create resources on the cluster.
kubectl patch: Partially update a resource
kubectl expose: Create a service

# How to terminate the debug session
Don't ask if the user needs any further assistance, simply reply with 'TERMINATE' if you
have completed the task to the best of your abilities. If you need the user to save code to a file
or you have no code left to run, respond with 'TERMINATE'."""
    
    async def _execute_kubectl_command(self, command: str, ctx: Optional[RunContext] = None) -> str:
        """Execute a kubectl command and return the output."""
        try:
            # Send the command to the output
            if hasattr(self, 'callback'):
                await self.callback(f"Executing: {command}\n")
            
            # Execute the command with a timeout to prevent hanging
            success, output = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.kubectl.execute_command, 
                    command
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Add to command history
            self.command_history.append({
                "command": command,
                "success": success,
                "output": output
            })
            
            # Check for common success patterns in non-read-only mode
            if not self.kubectl.read_only and success:
                lower_output = output.lower()
                if any(term in lower_output for term in ['created', 'updated', 'configured', 'patched']):
                    # If we just made a change, add a small delay to let the cluster stabilize
                    await asyncio.sleep(2)
            
            # Send output to callback if it exists
            if hasattr(self, 'callback'):
                if not success:
                    error_msg = f"Error: {output}"
                    await self.callback(f"{error_msg}\n")
                    return error_msg
                
                await self.callback(f"{output}\n")
            
            if not success:
                return f"Error: {output}"
            return output
            
        except asyncio.TimeoutError:
            error_msg = "Command timed out after 30 seconds"
            if hasattr(self, 'callback'):
                await self.callback(f"{error_msg}\n")
            return f"Error: {error_msg}"
    
    def _format_command_history(self) -> str:
        """Format the command history for display."""
        if not self.command_history:
            return "No commands run yet."
            
        history = []
        for i, cmd in enumerate(self.command_history, 1):
            status = "✓" if cmd["success"] else "✗"
            history.append(f"{i}. {status} {cmd['command']}")
            
            # Truncate long output in history
            output = cmd["output"]
            if len(output) > 100:
                output = output[:97] + "..."
                
            history.append(f"   Output: {output}")
            
        return "\n".join(history)
    
    async def _handle_agent_output(self, message: str) -> None:
        """Handle output from the agent."""
        if message.strip() and not message.startswith('```'):
            await self.callback(f"{message}\n")
    
    async def debug(self, issue: str) -> str:
        """Debug a Kubernetes issue.
        
        Args:
            issue: Description of the issue to debug.
            
        Returns:
            str: The final response from the debug session.
        """
        try:
            # Reset command history for this debug session
            self.command_history = []
            max_iterations = 10  # Maximum number of command iterations
            current_iteration = 0
            
            # Initial system prompt
            prompt = f"""You are an expert Kubernetes administrator helping to debug an issue.
            
    The user reported the following issue:
    {issue}

    Your task is to:
    1. Diagnose the issue using kubectl commands
    2. If in read-only mode, explain what needs to be fixed
    3. If write mode is enabled, fix the issue directly
    4. After fixing, respond with 'TERMINATE' to end the session

    You can use the following kubectl commands (but not limited to these):
    - kubectl get pods
    - kubectl describe pod <name>
    - kubectl logs <pod> [-c container]
    - kubectl get events --sort-by='.metadata.creationTimestamp'
    - kubectl get all
    - kubectl get <resource> <name> -o yaml

    IMPORTANT:
    - Only suggest one command at a time
    - Wait for the output before suggesting the next command
    - After fixing the issue, respond with 'TERMINATE' to end the session
    - Do not repeat commands that were already run
    - In read-only mode, only suggest commands that don't modify the cluster
    - If you've fixed the issue, respond with 'TERMINATE'
    - If you can't fix the issue, respond with 'TERMINATE' and explain why
    - Never ask for confirmation or input from the user
    - Always provide the exact command to run, don't describe it
    - If you need to create or modify resources, provide the full kubectl command
    - If you need to see the current state, use 'kubectl get all' or similar

    Here's the history of commands already run in this session:
    {self._format_command_history()}
    """
            
            # Run the agent in a loop to handle multiple commands
            while current_iteration < max_iterations:
                current_iteration += 1
                
                # Get the agent's response
                response = await self.agent.run(prompt)
                response_text = str(response).strip()
                
                # Check for termination condition
                if 'TERMINATE' in response_text.upper():
                    summary = "\n\n=== Debug Session Summary ===\n"
                    summary += f"Total commands executed: {len(self.command_history)}\n"
                    if self.command_history:
                        summary += "\nCommands executed:\n"
                        for i, cmd in enumerate(self.command_history, 1):
                            summary += f"{i}. {cmd['command']}\n"
                            if not cmd['success']:
                                summary += f"   Error: {cmd['output']}\n"
                    return summary
                
                # Extract the first kubectl command from the response
                command_match = re.search(r'(kubectl\s+[a-z]+(?:\s+[^\n\r]+)?)', response_text, re.IGNORECASE)
                if not command_match:
                    # No command found, update prompt and continue
                    prompt = f"Please provide a valid kubectl command.\n\n{response_text}"
                    continue
                    
                command = command_match.group(1).strip()
                
                # Skip if this command was just run
                if self.command_history and self.command_history[-1]['command'] == command:
                    prompt = f"Command already executed. Please provide a different command.\n\n{response_text}"
                    continue
                
                # Execute the command and get the output
                output = await self._execute_kubectl_command(command)
                
                # Update the prompt with the command's output
                prompt = f"Command output:\n{output}\n\n" \
                        f"What's the next command? (or respond with 'TERMINATE' if done)\n" \
                        f"Command history:\n{self._format_command_history()}"
            
            return f"Reached maximum number of iterations ({max_iterations}). Debug session terminated."
            
        except Exception as e:
            error_msg = f"Error in debug session: {str(e)}"
            if hasattr(self, 'callback'):
                await self.callback(f"\nERROR: {error_msg}\n")
            return error_msg
