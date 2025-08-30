"""CKAD Agent implementation using LLM for Kubernetes assistance."""
import os
from typing import Dict, Optional, Any

import typer
from pydantic_ai import Agent, Tool, RunContext

from .models import CKADRequest, CKADResponse, KubernetesResourceType, TaskType
from .kubectl_tool import KubectlTool


class CkadAgent:
    """Agent that assists with CKAD exam preparation and Kubernetes tasks."""

    def _format_response(self, response: str, response_type: str = "info") -> str:
        """Format the response with appropriate colors.
        
        Args:
            response: The response text to format
            response_type: Type of response (info, success, error, warning, command)
            
        Returns:
            Formatted string with color codes
        """
        if not response:
            return ""
            
        colors = {
            "info": typer.style,
            "success": lambda x: typer.style(x, fg=typer.colors.GREEN, bold=True),
            "error": lambda x: typer.style(x, fg=typer.colors.RED, bold=True),
            "warning": lambda x: typer.style(x, fg=typer.colors.YELLOW, bold=True),
            "command": lambda x: typer.style(x, fg=typer.colors.BLUE, bold=True),
            "header": lambda x: typer.style(x, fg=typer.colors.CYAN, bold=True, underline=True),
            "highlight": lambda x: typer.style(x, fg=typer.colors.MAGENTA, bold=True)
        }
        
        # If it's a command (starts with $ or kubectl), format as command
        if response.strip().startswith(('$', 'kubectl')):
            return colors["command"](response)
            
        return colors.get(response_type, typer.style)(response)


    def __init__(self, model: str = "gpt-4", read_only: bool = True):
        """Initialize the CKAD agent with the specified LLM model.
        
        Args:
            model: The LLM model to use (default: "gpt-4")
            read_only: If True, only read-only kubectl commands are allowed (default: True)
        """
        self.kubectl_tool = KubectlTool(read_only=read_only)
        self.read_only = read_only
        
        # Create the kubectl command tool
        self.kubectl_command_tool = Tool(
            name="kubectl_command",
            description="Execute a kubectl command to interact with the Kubernetes cluster.",
            function=self._execute_kubectl_command
        )
        
        self.llm_agent = Agent(
            model=model,
            system_prompt=self._get_system_prompt(),
            tools=[self.kubectl_command_tool]
        )
    
    async def _execute_kubectl_command(self, ctx: RunContext, command: str) -> str:
        """Execute a kubectl command.
        
        Args:
            ctx: The run context (automatically provided by the agent)
            command: The kubectl command to execute (e.g., 'kubectl get pods')
            
        Returns:
            The output of the command or an error message
        """
        success, output = self.kubectl_tool.execute_command(command)
        return output
        
    async def process_request(self, request: CKADRequest) -> CKADResponse:
        """Process a CKAD request and return a response."""
        try:
            # Print request header
            typer.echo(self._format_response(f"\n=== {request.task_type.value.upper()} REQUEST ===", "header"))
            if request.question:
                typer.echo(self._format_response(f"Question: {request.question}", "highlight"))
            if request.resource_type:
                typer.echo(self._format_response(f"Resource Type: {request.resource_type.value}", "info"))
                
            # Process the request
            if request.task_type == TaskType.DEBUG:
                response = await self._debug_yaml(request)
            elif request.task_type == TaskType.EXPLAIN:
                response = await self._explain_concept(request)
            elif request.task_type == TaskType.VALIDATE:
                response = await self._validate_yaml(request)
            else:
                response = CKADResponse(
                    success=False,
                    message=f"Unsupported task type: {request.task_type}"
                )
                
            # Print response with appropriate formatting
            self._print_response(response)
            return response
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            typer.echo(self._format_response(error_msg, "error"))
            return CKADResponse(success=False, message=error_msg)
            
    def _print_response(self, response: CKADResponse) -> None:
        """Print the response with appropriate formatting."""
        if not response.success:
            typer.echo(self._format_response("\n Error", "error"))
            typer.echo(self._format_response(response.message, "error"))
            return
            
        if response.solution:
            typer.echo(self._format_response("\n Solution", "success"))
            typer.echo(self._format_response(response.solution, "info"))
            
        if response.message and not response.solution:  # Only show message if no solution was provided
            typer.echo(self._format_response("\n Response", "info"))
            typer.echo(self._format_response(response.message, "info"))

    def _format_command_output(self, command: str, output: str, success: bool = True) -> str:
        """Format command execution output with colors."""
        formatted = []
        formatted.append(self._format_response(f"\n🔍 Executing: {command}", "command"))
        formatted.append("")
        
        # Format command output
        if success:
            formatted.append(output)
        else:
            formatted.append(self._format_response(output, "error"))
            
        formatted.append("")
        formatted.append(self._format_response("―" * 50, "info"))
        return "\n".join(formatted)

    async def _debug_yaml(self, request: CKADRequest) -> CKADResponse:
        """Debug Kubernetes YAML content using a streaming approach.
        
        The agent will run kubectl commands and stream the output in real-time.
        """
        from .simple_debugger import KubernetesDebugger
        
        # Buffer to collect all output
        output_buffer = []
        last_command = None
        
        # Define a callback to collect and display output
        async def collect_output(output: str) -> None:
            # Skip duplicate command outputs
            if output.startswith('Executing:') and output == last_command:
                return
                
            output_buffer.append(output)
            typer.echo(output)
            
        # Create the debugger with our callback
        debugger = KubernetesDebugger(
            read_only=self.read_only,
            callback=collect_output
        )
        
        # Add a header
        typer.echo(self._format_response("\n Starting Kubernetes Debug Session", "header"))
        typer.echo(self._format_response("Type 'TERMINATE' to end the session\n", "info"))
        
        if request.question:
            typer.echo(self._format_response(f" Issue: {request.question}", "highlight"))
        
        # Run the debugger
        try:
            result = await debugger.debug(issue=request.question)
            
            # Add the final result
            typer.echo("\n" + self._format_response(" Debug Session Completed", "success"))
            typer.echo(self._format_response(result, "info"))
            
            # Return the collected output as the response
            full_output = "\n".join(output_buffer)
            return CKADResponse(
                success=True,
                message=full_output,
                solution=result
            )
            
        except Exception as e:
            error_msg = f"Error during debugging: {str(e)}"
            typer.echo(self._format_response(f"\n Error: {error_msg}", "error"))
            return CKADResponse(
                success=False,
                message=error_msg,
                solution='\n'.join(output_buffer[-10:])  # Last 10 lines of output
            )

    async def _explain_concept(self, request: CKADRequest) -> CKADResponse:
        """Explain a Kubernetes concept or answer a question."""
        prompt = f"""
        Explain the following Kubernetes concept/question in the context of CKAD:
        
        {request.question}
        
        {f'Focus on: {request.context.get("focus")}' if request.context and 'focus' in request.context else ''}
        
        Provide a clear, concise explanation with examples if applicable.
        """
        
        response = await self.llm_agent.run(prompt)
        
        return CKADResponse(
            success=True,
            message="Explanation provided",
            explanation=response.output,
        )

    async def _validate_yaml(self, request: CKADRequest) -> CKADResponse:
        """Validate Kubernetes YAML and suggest improvements."""
        prompt = f"""
        Please validate the following Kubernetes {request.resource_type} YAML:
        
        ```yaml
        {request.yaml_content}
        ```
        
        Check for:
        1. Syntax errors
        2. Best practices violations
        3. Security issues
        4. Potential problems
        
        Provide a detailed analysis and suggest improvements.
        """
        
        analysis = await self.llm_agent.run(prompt)
        
        return CKADResponse(
            success=True,
            message="Validation completed",
            explanation=analysis.output,
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM agent."""
        return f"""
        You are an expert Kubernetes administrator and your job is to resolve issues relating to
        Kubernetes deployments using kubectl. Do not try and debug the issue with the containers themselves
        and only focus on issues relating to kubernetes itself. You are already logged in to the cluster.
        """
