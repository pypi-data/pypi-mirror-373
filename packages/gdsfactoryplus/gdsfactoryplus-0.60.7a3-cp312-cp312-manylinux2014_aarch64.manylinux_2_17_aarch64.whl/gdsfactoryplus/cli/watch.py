"""GDSFactory+ File Watcher."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .app import app

if TYPE_CHECKING:
    import typer

    import gdsfactoryplus.core.watch as watcher

else:
    from gdsfactoryplus.core.lazy import lazy_import

    typer = lazy_import("typer")
    watcher = lazy_import("gdsfactoryplus.core.watch")

__all__ = ["watch"]


@app.command()
def watch(path: str, server_url: str = "") -> None:
    """Watch a folder for changes.

    Args:
        path: Path to the folder.
        server_url: URL of the GDSFactory+ server.
    """
    if not server_url:
        server_url = os.environ.get("SERVER_URL", "")

    if not server_url:
        host = os.environ.get("GFP_KWEB_HOST", "localhost")
        if os.environ.get("GFP_KWEB_HTTPS", "false") == "true":
            server_url = f"https://{host}"
        else:
            server_url = f"http://{host}:8787"
    return watcher.watch(path, server_url)
