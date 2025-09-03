from __future__ import annotations

import json
import subprocess
from typing import Iterable

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt

console = Console()


def stream_to_console(chunks: Iterable[str]) -> str:
    out = []
    for chunk in chunks:
        console.print(chunk, end="")
        out.append(chunk)
    console.print()
    return "".join(out)


def pretty_json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def confirm_and_run(command: str, dry_run: bool = False) -> int:
    """
    Prompts the user to confirm a command before running it.
    """
    while True:
        console.print(Markdown(f"**Suggested command:**\n\n```bash\n{command}\n```"))
        if dry_run:
            console.print("[yellow]Dry-run: command not executed.[/yellow]")
            return 0

        choice = Prompt.ask(
            "What do you want to do?",
            choices=["e", "m", "a"],
            default="e",
            show_choices=True,
        )

        if choice == "e":
            return subprocess.call(command, shell=True)
        elif choice == "m":
            command = Prompt.ask("Modify the command", default=command)
        elif choice == "a":
            console.print("[yellow]Aborted by user.[/yellow]")
            return 0


def run_command_capture(command: str) -> tuple[str, str, int]:
    """Executes a shell command capturing stdout, stderr and return code.

    Minimal helper used by the experimental agent loop.
    """
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    return proc.stdout, proc.stderr, proc.returncode
