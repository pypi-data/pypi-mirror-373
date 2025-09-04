"""Get the GDSFactory+ version."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .app import app

if TYPE_CHECKING:
    import gdsfactoryplus.version as v
else:
    from gdsfactoryplus.core.lazy import lazy_import

    v = lazy_import("gdsfactoryplus.version")

__all__ = ["version"]


@app.command()
def version() -> None:
    """Get the GDSFactory+ version."""
    sys.stdout.write(f"{v.__version__}\n")
