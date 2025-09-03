# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

from typer import Typer, Option
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from typing import Any, Tuple, List 

from ezga.io.config_loader import load_config_yaml, dump_config_yaml
from ezga.cli.runners import run_standard_cli, run_hise_cli
from ezga.core.config import GAConfig
from ezga.factory import build_default_engine

app = Typer(help="Launch new EZGA runs")
console = Console()

def main():
    app()

@app.command("once")
def once(
    config: Path = Option(..., "--config", "-c", exists=True, readable=True, help="YAML config file.")
):
    """
    Entry point for running a single GA job from the CLI.

    This function acts as a thin dispatcher:
    it loads the YAML configuration, detects if an HiSE
    (Hierarchical Supercell Exploration) block is present,
    and routes the execution to the appropriate runner.

    Parameters
    ----------
    config : str
        Path to the YAML configuration file.

    Returns
    -------
    int
        Exit code: 0 if run completed successfully, non-zero otherwise.
    """
    # Load the configuration file as a validated GAConfig object
    cfg: GAConfig = load_config_yaml(config)
    _print_summary(cfg)

    # If the configuration contains HiSE settings, delegate to HiSE runner
    if getattr(cfg, "hise", None) and cfg.hise.supercells:
        return run_hise_cli(cfg)           # <-- Delegates to HiSE orchestration

    # Otherwise, run a standard GA job
    return run_standard_cli(cfg)


@app.command("validate")
def validate(
    config: Path = Option(..., "--config", "-c", exists=True, readable=True),
    strict: bool = Option(False, "--strict", help="Also build the engine to validate wiring."),
) -> None:

    """Validate a YAML file against the GAConfig schema and summarize it.

    Args:
      config: Path to a YAML file describing the GA run.

    Raises:
      SystemExit: If validation fails (formatted by the loader).
    """
    cfg: GAConfig = load_config_yaml(config)
    _print_summary(cfg)
    if strict:
        # Build all components (no physics execution)
        _ = run_validation_cli(cfg)
    console.print("[bold green]Configuration valid.[/]")

# ---------------------------------------------------------------------
# YAML HELPERS PRINT
# ---------------------------------------------------------------------
def _callable_label(obj: Any) -> str:
    """Return a human-friendly label for a callable or factory-built object."""
    if obj is None:
        return "None"
    if isinstance(obj, (list, tuple)):
        return ", ".join(_callable_label(x) for x in obj)
    if callable(obj):
        mod = getattr(obj, "__module__", "")
        name = getattr(obj, "__qualname__", getattr(obj, "__name__", str(obj)))
        return f"{mod}:{name}"
    return str(obj)

def _fmt_bool(b: bool) -> Text:
    """Pretty-print booleans with color."""
    return Text("true", style="green") if b else Text("false", style="red")

def _fmt_supercells(scs: list[tuple[int,int,int]] | None) -> str:
    """Format supercells as 'a×b×c, ...' or '—' if empty."""
    if not scs:
        return "—"
    return ", ".join(f"{a}×{b}×{c}" for a,b,c in scs)

def _fmt_constraints(constraints: Any) -> str:
    """Summarize population.constraints (callables or factory-spec dicts)."""
    if not constraints:
        return "—"
    items = constraints if isinstance(constraints, (list, tuple)) else [constraints]
    lines = []
    for i, c in enumerate(items, 1):
        if callable(c):
            lines.append(f"{i}. {_callable_label(c)}")
        elif isinstance(c, dict):
            fac = c.get("factory", "<factory>")
            args = c.get("args", [])
            kwargs = c.get("kwargs", {})
            meta = []
            if args: meta.append(f"args={len(args)}")
            if kwargs: meta.append(f"kwargs={len(kwargs)}")
            lines.append(f"{i}. {fac}" + (f" ({', '.join(meta)})" if meta else ""))
        else:
            lines.append(f"{i}. {type(c).__name__}")
        if i >= 6 and len(items) > 6:
            lines.append(f"… (+{len(items)-6} more)")
            break
    return "\n".join(lines)

def _table_pairs(title: str, items: dict[str, Any]) -> Table:
    """Build a compact two-column key/value table."""
    t = Table(title=title, box=box.SIMPLE, show_header=False, pad_edge=False)
    t.add_column(justify="right", style="bold dim")
    t.add_column()
    for k, v in items.items():
        t.add_row(k, v if isinstance(v, Text) else str(v))
    return t

def _print_summary(cfg: GAConfig) -> None:
    """Pretty-print a compact, multi-panel configuration summary for the CLI."""
    t_ga = _table_pairs("GA", {
        "initial_generation": cfg.initial_generation,
        "max_generations":   cfg.max_generations,
        "foreigners":        cfg.foreigners,
        "output_path":       cfg.output_path,
        "save_logs":         _fmt_bool(cfg.save_logs),
        "rng":               cfg.rng if cfg.rng is not None else "—",
    })

    t_pop = _table_pairs("Population", {
        "dataset_path":      cfg.population.dataset_path or "—",
        "template_path":     cfg.population.template_path or "—",
        "size_limit":        cfg.population.size_limit if cfg.population.size_limit is not None else "—",
        "filter_duplicates": _fmt_bool(cfg.population.filter_duplicates),
        "constraints":       _fmt_constraints(cfg.population.constraints),
    })

    t_sel = _table_pairs("Selection", {
        "size":               cfg.multiobjective.size,
        "method":             cfg.multiobjective.selection_method.value,
        "objective_temp":     cfg.multiobjective.objective_temperature,
        "sampling_temp":      cfg.multiobjective.sampling_temperature,
        "repulsion_weight":   cfg.multiobjective.repulsion_weight,
        "normalize_objectives": _fmt_bool(cfg.multiobjective.normalize_objectives),
        "metric":             cfg.multiobjective.metric,
        "random_seed":        cfg.multiobjective.random_seed,
        "divisions":          cfg.multiobjective.divisions,
    })

    t_var = _table_pairs("Variation", {
        "initial_mut_rate":   cfg.variation.initial_mutation_rate,
        "min_mutation_rate":  cfg.variation.min_mutation_rate,
        "alpha":              cfg.variation.alpha,
        "crossover_prob":     cfg.variation.crossover_probability,
        "use_mag_scaling":    _fmt_bool(cfg.variation.use_magnitude_scaling),
        "max_prob":           cfg.variation.max_prob,
        "min_prob":           cfg.variation.min_prob,
    })

    t_thermo = _table_pairs("Thermostat", {
        "T0":        cfg.thermostat.initial_temperature,
        "decay":     cfg.thermostat.decay_rate,
        "period":    cfg.thermostat.period,
        "T_bounds":  f"{cfg.thermostat.temperature_bounds[0]}..{cfg.thermostat.temperature_bounds[1]}",
        "constant_T": _fmt_bool(cfg.thermostat.constant_temperature),
    })

    t_conv = _table_pairs("Convergence", {
        "objective_thr":      cfg.convergence.objective_threshold,
        "feature_thr":        cfg.convergence.feature_threshold,
        "stall_thr":          cfg.convergence.stall_threshold,
        "information_driven": _fmt_bool(cfg.convergence.information_driven),
        "detailed_record":    _fmt_bool(cfg.convergence.detailed_record),
        "type":               cfg.convergence.convergence_type,
    })

    t_sim = _table_pairs("Simulator", {
        "mode":        cfg.simulator.mode,
        "calculator":  _callable_label(cfg.simulator.calculator),
    })

    t_hash = _table_pairs("HashMap", {
        "method":    cfg.hashmap.method,
        "r_max":     cfg.hashmap.r_max,
        "bin_width": cfg.hashmap.bin_width,
        "symprec":   cfg.hashmap.symprec,
    })

    t_agent = _table_pairs("Agentic", {
        "shared_dir":    cfg.agentic.shared_dir or "—",
        "shard_width":   cfg.agentic.shard_width,
        "persist_seen":  _fmt_bool(cfg.agentic.persist_seen),
        "poll_interval": cfg.agentic.poll_interval,
        "max_buffer":    cfg.agentic.max_buffer,
        "max_retained":  cfg.agentic.max_retained,
        "auto_publish":  _fmt_bool(cfg.agentic.auto_publish),
    })

    t_eval = _table_pairs("Evaluator", {
        "features":   _callable_label(cfg.evaluator.features_funcs),
        "objectives": _callable_label(cfg.evaluator.objectives_funcs),
        "debug":      _fmt_bool(cfg.evaluator.debug),
    })

    t_ops = _table_pairs("Operators", {
        "mutation_funcs":   _callable_label(cfg.mutation_funcs) if cfg.mutation_funcs else "—",
        "crossover_funcs":  _callable_label(cfg.crossover_funcs) if cfg.crossover_funcs else "—",
        "generative_model": _callable_label(cfg.generative_model) if cfg.generative_model else "—",
    })

    if getattr(cfg, "hise", None) and cfg.hise:
        h = cfg.hise
        overrides_keys = ", ".join(h.overrides.keys()) if h.overrides else "—"
        t_hise = _table_pairs("HiSE", {
            "supercells":        _fmt_supercells(h.supercells),
            "input_from":        h.input_from,
            "stage_dir_pattern": h.stage_dir_pattern,
            "restart":           _fmt_bool(h.restart),
            "carry":             h.carry,
            "reseed_fraction":   h.reseed_fraction,
            "lift_method":       h.lift_method,
            "overrides":         overrides_keys,
        })
    else:
        t_hise = _table_pairs("HiSE", {"enabled": Text("false", style="red")})

    cols_top = Columns([t_ga, t_pop, t_sel, t_var], equal=True, expand=True)
    cols_mid = Columns([t_thermo, t_conv, t_sim, t_hash, t_agent], equal=True, expand=True)
    cols_bot = Columns([t_eval, t_ops, t_hise], equal=True, expand=True)

    console.print(Panel(cols_top, title="EZGA • Core", box=box.ROUNDED))
    console.print(Panel(cols_mid, title="EZGA • Runtime", box=box.ROUNDED))
    console.print(Panel(cols_bot, title="EZGA • Logic & HiSE", box=box.ROUNDED))

