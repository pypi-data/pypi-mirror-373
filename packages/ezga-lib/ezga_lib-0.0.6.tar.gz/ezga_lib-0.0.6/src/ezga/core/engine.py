"""Main GA engine coordinating the evolutionary workflow.

The engine encapsulates the high-level control flow for one GA "agent".
It is the *only* place that defines the order of operations:

    selection → variation (mutation/crossover + immigrants) → simulation
    → evaluation (features/objectives) → survivor update → convergence check

Design notes:
  * SOLID-friendly: all stages depend on narrow interfaces (see .interfaces).
  * Latency hiding: physics is executed asynchronously via a thread pool.
  * Fault tolerance: validation and de-duplication filter problematic outputs
    without aborting the run; invalid structures are penalized and logged.

Threading model:
  - A single engine thread orchestrates stages and submits physics jobs.
  - Physical-model work is queued on a ThreadPoolExecutor (non-blocking).
  - `ctx.prev_future` carries the previous generation's physics Future.
"""
from __future__ import annotations

from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .interfaces import (
    IPopulation,
    IThermostat,
    IEvaluator,
    ISelector,
    IVariation,
    IGenerative,
    ISimulator,
    IConvergence,
    ILogger,
    IPlotter,
)

from ..io.resume import resume_if_possible
from .context import Context
from .config import GAConfig
from ..io.snapshot_recorder import GenerationSnapshotWriter

_TIMEOUT = 3600

class GeneticAlgorithm:
    """High-level GA coordinator (single agent).

    This class wires the modular stages and executes the per-generation loop.
    It assumes the heavy-cost physical model runs inside `ISimulator.run()`,
    which is overlapped with GA bookkeeping via a thread pool.

    Attributes:
      population: Repository of individuals plus partitioned views.
      thermostat: Temperature scheduler controlling exploration/exploitation.
      evaluator: Computes features and objectives for a set of individuals.
      selector: Parent-selection policy (e.g., Pareto, Boltzmann).
      variation: Mutation/crossover engine, including operator learning.
      generative: Optional immigrant source (DoE/BO/generative model).
      simulator: Physical-model driver (MD/relaxation/etc.).
      convergence: Convergence monitor with stall/novelty logic.
      logger: Structured logger that persists progress and diagnostics.
      plotter: Post-run plotting utility.
      ctx: Mutable run context (timers, generation state, caches).
      cfg: Static configuration (population sizes, limits, paths).
      _executor: Thread pool for asynchronous physics submission.
    """
    def __init__(
        self,
        population: IPopulation,
        thermostat: IThermostat,
        evaluator: IEvaluator,
        selector: ISelector,
        
        variation: IVariation,
        generative: IGenerative,
        simulator : ISimulator,
        convergence: IConvergence,

        logger: ILogger,
        plotter: IPlotter,

        cfg: GAConfig | None = None,
        ctx: Context | None = None,
    ) -> None:
        """Initializes the GA engine with modular components.

        Args:
          population: Population storage and partition manager.
          thermostat: Temperature controller.
          evaluator: Feature/objective evaluator.
          selector: Parent selector.
          variation: Mutation/crossover operator suite.
          generative: Immigrant generator (can be None if unused).
          simulator: Physical-model runner (MD + relaxation).
          convergence: Convergence detector.
          logger: Logger for progress and diagnostics.
          plotter: Plotting backend for final figures.
          cfg: Optional configuration; default `GAConfig()`.
          ctx: Optional context; default `Context()`.

        Side Effects:
          Creates a `ThreadPoolExecutor` for overlapping physics.

        Raises:
          ValueError: If mandatory dependencies are missing (defensive guard).
        """
        self.population = population
        self.thermostat = thermostat
        self.evaluator = evaluator
        self.selector = selector
        self.simulator = simulator
        self.variation = variation
        self.generative = generative

        self.convergence = convergence

        self.logger = logger
        self.plotter = plotter

        self.ctx = ctx or Context()
        self.cfg = cfg or GAConfig()

        # NOTE: Choose `max_workers` according to available devices.
        # The engine submits a *single* physics job per generation; if you
        # split physics internally (e.g., per-individual parallelism),
        # increase workers or delegate concurrency to `ISimulator`.
        self._executor = ThreadPoolExecutor(max_workers=8)

    # ------------------------------
    # Private helpers (stage blocks)
    # ------------------------------

    def load_population(self, ) -> None:
        """Loads or initializes the starting dataset from `IPopulation`.

        Expected to populate the 'dataset' partition and internal indices.

        Side Effects:
          - I/O: reads persisted individuals if present.
          - Logging: emits timing and status messages.
        """
        with self.ctx.timer("load data"):
            self.population.load_population(logger=self.logger)
            
            # Resume hook (keeps GA class clean)
            resume_if_possible(
                self.population, self.ctx, self.logger,
                enabled=getattr(self.cfg, "resume", True),
                mode=getattr(self.cfg, "resume_mode", "folders_all"),
            )

    def _evaluate(self, ) -> None:
        """Computes features and objectives for the current dataset.

        Sources:
          Uses the 'dataset' partition as the evaluation input.

        Stores:
          - `ctx.features` and `ctx.objectives` for subsequent stages.

        Performance:
          This call should be lightweight compared to physics; it often
          reuses results produced by `ISimulator.run()`.

        Raises:
          RuntimeError: if the evaluator fails unexpectedly.
        """
        with self.ctx.timer("Evaluation"):
            features, objectives = self.evaluator.evaluate_features_objectives( self.population.get_containers('dataset') )
            self.ctx.set_objectives(objectives)
            self.ctx.set_features(features)

    def _select(self, ) -> None:
        """Selects parents given current features/objectives and temperature.

        Stores:
          - Selection indices in `ctx.selection`.
          - 'selected' partition with chosen individuals.
        """
        with self.ctx.timer("selection"):
            self.selector.set_temperature( self.ctx.get_temperature() )
            objectives, features = self.ctx.get_objectives(), self.ctx.get_features()
            sel_idx = self.selector.select( objectives=objectives, features=features, )

            self.ctx.set_selection(sel_idx)
            population_selected = self.population.filter(name='dataset', idx=sel_idx)
            self.population.set_population(name='selected', population=population_selected)

    def _generate(self) -> None:
        """Produces candidate offspring and immigrants, then validates.

        Pipeline:
          1) Variation (mutation + crossover) on 'selected'.
          2) Optional immigration (DoE/BO/generative).
          3) Validation (schema/DoE/constraints).
          4) Self-collision pruning.

        Stores:
          - Overwrites 'selected' with validated current candidates.

        Notes:
          - Penalizes invalids via `variation.penalization`.
          - Logs filtered counts for traceability.
        """
        with self.ctx.timer("variation"):
            mutated_individuals, crossed_individuals, mutation_rate_array = (
                self.variation.apply_mutation_and_crossover(
                    individuals=self.population.get_containers('selected'), 
                    generation=self.ctx.generation, 
                    objectives=self.ctx.top_objectives,
                    temperature=self.ctx.temperature,
                )
            )
            current = mutated_individuals + crossed_individuals
        self.logger.info("Mutation and crossover completed. ")

        # Immigration (a.k.a. foreigners).
        with self.ctx.timer("Foreigners"):
            if self.ctx.foreigners > 0:
                # pull the current context values
                features = self.ctx.get_features()
                objectives = self.ctx.get_objectives()
                foreigners = self.ctx.foreigners
                temperature = self.ctx.temperature

                design_points = self.population.DoE.generate(
                    X=features,Y=objectives,n_candidates=foreigners,T=temperature
                )
                foreigners_individuals = (
                    self.generative.generate() 
                    if self.generative 
                    else self.variation.foreigners_generation(
                        structures=self.population.get_containers('template'), 
                        feature_func=self.evaluator.feature_func, 
                        design_points=design_points
                    )
                )
                current += foreigners_individuals
                self.logger.info("Foreigners generation completed. %i New individuals", len(foreigners_individuals) )
        
        with self.ctx.timer("validate"):
            features = self.evaluator.get_features(individuals=current)
            current_valid, current_invalid = self.population.validate_candidates(individuals=current, features=features)
            self.variation.penalization(individuals=current_invalid, process='out_of_doe')
            self.logger.info("Validate candidates completed. %i/%i Structures filtered.", len(current_invalid), len(current) ) 

        with self.ctx.timer("selfcollision"):
            current_total = len(current_valid)
            current_valid, current_invalid = self.population.filter_selfcollision(current_valid)
            self.variation.penalization(individuals=current_invalid, process='selfcollision')
            self.logger.info("Selfcollision check completed. %i/%i Structures filtered.", len(current_invalid), current_total )

        self.population.set_population(name='selected', population=current_valid)

    def _simulate(self, ):
        """Runs the physical model (MD/relax) on 'selected' and re-validates.

        Returns:
          List-like collection of *valid* post-physics individuals.

        Side Effects:
          - Writes per-generation simulation artifacts to disk.
          - Penalizes invalid candidates (out-of-DoE, hash/self collisions).
          - Updates 'current_valid' partition.
          - Exports validated structures under `output_path/generation/gen{g}`.
        """
        current = self.population.get_containers('selected')

        with self.ctx.timer(f"simulator{self.ctx.generation}"):
            current = self.simulator.run(
                individuals=current,
                temperature=self.ctx.temperature,
                generation=self.ctx.generation,
                output_path=self.population.output_path,
            )

        with self.ctx.timer("validate"):
            features = self.evaluator.get_features(individuals=current)
            current_valid, current_invalid = self.population.validate_candidates(individuals=current, features=features)
            self.variation.penalization(individuals=current_invalid, process='out_of_doe')
            self.logger.info("Validate candidates completed. %i/%i Structures filtered.", len(current_invalid), len(current) ) 
 
        with self.ctx.timer("hash_collisions"):
            current_total = len(current_valid)
            current_valid, current_invalid = self.population.filter_hash_collisions(current_valid)
            self.variation.penalization(individuals=current_invalid, process='hash_collision')
            self.logger.info("Hash collisions check completed. %i/%i Structures filtered.", len(current_invalid), current_total ) 

        with self.ctx.timer("selfcollision"):
            current_total = len(current_valid)
            current_valid, current_invalid = self.population.filter_selfcollision(current_valid)
            self.variation.penalization(individuals=current_invalid, process='selfcollision')
            self.logger.info("Selfcollision check completed. %i/%i Structures filtered.", len(current_invalid), current_total ) 

        self.population.set_population( name='current_valid', population=current_valid )
        self.population.export_structures( partition=self.population.get_partitions('current_valid'), file_path=f"{self.population.output_path}/generation/gen{self.ctx.generation}" )

        return current_valid

    def _agent_sync(self, ):
        """Pulls migrants from the shared mailbox and merges unique ones.

        Logic:
          - Pull candidate migrants via `population.agent_sync()`.
          - Drop duplicates via hash collision check (no rehashing).
          - Append uniques to 'current_valid'.

        Notes:
          Content-addressed digests ensure idempotent ingestion.
        """
        with self.ctx.timer("agent_sync"):
            self.logger.info("Exported %d structures to common genetic pool via HashBatchSync.", self.population.get_partitions('current_valid').size )
            individuals_candidates = self.population.agent_sync( self.population.get_partitions('current_valid').containers )
            unique_structures, not_unique_structures = self.population.filter_hash_collisions(individuals=individuals_candidates, force_rehash=False)
            self.logger.info("Genetic injection: %d structures added to dataset (Gen=%d).", len(unique_structures), self.ctx.generation, )
            self.population.get_partitions('current_valid').add(unique_structures)

    def _update_dataset(self, ):
        """Moves validated current individuals into the persistent dataset.

        Source:
          - 'current_valid' partition.

        Destination:
          - 'dataset' partition (archive for selection/evaluation/persistence).
        """
        with self.ctx.timer("Update_dataset"):
            individuals_new_valid = self.population._partitions['current_valid'].containers

            self.population.update_main_dataset(
                unique_structures=individuals_new_valid,
                generation=self.ctx.generation,
                features_prev=self.ctx.get_features(),
                objectives_prev=self.ctx.get_objectives(),
            )

    def _check_convergence(self, ):
        """Updates convergence status using the configured monitor.

        Populates in `ctx`:
          - `is_converge`: bool
          - `stagnation`: int (stall counter)

        Logging:
          Emits a single-line status with improvement flag, stall counters,
          convergence boolean, and generation elapsed time.
        """
        with self.ctx.timer("convergence"):

            self.convergence.check(
                generation=self.ctx.generation,
                objectives=self.ctx.get_objectives(),
                features=self.ctx.get_features(),
            )
            self.ctx.is_converge = self.convergence.is_converge()
            self.ctx.stagnation = self.convergence.get_stagnation()
            # {self._no_improvement_count_information}/{self._stall_threshold} (info)

        self.logger.info(
            "[Gen=%d] improvement=%s, stall_count=%d/%d (obj), converged=%s, time=%.2f s",
            self.ctx.generation,                       # %d
            self.convergence.improvement_found(),      # %s → “True” or “False”
            self.convergence.get_stagnation(),         # %d
            self.convergence._stall_threshold,         # %d
            self.ctx.is_converge,                      # %s → “True” or “False”
            self.ctx.elapsed('generation')            # %.2f
        )

    def _save_stats(self, ):
        """Flushes timers/metrics; hook to persist run-time stats.

        Notes:
          Extend this method to persist per-generation KPIs, operator usage,
          temperature schedule, and feature/obj snapshots for post-hoc analysis.
        """
        with self.ctx.timer("Save_stats"):
            
            GenerationSnapshotWriter.save_generation(
                population=self.population,
                convergence=self.convergence,
                variation=self.variation,
                ctx=self.ctx,
                output_dir=self.population.output_path,
                tag="full",  # or "post-sim", "selection", etc. if you want multiple phases
            )
            self.ctx.clear_timers()


    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def run(self, ):
        """Executes the full GA workflow for one agent.

        Control flow:
          - Load/initialize population.
          - For each generation:
              * Update temperature (thermostat).
              * Evaluate features/objectives on the dataset.
              * Adjust mutation probabilities (operator learning).
              * Select parents; generate offspring/immigrants; validate.
              * Finalize previous physics; submit next physics asynchronously.
              * Migrate, update dataset, check convergence, log & plot.
              * Early-break if converged (stop queuing further physics).
          - Finalize last pending physics if needed.
          - Export final dataset and plots.

        Returns:
          The final `IPopulation` (with persisted 'dataset' and artifacts).

        Raises:
          RuntimeError: Bubbling up unexpected stage failures; individual
            structure-level failures should be filtered/penalized, *not* raise.
        """
        self.logger.info("Workflow started.")
        self.ctx.start_timer('engine')   # Start overall workflow timer

        # (Optional) tame native thread pools to reduce teardown issues
        import os
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        os.environ.setdefault("MKL_NUM_THREADS", "1")
        os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
        os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

        self.load_population()
        # --- Compute effective start generation here (cfg stays immutable) ---
        start_gen = max(
            getattr(self.ctx, "generation", self.cfg.initial_generation),
            self.cfg.initial_generation,
        )
        max_gen = self.cfg.max_generations
        if start_gen != self.cfg.initial_generation:
            self.logger.info(
                "Resuming at generation %d (configured initial_generation=%d).",
                start_gen, self.cfg.initial_generation
            )

        self.ctx.start_timer('generation')
        self.ctx.prev_future = None
        self.ctx.break_early = False

        try:
            for generation in range(start_gen, max_gen + 1):
                self.logger.info(f"--- Generation {generation}/{self.cfg.max_generations} (Pop { self.population.size('dataset') }) ---")
                self.ctx.set_generation(generation)

                # 1) Thermostat
                self.ctx.temperature = self.thermostat.update(
                    generation=generation, 
                    stall=self.convergence._no_improvement_count
                )

                # 2) GA pipeline BEFORE simulation
                self._evaluate()
                self.variation.adjust_mutation_probabilities(population=self.population, ctx=self.ctx, )
                self._select()
                self._generate()

                # 3) Finalize previous physics (blocks until done)
                if self.ctx.prev_future:

                    # 10) Queue physics for current generation
                    #self.ctx.prev_future = self._executor.submit(self._simulate)

                    #self.population.set_population(name='current', population=self.ctx.prev_future.result() )

                    try:
                        prev_result = self.ctx.prev_future.result(timeout=_TIMEOUT)
                    except Exception as exc:
                        # Robust handling: log and penalize, but keep GA alive
                        import traceback
                        self.logger.exception("Physics job from Gen %d failed: %s\n%s",
                                             self.ctx.generation - 1, exc, traceback.format_exc())
                        prev_result = []  # or a safe empty list

                    self.population.set_population(name='current', population=prev_result)

                    # Queue physics for current generation ASAP to overlap with bookkeeping
                    self.ctx.prev_future = self._executor.submit(self._simulate)

                    # Post-physics bookkeeping for the generation we just finalized
                    self._agent_sync()
                    self._update_dataset()
                    self._check_convergence()

                    # 9) Logging
                    self.ctx.stop_timer('generation')
                    self._save_stats()
                    self.ctx.start_timer('generation')

                    if self.ctx.is_converge:
                        self.logger.info(f"Convergence reached at generation {self.ctx.generation-1}.")
                        self.ctx.break_early = True
                else:
                    # 10) Queue physics for current generation
                    self.ctx.prev_future = self._executor.submit(self._simulate)

                # If converged, stop queuing further physics
                if self.ctx.break_early:
                    # Optionally cancel the just-queued physics if the config says so
                    if False and self.ctx.prev_future and not self.ctx.prev_future.done():
                        self.logger.info("Cancelling queued physics for Gen %d due to convergence.", self.ctx.generation)
                        self.ctx.prev_future.cancel()
                    break

            # Finalize the last pending physics if not converged
            if self.ctx.prev_future and not self.ctx.prev_future.cancelled():
                try:
                    final_result = self.ctx.prev_future.result(timeout=_TIMEOUT)
                except Exception as exc:
                    import traceback
                    self.logger.exception("Final physics job failed: %s\n%s", exc, traceback.format_exc())
                    final_result = []
                self.population.set_population(name='current', population=final_result)

                self._agent_sync()
                self._update_dataset()
                self._check_convergence()
            
            self.ctx.stop_timer('engine')
            self._save_stats()
            
            # Final exports
            self.population.export_structures(
                partition=self.population.get_partitions('dataset'),
                file_path=f"{self.population.output_path}"
            )
            self.logger.info("Workflow completed in %.2f s.", self.ctx.elapsed('engine'))
            return self.population

        finally:
            # Ensure the executor is always cleaned up
            try:
                self._executor.shutdown(wait=True, cancel_futures=True)
            except Exception:
                pass






