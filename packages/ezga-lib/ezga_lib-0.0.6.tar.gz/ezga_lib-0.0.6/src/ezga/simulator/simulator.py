# ----------------------------------------------------------------------------- #
# Simulator
# ----------------------------------------------------------------------------- #
from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Optional, Union, Literal

import numpy as np
from tqdm import tqdm
import traceback   # only if you want the raw traceback string in logs
from math import nan
import logging

from ..core.interfaces import ISimulator, ILogger

# ----------------------------------------------------------------------------- #
# Utility
# ----------------------------------------------------------------------------- #
def linear_interpolation(data, N):
    """
    Generates N linearly interpolated points over M input points.

    Parameters
    ----------
    data : int, float, list, tuple, or numpy.ndarray
        Input data specifying M control points. If scalar or of length 1,
        returns a constant array of length N.
    N : int
        Number of points to generate. Must be a positive integer and at least
        as large as the number of control points when M > 1.

    Returns
    -------
    numpy.ndarray
        Array of N linearly interpolated points.

    Raises
    ------
    ValueError
        If N is not a positive integer, N < M (when M > 1), or data is invalid.
    """
    # Validate N
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")
    
    # Handle scalar input
    if isinstance(data, (int, float)):
        return np.full(N, float(data))
    
    # Convert sequence input to numpy array
    try:
        arr = np.asarray(data, dtype=float).flatten()
    except Exception:
        raise ValueError("Data must be an int, float, list, tuple, or numpy.ndarray of numeric values.")
    
    M = arr.size
    if M == 0:
        raise ValueError("Input data sequence must contain at least one element.")
    if M == 1:
        return np.full(N, arr[0])
    
    # Ensure N >= M for piecewise interpolation
    if N < M:
        raise ValueError(f"N ({N}) must be at least the number of input points M ({M}).")
    
    # Define original and target sample positions
    xp = np.arange(M)
    xi = np.linspace(0, M - 1, N)
    
    # Perform piecewise linear interpolation
    yi = np.interp(xi, xp, arr)
    
    return yi

# ----------------------------------------------------------------------------- #
# Simulator
# ----------------------------------------------------------------------------- #
Mode = Literal["sampling", "random", "uniform"]
Calculator = Callable[..., tuple[np.ndarray, list[str], np.ndarray, float]]

class Simulator(ISimulator):
    """
    """
    def __init__(
        self,
        *,
        mode: str = "sampling",
        output_path: Union[str, Path] = Path("config_simulator.xyz"),
        calculator: Calculator | Sequence[Calculator],
        logger: Optional[ILogger] = None,
        debug: bool = False, 
    ):
        """
        """
        self.mode = 'sampling' if mode is None else mode        
        self.output_path = 'config_simulator.xyz' if output_path is None else Path(output_path)

        self.logger = logger or logging.getLogger(__name__)
        self.debug = debug

        self._calculators: tuple[Calculator, ...] = self._normalise_calculator(calculator)

    # ──────────────────────────────────────────────────────────────────────
    # calculator property
    # ──────────────────────────────────────────────────────────────────────
    @property
    def calculator(self) -> Calculator | tuple[Calculator, ...]:
        """Return the current calculator pool."""
        return self._calculators if len(self._calculators) > 1 else self._calculators[0]

    @calculator.setter
    def calculator(self, value: Calculator | Sequence[Calculator]) -> None:
        """Replace the calculator pool, applying the same validation as ``__init__``."""
        self._calculators = self._normalise_calculator(value)

    def validate(self, population:list):
        """
        """
        return population

    # ──────────────────────────────────────────────────────────────────────
    # public API
    # ──────────────────────────────────────────────────────────────────────
    def run(
        self, 
        individuals: Sequence[object],
        *,
        temperature: float = 1.0,
        mode: Mode | None = "sampling",
        generation: Optional[int] = None,
        output_path: Path | str | None = None,
        constraints: Optional[Sequence[Callable]] = None,
    ) -> Sequence[object]:
        """
        """
        self._validate_args(individuals, temperature, mode, generation)

        n_struct = len(individuals)
        output_path = Path(output_path or self.output_path)

        total_individuals = len(individuals)
        generation_idx = generation if generation is not None else 0

        temps = self._build_temperature_array(total_individuals, temperature, mode)

        # 2) If device='cpu', run tasks sequentially in the main process
        self.logger.info(
            "Starting simulations on %d structures (Generation=%d, T=%.2f, mode=%s)",
            len(individuals),
            generation,
            temperature,
            mode,
        )

        for idx, (individual, T_i) in enumerate(
            tqdm(zip(individuals, temps),
                 total=total_individuals,
                 desc="Simulations"),
            start=1
        ):
            try:
                individual.AtomPositionManager.charge = None
                individual.AtomPositionManager.magnetization = None
                
                symbols = individual.AtomPositionManager.atomLabelsList
                positions = np.asarray(individual.AtomPositionManager.atomPositions, dtype=float)
                cell = np.asarray(individual.AtomPositionManager.latticeVectors, dtype=float)
                fixed = np.asarray(individual.AtomPositionManager.atomicConstraints, dtype=bool)

                out_file = (
                    Path(output_path)
                    / "generation"
                    / f"gen{generation if generation is not None else 0}"
                    / f"calculator_out.xyz"
                )
                   
                calc: Calculator = random.choice(self._calculators)
                new_positions, new_symbols, new_cell, energy = calc(
                    symbols=symbols,
                    positions=positions,
                    cell=cell,
                    fixed=fixed,
                    constraints=constraints,
                    sampling_temperature=T_i,
                    output_path=str(out_file),
                )

                # Update structure in-place
                individual.AtomPositionManager.atomPositions = new_positions
                individual.AtomPositionManager.atomLabelsList = new_symbols
                individual.AtomPositionManager.latticeVectors = new_cell
                individual.AtomPositionManager.E = energy

                self.logger.info(        
                    "Structure %d/%d → Energy: %s",
                    idx, len(individuals), f"{energy:.4f}" if not np.isnan(energy) else "NaN",
                )
            except Exception as exc:
                # -------- handle failure without aborting the whole run ----------
                self.logger.error(
                    "Calculator %s failed on structure %d/%d (Gen=%s): %s",
                    getattr(calc, "__name__", str(calc)),
                    idx, len(individuals), generation, exc,
                )
                self.logger.debug("Traceback:\n%s", traceback.format_exc())

        return individuals  # Done with CPU mode

    # ──────────────────────────────────────────────────────────────────────
    # helpers
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _normalise_calculator(
        calculator: Calculator | Sequence[Calculator],
    ) -> tuple[Calculator, ...]:
        if callable(calculator):
            return (calculator,)
        if isinstance(calculator, Sequence) and calculator:
            if not all(callable(c) for c in calculator):
                raise TypeError("every element of the calculator sequence must be callable")
            return tuple(calculator)
        raise TypeError("`calculator` must be a callable or a non-empty sequence of callables")

    def _validate_args(
        self,
        individuals: Sequence[object],
        temperature: float,
        mode: Mode,
        generation: Optional[int],
    ) -> None:
        if temperature < 0:
            raise ValueError("`temperature` must be non-negative")
        if generation is not None and not isinstance(generation, int):
            raise TypeError("`generation` must be an int or None")
        if mode not in {"sampling", "random", "uniform"}:          # FIX: mode variable name
            raise ValueError(f"unknown mode {mode!r}")
        if not hasattr(individuals, "__len__"):                    # FIX: clearer check
            raise TypeError("`individuals` must be a sized container")

    @staticmethod
    def _build_temperature_array(n: int, base_t: float, mode: Mode) -> np.ndarray:
        if mode == "uniform":
            return np.linspace(0.0, 1.0, num=n, dtype=float)
        if mode == "random":
            return np.random.uniform(0.0, 1.0, size=n)
        # "sampling"
        return np.full(n, base_t, dtype=float)
        



