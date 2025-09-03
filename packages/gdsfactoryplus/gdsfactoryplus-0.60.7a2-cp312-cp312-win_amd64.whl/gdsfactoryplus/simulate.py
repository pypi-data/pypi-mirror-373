"""Simulate a factory."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import gdsfactoryplus.models as m

if TYPE_CHECKING:
    import gdsfactory as gf
    import jax.numpy as jnp
    import sax

    import gdsfactoryplus.core.database as db
    from gdsfactoryplus.core.pdk import get_pdk, register_cells
else:
    from gdsfactoryplus.core.lazy import lazy_import

    sax = lazy_import("sax")
    jnp = lazy_import("jax.numpy")
    db = lazy_import("gdsfactoryplus.core.database")
    get_pdk = lazy_import("gdsfactoryplus.core.pdk", "get_pdk")
    register_cells = lazy_import("gdsfactoryplus.core.pdk", "register_cells")


def simulate(
    name: str,
    layout: dict[str, Any],
    model: dict[str, Any],
) -> sax.SType:
    """Simualate a factory."""
    sim = m.Simulation(name=name, layout=layout, model=model)

    record = db.get_factories_by_name(sim.name).get(sim.name)
    if not record or (src := record.absolute_source()) is None:
        msg = f"Cell '{sim.name}' not found in database."
        raise FileNotFoundError(msg)

    pdk = get_pdk()
    register_cells(paths=[src])
    if sim.name not in pdk.cells:
        msg = f"Cell '{sim.name}' not found in PDK."
        raise ValueError(msg)

    layout: gf.Component = pdk.get_component(sim.name, **sim.layout)
    model: Callable | None = pdk.models.get(sim.name)

    if model is not None:
        full_settings = {
            **layout.info.model_dump(),
            **layout.settings.model_dump(),
            **sim.model,
        }
        settings = {
            k: v
            for k, v in full_settings.items()
            if k in inspect.signature(model).parameters
        }
        return model(**_arrayfy(settings))

    netlist = layout.get_netlist(recursive=True)
    if not netlist:
        msg = f"Cell '{sim.name}' is a base component (has no netlist) with no model."
        raise FileNotFoundError(msg)

    flat_net = next(iter(netlist.values()))
    if not flat_net.get("instances"):
        msg = f"Cell '{sim.name}' is a base component (has no instances) with no model."
        raise FileNotFoundError(msg)

    ports = flat_net.get("ports", {})
    if not ports:
        msg = f"Cell '{sim.name}' has no ports."
        raise ValueError(msg)
    if len(ports) < 2:
        msg = f"Cell '{sim.name}' has less than two ports."
        raise ValueError(msg)

    circuit, _ = sax.circuit(netlist, models=pdk.models)
    return circuit(**_arrayfy(sim.model))


def _arrayfy(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _arrayfy(v) for k, v in obj.items()}
    if isinstance(obj, list | float | int):
        return jnp.asarray(obj, dtype=float)
    return obj
