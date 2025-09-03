# SPDX-License-Identifier: GPL-3.0-only
"""
Interactive configuration wizard.

Sub-CLI:
- `ezga wizard menu`      : full-screen, menu-driven assistant (colored).
- `ezga wizard new`       : quick prompts to build a minimal config.
- `ezga wizard template`  : write a non-interactive template (basic / HiSE).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import io

import typer
from typer import Typer
from ruamel.yaml import YAML

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.syntax import Syntax
from rich.theme import Theme
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt

from ezga.core.config import GAConfig
from ezga.io.config_loader import dump_config_yaml

app = typer.Typer(
    help="Interactive, menu-driven assistant to compose a YAML config.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# --- Rich theme (centralized brand colors) -----------------------------------
THEME = Theme({
    "title": "bold cyan",
    "ok": "bold green",
    "warn": "bold yellow",
    "danger": "bold red",
    "muted": "dim",
    "key": "bold white",
    "val": "bold magenta",
})
console = Console(theme=THEME)

yaml_rt = YAML()
yaml_rt.indent(mapping=2, sequence=4, offset=2)
yaml_rt.default_flow_style = False


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def _to_yaml_str(cfg_dict: Dict[str, Any]) -> str:
    """Serialize a Python dict to YAML string using ruamel.yaml."""
    buf = io.StringIO()
    yaml_rt.dump(cfg_dict, buf)
    return buf.getvalue()


def _preview_yaml(data: Dict[str, Any]) -> None:
    """Pretty, colored YAML preview panel."""
    yaml_str = _to_yaml_str(data)
    syntax = Syntax(yaml_str, "yaml", word_wrap=False)
    console.print(Panel(syntax, title="[title]YAML Preview[/title]", border_style="muted"))


def _kv_line(key: str, value: Any) -> Text:
    """Return a colored 'key: value' line."""
    return Text.assemble((f"{key}: ", "key"), (f"{value}", "val"))


def _main_summary_panel(data: Dict[str, Any]) -> Panel:
    """Build a compact summary panel of the current config state."""
    pop = data.get("population", {})
    hise = data.get("hise")
    lines = [
        _kv_line("max_generations", data.get("max_generations")),
        _kv_line("output_path", data.get("output_path")),
        _kv_line("dataset_path", pop.get("dataset_path")),
        _kv_line("constraints", len(pop.get("constraints", []) or [])),
        _kv_line("HiSE", "enabled" if hise else "disabled"),
    ]
    return Panel(Columns(lines, expand=True), title="[title]Summary[/title]", border_style="muted")


def _ensure_nested(d: Dict[str, Any], key: str, default: Any) -> Dict[str, Any]:
    """Ensure key exists as a dict with default; return that dict."""
    if key not in d or not isinstance(d[key], dict):
        d[key] = default
    return d[key]


def _ask_choice(title: str, choices: Dict[str, str], default: Optional[str] = None) -> str:
    """Ask user to choose among labeled options, returning the chosen key."""
    table = Table(title=f"[title]{title}[/title]", show_header=True, header_style="title")
    table.add_column("#", justify="right")
    table.add_column("Option", style="key")
    table.add_column("Description", style="muted")
    keys = list(choices.keys())
    for i, k in enumerate(keys, 1):
        table.add_row(str(i), k, choices[k])
    console.print(table)
    idx = IntPrompt.ask("Select option", default=(keys.index(default) + 1) if default in keys else 1)
    idx = max(1, min(idx, len(keys)))
    return keys[idx - 1]


def _normalize_cfg_for_dump(cfg: GAConfig) -> Dict[str, Any]:
    """Convert a GAConfig into a JSON-serializable dict that is YAML-friendly.

    - Ensures tuples → lists (especially HiSE supercells).
    - Ensures enums → strings (Pydantic JSON mode already does this for Enums).
    """
    data = cfg.model_dump(mode="json", by_alias=True, exclude_none=False)
    if data.get("hise", {}) and data["hise"].get("supercells"):
        data["hise"]["supercells"] = [list(sc) for sc in data["hise"]["supercells"]]
    return data


# -----------------------------------------------------------------------------
# Section editors (each returns None; they mutate the `data` dict in place)
# -----------------------------------------------------------------------------
def _edit_ga(data: Dict[str, Any]) -> None:
    """Edit top-level GA parameters."""
    console.rule("[title]GA Settings[/title]")
    data["max_generations"] = IntPrompt.ask("Max generations", default=int(data.get("max_generations", 100)))
    data["output_path"] = Prompt.ask("Output directory", default=str(data.get("output_path", "run")))
    _preview_yaml(data)


def _edit_population(data: Dict[str, Any]) -> None:
    """Edit population section."""
    console.rule("[title]Population[/title]")
    pop = _ensure_nested(data, "population", {})
    pop["dataset_path"] = Prompt.ask("Dataset path", default=str(pop.get("dataset_path", "config.xyz")))
    pop["template_path"] = Prompt.ask("Template path (empty for none)", default=str(pop.get("template_path") or "")) or None
    pop["filter_duplicates"] = Confirm.ask("Filter duplicates?", default=bool(pop.get("filter_duplicates", True)))
    # Constraints mini-loop
    if Confirm.ask("Edit constraints?", default=False):
        pop.setdefault("constraints", [])
        while True:
            console.print(Panel.fit("Constraint editor", style="muted"))
            table = Table(show_header=True, header_style="title", title="Current constraints")
            table.add_column("#", justify="right")
            table.add_column("Factory", style="key")
            table.add_column("Args / Kwargs", style="muted")
            for i, c in enumerate(pop["constraints"], 1):
                table.add_row(str(i), str(c.get("factory", c)), str({k: v for k, v in c.items() if k != "factory"}))
            console.print(table)

            action = _ask_choice(
                "Constraint actions",
                {
                    "add": "Add new constraint (factory spec)",
                    "remove": "Remove by index",
                    "back": "Return to previous menu",
                },
                default="back",
            )
            if action == "add":
                factory = Prompt.ask("Factory (e.g., ezga.DoE.DoE:ConstraintGenerator.sum_in_range)")
                has_args = Confirm.ask("Add positional args?", default=False)
                args = []
                if has_args:
                    raw = Prompt.ask("Args as Python literal list (e.g., [['C','H'], 100, 100])", default="[]")
                    try:
                        args = eval(raw, {})  # trusted local usage; no user input from network
                    except Exception:
                        console.print("[danger]Could not parse args list.[/]")
                        args = []
                has_kwargs = Confirm.ask("Add keyword args?", default=False)
                kwargs = {}
                if has_kwargs:
                    raw = Prompt.ask("Kwargs as Python dict (e.g., {lower: 100, upper: 100})", default="{}")
                    try:
                        kwargs = eval(raw, {})
                    except Exception:
                        console.print("[danger]Could not parse kwargs dict.[/]")
                        kwargs = {}
                spec: Dict[str, Any] = {"factory": factory}
                if args:
                    spec["args"] = args
                if kwargs:
                    spec["kwargs"] = kwargs
                pop["constraints"].append(spec)
            elif action == "remove":
                if not pop["constraints"]:
                    console.print("[warn]No constraints to remove.[/]")
                else:
                    ridx = IntPrompt.ask("Index to remove (1..N)", default=1)
                    if 1 <= ridx <= len(pop["constraints"]):
                        pop["constraints"].pop(ridx - 1)
            else:
                break
    _preview_yaml(data)


def _edit_thermostat(data: Dict[str, Any]) -> None:
    """Edit thermostat parameters."""
    console.rule("[title]Thermostat[/title]")
    th = _ensure_nested(data, "thermostat", {})
    th["initial_temperature"] = FloatPrompt.ask("Initial temperature", default=float(th.get("initial_temperature", 1.0)))
    th["decay_rate"] = FloatPrompt.ask("Decay rate", default=float(th.get("decay_rate", 0.005)))
    th["period"] = IntPrompt.ask("Period", default=int(th.get("period", 30)))
    lo = FloatPrompt.ask("Min temperature bound", default=float(th.get("temperature_bounds", [0.1, 2.0])[0]))
    hi = FloatPrompt.ask("Max temperature bound", default=float(th.get("temperature_bounds", [0.1, 2.0])[1]))
    th["temperature_bounds"] = [lo, hi]
    th["constant_temperature"] = Confirm.ask("Constant temperature?", default=bool(th.get("constant_temperature", False)))
    _preview_yaml(data)


def _edit_selection(data: Dict[str, Any]) -> None:
    """Edit multiobjective/selection parameters."""
    console.rule("[title]Selection[/title]")
    sel = _ensure_nested(data, "multiobjective", {})
    sel["size"] = IntPrompt.ask("Selection size", default=int(sel.get("size", 128)))
    method = _ask_choice(
        "Selection method",
        {"boltzmann": "Boltzmann sampling", "greedy": "Greedy", "roulette": "Roulette", "tournament": "Tournament"},
        default=str(sel.get("selection_method", "boltzmann")),
    )
    sel["selection_method"] = method
    sel["objective_temperature"] = FloatPrompt.ask("Objective temperature", default=float(sel.get("objective_temperature", 1.0)))
    sel["sampling_temperature"] = FloatPrompt.ask("Sampling temperature", default=float(sel.get("sampling_temperature", 1.0)))
    sel["repulsion_weight"] = FloatPrompt.ask("Repulsion weight", default=float(sel.get("repulsion_weight", 1.0)))
    sel["normalize_objectives"] = Confirm.ask("Normalize objectives?", default=bool(sel.get("normalize_objectives", False)))
    _preview_yaml(data)


def _edit_variation(data: Dict[str, Any]) -> None:
    """Edit variation (mutation/crossover) parameters."""
    console.rule("[title]Variation[/title]")
    var = _ensure_nested(data, "variation", {})
    var["initial_mutation_rate"] = FloatPrompt.ask("Initial mutation rate", default=float(var.get("initial_mutation_rate", 3.0)))
    var["min_mutation_rate"] = FloatPrompt.ask("Min mutation rate", default=float(var.get("min_mutation_rate", 1.0)))
    var["crossover_probability"] = FloatPrompt.ask("Crossover probability", default=float(var.get("crossover_probability", 0.1)))
    _preview_yaml(data)


def _edit_simulator(data: Dict[str, Any]) -> None:
    """Edit simulator/calculator adapter settings (lightweight)."""
    console.rule("[title]Simulator[/title]")
    sim = _ensure_nested(data, "simulator", {"mode": "sampling"})
    sim["mode"] = Prompt.ask("Mode", default=str(sim.get("mode", "sampling")))
    # Calculator is left as free-form (user may plug factories in YAML later)
    calc = Prompt.ask("Calculator factory shorthand (empty to skip)", default="")
    if calc.strip():
        sim["calculator"] = {"factory": calc.strip(), "kwargs": {}}
    _preview_yaml(data)


def _edit_convergence(data: Dict[str, Any]) -> None:
    """Edit convergence parameters."""
    console.rule("[title]Convergence[/title]")
    conv = _ensure_nested(data, "convergence", {})
    conv["objective_threshold"] = FloatPrompt.ask("Objective threshold", default=float(conv.get("objective_threshold", 0.01)))
    conv["feature_threshold"] = FloatPrompt.ask("Feature threshold", default=float(conv.get("feature_threshold", 0.01)))
    conv["stall_threshold"] = IntPrompt.ask("Stall threshold", default=int(conv.get("stall_threshold", 100)))
    mode = _ask_choice("Convergence type", {"and": "All criteria", "or": "Any criterion"}, default=str(conv.get("convergence_type", "and")))
    conv["convergence_type"] = mode
    _preview_yaml(data)


def _edit_hise(data: Dict[str, Any]) -> None:
    """Edit optional HiSE block."""
    console.rule("[title]HiSE[/title]")
    enable = Confirm.ask("Enable HiSE?", default=bool(data.get("hise")))
    if not enable:
        data.pop("hise", None)
        _preview_yaml(data)
        return

    hise = _ensure_nested(data, "hise", {})
    # Supercells editor (list of triples)
    console.print(Panel.fit("Edit supercells (triples). Example: 1,1,1", border_style="muted"))
    scells = []
    if isinstance(hise.get("supercells"), list) and hise["supercells"]:
        scells = [tuple(int(x) for x in sc) for sc in hise["supercells"]]
    else:
        scells = [(1, 1, 1), (2, 1, 1)]
    while True:
        table = Table(title="[title]Current supercells[/title]", show_header=True, header_style="title")
        table.add_column("#", justify="right")
        table.add_column("(a,b,c)", style="val")
        for i, sc in enumerate(scells, 1):
            table.add_row(str(i), str(sc))
        console.print(table)
        action = _ask_choice("HiSE actions", {"add": "Add triple", "remove": "Remove by index", "next": "Continue"}, default="next")
        if action == "add":
            triple = Prompt.ask("Enter a,b,c", default="2,1,1")
            try:
                a, b, c = (int(v.strip()) for v in triple.split(","))
                if a < 1 or b < 1 or c < 1:
                    raise ValueError
                scells.append((a, b, c))
            except Exception:
                console.print("[danger]Invalid triple. Use three positive integers.[/]")
        elif action == "remove":
            if not scells:
                console.print("[warn]No supercells to remove.[/]")
            else:
                ridx = IntPrompt.ask("Index to remove (1..N)", default=1)
                if 1 <= ridx <= len(scells):
                    scells.pop(ridx - 1)
        else:
            break

    hise["supercells"] = scells
    hise["input_from"] = Prompt.ask("Input from", choices=["final_dataset", "latest_generation"], default=str(hise.get("input_from", "final_dataset")))
    hise["stage_dir_pattern"] = Prompt.ask("Stage dir pattern", default=str(hise.get("stage_dir_pattern", "supercell_{a}_{b}_{c}")))
    hise["restart"] = Confirm.ask("Restart (skip completed)?", default=bool(hise.get("restart", True)))
    hise["carry"] = Prompt.ask("Carry mode", choices=["pareto", "elites", "all"], default=str(hise.get("carry", "all")))
    hise["reseed_fraction"] = FloatPrompt.ask("Reseed fraction", default=float(hise.get("reseed_fraction", 1.0)))
    hise["lift_method"] = Prompt.ask("Lift method", choices=["tile", "best_compatible", "ase"], default=str(hise.get("lift_method", "tile")))

    # Per-stage overrides (simple key → list editor)
    if Confirm.ask("Edit per-stage overrides?", default=False):
        hise.setdefault("overrides", {})
        while True:
            table = Table(title="[title]Overrides[/title]", show_header=True, header_style="title")
            table.add_column("Key (dot path)", style="key")
            table.add_column("Values (per stage)", style="val")
            for k, v in hise["overrides"].items():
                table.add_row(k, str(v))
            console.print(table)
            action = _ask_choice("Override actions", {"add": "Add / replace", "remove": "Remove key", "back": "Return"}, default="back")
            if action == "add":
                dotted = Prompt.ask("Key (dot path, e.g., multiobjective.size)")
                raw = Prompt.ask("Python list of values (len == #stages)", default="[]")
                try:
                    vals = eval(raw, {})
                    if not isinstance(vals, list):
                        raise ValueError
                    hise["overrides"][dotted] = vals
                except Exception:
                    console.print("[danger]Invalid list literal.[/]")
            elif action == "remove":
                if not hise["overrides"]:
                    console.print("[warn]No overrides to remove.[/]")
                else:
                    k = Prompt.ask("Key to remove")
                    hise["overrides"].pop(k, None)
            else:
                break

    _preview_yaml(data)


# -----------------------------------------------------------------------------
# Interactive hub
# -----------------------------------------------------------------------------
@app.command("menu")
def wizard_menu() -> None:
    """Launch a full-color, interactive wizard with navigable sections.

    The wizard keeps an in-memory Python dict (`data`) and updates it as the
    user navigates sections. At any time the user can preview the YAML, save,
    or exit without saving.
    """
    # Seed with a minimal skeleton
    data: Dict[str, Any] = {
        "max_generations": 100,
        "output_path": "run",
        "population": {"dataset_path": "config.xyz"},
    }

    console.print(Panel.fit("EZGA Wizard · interactive menu", style="title"))
    out = Path(Prompt.ask("Output YAML", default="ezga.yaml"))
    if out.exists() and not Confirm.ask(f"{out} exists. Overwrite?", default=False):
        raise typer.Exit(1)

    while True:
        # Main dashboard: summary + menu
        left = _main_summary_panel(data)
        menu = Table(title="[title]Main Menu[/title]", show_header=False, box=None)
        menu.add_row("[key]1[/key] · GA")
        menu.add_row("[key]2[/key] · Population")
        menu.add_row("[key]3[/key] · Thermostat")
        menu.add_row("[key]4[/key] · Selection")
        menu.add_row("[key]5[/key] · Variation")
        menu.add_row("[key]6[/key] · Simulator")
        menu.add_row("[key]7[/key] · Convergence")
        menu.add_row("[key]8[/key] · HiSE")
        menu.add_row("[key]p[/key] · Preview YAML")
        menu.add_row("[key]s[/key] · Save & Exit")
        menu.add_row("[key]q[/key] · Quit without save")
        right = Panel(menu, border_style="muted")
        console.print(Columns([left, right], expand=True))

        choice = Prompt.ask("Choose", default="p").strip().lower()
        if choice == "1":
            _edit_ga(data)
        elif choice == "2":
            _edit_population(data)
        elif choice == "3":
            _edit_thermostat(data)
        elif choice == "4":
            _edit_selection(data)
        elif choice == "5":
            _edit_variation(data)
        elif choice == "6":
            _edit_simulator(data)
        elif choice == "7":
            _edit_convergence(data)
        elif choice == "8":
            _edit_hise(data)
        elif choice == "p":
            _preview_yaml(data)
        elif choice == "s":
            # Validate via Pydantic, then dump via our YAML writer
            cfg = GAConfig(**data)
            dump_data = _normalize_cfg_for_dump(cfg)
            with out.open("w", encoding="utf-8") as fh:
                yaml_rt.dump(dump_data, fh)
            console.print(Panel.fit(f"Saved to [bold]{out}[/]", style="ok"))
            break
        elif choice == "q":
            if Confirm.ask("Discard changes and quit?", default=True):
                console.print("[warn]Aborted; no file written.[/]")
                raise typer.Exit(1)
        else:
            console.print("[warn]Unknown option.[/]")


# -----------------------------------------------------------------------------
# Your existing commands (new/template) can remain as-is below...
# (No changes needed unless quieres unificar estilo/tema)
# -----------------------------------------------------------------------------
