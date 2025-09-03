"""Module entry-point so users can run `python -m termai` or `uvx termai`.

This simply delegates to the Typer app defined in `cli.py`.
"""
from .cli import app

if __name__ == "__main__":  # pragma: no cover
    app()
