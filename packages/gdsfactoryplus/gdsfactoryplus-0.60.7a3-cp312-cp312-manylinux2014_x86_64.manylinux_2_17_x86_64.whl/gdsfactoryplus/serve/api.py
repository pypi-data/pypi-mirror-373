"""API module for the application."""

from __future__ import annotations

import sax

from gdsfactoryplus.core import database as db
from gdsfactoryplus.core import kcl
from gdsfactoryplus.core.build import build_by_names
from gdsfactoryplus.core.pdk import register_cells
from gdsfactoryplus.models import (
    SerializedComplexArray,
    SerializedSimulationResult,
    Simulation,
)
from gdsfactoryplus.simulate import simulate as _simulate

from .app import app, logger


@app.get("/api/build-cell")
def build_cell(name: str, *, with_metadata: bool = True, register: bool = True) -> None:
    """Build a GDS cell by name.

    Args:
        name: Name of the cell to build.
        with_metadata: Whether to include metadata in the GDS file.
        register: Whether to re-register the cell in the KLayout cache.
    """
    paths = db.get_factory_sources_by_name(name)
    if register and paths:
        names, _ = register_cells(paths=paths.values())
        kcl.clear_cells_from_cache(*names)
    else:
        kcl.clear_cells_from_cache(name)
    build_by_names(name, with_metadata=with_metadata)


@app.post("/api/build-cells")
def build_cells(
    names: list[str],
    *,
    with_metadata: bool = True,
    register: bool = True,
) -> None:
    """Build multiple GDS cells by names.

    Args:
        names: List of cell names to build.
        with_metadata: Whether to include metadata in the GDS files.
        register: Whether to re-register the cells in the KLayout cache.
    """
    logger.warning(f"{names}")
    paths = db.get_factory_sources_by_name(*names)
    if register and paths:
        registered_names, _ = register_cells(paths=paths.values())
        kcl.clear_cells_from_cache(*registered_names)
        names = list({*names, *registered_names})
    else:
        kcl.clear_cells_from_cache(*names)
    build_by_names(*names, with_metadata=with_metadata)


@app.post("/api/simulate")
def simulate(
    sim: Simulation,
) -> SerializedSimulationResult | dict[str, str]:
    """Simulate a factory.

    Args:
        sim: Simulation object containing the name, layout, and model.

    Returns:
        SerializedSimulationResult: The result of the simulation, serialized.
    """
    logger.warning(f"{sim=}")
    try:
        sdict = sax.sdict(_simulate(sim.name, layout=sim.layout, model=sim.model))
        result: SerializedSimulationResult = {}
        for (p, q), v in sdict.items():
            if (abs(v) < 1e-7).all():
                continue
            if p not in result:
                result[p] = {}
            result[p][q] = SerializedComplexArray.from_numpy(v)
    except Exception as e:  # noqa: BLE001
        return {"detail": str(e)}
    return result


@app.get("/api/simulate")
def simulate_get(
    name: str,
) -> SerializedSimulationResult | dict[str, str]:
    """Simulate a factory.

    Args:
        name: name of the factory to simulate with default arguments.

    Returns:
        SerializedSimulationResult: The result of the simulation, serialized.
    """
    return simulate(Simulation(name=name, layout={}, model={}))
