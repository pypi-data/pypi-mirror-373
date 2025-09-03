# ezga/simulator/calculators/__init.py__
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Any, Tuple, Optional
import importlib
import numpy as np

CalculatorFn = Callable[[np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]]

_REGISTRY: Dict[str, CalculatorFn] = {}


def list_calculators() -> Dict[str, CalculatorFn]:
    return dict(_REGISTRY)


def register_calculator(name: str, fn: Optional[CalculatorFn] = None):
    if fn is not None:
        _REGISTRY[name] = fn
        return fn
    def deco(f: CalculatorFn):
        _REGISTRY[name] = f
        return f
    return deco


@dataclass(frozen=True)
class CalculatorSpec:
    name: str
    kwargs: Dict[str, Any]

    @staticmethod
    def from_any(spec: Any) -> "CalculatorSpec":
        if isinstance(spec, str):
            return CalculatorSpec(name=spec, kwargs={})
        if isinstance(spec, dict):
            if "name" not in spec:
                raise ValueError("Calculator spec dict must include a 'name' key.")
            return CalculatorSpec(name=spec["name"], kwargs=dict(spec.get("kwargs", {})))
        raise TypeError("Calculator spec must be a string or a {name, kwargs} dict.")


# Eagerly import built‑ins so they self‑register via the decorator
# (kept very small; add new modules here)
for _mod in [
    "ezga.simulator.calculators.constant_zero",
    "ezga.simulator.calculators.ase_lj",
    "ezga.simulator.calculators.numba_lj_single",
]:
    try:
        importlib.import_module(_mod)
    except Exception:  # do not crash registry init if optional deps missing
        pass

# also try to import optional mixer (uses tables/ASE data)    
for _mod in [
    "ezga.simulator.calculators.lj_mixer",
]:
    try:
        importlib.import_module(_mod)
    except Exception:
        pass


def make_calculator(spec_like: Any) -> CalculatorFn:
    spec = CalculatorSpec.from_any(spec_like)
    if spec.name not in _REGISTRY:
        raise KeyError(f"Unknown calculator '{spec.name}'. Known: {list(_REGISTRY.keys())}")

    base_fn = _REGISTRY[spec.name]

    def wrapped(symbols: np.ndarray, positions: np.ndarray, cell: np.ndarray, *args, **kwargs):
        merged = dict(spec.kwargs)
        merged.update(kwargs)
        return base_fn(symbols, positions, cell, *args, **merged)

    return wrapped