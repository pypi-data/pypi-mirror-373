# ezga/hise/manager.py
# SPDX-License-Identifier: GPL-3.0-only
"""
HiSE (Hierarchical Supercell Escalation) manager.

Lift methods (hise.lift_method):
  - "tile":            Use Partition + AtomPositionManager.generate_supercell(repeat=...).
  - "best_compatible": Pick the largest previous supercell (by volume) that divides the
                       target coord-wise, then lift via Partition as above.
  - "ase":             Fallback method using ASE Atoms.repeat (no Partition required).

Both "tile" and "best_compatible" REQUIRE `sage_lib.partition.Partition`.
"""

from __future__ import annotations
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path
import logging
import numpy as np

from ase import Atoms
from ase.io import read as ase_read, write as ase_write

from sage_lib.partition.Partition import Partition  # <-- REQUIRED
from ezga.core.config import GAConfig, HiSEParams
from ezga.factory import build_default_engine
from ezga.io.config_loader import _materialize_factories  

logger = logging.getLogger(__name__)


def _materialize_stage_constraints_if_any(stage_cfg: GAConfig) -> None:
    """Normalize and materialize ``population.constraints`` into callables.

    This helper fixes two common situations that arise when constraints are
    provided via YAML overrides on a per-stage basis:

    1) **Single dict instead of list**  
       Some YAMLs assign one factory-spec (a dict) to ``population.constraints``
       for a given stage (e.g., via an overrides array). The population expects a
       *list* of callables, so we wrap a single dict into a list.

    2) **Unmaterialized factory-specs**  
       Constraints may appear as factory-specs (e.g.,
       ``{"factory": "pkg.mod:make_constraint", "args": [...], ...}``) or dotted
       references. We convert them into *live Python callables* using the same
       materializer employed by the config loader.

    If a mapping ``population.constraint_name_map`` is present (e.g., ``{"C": 0,
    "H": 1}``), we register it with ``ConstraintGenerator.set_name_mapping`` so
    any constraint that accepts *string* feature keys (like ``"C"``/``"H"``) can
    resolve them to integer indices at runtime.

    The function mutates ``stage_cfg`` in place and is safe to call multiple times.

    Args:
      stage_cfg: Stage-local :class:`GAConfig` that will be mutated in place.

    Returns:
      None

    Notes:
      - Input shapes accepted:
        * ``None`` → no-op
        * a single dict factory-spec → wrapped as a list, then materialized
        * a list/tuple of factory-specs or callables → materialized element-wise
        * already-live callables → left as-is
      - This uses ``_materialize_factories`` from the loader to keep behavior
        consistent with top-level YAML parsing.
    """
    pop = getattr(stage_cfg, "population", None)
    if pop is None:
        return

    cons = getattr(pop, "constraints", None)
    if cons is None:
        return

    # 1) Tolerate a single dict by wrapping it as a list.
    if isinstance(cons, dict):
        cons = [cons]
    elif isinstance(cons, tuple):
        cons = list(cons)

    # 2) Materialize a list of factory-specs/dotted refs into live callables.
    if isinstance(cons, list):
        try:
            pop.constraints = _materialize_factories(cons)
        except Exception as e:
            logger.warning("[HiSE] Failed to materialize population.constraints: %s", e)
            # Keep the original value so downstream code can decide how to react.
            pop.constraints = cons

    # Optional: register a name→index mapping for string feature keys ("C", "H", ...).
    cmap = getattr(pop, "constraint_name_map", None)
    if cmap:
        try:
            # Local import to avoid import-time cycles and heavy modules at import.
            from ezga.DoE.DoE import ConstraintGenerator
            ConstraintGenerator.set_name_mapping(dict(cmap))
        except Exception as e:
            logger.warning("[HiSE] Could not register constraint_name_map on ConstraintGenerator: %s", e)

# ---------------------------------------------------------------------
# Path & discovery helpers
# ---------------------------------------------------------------------
def _stage_dir(root: Path, sc: Tuple[int, int, int], pattern: str) -> Path:
    """Return absolute stage directory path."""
    a, b, c = map(int, sc)
    return (root / pattern.format(a=a, b=b, c=c)).resolve()


def _detect_stage_inputs(stage_root: Path, mode: str) -> List[Path]:
    """Return input XYZ files according to `mode` for a given stage directory."""
    if mode == "final_dataset":
        p = stage_root / "config.xyz"
        return [p] if p.exists() else []
    gen_root = stage_root / "generation"
    return sorted(gen_root.glob("*/config.xyz")) if gen_root.exists() else []


def _is_stage_complete(stage_root: Path) -> bool:
    """Heuristic: a stage is complete if stage_root/config.xyz exists."""
    return (stage_root / "config.xyz").exists()


def _ratio_or_raise(next_sc: Tuple[int, int, int], prev_sc: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Compute integer replication ratio next/prev; raise if not an exact divisor."""
    r: List[int] = []
    for n, p in zip(next_sc, prev_sc):
        if p == 0 or (n % p) != 0:
            raise ValueError(f"Target supercell {next_sc} is not an integer multiple of {prev_sc}")
        r.append(n // p)
    return tuple(r)  # type: ignore[return-value]


def _best_compatible_source(
    target: Tuple[int, int, int],
    candidates: List[Tuple[int, int, int]],
) -> Optional[Tuple[int, int, int]]:
    """Pick volume-maximizing candidate that divides `target` coord-wise."""
    best: Optional[Tuple[int, int, int]] = None
    best_vol = -1
    ta, tb, tc = target
    for ca, cb, cc in candidates:
        if (ta % ca == 0) and (tb % cb == 0) and (tc % cc == 0):
            vol = ca * cb * cc
            if vol > best_vol:
                best = (ca, cb, cc)
                best_vol = vol
    return best

def _is_commensurate(target: Tuple[int, int, int], prev: Tuple[int, int, int]) -> bool:
    """Return True if each target coord is an integer multiple of prev coord."""
    ta, tb, tc = target
    pa, pb, pc = prev
    return (pa != 0 and tb % pb == 0 and tc % pc == 0 and ta % pa == 0)

def _compute_stage_shared_dir(base_shared: Path, out_root: Path, stage_root: Path) -> Path:
    """Make a stage-shared mailbox path (common to all agents of the stage)."""
    try:
        rel = stage_root.relative_to(out_root)
    except Exception:
        rel = Path(stage_root.name)
    return (base_shared / rel).resolve()

# ---------------------------------------------------------------------
# Lift implementations (Partition / ASE)
# ---------------------------------------------------------------------
def _lift_inputs_to_partition(
    inputs: List[Path],
    ratio: Tuple[int, int, int],
    reseed_fraction: float,
    rng: np.random.Generator,
) -> Optional[Partition]:
    """Build a Partition from inputs and apply supercell tiling via AtomPositionManager.

    Args:
      inputs: XYZ files to ingest (each may contain multiple frames).
      ratio: Integer (ra, rb, rc) to pass to generate_supercell(repeat=...).
      reseed_fraction: Probability to keep a container (Bernoulli downsampling).
      rng: Random generator.

    Returns:
      A `Partition` with tiled containers, or `None` if nothing could be read.
    """
    part = Partition()
    n_reads = 0
    for p in inputs:
        try:
            part.read_files(file_location=str(p), source="xyz", verbose=False)
            n_reads += 1
        except Exception as e:
            logger.warning(f"[HiSE] Partition could not read {p}: {e}")

    if n_reads == 0 or not getattr(part, "containers", None):
        logger.warning("[HiSE] Partition read yielded no containers.")
        return None

    # Downsample if requested
    if reseed_fraction < 1.0 - 1e-12:
        n = len(part.size)
        if reseed_fraction >= 1.0 - 1e-12:
            keep_mask = np.ones(n, dtype=bool)
        elif reseed_fraction <= 1e-12:
            keep_mask = np.zeros(n, dtype=bool)
        else:
            keep_mask = rng.random(n) <= reseed_fraction

        # Prefer library mask API if available
        if hasattr(part, "apply_filter_mask"):
            try:
                part.apply_filter_mask(keep_mask)
            except Exception as e:
                # Fallback: manual filter
                part.containers = [c for c, k in zip(list(part.containers), keep_mask) if k]
        else:
            part.containers = [c for c, k in zip(list(part.containers), keep_mask) if k]

    # Apply supercell replication
    for container in list(part.containers):
        try:
            container.AtomPositionManager.generate_supercell(
                repeat=tuple(int(x) for x in ratio)
            )
        except Exception as e:
            logger.warning(f"[HiSE] generate_supercell failed on a container: {e}")

    return part.containers


def _export_partition_to_xyz(container: list, out_xyz: Path) -> int:
    """Export a Partition to a single XYZ file; returns frames written."""
    out_xyz.parent.mkdir(parents=True, exist_ok=True)

    try:
        part = Partition()
        part.add(container)
        part.export_files(
            file_location=str(out_xyz),
            source="xyz",
            label="enumerate",
            verbose=False,
        )
        return part.size

    except Exception as e:
        logger.warning(f"[HiSE] Partition export to XYZ failed: {e}")
        return 0

def _write_lifted_xyz_ase(
    inputs: List[Path],
    out_xyz: Path,
    repeat: Tuple[int, int, int],
    reseed_fraction: float,
    rng: np.random.Generator,
) -> int:
    """ASE-based tiling of frames into a single XYZ (optional fallback)."""
    frames_out = 0
    out_xyz.parent.mkdir(parents=True, exist_ok=True)
    if out_xyz.exists():
        out_xyz.unlink()

    keep_all = (reseed_fraction >= 1.0 - 1e-12)
    for f in inputs:
        try:
            frames = ase_read(str(f), index=":")
        except Exception as e:
            logger.warning(f"[HiSE] Skipping unreadable file {f}: {e}")
            continue
        frames = frames if isinstance(frames, list) else [frames]
        for at in frames:
            if not isinstance(at, Atoms):
                continue
            if not keep_all and rng.random() > reseed_fraction:
                continue
            tiled = at.repeat(tuple(int(x) for x in repeat))
            ase_write(str(out_xyz), tiled, format="xyz", append=True)
            frames_out += 1
    return frames_out


def _lift_inputs_to_xyz(
    method: str,
    inputs: List[Path],
    out_xyz: Path,
    ratio: Tuple[int, int, int],
    reseed_fraction: float,
    rng: np.random.Generator,
) -> tuple[int, Optional[Partition]]:
    """Dispatch lifting to the requested method.

    Returns:
      (frames_written, partition_if_available)
    """
    if method in ("tile", "best_compatible"):
        container = _lift_inputs_to_partition(inputs, ratio, reseed_fraction, rng)
        if container is None:
            return 0, None
        written = _export_partition_to_xyz(container, out_xyz)
        return written, container

    if method == "ase":
        written = _write_lifted_xyz_ase(inputs, out_xyz, ratio, reseed_fraction, rng)
        return written, None

    raise NotImplementedError(f"hise.lift_method='{method}' is not implemented.")


# ---------------------------------------------------------------------
# Config utilities
# ---------------------------------------------------------------------
def _deep_set(cfg: GAConfig, dotted_key: str, value: Any) -> None:
    """Set nested value on a GAConfig using dotted-path keys."""
    obj: Any = cfg
    parts = dotted_key.split(".")
    for k in parts[:-1]:
        obj = getattr(obj, k)
    setattr(obj, parts[-1], value)


def _apply_stage_overrides(stage_cfg: GAConfig, overrides: Dict[str, List[Any]] | None, idx: int) -> None:
    """Apply per-stage overrides (dot path → list of values), if present."""
    if not overrides:
        return
    for dotted_key, values in overrides.items():
        if idx < len(values):
            _deep_set(stage_cfg, dotted_key, values[idx])


def _adjust_stage_scoped_paths(stage_cfg: GAConfig, out_root: Path, stage_root: Path) -> None:
    """Set output_path and agentic.shared_dir for the given stage.

    The agentic.shared_dir becomes a *stage-shared* mailbox:
      base_shared / stage_root.relative_to(out_root)
    """
    stage_cfg.output_path = str(stage_root)
    try:
        if stage_cfg.agentic and stage_cfg.agentic.shared_dir:
            base_shared = Path(stage_cfg.agentic.shared_dir)
            stage_shared = _compute_stage_shared_dir(base_shared, out_root, stage_root)
            stage_shared.mkdir(parents=True, exist_ok=True)
            stage_cfg.agentic.shared_dir = str(stage_shared)
    except Exception:
        pass


# ---------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------
def run_hise(cfg: GAConfig) -> Dict[Tuple[int, int, int], Path]:
    """Execute a HiSE (coarse-to-fine) campaign.

    For each supercell stage:
      * Build an isolated stage directory.
      * Optionally **replace** the base input by lifting (tiling) previous results
        according to `hise.lift_method` and `hise.input_from`.
      * Apply per-stage overrides.
      * Scope agentic.shared_dir to a stage-shared mailbox directory.
      * Skip completed stages if `hise.restart=True`.
      * Run the GA.

    Lift methods:
      - "tile":            Partition lifting by generate_supercell (immediate previous).
      - "best_compatible": Partition lifting from the largest prior stage that divides target.
      - "ase":             ASE fallback (Atoms.repeat).

    Returns:
      Mapping from supercell tuple → stage directory Path.
    """
    assert cfg.hise and cfg.hise.supercells, "HiSE requires a non-empty list of supercells."
    hise: HiSEParams = cfg.hise

    supercells = [tuple(map(int, sc)) for sc in hise.supercells]
    out_root = Path(cfg.output_path).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    stage_dirs: Dict[Tuple[int, int, int], Path] = {}
    done_sc: List[Tuple[int, int, int]] = []   # stages already completed (for best_compatible)
    rng = np.random.default_rng(73)

    for idx, sc in enumerate(supercells):
        stage_root = _stage_dir(out_root, sc, hise.stage_dir_pattern)
        stage_dirs[sc] = stage_root
        stage_root.mkdir(parents=True, exist_ok=True)

        # Build a deep-copied stage-local config
        stage_cfg: GAConfig = cfg.model_copy(deep=True)
        _apply_stage_overrides(stage_cfg, hise.overrides, idx)
        _materialize_stage_constraints_if_any(stage_cfg)

        if "max_generations" not in (hise.overrides or {}):
            stage_cfg.max_generations = cfg.max_generations
        _adjust_stage_scoped_paths(stage_cfg, out_root, stage_root)

        # Restart/skip if the stage sentinel exists
        if hise.restart and _is_stage_complete(stage_root):
            logger.info(f"[HiSE] Skipping completed stage {sc} at {stage_root}")
            done_sc.append(sc)
            continue

        # Replace base input from previous results for idx>0
        pre_container: Optional[list] = None
        if idx > 0:
            source_sc: Optional[Tuple[int, int, int]] = None

            if hise.lift_method in ("tile", "ase"):
                # Prefer the immediately previous (or last completed) stage,
                # but only if it is commensurate with the target.
                preferred = done_sc[-1] if done_sc else supercells[idx - 1]
                if preferred and _is_commensurate(sc, preferred):
                    source_sc = preferred
                else:
                    # Fallback: pick the largest commensurate prior stage (if any).
                    bc = _best_compatible_source(sc, done_sc)
                    if bc is not None:
                        if preferred and preferred != bc:
                            logger.info(
                                "[HiSE] Preferred source %s not commensurate with target %s; "
                                "falling back to best-compatible %s.",
                                preferred, sc, bc
                            )
                        source_sc = bc
                    else:
                        logger.warning(
                            "[HiSE] No commensurate previous stage found for target %s; "
                            "keeping original dataset for this stage.", sc
                        )

            elif hise.lift_method == "best_compatible":
                source_sc = _best_compatible_source(sc, done_sc)
                if source_sc is None:
                    logger.warning(
                        "[HiSE] No compatible previous stage found for target %s; "
                        "proceeding without input replacement.", sc
                    )
            else:
                raise NotImplementedError(f"hise.lift_method='{hise.lift_method}' is not implemented.")

            if source_sc is not None:
                src_root = _stage_dir(out_root, source_sc, hise.stage_dir_pattern)
                src_inputs = _detect_stage_inputs(src_root, hise.input_from)
                if not src_inputs:
                    logger.warning(f"[HiSE] No inputs found in {src_root} (mode={hise.input_from}); "
                                   f"keeping original dataset_path for stage {sc}.")
                else:
                    # Safety: this should never raise now, but guard anyway.
                    try:
                        ratio = _ratio_or_raise(sc, source_sc)
                    except ValueError:
                        logger.warning(
                            "[HiSE] Source stage %s unexpectedly not commensurate with target %s; "
                            "skipping input replacement.", source_sc, sc
                        )
                        ratio = None
                    out_xyz = stage_root / "input_lifted"

                    if ratio is not None:
                        written, pre_container = _lift_inputs_to_xyz(
                            method=hise.lift_method,
                            inputs=src_inputs,
                            out_xyz=out_xyz,
                            ratio=ratio,
                            reseed_fraction=float(hise.reseed_fraction),
                            rng=rng,
                        )
                    else:
                        written, pre_container = 0, None

                    # Prefer direct preloading if engine supports it; otherwise use the file.
                    if written > 0:
                        stage_cfg.population.dataset_path = str(Path(out_xyz) / "config.xyz")
                    else:
                        stage_cfg.population.dataset_path = None

        # Run GA for this stage
        logger.info(f"[HiSE] Stage {idx+1}/{len(supercells)} — SC={sc} → {stage_root}")
        engine = build_default_engine(stage_cfg)

        # Optional: try to push the preloaded Partition directly (no double I/O) if supported.
        if pre_container is not None:
            try:
                if hasattr(engine, "population") and hasattr(engine.population, "set_population_from_partition"):
                    engine.population.set_population_from_partition(pre_container)  # hypothetical public API
                    # Ensure we don't also re-read the file:
                    engine.population.clear_pending_dataset_path = getattr(engine.population, "clear_pending_dataset_path", lambda: None)
                    engine.population.clear_pending_dataset_path()
                # else: keep dataset_path set above (one read, not two).
            except Exception as e:
                logger.warning(f"[HiSE] Direct preload from Partition not available/failed: {e}. "
                               f"Falling back to dataset_path.")

        _ = engine.run()

        done_sc.append(sc)

    return stage_dirs