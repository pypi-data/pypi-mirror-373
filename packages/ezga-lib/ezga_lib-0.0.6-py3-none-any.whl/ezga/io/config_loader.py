# SPDX-License-Identifier: GPL-3.0-only
"""YAML → GAConfig loader for EZGA (no-plugins fast path).

This module parses a user YAML into a validated :class:`GAConfig` and
materializes any dotted references or factory specs into live Python objects.

Supported reference forms
-------------------------
- "package.module:attr"   (preferred)
- "package.module.attr"
- "/abs/or/rel/path/to/file.py:attr"   (loads a module directly from the FS)

Factory specs
-------------
Anywhere in the YAML you can use:

  calculator:
    factory: "some.module:make_calc"     # dotted or /path/to/file.py:attr
    args: [..]                           # optional positional args
    kwargs: {..}                         # optional keyword args

Notes
-----
- This loader is intentionally lightweight; it does not import heavy subsystems
  during YAML parsing.
- It deliberately ignores “ordinary” strings (e.g., "cpu", "float32", "FIRE")
  so they don’t get treated as importable references.
"""

from __future__ import annotations

from pathlib import Path
import os
from types import ModuleType
from typing import Any, Iterable, Mapping, Optional, List
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec

from pydantic import ValidationError
from ruamel.yaml import YAML

from ezga.core.config import GAConfig

__all__ = ["load_config_yaml", "dump_config_yaml"]

# One safe loader for reading; one round-trip writer for pretty dumps.
_YAML_SAFE = YAML(typ="safe")
_YAML_RT = YAML()
_YAML_RT.indent(mapping=2, sequence=4, offset=2)
_YAML_RT.default_flow_style = False


# --------------------------------------------------------------------------- #
# Low-level import helpers
# --------------------------------------------------------------------------- #
def _resolve_callable_like(spec: Any) -> Any:
    """Normalize a YAML-provided callable specification into a live callable.

    This helper accepts several shapes that may appear in YAML and returns
    a ready-to-use Python object:

    Accepted forms
    --------------
    - ``None`` → returns ``None``.
    - ``str`` → treated as a dotted path (``"pkg.mod:attr"`` or ``"pkg.mod.attr"``);
      resolved via :func:`_resolve_dotted`.
    - ``Mapping`` (dict-like) → treated as a factory specification
      (e.g., ``{"factory": "pkg.mod:make_fn", "args": [...], "kwargs": {...}}``)
      and materialized via :func:`_materialize_factories`.
    - ``Sequence`` (list/tuple) → container of the above; each element is
      recursively materialized via :func:`_materialize_factories`. This is
      useful for "multiple objectives" or "multiple feature functions".
    - Any other Python object is returned unchanged (assumed already live).

    Args:
      spec: The value parsed from YAML.

    Returns:
      A live callable (or a list/tuple of callables), or ``None``.

    Notes:
      This function does **not** validate the signature of the resulting
      callables; the downstream components are expected to call them with
      the appropriate arguments.
    """
    if spec is None:
        return None

    # Dotted path string → import the attribute/function/class.
    if isinstance(spec, str):
        return _resolve_dotted(spec)

    # Factory spec or container → recursively build objects.
    if isinstance(spec, Mapping) or isinstance(spec, (list, tuple)):
        return _materialize_factories(spec)

    # Already a callable/object; leave as-is.
    return spec

def _looks_like_ref(s: str) -> bool:
    """Heuristic: return True if string *probably* denotes an importable ref.

    We treat a string as a reference only if it:
      * contains ':' (e.g., 'pkg.mod:attr' or '/path/file.py:attr'), OR
      * ends with '.py:Something', OR
      * contains a dot AND is not a trivial token (e.g., not 'cpu', 'float32').

    Args:
      s: Candidate string.

    Returns:
      True if `s` should be resolved via import, False otherwise.
    """
    if ":" in s:
        return True
    if s.endswith(".py"):
        # Without ':attr' it's not actionable; keep it literal.
        return False
    if "." in s:
        # Filter out common non-reference tokens like 'float32', 'FIRE', 'cpu'.
        # Adjust this set as needed for your domain.
        trivial = {"cpu", "cuda", "float16", "float32", "float64", "FIRE"}
        if s in trivial:
            return False
        return True
    return False


def _resolve_dotted(name: str) -> Any:
    """Import and return an attribute from a dotted reference or a .py file path.

    Supported forms:
      - "package.module:attr"  (preferred)
      - "package.module.attr"
      - "/abs/or/rel/path/file.py:attr"

    When a filesystem path is used, the module is loaded under a synthetic
    unique name so different files can be imported in the same process.

    Args:
      name: Reference string (module + attribute).

    Returns:
      Imported Python object (function, class, variable, etc.).

    Raises:
      TypeError: If `name` is not a string.
      ValueError: If the reference is malformed.
      FileNotFoundError: If a file path does not exist.
      ImportError: If the module cannot be loaded.
      AttributeError: If the attribute is missing.
    """
    if not isinstance(name, str):
        raise TypeError(f"Expected dotted string, got {type(name)!r}")

    # 1) Parse "module:attr" first; fallback a "module.attr"
    if ":" in name:
        module_part, attr = name.split(":", 1)
    else:
        parts = name.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(
                "Malformed reference "
                f"{name!r}. Use 'pkg.mod:attr', 'pkg.mod.attr', or '/path/to/file.py:attr'."
            )
        module_part, attr = parts



    # 2) Importar módulo (soporta path a .py)
    is_fs_path = module_part.endswith(".py") or os.path.sep in module_part
    if is_fs_path:
        path = os.path.abspath(module_part)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        mod_name = f"_ezga_dyn_{abs(hash(path))}"
        spec = spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from path: {path}")
        module: ModuleType = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    else:
        module = import_module(module_part)

    # 3) **Soportar atributos anidados**: p.ej. "ConstraintGenerator.greater_than"
    obj: Any = module
    for token in attr.split("."):
        obj = getattr(obj, token)

    return obj

def _resolve_many(seq: Optional[Iterable[Any]]) -> list[Any]:
    """Resolve a heterogeneous list, importing strings when needed.

    Strings are treated as dotted import paths and resolved; non-strings are
    returned unchanged.

    Args:
      seq: Iterable of items (may be None).

    Returns:
      List with string items resolved to live Python objects.
    """
    if not seq:
        return []
    out: list[Any] = []
    for item in seq:
        out.append(_resolve_dotted(item) if isinstance(item, str) and _looks_like_ref(item) else item)
    return out


# --------------------------------------------------------------------------- #
# Calculator factory materialization
# --------------------------------------------------------------------------- #

def _is_factory_spec(obj: Any) -> bool:
    """Return True if obj looks like {'factory': 'mod:attr', ...}."""
    return isinstance(obj, Mapping) and "factory" in obj


def _is_calc_shorthand(obj: Any) -> bool:
    """Return True if obj looks like {'type': 'ase', 'class': 'mod:Class', ...}."""
    return isinstance(obj, Mapping) and ("type" in obj and "class" in obj)


def _normalize_calc_shorthand(obj: Mapping[str, Any]) -> Mapping[str, Any]:
    """Convert calculator shorthand into explicit adapter factory spec.

    Shorthand:
      {'type': 'ase', 'class': 'ase.calculators.lj:LennardJones', 'kwargs': {...}, ...}

    Normalized:
      {'factory': 'ezga.simulator.ase_calculator:ase_calculator',
       'kwargs': {'calculator': {'factory': 'ase.calculators.lj:LennardJones',
                                 'kwargs': {...}},
                  ...adapter kwargs...}}

    Args:
      obj: Mapping with keys 'type', 'class', optional 'kwargs', and any
           adapter kwargs (e.g., fmax, T, device, ...).

    Returns:
      A normalized factory spec mapping.

    Raises:
      ValueError: Unknown shorthand type.
    """
    ctype = str(obj.get("type", "")).lower()
    klass = obj["class"]                 # dotted path 'module:Class'
    inner = dict(obj.get("kwargs", {}))  # kwargs for the inner ASE class
    adapter_kwargs = {k: v for k, v in obj.items() if k not in ("type", "class", "kwargs")}

    if ctype == "ase":
        return {
            "factory": "ezga.simulator.ase_calculator:ase_calculator",
            "kwargs": {
                "calculator": {"factory": klass, "kwargs": inner},
                **adapter_kwargs,
            },
        }
    raise ValueError(f"Unknown calculator shorthand type={ctype!r}")


def _materialize_factories(tree: Any) -> Any:
    """Recursively build objects from factory specs and dotted strings.

    Accepts:
      - Dotted strings (only if `_looks_like_ref` is True) → imported objects.
      - {'factory': 'mod:attr', 'args': [...], 'kwargs': {...}} → factory(*args, **kwargs).
      - Calculator shorthand (see `_normalize_calc_shorthand`).
      - Nested dicts/lists/tuples (processed recursively).

    Returns:
      The same structure with live objects instead of specs.
    """
    # 1) Turn calculator shorthand into explicit factory spec
    if _is_calc_shorthand(tree):
        tree = _normalize_calc_shorthand(tree)

    # 2) Factory spec → call it
    if _is_factory_spec(tree):
        factory = _resolve_dotted(tree["factory"])
        args = tree.get("args") or []
        kwargs = tree.get("kwargs") or {}
        args = _materialize_factories(args)
        kwargs = _materialize_factories(kwargs)

        if isinstance(args, (list, tuple)):
            if isinstance(kwargs, Mapping):
                return factory(*args, **kwargs)
            return factory(*args, kwargs)

        if isinstance(kwargs, Mapping):
            return factory(**kwargs)
        return factory(kwargs)

    # 3) Dotted string → import (only if it "looks like" a ref)
    if isinstance(tree, str) and _looks_like_ref(tree):
        return _resolve_dotted(tree)

    # 4) Containers → recurse
    if isinstance(tree, Mapping):
        return {k: _materialize_factories(v) for k, v in tree.items()}
    if isinstance(tree, list):
        return [_materialize_factories(v) for v in tree]
    if isinstance(tree, tuple):
        return tuple(_materialize_factories(v) for v in tree)

    # 5) Primitive or already-live object
    return tree


# --------------------------------------------------------------------------- #
# Post-processing of GAConfig
# --------------------------------------------------------------------------- #
def _postprocess(cfg: GAConfig) -> GAConfig:
    """Resolve dotted strings and factory specs into live objects on GAConfig.

    This step is applied *after* Pydantic validation. It converts user-friendly
    YAML entries into actual Python callables/objects used at runtime.

    Transforms
    ----------
    - ``cfg.evaluator.features_funcs``:
        * str → imported callable
        * dict/list → materialized factories/containers
        * None/other → left as-is
    - ``cfg.evaluator.objectives_funcs``:
        * same rules as above
    - ``cfg.mutation_funcs`` / ``cfg.crossover_funcs``:
        * list[str|object] → resolve strings into objects (others untouched)
    - ``cfg.generative_model``:
        * str → imported object
    - ``cfg.simulator.calculator``:
        * str → imported callable
        * dict ``{"factory": ..., "args": ..., "kwargs": ...}`` → materialized
        * shorthand dict (e.g., ASE) → normalized then materialized
        * list/tuple → each element materialized (multi-calculator)

    Args:
      cfg: A validated :class:`GAConfig` instance.

    Returns:
      The same :class:`GAConfig` instance with selected fields replaced by
      live Python objects.

    Raises:
      Any import or attribute errors originating from the resolver functions
      (e.g., :func:`_resolve_dotted`) will propagate to the caller. This is
      intentional to surface misconfigurations early.
    """
    ev = cfg.evaluator

    # Features: str | factory-spec | list/tuple → live callable(s)
    ev.features_funcs = _resolve_callable_like(ev.features_funcs)

    # Objectives: str | factory-spec | list/tuple → live callable(s)
    ev.objectives_funcs = _resolve_callable_like(ev.objectives_funcs)

    # Mutation / crossover lists: resolve only string elements.
    cfg.mutation_funcs = _resolve_callable_like(cfg.mutation_funcs)
    cfg.crossover_funcs = _resolve_callable_like(cfg.crossover_funcs)
    # Optional generative model: string → object.
    if isinstance(cfg.generative_model, str):
        cfg.generative_model = _resolve_dotted(cfg.generative_model)

    # Simulator calculator: may be a dotted string, a factory spec (possibly nested),
    # a shorthand dict, or a sequence of any of those.
    if getattr(cfg, "simulator", None) is not None:
        cfg.simulator.calculator = _materialize_factories(cfg.simulator.calculator)

    if getattr(cfg, "population", None) is not None:
        if getattr(cfg.population, "constraints", None):
            cfg.population.constraints = _materialize_factories(cfg.population.constraints)

    return cfg


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def load_config_yaml(path: Union[str, Path]) -> GAConfig:
    """Load a YAML file and return a validated :class:`GAConfig`.

    The YAML is parsed with a safe loader, validated against the Pydantic
    schema, and then post-processed to resolve any dotted import strings and
    factory specs.

    Args:
      path: Path to the YAML configuration file.

    Returns:
      Fully validated :class:`GAConfig`.

    Raises:
      FileNotFoundError: If the file does not exist.
      SystemExit: If validation fails; message is formatted for CLI use.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")

    data: dict[str, Any] = _YAML_SAFE.load(p.read_text(encoding="utf-8")) or {}

    try:
        cfg = GAConfig(**data)
    except ValidationError as exc:
        # Pretty, one-shot message for CLI (keeps stack traces out of user view)
        raise SystemExit(f"[Config validation error]\n{exc}") from exc

    return _postprocess(cfg)


def dump_config_yaml(cfg: GAConfig, path: Union[str, Path]) -> None:
    """Write a :class:`GAConfig` to a YAML file.

    Convenient for emitting editable templates or checkpoints.

    Args:
      cfg: Configuration object to serialize.
      path: Output YAML path. Parent directories are created if missing.
    """
    #p = Path(path)
    #p.parent.mkdir(parents=True, exist_ok=True)
    #with p.open("w", encoding="utf-8") as fh:
    #    _YAML_RT.dump(cfg.model_dump(), fh)


    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    data = cfg.model_dump(mode="json", by_alias=True, exclude_none=False)

    hise_block = data.get("hise")
    if isinstance(hise_block, dict) and hise_block.get("supercells"):
        data["hise"]["supercells"] = [list(sc) for sc in hise_block["supercells"]]

    with p.open("w", encoding="utf-8") as fh:
        _YAML_RT.dump(data, fh)







