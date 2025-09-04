"""Get component settings."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from .app import app

if TYPE_CHECKING:
    import sax
    import toml
    import typer
    import yaml
    from rich.console import Console
    from rich.table import Table

    from gdsfactoryplus.settings import get_settings
else:
    from gdsfactoryplus.core.lazy import lazy_import

    typer = lazy_import("typer")
    sax = lazy_import("sax")
    toml = lazy_import("toml")
    yaml = lazy_import("yaml")
    Console = lazy_import("rich.console", "Console")
    Table = lazy_import("rich.table", "Table")
    get_settings = lazy_import("gdsfactoryplus.settings", "get_settings")

__all__ = ["settings"]


@app.command()
def settings(
    key: str = "",
    format: str = "table",  # noqa: A002
) -> None:
    """Display or modify component arguments and their default values.

    Args:
        format: The output format for displaying settings.
            Options are 'table', 'json', 'yaml', or 'toml'.
        key: A specific key to look for within the settings.
            Supports nested keys separated by dots.
    """
    console = Console()
    settings = json.loads(get_settings().model_dump_json())

    # Retrieve nested key if specified
    if key:
        parts = key.split(".")
        try:
            for subkey in parts:
                settings = settings[subkey]
        except KeyError as e:
            msg = f"Invalid {key=} not found in settings {list(settings.keys())}.\n"
            sys.stderr.write(msg)
            raise typer.Exit(2) from e
        if isinstance(settings, str):
            sys.stdout.write(f"{settings}\n")
            raise typer.Exit(0)

    # Display settings in the specified format
    if format == "table":
        flat_dict = sax.flatten_dict(settings, "_")
        flat_dict = {f"GFP_{k.upper()}": v for k, v in flat_dict.items()}
        table = Table(title="Settings")
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        for field, value in flat_dict.items():
            table.add_row(field, str(value))
        console.print(table)
    elif format == "json":
        sys.stdout.write(json.dumps(settings, indent=2) + "\n")
    elif format == "yaml":
        sys.stdout.write(yaml.safe_dump(settings, sort_keys=False) + "\n")
    elif format == "toml":
        sys.stdout.write(toml.dumps({"tool": {"gdsfactoryplus": settings}}) + "\n")
    else:
        msg = f"Invalid format '{format}'. Expected 'table', 'json', 'yaml', or 'toml'."
        sys.stderr.write(msg)
        raise typer.Exit(1)
