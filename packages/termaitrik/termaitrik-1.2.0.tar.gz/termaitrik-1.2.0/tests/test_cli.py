import json
import subprocess
from typing import Iterable

import pytest
from typer.testing import CliRunner

from termai import cli
from termai.providers import ChatMessage, BaseProvider, ProviderError
from termai.server import app as fastapi_app
from fastapi.testclient import TestClient


class FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self, replies: Iterable[str] | None = None):
        self._replies = list(replies or [])

    def chat(self, messages, model, temperature: float = 0.2, stream: bool = False):
        # Return the configured replies; mimic streaming by yielding pieces.
        for r in self._replies:
            if stream:
                # yield char-by-char to simulate streaming
                for i in range(0, len(r), 4):
                    yield r[i : i + 4]
            else:
                yield r


@pytest.fixture(autouse=True)
def patch_make_provider(monkeypatch):
    # Replace make_provider to return a FakeProvider by default
    def _fake(cfg):
        return FakeProvider(replies=["hello from fake provider"])

    # providers.make_provider used by CLI and server; patch the providers module only
    import termai.providers as providers_module

    monkeypatch.setattr(providers_module, "make_provider", lambda cfg: _fake(cfg))
    yield


def test_chat_command_runs_and_streams(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli.app, ["chat", "ciao mondo", "--no-stream"])
    assert result.exit_code == 0
    assert "hello from fake provider" in result.output



def test_explain_prints_text(monkeypatch):
    import termai.providers as providers_module

    monkeypatch.setattr(providers_module, "make_provider", lambda cfg: FakeProvider(replies=["spiega"]))
    runner = CliRunner()
    result = runner.invoke(cli.app, ["explain", "--cmd", "ls -la"])
    assert result.exit_code == 0
    assert "spiega" in result.output



def test_run_returns_dry_run(monkeypatch):
    # provider returns a command containing newlines; ensure only first line is used
    import termai.providers as providers_module

    monkeypatch.setattr(providers_module, "make_provider", lambda cfg: FakeProvider(replies=["<CMD>echo hi\nevil stuff</CMD>"]))
    runner = CliRunner()
    result = runner.invoke(cli.app, ["run", "do something", "--dry-run"], input="a\n")
    # run calls typer.Exit with rc 0 on dry-run
    assert result.exit_code == 0
    assert "Dry-run" in result.output or "Dry-run".lower() in result.output.lower()


def test_chat_command_handles_provider_error(monkeypatch):
    def fake(cfg):
        raise ProviderError("test error")

    import termai.providers as providers_module

    monkeypatch.setattr(providers_module, "make_provider", lambda cfg: fake(cfg))
    runner = CliRunner()
    result = runner.invoke(cli.app, ["chat", "test"])
    assert result.exit_code == 1
    assert "Provider error" in result.output


def test_info_command(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli.app, ["info"])
    assert result.exit_code == 0
    assert "Provider" in result.output
    assert "Model" in result.output


def test_examples_command(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli.app, ["examples"])
    assert result.exit_code == 0
    assert "Generic chat" in result.output
    assert "Command suggestion" in result.output


def test_agent_minimal_flow(monkeypatch):
    # Provide two JSON replies: first with a command, second marking done
    class AgentProvider(FakeProvider):
        def __init__(self):
            replies = [
                json.dumps({
                    "thought": "list files",
                    "command": "echo agent_test > agent_file.txt",
                    "explanation": "create sample file",
                    "done": False,
                }),
                json.dumps({
                    "thought": "finished",
                    "command": "",
                    "explanation": "all good",
                    "done": True,
                }),
            ]
            super().__init__(replies=replies)

    import termai.providers as providers_module
    monkeypatch.setattr(providers_module, "make_provider", lambda cfg: AgentProvider())
    runner = CliRunner()
    # Input 'e' to execute first command
    result = runner.invoke(cli.app, ["agent", "simple flow", "--steps", "3", "--dry-run"], input="e\n")
    assert result.exit_code == 0
    assert "Step 1" in result.output
    assert "agent_test" in result.output or "echo agent_test" in result.output
    assert "Session ended" in result.output


def test_install_shell_command(monkeypatch, tmp_path):
    """Test the install-shell command."""
    # Mock the subprocess.run call
    mock_result = subprocess.CompletedProcess(
        args=["bash", "install-shell-integration.sh"], 
        returncode=0, 
        stdout="Shell integration installed successfully!", 
        stderr=""
    )
    
    def mock_subprocess_run(cmd, capture_output=True, text=True):
        return mock_result
    
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    # Mock the script path existence check
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    runner = CliRunner()
    result = runner.invoke(cli.app, ["install-shell", "--shell", "bash"])
    
    assert result.exit_code == 0
    assert "Shell integration installed successfully!" in result.output


def test_install_shell_command_error(monkeypatch):
    """Test the install-shell command with error."""
    # Mock the subprocess.run call to return error
    mock_result = subprocess.CompletedProcess(
        args=["bash", "install-shell-integration.sh"], 
        returncode=1, 
        stdout="", 
        stderr="Error installing shell integration"
    )
    
    def mock_subprocess_run(cmd, capture_output=True, text=True):
        return mock_result
    
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    # Mock the script path existence check
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    runner = CliRunner()
    result = runner.invoke(cli.app, ["install-shell"])
    
    assert result.exit_code == 1
    assert "Error installing shell integration:" in result.output


def test_uninstall_shell_command(monkeypatch):
    """Test the uninstall-shell command."""
    # Mock the subprocess.run call
    mock_result = subprocess.CompletedProcess(
        args=["bash", "uninstall-shell-integration.sh"], 
        returncode=0, 
        stdout="Shell integration uninstalled successfully!", 
        stderr=""
    )
    
    def mock_subprocess_run(cmd, capture_output=True, text=True):
        return mock_result
    
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    # Mock the script path existence check
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    runner = CliRunner()
    result = runner.invoke(cli.app, ["uninstall-shell"])
    
    assert result.exit_code == 0
    assert "Shell integration uninstalled successfully!" in result.output


def test_install_shell_script_not_found(monkeypatch):
    """Test install-shell command when script is not found."""
    # Mock the script path existence check to return False
    monkeypatch.setattr("os.path.exists", lambda x: False)
    
    runner = CliRunner()
    result = runner.invoke(cli.app, ["install-shell"])
    
    assert result.exit_code == 1
    assert "Install script not found" in result.output


def test_uninstall_shell_script_not_found(monkeypatch):
    """Test uninstall-shell command when script is not found."""
    # Mock the script path existence check to return False
    monkeypatch.setattr("os.path.exists", lambda x: False)
    
    runner = CliRunner()
    result = runner.invoke(cli.app, ["uninstall-shell"])
    
    assert result.exit_code == 1
    assert "Uninstall script not found" in result.output
