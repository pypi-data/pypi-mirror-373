"""Data models for the CKAD Agent."""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Types of tasks the agent can perform."""
    DEBUG = "debug"
    EXPLAIN = "explain"
    GENERATE = "generate"
    VALIDATE = "validate"
    EXECUTE = "execute"  # For executing kubectl commands


class KubernetesResourceType(str, Enum):
    """Supported Kubernetes resource types."""
    POD = "Pod"
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    PERSISTENT_VOLUME_CLAIM = "PersistentVolumeClaim"
    SERVICE_ACCOUNT = "ServiceAccount"
    ROLE = "Role"
    ROLE_BINDING = "RoleBinding"


class CKADRequest(BaseModel):
    """Request model for CKAD agent tasks."""
    task_type: TaskType
    resource_type: Optional[KubernetesResourceType] = None
    yaml_content: Optional[str] = Field(
        None, 
        description="YAML content to analyze or validate"
    )
    question: str = Field(
        ...,
        description="The user's question or task description"
    )
    context: Optional[Dict[str, str]] = Field(
        None,
        description="Additional context for the task"
    )


class CKADResponse(BaseModel):
    """Response model for CKAD agent tasks."""
    success: bool
    command_output: Optional[str] = Field(
        None,
        description="Output from the executed command, if any"
    )
    message: str
    solution: Optional[str] = None
    fixed_yaml: Optional[str] = Field(
        None,
        description="Fixed or generated YAML content if applicable"
    )
    explanation: Optional[str] = Field(
        None,
        description="Detailed explanation of the solution"
    )
    references: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of references or documentation links"
    )
