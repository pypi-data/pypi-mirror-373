# SPDX-License-Identifier: GPL-3.0-only

"""Factory helpers to build a fully wired GeneticAlgorithm from config.

This module centralizes two user-facing primitives:

* :func:`load_config` — convert user configuration (YAML path or dict) into a
  validated :class:`GAConfig`. When a path is provided, it delegates to the
  YAML loader under :mod:`ezga.io.config_loader` so you reuse the same parsing,
  validation, and dotted-path resolution logic across CLI and notebooks.

* :func:`build_default_engine` — instantiate all concrete components (population,
  thermostat, evaluator, selector, variation, simulator, convergence, logger,
  plotter), wire them together, and return a ready-to-run
  :class:`~ezga.core.engine.GeneticAlgorithm`.

Design goals:
  - Keep the engine constructor free of wiring/DI concerns.
  - Provide explicit dependency-injection points (overrides) for testing or
    experiments without editing the core pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union, Type
import warnings

from ezga.core.engine import GeneticAlgorithm
from ezga.core.config import GAConfig
from ezga.core.context import Context
from ezga.core.population import Population

from ezga.core.interfaces import (
    IPopulation, IThermostat, IEvaluator, ISelector, IVariation, ISimulator, 
    IConvergence, IHash, IAgent, IDoE, ILineage, ILogger, IPlotter
)

# --- Import your real implementations here ---
from ezga.thermostat.thermostat import Thermostat  # type: ignore
from ezga.selection.selector import Selector       # type: ignore
from ezga.variation.variation import Variation_Operator  # type: ignore
from ezga.evaluator.evaluator import Evaluator     # type: ignore
from ezga.simulator.simulator import Simulator     # type: ignore
from ezga.convergence.convergence import Convergence  # type: ignore
from ezga.utils.logger import WorkflowLogger       # type: ignore
from ezga.utils.lineage import LineageTracker      # type: ignore
from ezga.utils.structure_hash_map import Structure_Hash_Map  # type: ignore
from ezga.visualization.plotter import Plotter     # type: ignore
from ezga.sync.agenticsync import Agentic_Sync     # type: ignore

# YAML path loading & dotted-path resolution are delegated here
from ezga.io.config_loader import load_config_yaml

ConfigInput = Union[str, Path, Dict[str, Any]]
__all__ = ["load_config", "build_default_engine"]

def load_config(source: ConfigInput) -> GAConfig:
    """Create a validated :class:`GAConfig` from YAML path or Python dict.

    If ``source`` is a string/Path, it is interpreted as a YAML file and parsed
    via :func:`ezga.io.config_loader.load_config_yaml` (which also resolves
    dotted callable references). If ``source`` is a dict, it is validated
    directly using Pydantic.

    Args:
      source: YAML file path or a Python dict matching the GAConfig schema.

    Returns:
      A validated :class:`GAConfig` instance.

    Raises:
      SystemExit: If the YAML fails validation (the loader prints a friendly
        error message and exits).
      TypeError: If ``source`` is neither a path-like nor a dict.
    """
    if isinstance(source, (str, Path)):
        return load_config_yaml(source)  # parsea + valida + resuelve import strings
    if isinstance(source, dict):
        return GAConfig.model_validate(source)
    raise TypeError(...)

def _make_component(value: Any, cls: Type, **kwargs) -> Any:
    """
    """
    import inspect
    # Already an instance
    if isinstance(value, cls):
        return value
    # Determine which class to instantiate
    if value is None:
        Klass = cls
    elif inspect.isclass(value):
        Klass = value
    else:
        raise TypeError(f"Override must be a {cls.__name__} subclass or instance, got {type(value)}")
    return Klass(**kwargs)

def build_default_engine(
    cfg: GAConfig,
    *,
    # ---------- overrides (dependency-injection points) ---------- #
    lineage: Type[ILineage] = LineageTracker,
    hash_map: Type[IHash] = Structure_Hash_Map,
    agent: Type[IAgent] = Agentic_Sync,
    population: Optional[Union[Type[IPopulation], IPopulation]] = Population,
    thermostat: Type[IThermostat] = Thermostat,
    evaluator: Type[IEvaluator] = Evaluator,
    selector:  Type[ISelector]  = Selector,
    variation: Type[IVariation] = Variation_Operator,
    simulator: Type[ISimulator]  = Simulator,
    convergence: Type[IConvergence] = Convergence,
    logger: Type[ILogger] = WorkflowLogger,
    plotter: Type[IPlotter] = Plotter,
    # -------------------------------------------------------------- #
    ctx: Optional[Context] = None,
    ) -> GeneticAlgorithm:
    """Instantiate the default components and return a ready GeneticAlgorithm.

    Replace the placeholders with your actual component constructors or factories.
    """
    debug = cfg.debug
    rng = cfg.rng

    lineage = lineage()
    hash_map = _make_component(hash_map, Structure_Hash_Map, **cfg.hashmap.model_dump())

    agent = _make_component(agent, Agentic_Sync,**cfg.agentic.model_dump())

    population = _make_component(
        population, Population,
        debug                            = cfg.debug,
        output_path                      = cfg.output_path,
        hash_map                         = hash_map,
        agent                            = agent,
        lineage                          = lineage,
        **cfg.population.model_dump()
    )

    # 2) Core services
    thermostat = _make_component(thermostat, Thermostat, **cfg.thermostat.model_dump() )
    evaluator = _make_component(evaluator, Evaluator, **cfg.evaluator.model_dump() )
    try:
        population.DoE.set_name_mapping( evaluator.features_funcs.get_feature_index_map() )
    except Exception as e:
        warnings.warn(f"Skipping name mapping: {e}")  
          
    selector = _make_component(selector, Selector, **cfg.multiobjective.model_dump())

    #simulator = _make_component(simulator, Simulator, **cfg.simulator.model_dump())
    sim_kwargs = cfg.simulator.model_dump(exclude={'calculator'}, exclude_none=True)
    simulator = _make_component(
        simulator, Simulator,
        **sim_kwargs,
        calculator=cfg.simulator.calculator,  # <- aquí preservamos el callable
    )
    
    variation = _make_component(
        variation, Variation_Operator, 
        lineage=lineage, 
        mutation_funcs=cfg.mutation_funcs,
        crossover_funcs=cfg.crossover_funcs,
        **cfg.variation.model_dump())
    convergence = _make_component(convergence, Convergence, **cfg.convergence.model_dump())

    logger = logger.setup_logger('EZGA engine', cfg.output_path)
    ctx = Context(rng_seed=rng)
    plotter = Plotter()

    generative = cfg.generative_model

    engine = GeneticAlgorithm(
        population=population,
        thermostat=thermostat,
        evaluator=evaluator,
        selector=selector,
        simulator=simulator,
        variation=variation,
        generative=generative,
        convergence=convergence,
        logger=logger,
        plotter=plotter,
        cfg=cfg,
        ctx=ctx,
    )

    return engine