from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Dict, Any
import json
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Config
# ----------------------------
@dataclass
class PlotConfig:
    dpi: int = 140
    fmt: str = "png"          # e.g. "png" | "svg" | "pdf"
    width: float = 8.0        # inches
    height: float = 4.0       # inches
    correlation_vars: Optional[Sequence[str]] = None  # columns to include in corr


# ----------------------------
# Loader
# ----------------------------
class SnapshotLoader:
    """
    Load per-generation JSON snapshots produced by your GenerationSnapshotWriter
    and return a tidy pandas.DataFrame suitable for plotting.
    """
    def __init__(self, logger_dir: str | Path, pattern: str = r"gen_(\d+).*\.json"):
        self.base = Path(logger_dir)
        self.pattern = re.compile(pattern)

    def _sum_or_none(self, x):
        if isinstance(x, list):
            arr = np.asarray(x, dtype=float)
            return int(np.nansum(arr))
        return x

    def load(self) -> pd.DataFrame:
        rows = []
        for f in sorted(self.base.glob("gen_*.json")):
            if not f.is_file():
                continue
            if not self.pattern.match(f.name):
                continue
            with f.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

            row: Dict[str, Any] = {}
            # basics
            row["generation"] = data.get("generation")
            row["temperature"] = data.get("temperature")
            row["dataset_size"] = data.get("dataset_size")
            row["current_valid_size"] = data.get("current_valid_size")
            row["selected_size"] = data.get("selected_size")

            # timers
            for k, v in (data.get("timers") or {}).items():
                row[f"time_{k}"] = v

            # convergence
            conv = data.get("convergence_results") or {}
            for k, v in conv.items():
                row[f"conv_{k}"] = v
            row["stall_count_objective"] = data.get("stall_count_objective")
            row["stall_count_information"] = data.get("stall_count_information")

            # variation (flatten to totals across operators)
            var = data.get("variation_stats") or {}
            row["mut_attempts"]   = self._sum_or_none(var.get("mutation_attempt_counts"))
            row["mut_success"]    = self._sum_or_none(var.get("mutation_success_counts"))
            row["mut_fails"]      = self._sum_or_none(var.get("mutation_fails_counts"))
            row["mut_unsuccess"]  = self._sum_or_none(var.get("mutation_unsuccess_counts"))
            row["mut_hashcol"]    = self._sum_or_none(var.get("mutation_hashcolition_counts"))
            row["mut_outofdoe"]   = self._sum_or_none(var.get("mutation_outofdoe_counts"))

            row["xov_attempts"]   = self._sum_or_none(var.get("crossover_attempt_counts"))
            row["xov_success"]    = self._sum_or_none(var.get("crossover_success_counts"))
            row["xov_fails"]      = self._sum_or_none(var.get("crossover_fails_counts"))
            row["xov_unsuccess"]  = self._sum_or_none(var.get("crossover_unsuccess_counts"))
            row["xov_hashcol"]    = self._sum_or_none(var.get("crossover_hashcolition_counts"))
            row["xov_outofdoe"]   = self._sum_or_none(var.get("crossover_outofdoe_counts"))

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows).sort_values("generation").reset_index(drop=True)

        # Derived columns
        for p in ("mut", "xov"):
            a = f"{p}_attempts"
            s = f"{p}_success"
            if a in df.columns and s in df.columns:
                df[f"{p}_success_rate"] = np.where(df[a].fillna(0) > 0,
                                                   df[s].fillna(0) / df[a].replace(0, np.nan),
                                                   np.nan)

        time_cols = [c for c in df.columns if c.startswith("time_")]
        if time_cols:
            df["time_total"] = df[time_cols].sum(axis=1)

        return df


# ----------------------------
# Plotter
# ----------------------------
class SnapshotPlotter:
    """
    Generate a comprehensive set of figures summarizing GA evolution and
    variable correlations from the loaded snapshots.
    """
    def __init__(self, df: pd.DataFrame, out_dir: str | Path, cfg: PlotConfig = PlotConfig()):
        self.df = df.copy()
        self.out = Path(out_dir)
        self.cfg = cfg
        self.out.mkdir(parents=True, exist_ok=True)

    def _save(self, name: str):
        plt.tight_layout()
        fp = self.out / f"{name}.{self.cfg.fmt}"
        plt.savefig(fp, dpi=self.cfg.dpi, bbox_inches="tight")
        plt.close()

    # --- Individual plots ---
    def plot_temperature(self):
        if "temperature" not in self.df:
            return
        plt.figure(figsize=(self.cfg.width, self.cfg.height))
        plt.plot(self.df["generation"], self.df["temperature"], marker="o")
        plt.xlabel("Generation")
        plt.ylabel("Temperature")
        plt.title("Temperature schedule")
        self._save("temperature")

    def plot_population_sizes(self):
        plt.figure(figsize=(self.cfg.width, self.cfg.height))
        plt.plot(self.df["generation"], self.df["dataset_size"], label="dataset")
        if "current_valid_size" in self.df:
            plt.plot(self.df["generation"], self.df["current_valid_size"], label="current_valid")
        if "selected_size" in self.df:
            plt.plot(self.df["generation"], self.df["selected_size"], label="selected")
        plt.xlabel("Generation")
        plt.ylabel("Count")
        plt.title("Population sizes over generations")
        plt.legend()
        self._save("population_sizes")

    def plot_convergence_and_stalls(self):
        has_any = False
        plt.figure(figsize=(self.cfg.width, self.cfg.height))
        if "conv_stagnation" in self.df:
            plt.plot(self.df["generation"], self.df["conv_stagnation"], label="stagnation")
            has_any = True
        if "stall_count_objective" in self.df:
            plt.plot(self.df["generation"], self.df["stall_count_objective"], label="stall(objective)")
            has_any = True
        if "stall_count_information" in self.df:
            plt.plot(self.df["generation"], self.df["stall_count_information"], label="stall(info)")
            has_any = True
        if has_any:
            plt.xlabel("Generation")
            plt.ylabel("Count")
            plt.title("Convergence / stall counters")
            plt.legend()
            self._save("convergence_stalls")
            plt.close()

        # Improvement events as stems
        if "conv_improvement_found" in self.df:
            plt.figure(figsize=(self.cfg.width, self.cfg.height))
            y = self.df["conv_improvement_found"].astype(float)
            plt.stem(self.df["generation"], y, use_line_collection=True)
            plt.xlabel("Generation")
            plt.ylabel("Improvement flag")
            plt.title("Improvement events")
            self._save("improvement_events")

    def plot_operator_counts_and_rates(self):
        # Mutation
        has_any = any(c in self.df for c in ("mut_attempts", "mut_success", "mut_fails"))
        if has_any:
            plt.figure(figsize=(self.cfg.width, self.cfg.height))
            for col, label in [
                ("mut_attempts", "mutation attempts"),
                ("mut_success",  "mutation success"),
                ("mut_fails",    "mutation fails"),
                ("mut_unsuccess","mutation unsuccess"),
            ]:
                if col in self.df:
                    plt.plot(self.df["generation"], self.df[col], label=label)
            plt.xlabel("Generation")
            plt.ylabel("Count")
            plt.title("Mutation counts")
            plt.legend()
            self._save("mutation_counts")

        if "mut_success_rate" in self.df:
            plt.figure(figsize=(self.cfg.width, self.cfg.height))
            plt.plot(self.df["generation"], self.df["mut_success_rate"], marker="o")
            plt.xlabel("Generation")
            plt.ylabel("Success rate")
            plt.title("Mutation success rate")
            self._save("mutation_success_rate")

        # Crossover
        has_any = any(c in self.df for c in ("xov_attempts", "xov_success", "xov_fails"))
        if has_any:
            plt.figure(figsize=(self.cfg.width, self.cfg.height))
            for col, label in [
                ("xov_attempts", "crossover attempts"),
                ("xov_success",  "crossover success"),
                ("xov_fails",    "crossover fails"),
                ("xov_unsuccess","crossover unsuccess"),
            ]:
                if col in self.df:
                    plt.plot(self.df["generation"], self.df[col], label=label)
            plt.xlabel("Generation")
            plt.ylabel("Count")
            plt.title("Crossover counts")
            plt.legend()
            self._save("crossover_counts")

        if "xov_success_rate" in self.df:
            plt.figure(figsize=(self.cfg.width, self.cfg.height))
            plt.plot(self.df["generation"], self.df["xov_success_rate"], marker="o")
            plt.xlabel("Generation")
            plt.ylabel("Success rate")
            plt.title("Crossover success rate")
            self._save("crossover_success_rate")

    def plot_stage_times(self):
        time_cols = [c for c in self.df.columns if c.startswith("time_")]
        if not time_cols:
            return
        plt.figure(figsize=(self.cfg.width, self.cfg.height))
        for c in time_cols:
            plt.plot(self.df["generation"], self.df[c], label=c.replace("time_", ""))
        plt.xlabel("Generation")
        plt.ylabel("Seconds")
        plt.title("Stage wall-times")
        plt.legend()
        self._save("stage_times")

    def plot_correlation_matrix(self):
        # Choose variables for correlation
        default_vars = [
            "temperature", "dataset_size", "current_valid_size", "selected_size",
            "mut_success_rate", "xov_success_rate",
            "conv_stagnation", "stall_count_objective", "stall_count_information",
            "time_total"
        ]
        vars_ = self.cfg.correlation_vars or default_vars
        cols = [c for c in vars_ if c in self.df.columns]
        if len(cols) < 2:
            return

        X = self.df[cols].astype(float)
        C = X.corr(method="pearson")

        plt.figure(figsize=(max(4, len(cols) * 0.75), max(3.5, len(cols) * 0.75)))
        im = plt.imshow(C.values, interpolation="nearest")
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
        plt.yticks(range(len(cols)), cols)
        plt.title("Correlation matrix (Pearson)")
        self._save("correlation_matrix")

    # --- Orchestrator ---
    def generate_all(self):
        if self.df.empty:
            raise RuntimeError(f"No snapshots found to plot in {self.out}")
        self.plot_temperature()
        self.plot_population_sizes()
        self.plot_convergence_and_stalls()
        self.plot_operator_counts_and_rates()
        self.plot_stage_times()
        self.plot_correlation_matrix()
