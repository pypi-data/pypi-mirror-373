# CKAD Agent

A powerful AI-powered agent. This tool leverages large language models to help you understand, debug, and generate Kubernetes configurations.

## Features

- 🐛 Debug Kubernetes YAML manifests
- 📚 Explain Kubernetes concepts and best practices
- ✨ Generate valid Kubernetes YAML from requirements
- ✅ Validate and improve existing configurations
- 🎯 Focus on CKAD exam topics and patterns

## Installation

1. Install the package:
   ```bash
   pip install ckad-agent
   ```

2. Create a `.env` file with your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Usage

### Command Line Interface

The CKAD Agent provides a convenient CLI for common tasks:

```bash
# Explain a Kubernetes concept
ckad explain "How do I configure liveness and readiness probes?"

# Debug a YAML file
ckad debug "My pod keeps crashing" pod.yaml --resource Pod

# Validate a YAML file
ckad validate deployment.yaml --resource Deployment
```

### Python API

```python
from ckad_agent import CkadAgent, CKADRequest, TaskType, KubernetesResourceType
import asyncio

async def main():
    agent = CkadAgent()
    
    # Example: Debug a YAML
    request = CKADRequest(
        task_type=TaskType.DEBUG,
        resource_type=KubernetesResourceType.POD,
        yaml_content="""
        apiVersion: v1
        kind: Pod
        metadata:
          name: my-pod
        spec:
          containers:
          - name: nginx
            image: nginx:latest
        """,
        question="Why isn't this pod starting?"
    )
    
    response = await agent.process_request(request)
    print(response.solution)

asyncio.run(main())
```

## Development with uv

### Prerequisites
- Install `uv` (if not already installed):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Or install via pip:
  ```bash
  pip install uv
  ```

### Setup and Development
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # .\.venv\Scripts\activate  # On Windows
   ```
3. Install the package in development mode with all dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   pytest
   ```

## License

MIT
