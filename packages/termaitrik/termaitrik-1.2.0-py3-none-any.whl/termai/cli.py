from __future__ import annotations

"""CLI entry-point for TermAI.

Supports three invocation modes:
1. Installed package / console script (normal) -> relative imports work.
2. Module execution: python -m termai.cli (works unchanged).
3. Script execution: uv run termai/cli.py (no package context). We add a
   fallback that rewrites imports so the file can still run, enabling
   quick ad-hoc execution (and therefore uvx/uv run based workflows before
   installation/publishing).
"""

import json
from typing import Optional, List
import os
import re
import subprocess
import sys
import typer
from rich import print
from rich.status import Status

# When executed directly (python termai/cli.py) __package__ is None/"" and
# relative imports fail. Add the directory to sys.path and fall back to
# absolute intra-package imports so `uv run termai/cli.py ...` works.
if not __package__:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # project/termai
    try:  # absolute (script) style
        from config import load_config  # type: ignore
        import providers  # type: ignore
        from providers import ProviderError  # type: ignore
        from prompts import (
            SYSTEM_SHELL_EXPERT,
            PROMPT_SUGGEST,
            PROMPT_EXPLAIN,
            PROMPT_FIX,
            AGENT_SYSTEM_PROMPT,
            AGENT_STEP_USER_PROMPT,
        )  # type: ignore
        from utils import stream_to_console, pretty_json, confirm_and_run, run_command_capture  # type: ignore
    except Exception as _import_err:  # pragma: no cover - only on direct script run
        raise
else:  # normal package-relative imports
    from .config import load_config
    from . import providers
    from .providers import ProviderError
    from .prompts import (
        SYSTEM_SHELL_EXPERT,
        PROMPT_SUGGEST,
        PROMPT_EXPLAIN,
        PROMPT_FIX,
        AGENT_SYSTEM_PROMPT,
        AGENT_STEP_USER_PROMPT,
    )
    from .utils import stream_to_console, pretty_json, confirm_and_run, run_command_capture

# ASCII Art for TermAI
ASCII_ART = """[cyan]
████████╗███████╗██████╗ ███╗   ███╗ █████╗ ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██║
   ██║   █████╗  ██████╔╝██╔████╔██║███████║██║
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║██║
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
[/cyan]
         [bold]AI Assistant for your Terminal[/bold]
"""

def get_help_text():
    from rich.text import Text
    # We need to return a plain text for Typer's help
    # but we'll create a custom callback to show formatted help
    return "TermAI — AI assistant for your terminal (Ollama + BYOK)."

# Custom help function
def custom_help_callback(ctx: typer.Context):
    # Only show formatted help when we're at the root level and help is requested
    # We check if we're not in a subcommand context
    if ctx.invoked_subcommand is None:
        # Check if help was explicitly requested
        if "--help" in sys.argv or "-h" in sys.argv:
            show_formatted_help()
            raise typer.Exit()
    # For subcommands, let Typer handle the help normally
    return False

app = typer.Typer(help=get_help_text(), no_args_is_help=False)

from rich.console import Console

def show_formatted_help():
    console = Console()
    console.print(ASCII_ART)
    console.print("\n[bold]TermAI[/bold] — AI assistant for your terminal (Ollama + BYOK).\n")
    console.print("[bold]Features:[/bold]")
    console.print("• [green]chat[/green] - General chat with AI")
    console.print("• [green]suggest[/green] - Generate shell commands")
    console.print("• [green]explain[/green] - Explain shell commands")
    console.print("• [green]fix[/green] - Fix failed commands")
    console.print("• [green]run[/green] - Execute commands with confirmation")
    console.print("• [green]agent[/green] - Multi-step iterative assistant")
    console.print("• [green]install-shell[/green] - Install shell integration (ai alias)")
    console.print("• [green]uninstall-shell[/green] - Uninstall shell integration")
    console.print("• [green]info[/green] - Show configuration")
    console.print("• [green]examples[/green] - Show usage examples")
    console.print("\n[dim]Use [bold]termai [COMMAND] --help[/bold] for more information about a command.[/dim]")

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context,
            help: Optional[bool] = typer.Option(
                None, "--help", "-h", 
                help="Show this message and exit.",
                is_eager=True
            )):
    # Check if help was explicitly requested and we're at the root level
    if help is True and ctx.invoked_subcommand is None:
        show_formatted_help()
        raise typer.Exit()
    # If no subcommand and no arguments, show formatted help
    elif ctx.invoked_subcommand is None and not any(arg.startswith('-') for arg in sys.argv[1:]):
        show_formatted_help()


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Message for the chat."),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
    stream: bool = typer.Option(
        True, "--stream/--no-stream", help="Stream output if supported."
    ),
    temperature: float = typer.Option(
        0.2, "--temperature", "-t", help="Model creativity."
    ),
):
    """
    Sends a message to the AI and prints the response.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    # Provider creation inside try to catch ProviderError correctly for tests
    messages = [
        providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
        providers.ChatMessage(role="user", content=prompt),
    ]
    try:
        provider = providers.make_provider(cfg)
        if not stream:
            with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
                text = "".join(
                    provider.chat(
                        messages, cfg["model"], temperature=temperature, stream=stream
                    )
                )
            print(text)
        else:
            _ = stream_to_console(
                provider.chat(
                    messages, cfg["model"], temperature=temperature, stream=stream
                )
            )
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def suggest(
    goal: str = typer.Argument(..., help="Goal in natural language."),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Context: path, available tools, etc."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Suggests a command to achieve a given goal.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = PROMPT_SUGGEST.format(goal=goal, context=context or "N/A")
    messages = [
        providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            text = "".join(
                provider.chat(messages, cfg["model"], temperature=0.1, stream=False)
            )
        try:
            data = json.loads(text)
            # Verifica se i dati contengono le chiavi attese
            if "commands" in data:
                print(pretty_json(data))
            else:
                # Se non contiene le chiavi attese, stampa il testo originale
                print(text)
        except json.JSONDecodeError:
            print(text)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def explain(
    cmd: str = typer.Option(..., "--cmd", "-c", help="Command to explain."),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Explains a shell command.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = PROMPT_EXPLAIN.format(cmd=cmd)
    messages = [
        providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            out = "".join(
                provider.chat(messages, cfg["model"], temperature=0.1, stream=False)
            )
        print(out)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def fix(
    cmd: str = typer.Option(..., "--cmd", "-c", help="Command that failed."),
    error: str = typer.Option(..., "--error", "-e", help="Error message from stderr."),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Fixes a failed shell command.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = PROMPT_FIX.format(cmd=cmd, err=error)
    messages = [
        providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            text = "".join(
                provider.chat(messages, cfg["model"], temperature=0.1, stream=False)
            )
        try:
            data = json.loads(text)
            # Verifica se i dati contengono le chiavi attese
            if "cause" in data:
                print(pretty_json(data))
            else:
                # Se non contiene le chiavi attese, stampa il testo originale
                print(text)
        except json.JSONDecodeError:
            print(text)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def run(
    goal: str = typer.Argument(..., help="Goal in natural language."),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Optional context."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print the command without executing it."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Generates and executes a command to achieve a given goal.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = (
        "Translate the following goal into a single executable shell command.\n"
        "The command must be valid and safe.\n"
        "Respond ONLY with the command, wrapped in <CMD></CMD> tags.\n"
        'Example: <CMD>echo "hello" > world.txt</CMD>\n\n'
        f"Goal: {goal}\n"
        f"Context: {context or 'None'}\n"
        "Response:"
    )
    messages = [
        providers.ChatMessage(
            role="system",
            content="You are a shell expert that translates goals into commands.",
        ),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            response_text = "".join(
                provider.chat(messages, cfg["model"], temperature=0.0, stream=False)
            )

        command = ""
        match = re.search(r"<CMD>(.*)</CMD>", response_text, re.DOTALL)
        if match:
            command = match.group(1).strip()

        if not command:
            print(
                f"[red]Error: the AI did not return a valid command.[/red]\n[dim]Received response:[/dim]\n{response_text}"
            )
            raise typer.Exit(code=1)

        rc = confirm_and_run(command, dry_run=dry_run)
        raise typer.Exit(code=rc)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def info():
    """Shows the configured provider and the default model."""
    cfg = load_config()
    model = cfg.get("model") or "N/A"
    env_provider = os.getenv("TERMAI_PROVIDER")
    # Resolve provider and indicate the source of the choice
    source = "fallback"
    cfg_default = cfg.get("default_provider")
    if cfg_default:
        source = "config"
    elif env_provider:
        source = "env"

    try:
        prov = providers.make_provider(cfg)
        provider_name = getattr(prov, "name", None) or (
            cfg_default or env_provider or "ollama"
        )
    except ProviderError:
        provider_name = cfg_default or env_provider or "ollama"

    print(f"[bold]Provider:[/bold] {provider_name}  [dim]({source})[/dim]")
    # show the resolved configuration file path
    from pathlib import Path
    from .config import DEFAULT_CONFIG_PATH

    local_cfg = Path.cwd() / "config.yaml"
    resolved_path = local_cfg if local_cfg.exists() else DEFAULT_CONFIG_PATH
    print(
        f"[bold]Config file:[/bold] {resolved_path} {'(exists)' if resolved_path.exists() else '(not found)'}"
    )
    print(f"[bold]Model:[/bold] {model}")


@app.command()
def examples():
    """Shows usage examples."""
    from rich.panel import Panel

    examples = [
        {
            "title": "Generic chat",
            "code": 'termai chat "how can I use `tar` to compress a folder?"',
        },
        {
            "title": "Command suggestion",
            "code": 'termai suggest "find all `.py` files modified in the last week"',
        },
        {
            "title": "Command explanation",
            "code": "termai explain --cmd \"awk -F':' '{print $1}' /etc/passwd\"",
        },
        {
            "title": "Fix command with error",
            "code": 'termai fix --cmd "git push" --error "fatal: repository \'https\' not found"',
        },
        {
            "title": "Direct execution",
            "code": 'termai suggest "list all files in the current directory, including hidden ones, and sort them by size"',
        },
        {
            "title": "Run command (dry-run)",
            "code": 'termai run --dry-run "create a file named \'test.txt\' with the content \'hello world\'"',
        },
        {
            "title": "Agent multi-step (experimental)",
            "code": "termai agent \"create a new directory called 'test_agent', and create a file inside it called 'test.txt' with the content 'hello from agent'\"",
        },
    ]
    for example in examples:
        print(Panel(example["code"], title=example["title"], border_style="green"))



# ---------------- Experimental minimal agent command ---------------- #

@app.command()
def agent(
    goal: str = typer.Argument(..., help="High-level multi-step goal."),
    steps: int = typer.Option(6, "--steps", "-s", help="Maximum reasoning steps."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model override."),
    temperature: float = typer.Option(0.1, "--temperature", "-t", help="Model temperature."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not execute proposed commands."),
):
    """Iterative loop (plan -> propose command -> confirm -> observe -> repeat). Minimal POC."""
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)

    history: List[providers.ChatMessage] = [
        providers.ChatMessage(role="system", content=AGENT_SYSTEM_PROMPT),
        providers.ChatMessage(role="user", content=f"Obiettivo: {goal}"),
    ]

    def last_events() -> str:
        msgs = [m for m in history if m.role != "system"][-8:]
        lines: List[str] = []
        for m in msgs:
            tag = "U" if m.role == "user" else "A"
            c = m.content
            if len(c) > 250:
                c = c[:250] + "..."
            lines.append(f"[{tag}] {c}")
        return "\n".join(lines) or "(vuoto)"

    for step in range(1, steps + 1):
        user_prompt = AGENT_STEP_USER_PROMPT.format(goal=goal, history_snippet=last_events())
        history.append(providers.ChatMessage(role="user", content=user_prompt))
        with Status(f"[dim]Agent step {step}...[/dim]", spinner="dots"):
            raw = "".join(
                provider.chat(history, cfg["model"], temperature=temperature, stream=False)
            )
        history.append(providers.ChatMessage(role="assistant", content=raw))
        # Some naive providers may concatenate multiple JSON objects; take the first one that parses.
        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to split by '}{' boundaries
            fragments = []
            buf = ""
            depth = 0
            for ch in raw:
                buf += ch
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        fragments.append(buf)
                        buf = ""
            for frag in fragments:
                try:
                    data = json.loads(frag)
                    break
                except Exception:
                    continue
            if data is None:
                print(f"[red]Invalid JSON at step {step}.[/red]\n{raw}")
                break

        thought = data.get("thought", "")
        command = (data.get("command") or "").strip()
        explanation = data.get("explanation", "")
        done = bool(data.get("done", False))

        print(f"[bold cyan]Step {step}[/bold cyan]")
        if thought:
            print(f"[dim]Thought:[/dim] {thought}")
        if command:
            print(f"[green]Command:[/green] {command}")
        if explanation:
            print(f"[dim]Explanation:[/dim] {explanation}")
        if done and not command:
            print("[yellow]Agent finished (done=true).[/yellow]")
            break

        if command:
            rc = confirm_and_run(command, dry_run=dry_run)
            if dry_run:
                observation = f"Dry-run: would have executed: {command}"
            else:
                out, err, rcode = run_command_capture(command)
                text = out + ("\nSTDERR:\n" + err if err else "")
                if len(text) > 800:
                    text = text[:800] + "... (truncated)"
                observation = f"RC={{rcode}}\n{text.strip()}" if text.strip() else f"Return code: {rcode}"
            history.append(
                providers.ChatMessage(role="user", content=f"Observation after command:\n{observation}")
            )

        if done:
            break
    print("[bold]Session ended.[/bold]")


@app.command("install-shell")
def install_shell(
    shell: Optional[str] = typer.Option(
        None, "--shell", "-s", help="Target shell (bash, zsh, fish). Auto-detected if not specified."
    ),
):
    """Install shell integration (ai alias) for TermAI."""
    # Find the script relative to the repository root
    # The CLI module is in termai/cli.py, so we need to go up two levels to get to repo root
    current_file = os.path.abspath(__file__)
    repo_root = os.path.dirname(os.path.dirname(current_file))
    install_script = os.path.join(repo_root, "scripts", "install-shell-integration.sh")
    
    # Check if script exists
    if not os.path.exists(install_script):
        print(f"[red]Error:[/red] Install script not found at {install_script}")
        raise typer.Exit(code=1)
    
    try:
        # Build command
        cmd = ["bash", install_script]
        if shell:
            cmd.extend(["--shell", shell])
        
        # Execute the installation script
        with Status("[dim]Installing shell integration...[/dim]", spinner="dots"):
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[green]✓[/green] Shell integration installed successfully!")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"[red]Error installing shell integration:[/red]")
            if result.stderr.strip():
                print(result.stderr.strip())
            if result.stdout.strip():
                print(result.stdout.strip())
            raise typer.Exit(code=result.returncode)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("uninstall-shell")
def uninstall_shell():
    """Uninstall shell integration (ai alias) for TermAI."""
    # Find the script relative to the repository root  
    # The CLI module is in termai/cli.py, so we need to go up two levels to get to repo root
    current_file = os.path.abspath(__file__)
    repo_root = os.path.dirname(os.path.dirname(current_file))
    uninstall_script = os.path.join(repo_root, "scripts", "uninstall-shell-integration.sh")
    
    # Check if script exists
    if not os.path.exists(uninstall_script):
        print(f"[red]Error:[/red] Uninstall script not found at {uninstall_script}")
        raise typer.Exit(code=1)
    
    try:
        # Execute the uninstallation script
        with Status("[dim]Uninstalling shell integration...[/dim]", spinner="dots"):
            result = subprocess.run(["bash", uninstall_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[green]✓[/green] Shell integration uninstalled successfully!")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"[red]Error uninstalling shell integration:[/red]")
            if result.stderr.strip():
                print(result.stderr.strip())
            if result.stdout.strip():
                print(result.stdout.strip())
            raise typer.Exit(code=result.returncode)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
