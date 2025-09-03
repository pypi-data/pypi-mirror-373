# ezga/io/snapshot_recorder.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional, Mapping
import json
import numpy as np

@dataclass(frozen=True)
class SnapshotSchema:
    schema_version: str
    generation: int
    temperature: float

    # population
    dataset_size: int
    current_valid_size: int
    selected_indices: list[int]

    # eval
    features_shape: Optional[tuple[int, ...]]
    objectives_shape: Optional[tuple[int, ...]]

    # convergence
    convergence_results: Mapping[str, Any]
    stall_count_objective: int
    information_driven: bool
    stall_count_information: Optional[int]

    # variation diagnostics (optional; may be None)
    variation_stats: Mapping[str, Any]

    # timers
    timers: Mapping[str, float]


class _NpEncoder(json.JSONEncoder):
    """NumPy-safe JSON encoder."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):  return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.ndarray,)):  return obj.tolist()
        return super().default(obj)


class GenerationSnapshotWriter:
    """Stateless utility to persist per-generation snapshots."""

    @staticmethod
    def build_snapshot(
        *,
        population,
        convergence,
        variation,
        ctx,
    ) -> SnapshotSchema:
        # --- context / temperature ---
        gen = int(getattr(ctx, "generation", -1))
        temperature = float(getattr(ctx, "temperature", np.nan))

        # --- eval shapes ---
        features = ctx.get_features() if hasattr(ctx, "get_features") else None
        objectives = ctx.get_objectives() if hasattr(ctx, "get_objectives") else None
        feat_shape = tuple(features.shape) if features is not None else None
        obj_shape  = tuple(objectives.shape) if objectives is not None else None

        # --- selection indices ---
        selected = getattr(ctx, "selection", []) or []
        try:
            selected = list(np.asarray(selected, dtype=int))
        except Exception:
            selected = []

        # --- population sizes (defensive) ---
        def psize(name: str) -> int:
            try:
                return int(population.size(name))
            except Exception:
                return 0

        dataset_sz       = psize("dataset")
        current_valid_sz = psize("current_valid")

        # --- convergence block (defensive) ---
        conv_results = {}
        try:
            conv_results = {
                "improvement_found": bool(convergence.improvement_found()),
                "stagnation":        int(convergence.get_stagnation()),
                "is_converge":       bool(convergence.is_converge()),
                "stall_threshold":   int(getattr(convergence, "_stall_threshold", -1)),
            }
        except Exception:
            pass

        info_driven = bool(getattr(convergence, "_information_driven", False))
        stall_info  = getattr(convergence, "_no_improvement_count_information", None)
        stall_obj   = int(getattr(convergence, "_no_improvement_count", 0))

        # --- variation diagnostics (optional attributes) ---
        var = variation
        def getv(name: str, default=None):
            return getattr(var, name, default)
        variation_stats = {
            "mutation_rate_history":         getv("mutation_rate_array"),
            "mutation_probabilities":        getv("_mutation_probabilities"),
            "mutation_attempt_counts":       getv("_mutation_attempt_counts"),
            "mutation_success_counts":       getv("_mutation_success_counts"),
            "mutation_fails_counts":         getv("_mutation_fails_counts"),
            "mutation_unsuccess_counts":     getv("_mutation_unsuccess_counts"),
            "mutation_hashcolition_counts":  getv("_mutation_hashcolition_counts"),
            "mutation_outofdoe_counts":      getv("_mutation_outofdoe_counts"),
            "crossover_attempt_counts":      getv("_crossover_attempt_counts"),
            "crossover_success_counts":      getv("_crossover_success_counts"),
            "crossover_fails_counts":        getv("_crossover_fails_counts"),
            "crossover_unsuccess_counts":    getv("_crossover_unsuccess_counts"),
            "crossover_hashcolition_counts": getv("_crossover_hashcolition_counts"),
            "crossover_outofdoe_counts":     getv("_crossover_outofdoe_counts"),
        }

        # --- timers from ctx (defensive) ---
        timers = dict(getattr(ctx, "timers", {}))

        return SnapshotSchema(
            schema_version="1.0",
            generation=gen,
            temperature=temperature,
            dataset_size=dataset_sz,
            current_valid_size=current_valid_sz,
            selected_indices=selected,
            features_shape=feat_shape,
            objectives_shape=obj_shape,
            convergence_results=conv_results,
            stall_count_objective=stall_obj,
            information_driven=info_driven,
            stall_count_information=stall_info,
            variation_stats=variation_stats,
            timers=timers,
        )

    @staticmethod
    def save_generation(
        *,
        population,
        convergence,
        variation,
        ctx,
        output_dir: str | Path,
        tag: str | None = None,
        filename: str | None = None,
    ) -> Path:
        """
        Build and persist a generation snapshot as JSON.

        Parameters
        ----------
        population, convergence, variation, ctx : objects
            Runtime objects providing the public attributes used above.
        output_dir : str | Path
            Destination directory; created if missing.
        tag : str | None
            Optional suffix to distinguish phases (e.g. 'final', 'post-sim').
        filename : str | None
            Optional explicit filename; default uses generation index.

        Returns
        -------
        Path
            Path to the written JSON file.
        """
        snapshot = GenerationSnapshotWriter.build_snapshot(
            population=population, convergence=convergence, variation=variation, ctx=ctx
        )

        out = Path(output_dir) / 'logger'
        out.mkdir(parents=True, exist_ok=True)

        if filename is None:
            base = f"gen_{snapshot.generation:06d}"
            if tag:
                base = f"{base}_{tag}"
            filename = f"{base}.json"

        fpath = out / filename
        with fpath.open("w", encoding="utf-8") as fh:
            json.dump(asdict(snapshot), fh, cls=_NpEncoder, indent=2, sort_keys=True)
        return fpath
