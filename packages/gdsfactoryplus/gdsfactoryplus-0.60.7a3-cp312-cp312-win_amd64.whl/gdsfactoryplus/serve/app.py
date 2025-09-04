"""GDSFactory+ Server Application."""

from __future__ import annotations

from pathlib import Path
from sqlite3 import OperationalError
from typing import cast

from doweb.browser import (
    get_app as _get_app,  # type: ignore[reportAttributeAccessIssue]
)
from doweb.layout_server import (
    LayoutViewServerEndpoint,  # type: ignore[reportAttributeAccessIssue]
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse

from gdsfactoryplus import logger as log
from gdsfactoryplus import project, settings
from gdsfactoryplus.core import database as db
from gdsfactoryplus.core import pdk

__all__ = ["app"]
logger = log.get_logger()

LayoutViewServerEndpoint.mode_dump = lambda _: ("ruler", "move instances")

THIS_DIR = Path(__file__).resolve().parent
GFP_DIR = THIS_DIR.parent

SETTINGS = settings.get_settings()
PDK: str = SETTINGS.pdk.name
_msg = f"Using PDK: {PDK}"
logger.info(_msg)
PROJECT_DIR = project.maybe_find_project_dir() or Path.cwd().resolve()
_msg = f"{PROJECT_DIR=}"
logger.info(_msg)

app = cast("FastAPI", _get_app(fileslocation=str(PROJECT_DIR), editable=True))


def _needs_to_be_removed(path: str) -> bool:
    return path == "/" or path.startswith(("/file", "/gds"))


app.router.routes = [
    r for r in app.routes if not _needs_to_be_removed(getattr(r, "path", ""))
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def redirect() -> RedirectResponse:
    """Index should redirect to /code to make online workspaces open in code editor."""
    return RedirectResponse("/code/")


@app.get("/code")
def code() -> PlainTextResponse:
    """Dummy response which will be overwritten in online workspaces."""
    return PlainTextResponse("gfp server is running.")


@app.on_event("startup")
async def startup_event() -> None:
    """Event handler that runs when the server has fully started."""
    db.reset_timestamps()


def get_app() -> FastAPI:
    """Get the FastAPI app instance."""
    msg = f"Activating PDK: {PDK}"
    logger.info(msg)
    pdk.get_pdk()
    try:
        pdk.register_cells()
    except OperationalError:
        logger.warning("Creating new database due to OperationalError.")
        db_path = settings.get_db_path()
        db_path.unlink(missing_ok=True)
        pdk.register_cells()

    return app
