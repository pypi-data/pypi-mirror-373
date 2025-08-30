"""Command-line interface for the CKAD Agent."""
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from .agent import CkadAgent
from .models import CKADRequest, TaskType, KubernetesResourceType

app = typer.Typer()
load_dotenv()


def read_yaml_file(file_path: str) -> str:
    """Read YAML content from a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        raise typer.BadParameter(f"Error reading file {file_path}: {str(e)}")


async def process_task(
    task_type: TaskType,
    question: str,
    resource_type: Optional[KubernetesResourceType] = None,
    yaml_file: Optional[Path] = None,
    context: Optional[str] = None,
    output_format: str = "text",
    read_only: bool = True
):
    """Process a CKAD task using the agent."""
    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
            if not isinstance(context_dict, dict):
                raise ValueError("Context must be a valid JSON object")
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON context: {str(e)}")
    
    # Read YAML file if provided
    yaml_content = None
    if yaml_file:
        yaml_content = read_yaml_file(str(yaml_file))
    
    # Create request
    request = CKADRequest(
        task_type=task_type,
        resource_type=resource_type,
        yaml_content=yaml_content,
        question=question,
        context=context_dict
    )
    
    # Process request
    agent = CkadAgent(read_only=read_only)
    response = await agent.process_request(request)
    
    # Format output
    if output_format.lower() == "json":
        typer.echo(response.model_dump_json(indent=2))
    else:
        if response.success:
            typer.secho("✓ Success", fg=typer.colors.GREEN, bold=True)
            if response.solution:
                typer.echo("\nSolution:")
                typer.echo(response.solution)
            if response.fixed_yaml:
                typer.echo("\nGenerated/Fixed YAML:")
                typer.echo(response.fixed_yaml)
            if response.explanation:
                typer.echo("\nExplanation:")
                typer.echo(response.explanation)
            if response.references:
                typer.echo("\nReferences:")
                for ref in response.references:
                    typer.echo(f"- {ref.get('title', 'Link')}: {ref.get('url', 'No URL')}")
        else:
            typer.secho("✗ Error", fg=typer.colors.RED, bold=True)
            typer.echo(response.message)


@app.command()
def debug(
    question: str = typer.Argument(..., help="Description of the issue or question"),
    resource_type: KubernetesResourceType = typer.Option(
        None,
        "--resource", "-r",
        help="Type of Kubernetes resource"
    ),
    context: str = typer.Option(
        None,
        "--context", "-c",
        help="Additional context as a JSON string"
    ),
    output_format: str = typer.Option(
        "text",
        "--output", "-o",
        help="Output format (text or json)"
    ),
    read_only: bool = typer.Option(
        True,
        "--read-only/--no-read-only",
        help="Enable or disable read-only mode. When disabled, the agent can modify the cluster state."
    )
):
    """Debug a Kubernetes YAML file."""
    asyncio.run(process_task(
        task_type=TaskType.DEBUG,
        question=question,
        resource_type=resource_type,
        context=context,
        output_format=output_format,
        read_only=read_only
    ))


@app.command()
def explain(
    question: str = typer.Argument(..., help="Concept or question to explain"),
    resource_type: KubernetesResourceType = typer.Option(
        None,
        "--resource", "-r",
        help="Type of Kubernetes resource"
    ),
    context: str = typer.Option(
        None,
        "--context", "-c",
        help="Additional context as a JSON string"
    ),
    output_format: str = typer.Option(
        "text",
        "--output", "-o",
        help="Output format (text or json)"
    ),
    read_only: bool = typer.Option(
        True,
        "--read-only/--no-read-only",
        help="Enable or disable read-only mode. When disabled, the agent can modify the cluster state."
    )
):
    """Explain a Kubernetes concept or answer a question."""
    asyncio.run(process_task(
        task_type=TaskType.EXPLAIN,
        question=question,
        resource_type=resource_type,
        context=context,
        output_format=output_format,
        read_only=read_only
    ))


@app.command()
def validate(
    yaml_file: Path = typer.Argument(..., help="Path to YAML file to validate"),
    resource_type: KubernetesResourceType = typer.Option(
        None,
        "--resource", "-r",
        help="Type of Kubernetes resource"
    ),
    context: str = typer.Option(
        None,
        "--context", "-c",
        help="Additional context as a JSON string"
    ),
    output_format: str = typer.Option(
        "text",
        "--output", "-o",
        help="Output format (text or json)"
    ),
    read_only: bool = typer.Option(
        True,
        "--read-only/--no-read-only",
        help="Enable or disable read-only mode. When disabled, the agent can modify the cluster state."
    )
):
    """Validate a Kubernetes YAML file."""
    asyncio.run(process_task(
        task_type=TaskType.VALIDATE,
        question="Validate this Kubernetes YAML",
        resource_type=resource_type,
        yaml_file=yaml_file,
        context=context,
        output_format=output_format,
        read_only=read_only
    ))


if __name__ == "__main__":
    app()
