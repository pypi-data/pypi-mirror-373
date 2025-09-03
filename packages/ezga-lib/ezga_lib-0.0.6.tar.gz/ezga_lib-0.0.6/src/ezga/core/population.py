from __future__ import annotations

import os
import time
import copy
import logging
import warnings
import numpy as np
import json  # Added for parameter logging
from typing import List
from sage_lib.partition.Partition import Partition

from ezga.core.interfaces import (
    IPopulation, ILineage, IHash, IAgent, IDoE
)

from ezga.utils.lineage import LineageTracker  # type: ignore
from ezga.utils.structure_hash_map import Structure_Hash_Map # type: ignore
from ezga.sync.agenticsync import Agentic_Sync
from ezga.DoE.DoE import DesignOfExperiments

class Population(IPopulation):
    """
    """

    def __init__(
        self,
        *,
        dataset_path: str | None = None,
        template_path: str | None = None,
        output_path: str | None = None,
        collision_factor: float | None = None,
        filter_duplicates: bool | None = True,
        size_limit: float | None = None,

        debug: bool = False,
        hash_map: Type[IHash] = Structure_Hash_Map,
        agent: Type[IAgent] = Agentic_Sync,
        lineage: Type[ILineage] = LineageTracker,

        constraints = None,
        ef_bounds: Tuple[float, float] | None = (-1e-6, 1e5),  # Pontetial units/atom bounds (typical GGAs)
        #initialization = None,
    ):
        """
        Initializes the Population with file paths and default parameters.

        Parameters
        ----------
        dataset_path : str
            Path to the initial structures file.
        template_path : str
            Path to the template structure file.
        output_path : str
            Directory to save output files and logs.
        """
        self._dataset_path = 'config.xyz' if dataset_path is None else dataset_path
        self._template_path = None if template_path is None else template_path 
        self._output_path = '.' if output_path is None else output_path
        self.collision_factor = collision_factor
        self._filter_duplicates = filter_duplicates
        self.size_limit = size_limit
        self.ef_bounds = ef_bounds

        self.debug = debug

        # Placeholder for Partition objects
        self._partitions = {
            'template':None,
            'dataset':None,
            'generation':None,
            'template_preload':None,
            'dataset_preload':None,
        }  # Should be set by load_population()

        self.hash_map   = hash_map
        self.agent      = agent
        self.lineage    = lineage
        self.DoE        = DesignOfExperiments(constraints=constraints)

    # ----------------------------------------------------------------
    # GETTERS/SETTERS
    # ----------------------------------------------------------------
    @property
    def dataset_path(self):
        """Gets the file path for the initial structures."""
        return self._dataset_path

    @dataset_path.setter
    def dataset_path(self, value):
        """Sets the file path for the initial structures."""
        self._dataset_path = value

    @property
    def template_path(self):
        """Gets the template file path."""
        return self._template_path

    @template_path.setter
    def template_path(self, value):
        """Sets the template file path."""
        self._template_path = value

    @property
    def output_path(self):
        """Gets the output directory path."""
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        """Sets the output directory path."""
        self._output_path = value

    @property
    def partitions(self):
        """Gets the dictionary of partition objects."""
        return self._partitions

    def get_partitions(self, name:str):
        """Gets the dictionary of partition objects."""
        return self._partitions[name]

    def get_containers(self, name:str):
        """Gets the dictionary of partition objects."""
        if name in self._partitions:
            return self._partitions[name].containers

        return None

    def set_partitions(self, name:str, partition:object=None):
        """Gets the dictionary of partition objects."""
        self._partitions[name] = partition if partition else Partition()
        return self._partitions[name]

    def size(self, name:str=None):
        """
        """
        return self._partitions[name].size if name else self._partitions['dataset'].size
 
    def filter(self, name:str, idx:list):
        """
        """
        return copy.deepcopy([self.partitions[name].containers[i] for i in idx])

    def set_population(self, name:str, population:list) -> bool:
        """
        """
        self.set_partitions( name, Partition() )
        self._partitions[name].add( population )

        return True

    # ----------------------------------------------------------------
    # LOAD
    # ----------------------------------------------------------------
    def load_population(self, logger:object = None): 
        """
        """

        # ------------------------------------------------------------------
        # 0)  Book‑keeping: log start‑up and start a wall‑clock timer
        # ------------------------------------------------------------------
        if logger:
            logger.info("Loading partitions from files.")

        # ------------------------------------------------------------------
        # 1)  DATASET PARTITION ------------------------------------------------
        # ------------------------------------------------------------------
        # 1.1  Always create an *empty* Partition object first so that we have a
        #      valid container even if subsequent file I/O fails.  This avoids
        #      having to repeat *None* checks later on.
        self.set_partitions( 'dataset', Partition() )

        # 1.2  If the caller provided a valid *path* (and not, e.g., ``None`` or
        #      an already‑opened file object), read the structure files.
        if isinstance(self.dataset_path, str):
            self._partitions['dataset'].read_files(
                file_location=self.dataset_path,
                #source='xyz',
                verbose=True
            )

        # 1.3  Merge any *pre‑loaded* containers (prepared by the caller before
        #      invoking this method) into the freshly created partition.
        if isinstance(self._partitions['dataset_preload'], list):
            self._partitions['dataset'].add( self._partitions['dataset_preload'] )

        # 1.4  Feed every single *Structure* object into the global hash map so
        #      that the rest of the code base can perform O(1) look‑ups for
        #      de‑duplication or collision tracking.
        for container in self._partitions['dataset'].containers:
            self.hash_map.add_structure( container )

        # 1.5  If we are running in *synchronised* mode (i.e., multiple workers
        #      on different nodes), pull the current batch of structures from
        #      the synchronisation backend and add only the ones that do *not*
        #      produce a hash collision.
        if self.agent.active():
            sync_new = list(self.agent.get_batch())
            containers_list = [];  [containers_list.extend(sub.containers) for _, sub in sync_new]
            unique_structures, not_unique_structures = self.filter_hash_collisions(individuals=containers_list, force_rehash=False)
            self._partitions['dataset'].add_container( unique_structures )

            logger.info(
                "Genetic injection: %d structures added to dataset (Gen=%d).",
                len(unique_structures),         
                0,                                            
            )

        # ------------------------------------------------------------------
        # 2)  TEMPLATE PARTITION ---------------------------------------------
        # ------------------------------------------------------------------
        # 2.1  Create an empty partition exactly as was done for the dataset.
        self._partitions['template'] = Partition()
        if isinstance(self.template_path, str):
            self._partitions['template'].read_files(
                file_location=self.template_path,
                source='xyz',
                verbose=True
            )
        else:
            logger.info("No template file provided, skipping template partition.")
        if isinstance(self._partitions['template_preload'], list):
            self._partitions['template'].add_container( self._partitions['template_preload'] )

        # ------------------------------------------------------------------
        # 3)  RECORD LINEAGE ---------------------------------------------------
        # ------------------------------------------------------------------
        # Every *Structure* gets tagged with lineage metadata so that its origin
        # can be traced throughout the workflow.  Stage‑index *0* indicates the
        # very first step; the empty list is the parent set, and the string
        # "initialization" becomes the *event* label.
        self.lineage.assign_lineage_info_par_partition(
            self._partitions['dataset'],     # partition to annotate
            0,                              # stage index generation
            [],                             # parent UIDs (none at this point)
            "initialization"                # event label
        )

        logger.info(f"Partitions loaded successfully.")

    def export_structures(self, partition, file_path: str, sort: bool=False, key:int=0):
        """
        Export structures in the given partition to the specified file path.

        Parameters
        ----------
        partition : Partition
            Partition containing the structures to export.
        file_path : str
            Output directory to store the exported structure files.
        sort : bool
        """
        os.makedirs(file_path, exist_ok=True)

        if sort:
            objectives = evaluate_objectives(partition.containers, self.objective_funcs)
            for container, objective in zip(partition.containers, objectives):
                apm = container.AtomPositionManager
                if not isinstance(getattr(apm, 'metadata', None), dict):
                    apm.metadata = {}
                apm.metadata['objectives'] = list(objective)

            numeric_objectives = np.array([float(obj[key]) for obj in objectives])
            sorted_indices = np.argsort(numeric_objectives, kind='mergesort')
            partition.containers = [partition.containers[i] for i in sorted_indices]

        partition.export_files(
            file_location=f"{file_path}",
            source='xyz',
            label='enumerate',
            verbose=True
        )

        return True

    def agent_sync(self, containers:list) -> list:
        """
        """
        if self.agent.active():
            # ---
            self.agent.append( containers )


            # ---
            sync_new = list(self.agent.get_batch())
            containers_list = [];  [containers_list.extend(sub.containers) for _, sub in sync_new]

            return containers_list

        return []

    def validate_candidates(self, individuals: list, features: np.array) -> list:
        """
        Validate candidate individuals based on their composition in feature space.

        This method computes feature descriptors for each candidate structure using the provided
        feature functions (self.features_funcs) and then validates each candidate by applying the
        design validator (self.DoE.validate). The validator returns True if the candidate's features
        satisfy the design requirements and False otherwise.

        Parameters
        ----------
        individuals : list
            A list of candidate structure objects to be validated.

        Returns
        -------
        list
            A list of candidate individuals that meet the feature space requirements.
        """

        # 2) Local bindings for speed
        validate = self.DoE.validate if self.DoE else lambda *args, **kwargs: True

        # 3) Single pass: build valid list and penalise invalid
        valid_candidates = []
        physically_invalid_candidates = []
        out_of_doe_candidates = []

        for struct, feat in zip(individuals, features):
            # 1) DOE‐validation check
            if not self.DoE.validate(features=feat):
                out_of_doe_candidates.append(struct)
                continue  # skip to next structure

            # 2) Physical‐sanity check
            apm = struct.AtomPositionManager
            if apm.E and self.ef_bounds[0] <= apm.E / apm.atomCount <= self.ef_bounds[1]:
                physically_invalid_candidates.append(struct)
                continue

            valid_candidates.append(struct)

        # 3a) Export any out_of_doe invalid individuals
        if out_of_doe_candidates:
            invalid_partition = Partition()
            invalid_partition.add_container( out_of_doe_candidates )
            self.export_structures(
                invalid_partition,
                f'{self.output_path}/out_of_doe'
            )

        # 3b) Export any physically invalid individuals
        if physically_invalid_candidates:
            invalid_partition = Partition()
            invalid_partition.add_container( physically_invalid_candidates )
            self.export_structures(
                invalid_partition,
                f'{self.output_path}/not_valid'
            )

        return valid_candidates, out_of_doe_candidates+physically_invalid_candidates 


    def filter_hash_collisions(self, individuals:list, force_rehash:bool=True):
        """
        Filters out individuals that collide in the hash map (i.e., duplicates).

        Parameters
        ----------
        individuals : list
            List of candidate individuals after the physical model.

        Returns
        -------
        unique_structures : list
            Structures that are unique (not in the hash map).
        """

        def _composition_key(comp: dict) -> str:
            """
            Return a deterministic, reduced-formula key such as 'C1-H1-N1-O2'
            for any integer multiple - e.g. both {'C':2,'H':2,'N':2,'O':4}
            and {'C':6,'H':6,'N':6,'O':12} collapse onto the same key.

            • Counts **must** be non-negative integers.  If you store floats,
              cast/round them beforehand.
            • Element order is alphabetical to keep the key canonical.
            """
            counts = [int(comp[el]) for el in comp]
            g = 1 #reduce(gcd, counts) or 1                       # robust gcd
            return "-".join(
                f"{el}{int(comp[el] // g)}"                    # always include ‘1’
                for el in sorted(comp)
            )

        if not self._filter_duplicates:
            return individuals

        unique_structures = []
        not_unique_structures = []
        for individual in individuals:
            if self.hash_map.add_structure(individual, force_rehash=force_rehash):
                unique_structures.append(individual)
                continue
                
            elif force_rehash:
                partition = Partition()
                partition.add_container(individual)
                
                comp_key = _composition_key(individual.AtomPositionManager.atomCountDict)
                self.export_structures(
                    partition=partition,
                    file_path=f'{self._output_path}/basin/{comp_key}/{individual.AtomPositionManager.metadata["hash"]}',
                )

            not_unique_structures.append(individual)

        return unique_structures, not_unique_structures


    def filter_selfcollision(self, individuals):
        """
        Filters out individuals that have self-collision above the collision factor threshold.

        Parameters
        ----------
        individuals : list
            List of candidate individuals to filter.

        Returns
        -------
        non_colliding : list
            Filtered list of individuals without self-collisions.
        """
        if self.collision_factor < 1e-6:
            return individuals

        # 1) Compute collision mask in one pass (C-optimized list comp)
        mask = [
            s.AtomPositionManager.self_collision(factor=self.collision_factor)
            for s in individuals
        ]

        # 2) Use mask to filter in C-level loops
        non_colliding = [s for s, m in zip(individuals, mask) if not m]
        colliding = [s for s, m in zip(individuals, mask) if m]

        # 3) Export invalid individuals, if any
        if colliding:
            partition = Partition()
            partition.add_container( colliding )
            self.export_structures(
                partition,
                f"{self.output_path}/colliding"
            )

        return non_colliding, colliding


    def update_main_dataset(
        self,
        unique_structures: list,
        generation: int,
        features_prev: np.ndarray,
        objectives_prev: np.ndarray,
    ) -> bool:
        """
        Updates the main dataset with new structures and records the structure IDs and generations.

        Parameters
        ----------
        unique_structures : list
            Newly generated unique structures.
        generation : int
            Current generation index.
        """

        cap  = self.size_limit
        ds   = self.partitions["dataset"]

        if not cap is None:
            # --- Global size population control --------------------------
            needed_size = ds.size + len(unique_structures)
            if needed_size > cap: 
                excess = needed_size - cap

                # --- Rank only the *old* population --------------------------
                w       = np.ones(objectives_prev.shape[1])
                scores  = objectives_prev @ w                  # lower = better
                idx_bad = np.argsort(scores)[-excess:]         # worst performers

                # Build keep / discard lists
                old_containers   = list(ds.containers)
                discard_structs  = [old_containers[i] for i in idx_bad]
                keep_structs_old = [
                    c for i, c in enumerate(old_containers) if i not in idx_bad
                ]

                # Export the overflow
                if discard_structs:
                    overflow = Partition()
                    overflow.add_container(discard_structs)
                    overflow.export_files(
                        file_location=f"{self.output_path}/config_overflow",
                        source="xyz",
                        label="enumerate",
                        verbose=True,
                    )

                # Replace the dataset with survivors
                ds.set_container(keep_structs_old)

        # --- 2) Insert the new generation (always survives) -------------- ###
        ds.add(unique_structures)

        return True