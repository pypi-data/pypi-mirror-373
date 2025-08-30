"""Tests for the kubectl tool."""
import pytest
from unittest.mock import patch, MagicMock

from ckad_agent.kubectl_tool import KubectlTool


def test_execute_command_success():
    """Test successful command execution."""
    tool = KubectlTool(read_only=True)
    with patch('subprocess.run') as mock_run:
        # Configure the mock to return a successful result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "pods found"
        mock_run.return_value = mock_result
        
        success, output = tool.execute_command("kubectl get pods")
        
        assert success is True
        assert "pods found" in output
        mock_run.assert_called_once_with(
            "kubectl get pods",
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )


def test_execute_command_invalid_command():
    """Test execution of invalid command."""
    tool = KubectlTool(read_only=True)
    success, output = tool.execute_command("invalid command")
    assert success is False
    assert "must start with 'kubectl'" in output


def test_execute_command_blocked_in_read_only():
    """Test that write commands are blocked in read-only mode."""
    tool = KubectlTool(read_only=True)
    success, output = tool.execute_command("kubectl create deployment nginx --image=nginx")
    assert success is False
    assert "Write operations are not allowed in read-only mode" in output


def test_execute_command_blocking_commands():
    """Test that blocking commands are not allowed."""
    tool = KubectlTool(read_only=True)
    success, output = tool.execute_command("kubectl get pods --watch")
    assert success is False
    assert "Blocking commands" in output


def test_execute_command_error():
    """Test command execution with error."""
    tool = KubectlTool(read_only=True)
    with patch('subprocess.run') as mock_run:
        # Configure the mock to raise an exception
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="kubectl get pods",
            stderr="Error: pods is forbidden"
        )
        
        success, output = tool.execute_command("kubectl get pods")
        
        assert success is False
        assert "Error executing command" in output
        assert "pods is forbidden" in output
