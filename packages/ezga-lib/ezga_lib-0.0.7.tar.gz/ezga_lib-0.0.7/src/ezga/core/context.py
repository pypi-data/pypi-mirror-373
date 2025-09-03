"""Shared run‑time context for the Genetic Algorithm (GA).

This module defines :class:`Context`, a lightweight container that groups the
state and utilities commonly required during a GA run—such as generation
counters, seeded pseudo‑random number generation and high‑resolution timing.

Example:
    >>> ctx = Context(rng_seed=42)
    >>> ctx.start_timer("evaluation")
    >>> # ... evaluate a population ...
    >>> elapsed = ctx.stop_timer("evaluation")
    >>> print(f"Evaluation took {elapsed:.3f}s")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional
import random
from time import perf_counter
from contextlib import contextmanager

__all__ = ["Context"]

@dataclass
class Context:
    """Runtime context object for a GA execution.

    The class encapsulates mutable state that would otherwise be stored in
    scattered global variables and provides a minimal API for deterministic
    randomness and labelled timing.

    Attributes:
        generation: Index of the current GA generation.
        temperature: (Optional) simulated‑annealing temperature.
        rng_seed: Seed used to initialise :pyattr:`rng`. ``None`` yields a
            non‑deterministic seed.
        rng: Instance of :class:`random.Random` seeded with *rng_seed*.
        data: Arbitrary user key–value store shared across GA components.
        _timers: Private mapping from *label* to timer start instant.
    """
    # ───────────────────────────────── dataclass fields ─────────────────────────
    generation: int = 0
    temperature: float = 0.0
    rng_seed: Optional[int] = None
    foreigners:int = 0

    # These fields are initialised post‑construction or via default factories.
    rng: random.Random = field(init=False, repr=False)
    data: Dict[str, Any] = field(default_factory=dict, repr=False)

    _start_times: Dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _elapsed_times: Dict[str, float] = field(default_factory=dict, init=False, repr=False)

    # ───────────────────────────────── magic methods ───────────────────────────
    def __post_init__(self):
        self.features = None
        self.objetives = None
        
        self.selected_indices = None
        self.top_objectives = None
        self.top_features = None

    # ───────────────────────────────── timing helpers ──────────────────────────
    def start_timer(self, label: str) -> None:
        """(Re)start a high‑resolution timer for *label*.

        If *label* is already running its start instant is reset, **without**
        discarding previous accumulated time. Never raises an exception.

        Args:
            label: Unique identifier for the timed block.
        """
        self._start_times[label] = perf_counter()
        self._elapsed_times.setdefault(label, 0.0)

    def stop_timer(self, label: str) -> float:
        """Stop the timer and return cumulative elapsed seconds.

        Stopping an inactive or unknown timer simply returns its current
        accumulated value (``0.0`` if unseen). No exception is raised.

        Args:
            label: Identifier of the timer to stop.

        Returns:
            Cumulative elapsed time in seconds after this stop operation.
        """
        if (start := self._start_times.pop(label, None)) is not None:
            # accumulate without risking KeyError
            self._elapsed_times[label] = (
                self._elapsed_times.get(label, 0.0) + perf_counter() - start
            )
        # likewise, return 0.0 for unseen labels
        return self._elapsed_times.get(label, 0.0)
    def elapsed(self, label: str) -> float:
        """Return cumulative seconds, running or not.

        Args:
            label: Identifier of the timer to query.

        Returns:
            Cumulative elapsed seconds, ``0.0`` if timer has never been used.
        """
        elapsed_time = self._elapsed_times.get(label, 0.0)
        if label in self._start_times:
            elapsed_time += perf_counter() - self._start_times[label]
        return elapsed_time

    def clear_timers(self, clean_all:bool=False) -> None:
        """Remove **all** timing information (both running and stored)."""
        if clean_all:self._start_times.clear()
        self._elapsed_times.clear()

    # ───────────────────────── context-manager wrapper ────────────────────────
    @contextmanager
    def timer(self, label: str):
        """Context-manager wrapper around start_timer/stop_timer.

        Example
        -------
        >>> with ctx.timer("generation"):
        ...     current_no_collision = population.filter_self_collision(current)
        """
        self.start_timer(label)
        try:
            yield
        finally:
            self.stop_timer(label)
            
    # ───────────────────────────────── public helpers ──────────────────────────
    @property
    def timers(self) -> Mapping[str, float]:
        """Snapshot of cumulative elapsed times for every label.

        Returns:
            Mapping ``{label: seconds}`` including running timers; empty dict if
            no timers exist.
        """
        return {lbl: self.elapsed(lbl) for lbl in self._elapsed_times}

    def set_generation(self, generation:int):
        self.generation = generation
        return generation

    def set_features(self, features:np.array):
        self.features = features
        return True

    def set_objectives(self, objetives:np.array):
        self.objetives = objetives
        return True

    def set_temperature(self, ):
        self.temperature
        return self.temperature

    def get_features(self, ):
        return self.features
    
    def get_objectives(self, ):
        return self.objetives

    def get_temperature(self, ):
        return self.temperature

    def set_selection(self, selected_indices:list) -> bool:
        """
        """
        self.selected_indices = selected_indices
        self.top_objectives = self.get_objectives()[selected_indices,:]
        self.top_features = self.get_features()[selected_indices]

        return True 
    
    def save(
        self,
        generation: int,
        conv_results: dict,
        features: np.ndarray,
        objectives: np.ndarray,
        selected_indices: np.ndarray,
        temperature:float,
        partition_path: str
    ):
        """ 
        Saves the key results for a given generation to disk
        and logs the elapsed time for this step.

        Parameters
        ----------
        generation : int
            Current generation index.
        conv_results : dict
            Convergence results for this generation.
        features : np.ndarray
            Features array.
        objectives : np.ndarray
            Objectives array.
        selected_indices : np.ndarray
            Indices of selected structures.
        temperature : float
            Temperature used in this generation.
        partition_path : str
            Subdirectory path for logging (e.g., "my_partition").
        """
        t0 = time.time()

        # Build the 'data' dict
        data_dict = {
            "convergence_results": conv_results,
            #"features": features.tolist() if features is not None else None,

            "generation": generation,
            "num_structures_in_dataset": int(self.partitions['dataset'].size),
            "num_newstructures": int(self.partitions['generation'].size),
            #"objectives": objectives.tolist() if objectives is not None else None,

            "selected_indices": (
                selected_indices.tolist()
                if (selected_indices is not None)
                else []
            ),

            "stall_count": self.convergence_checker._no_improvement_count,
            "stall_count_objetive": self.convergence_checker._no_improvement_count_objectives,

            #"objectives_for_features_history": self.convergence_checker._objectives_for_features_history,
            "mutation_rate_history": self.mutation_rate_array,
            "mutation_probabilities": self.mutation_crossover_handler._mutation_probabilities,

            "mutation_attempt_counts": self.mutation_crossover_handler._mutation_attempt_counts,
            "mutation_fails_counts": self.mutation_crossover_handler._mutation_fails_counts,
            "mutation_success_counts": self.mutation_crossover_handler._mutation_success_counts,
            "mutation_unsuccess_counts": self.mutation_crossover_handler._mutation_unsuccess_counts,
            "mutation_hashcolition_counts": self.mutation_crossover_handler._mutation_hashcolition_counts,
            "mutation_outofdoe_counts": self.mutation_crossover_handler._mutation_outofdoe_counts,

            "crosvover_attempt_counts": self.mutation_crossover_handler._crossover_attempt_counts,
            "crossover_fails_counts": self.mutation_crossover_handler._crossover_fails_counts,
            "crossover_success_counts": self.mutation_crossover_handler._crossover_success_counts,
            "crossover_unsuccess_counts": self.mutation_crossover_handler._crossover_unsuccess_counts,
            "crossover_hashcolition_counts": self.mutation_crossover_handler._crossover_hashcolition_counts,
            "crossover_outofdoe_counts": self.mutation_crossover_handler._crossover_outofdoe_counts,

            "time_log": self.time_log,
            "T": temperature
            #"model_evolution_info": self.model_evolution_info  # additional logging
        }

        if self.convergence_checker._information_driven:
             data_dict["novelty_history"] = self.information_ensamble_metric.get_latest_novelty()
             data_dict["novelty_thresh_history"] = self.information_ensamble_metric.get_latest_novelty_thresh()
             data_dict["stall_count_information"] = self.convergence_checker._no_improvement_count_information

        # Call your existing save_generation_data utility
        save_generation_data(
            generation=generation,
            data=data_dict,
            output_directory=f"{self._output_path}/{partition_path}/logger"
        )

        # Log elapsed time
        self.time_log['save_generation_data'] = time.time() - t0
        if self.debug:
            self.logger.info(f"[DEBUG] Generation data saved for Gen={generation}.")
