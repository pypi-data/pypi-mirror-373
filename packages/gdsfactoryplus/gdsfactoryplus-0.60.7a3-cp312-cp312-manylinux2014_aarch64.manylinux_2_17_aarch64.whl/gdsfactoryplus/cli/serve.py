"""Serve the GDSFactory+ server."""

from __future__ import annotations

import subprocess
import sys
from multiprocessing import cpu_count
from pathlib import Path

import typer

from .app import app

__all__ = ["serve"]


@app.command()
def serve(
    port: int = 8787,
    host: str = "localhost",
    workers: int = 1,
    runner: str = "uvicorn",
    *,
    reload: bool = False,
    max_requests: int = 200,
) -> None:
    """Start the GDSFactory+ background service.

    Args:
        port: the port on which to run the background service
        host: the host on which to run the background service
        workers: the number of workers of the background service
        runner: Which server process to use ('uvicorn' or 'granian')
        reload: run the background service in debug mode (not recommended)
        max_requests: max requests per worker before restarting (only gunicorn runner)
    """
    if host == "localhost":
        host = "127.0.0.1"

    num_cpus = cpu_count()
    workers = workers if workers > 0 else num_cpus
    workers = min(workers, num_cpus)
    sys.stderr.write(f"{port=}\n{host=}\n{workers=}\n{reload=}\n")

    target = "gdsfactoryplus.serve.app:get_app"
    if runner == "gunicorn":
        gunicorn = str(Path(sys.executable).resolve().parent / "gunicorn")
        exit_code = subprocess.call(  # noqa: S603
            [
                gunicorn,
                target,
                "--worker-class",
                "uvicorn.workers.UvicornWorker",
                "--bind",
                f"{host}:{port}",
                "--workers",
                str(workers),
                "--forwarded-allow-ips",
                "*",
                "--access-logfile",
                "/dev/stdout",
                "--max-requests",
                f"{max_requests}",
                "--max-requests-jitter",
                "50",
                "--timeout",
                "120",
            ]
        )
        raise typer.Exit(exit_code)
    elif runner == "uvicorn":  # noqa: RET506
        import uvicorn

        uvicorn.run(
            target,
            forwarded_allow_ips="*",
            host=host,
            port=int(port),
            proxy_headers=True,
            reload=reload,
            use_colors=True,
            workers=workers,
            factory=True,
        )
    elif runner == "granian":
        from granian import Granian  # type: ignore[reportMissingImports]
        from granian.constants import Interfaces  # type: ignore[reportMissingImports]

        server = Granian(
            target=target,
            address=host,
            port=int(port),
            reload=reload,
            workers=workers,
            interface=Interfaces.ASGI,
        )
        server.serve()
    else:
        sys.stderr.write("Invalid runner. Use 'gunicorn', 'uvicorn' or 'granian'.\n")
        raise typer.Exit(1)
