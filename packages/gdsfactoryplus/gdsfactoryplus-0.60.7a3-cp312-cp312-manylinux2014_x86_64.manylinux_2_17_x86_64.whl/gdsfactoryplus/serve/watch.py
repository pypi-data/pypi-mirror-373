"""Server watcher handlers."""

from __future__ import annotations

from pathlib import Path

from gdsfactoryplus.core import kcl
from gdsfactoryplus.core.build import build_by_names
from gdsfactoryplus.core.pdk import register_cells
from gdsfactoryplus.settings import get_db_path, get_settings

from .app import app, logger


@app.get("/watch/on-modified")
def on_modified(path: str) -> dict:
    """Handle an on-modified event."""
    p = Path(path).resolve()
    if not p.is_file():
        return {"detail": "not a file."}

    if p.name == "pyproject.toml":
        # while the server is running the only valid modification to the
        # pyproject.toml is to ignore cells.
        get_settings.cache_clear()
        _, names = register_cells(reload=False)
        kcl.clear_cells_from_cache(*names)
        return {"detail": "pyproject.toml modified."}

    names, _ = register_cells(paths=[p])
    kcl.clear_cells_from_cache(*names)
    logger.info(f"registered / updated cells from {p}: {names}")

    build_by_names(*names, with_metadata=True)
    logger.info(f"build cells from {p}: {names}")

    return {"detail": f"registered cells from {p}."}


@app.get("/watch/on-deleted")
def on_deleted(path: str) -> dict:
    """Handle an on-deleted event."""
    p = Path(path).resolve()
    logger.info(f"on-deleted: {p}")

    if p.is_dir() and p.name == "build":
        # register_cells()
        return {"detail": "deleted build folder."}

    if p.is_file() and p.name == get_db_path().name and p.parent.name == "build":
        # register_cells()
        return {"detail": "deleted database."}

    if p.name.endswith(".pic.yml"):
        scm_path = p.parent / f"{p.name[:-8]}.scm.yml"
        logger.warning(f"deleting {scm_path} as well.")
        scm_path.unlink(missing_ok=True)

    # TODO: add pdk.unregister_cells for more targeted deletion
    _, names = register_cells(reload=False)
    kcl.clear_cells_from_cache(*names)
    logger.info(f"unregistered cells from {p}.")

    return {"detail": f"unregistered cells from {p}."}
