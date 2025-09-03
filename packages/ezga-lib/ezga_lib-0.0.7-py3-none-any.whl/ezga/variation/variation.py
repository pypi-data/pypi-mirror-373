# mutation_crossover_handler.py
import copy
import random
import numpy as np
from typing import List, Any, Optional, Union
import time
from ..utils.helper_functions import solver_integer_local, fitness_factor
import unittest
from ..core.interfaces import IVariation

class Variation_Operator(IVariation):
    """
    A class encapsulating the mutation and crossover workflow, 
    along with associated utility methods.
    """

    def __init__(self, 
        mutation_funcs: list = None, 
        crossover_funcs: list = None, 
        initial_mutation_rate: int = 1, 
        min_mutation_rate: int = 1,
        max_prob: float = 1,
        min_prob: float = .001,
        use_magnitude_scaling: bool = True, 
        alpha: float = 0.1,
        crossover_probability: float = 0.2, 
        lineage:object = None, 
        logger:object = None, 
        debug:bool =False,
        rng_seed: Optional[int] = None
    ):
        """
        Parameters
        ----------
        lineage_tracker : object
            Object responsible for tracking lineages (assign_lineage_info, etc.).
        logger : object
            Logging object with at least .info(...) available.
        mutation_rate_params : dict, optional
            Parameters controlling the mutation rate, by default None.
        debug : bool, optional
            If True, enables debug prints, by default False.
        """
        self.lineage_tracker = lineage
        self.logger = logger

        self.crossover_rate = 1
        self.debug = debug

        self.mutation_funcs = mutation_funcs or []
        self.crossover_funcs = crossover_funcs or []

        # Track usage and success/failure of each mutation function
        self._mutation_attempt_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_fails_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_success_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_unsuccess_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_hashcolition_counts = np.zeros(len(self.mutation_funcs), dtype=int)
        self._mutation_outofdoe_counts = np.zeros(len(self.mutation_funcs), dtype=int)

        self._initial_mutation_rate = initial_mutation_rate
        self._min_mutation_rate = min_mutation_rate

        # Initialize uniform probabilities for each mutation function
        if len(self.mutation_funcs) > 0:
            self._mutation_probabilities = np.ones(len(self.mutation_funcs),  dtype=float) / max(1, len(self.mutation_funcs))
        else:
            self._mutation_probabilities = []

        self._max_prob = max_prob
        self._min_prob = min_prob
        self._use_magnitude_scaling = use_magnitude_scaling
        self._alpha = alpha
        self.min_alpha, self.max_alpha = 0.00001, 0.1

        # Track usage and success/failure of each mutation function
        self._crossover_attempt_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_fails_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_success_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_unsuccess_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_hashcolition_counts = np.zeros(len(self.crossover_funcs), dtype=int)
        self._crossover_outofdoe_counts = np.zeros(len(self.crossover_funcs), dtype=int)

        self._crossover_probability = crossover_probability

        # Initialize uniform probabilities for each mutation function
        if len(self.crossover_funcs) > 0:
            self._crossover_probabilities = np.ones(len(self.crossover_funcs), dtype=float) / max(1, len(self.crossover_funcs))
        else:
            self._crossover_probabilities = []

        self._mutation_feature_effects = None

        self._rng = np.random.default_rng(rng_seed)

    @property
    def mutation_feature_effects(self):
        """Gets the _mutation_feature_effects."""
        return self._mutation_feature_effects


    def clamp_and_renormalize(self, probabilities: np.ndarray, *,inplace: bool = False) -> np.ndarray:
        r"""
        Clamp all probability values into a specified range and renormalize to unit sum.

        This method ensures each entry of the input array lies within the interval
        \\([p_{\\min},\\,p_{\\max}]\\) and that the resulting vector sums to 1.  All
        operations are done efficiently, with optional in‐place modification.

        **Steps**:

        1. **Select working array**  
           .. code-block:: python
              arr = probabilities                      # if inplace
              arr = probabilities.copy()               # otherwise

        2. **Clamping**  
           Clamp each element \\(p_i\\) into the interval \\([p_{\\min},p_{\\max}]\\):  
           .. math::
              p_i' = 
              \begin{cases}
                p_{\\min}, & p_i < p_{\\min}, \\\\
                p_i,       & p_{\\min} \\le p_i \\le p_{\\max}, \\\\
                p_{\\max}, & p_i > p_{\\max}.
              \end{cases}

           Implemented via  
           ```python
           np.clip(arr, self._min_prob, self._max_prob, out=arr)
           ```

        3. **Normalization**  
           Compute the total mass  
           .. math::
              S = \sum_{i} p_i'
           If \\(S > \\epsilon\\) (with \\(\\epsilon=1\\times10^{-12}\\)), scale each entry:  
           .. math::
              \tilde p_i = \frac{p_i'}{S}.
           This guarantees \\(\sum_i \tilde p_i = 1\\).  

        :param probabilities:
            1D array of non‐negative values to be clamped and normalized.
        :type probabilities: numpy.ndarray
        :param inplace:
            If ``True``, perform clamping and normalization directly on
            the input array; otherwise operate on a copy.
        :type inplace: bool
        :returns:
            Array of the same shape, with each element in
            \\([p_{\\min},p_{\\max}]\\) and summing to 1.
        :rtype: numpy.ndarray
        """

        # --- Coerce and early exits ------------------------------------------------
        arr = np.asarray(probabilities, dtype=float)
        arr = arr if inplace else arr.copy()
        arr = arr.ravel()  # ensure 1-D

        n = arr.size
        if n == 0:
            return arr  # empty-safe

        # Replace non-finite with 0 before clamping
        np.nan_to_num(arr, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

        # --- Sanity/fixup for bounds ----------------------------------------------
        min_p = float(getattr(self, "_min_prob", 0.0))
        max_p = float(getattr(self, "_max_prob", 1.0))
        if min_p < 0.0:   min_p = 0.0
        if max_p <= 0.0:  max_p = 1.0
        if min_p > max_p: min_p, max_p = max_p, min_p

        # Check feasibility: there exists a vector in [min_p, max_p]^n that sums to 1 iff
        #   n*min_p <= 1 <= n*max_p
        feasible = (n * min_p <= 1.0 + 1e-12) and (n * max_p >= 1.0 - 1e-12)

        if not feasible:
            # Fall back to a valid simplex projection ignoring bounds:
            # - make nonnegative, renormalize; if all zero -> uniform
            arr[arr < 0.0] = 0.0
            s = arr.sum()
            if s <= 1e-12:
                arr.fill(1.0 / n)
            else:
                arr /= s
            return arr

        # --- Main path: clamp then try to renormalize ------------------------------
        np.clip(arr, min_p, max_p, out=arr)
        total = arr.sum()

        if total <= 1e-12:
            # Construct a bounded-uniform vector that satisfies sum=1:
            # start at min_p and distribute the remainder without exceeding max_p
            arr.fill(min_p)
            remainder = 1.0 - n * min_p
            if remainder > 1e-12:
                capacity = max_p - min_p
                # number of slots needed if we fill up to capacity
                k = int(min(n, np.ceil(remainder / max(capacity, 1e-12))))
                # distribute evenly over k positions (randomize to avoid bias)
                idx = np.arange(n)
                np.random.shuffle(idx)
                arr[idx[:k]] += remainder / k
            return arr

        # Renormalize to sum 1
        arr /= total

        # Safety: if scaling broke bounds (very rare), repair by bounded fill
        if (arr < min_p - 1e-12).any() or (arr > max_p + 1e-12).any():
            np.clip(arr, min_p, max_p, out=arr)
            deficit = 1.0 - arr.sum()
            if abs(deficit) > 1e-12:
                # Distribute deficit within available capacity
                if deficit > 0:
                    cap = max_p - arr
                    w = cap / (cap.sum() + 1e-12)
                    arr += deficit * w
                else:
                    # surplus > 0: remove proportionally from entries above min_p
                    cap = arr - min_p
                    w = cap / (cap.sum() + 1e-12)
                    arr += deficit * w  # deficit is negative
            # Final tiny clip/renorm to kill numerical dust
            np.clip(arr, min_p, max_p, out=arr)
            s = arr.sum()
            if s > 1e-12:
                arr /= s
            else:
                arr.fill(1.0 / n)

        return arr

    def _combined_rate(self, generation:int, objectives:np.array, temperature:float) -> np.array:
        r"""
        Compute a discrete mutation count per individual by combining fitness and temperature.

        This method translates each individual’s fitness objective into an integer number
        of mutation attempts.  The pipeline is:

        1. **Fitness factor computation**  
           Evaluate the continuous fitness factor \\(r_i\\) for each objective \\(O_i\\) at
           temperature \\(T\\):  
           .. math::
              r_i \;=\; \mathrm{fitness\_factor}(O_i,\,T)
           where \\(\mathrm{fitness\_factor}\\) is a user–provided scaling of objective values.

        2. **Temperature scaling**  
           Scale the factor by the current temperature \\(T\\):  
           .. math::
              \hat r_i = T \,\times\, r_i.

        3. **Initial rate application**  
           Multiply by the initial mutation rate \\(r_0\\) = ``self._initial_mutation_rate``:  
           .. math::
              \tilde r_i = \hat r_i \,\times\, r_0.

        4. **Integer conversion**  
           Convert to 32‐bit integers via floor/truncation:  
           .. math::
              m_i = \lfloor \tilde r_i \rfloor, 
              \quad m_i \in \mathbb{Z}_{\ge0}.

        5. **Minimum rate enforcement**  
           Ensure each \\(m_i\\) is at least \\(m_{\min}\\) = ``self._min_mutation_rate``:  
           .. math::
              m_i \leftarrow \max\bigl(m_i,\,m_{\min}\bigr).

        **Returns** a 1D integer array \\([m_i]_{i=1}^N\\) of mutation counts.

        :param generation:
            Current generation index (unused internally but kept for API consistency).
        :type generation: int
        :param objectives:
            1D array of objective values \\((O_1,\dots,O_N)\\).
        :type objectives: numpy.ndarray
        :param temperature:
            Scalar temperature \\(T\\) modulating exploration versus exploitation.
        :type temperature: float
        :returns:
            Integer array of length \\(N\\) with each entry \\(m_i\\ge m_{\min}\\).
        :rtype: numpy.ndarray
        """
        
        # Calculate base rate: fitness factor scaled by temperature
        rates = temperature * fitness_factor(objectives=objectives, temperature=temperature)

        # Apply initial mutation rate and convert to 32-bit integers
        rates = (rates * self._initial_mutation_rate).astype(np.int32)

        # Enforce minimum mutation rate to avoid zero or too-small rates
        rates[rates < self._min_mutation_rate] = self._min_mutation_rate

        return rates

    def apply_mutation_and_crossover(self, individuals, generation, objectives, temperature:float=1.0):
        r"""
        Perform mutation and crossover operations on an entire population.

        This method orchestrates two canonical evolutionary operators:
        1. **Mutation**: each individual receives a number of random perturbations
           proportional to its fitness and current temperature.
        2. **Crossover**: randomly paired individuals exchange genetic material
           with probability `self._crossover_probability`.

        **Workflow**:

        1. **Compute mutation counts**  
           For each individual \\(i\\) with objective value \\(O_i\\), compute a
           non‐negative integer mutation count \\(m_i\\) via  
           .. math::
              r_i = \\text{fitness\\_factor}(O_i, T), 
              \\quad
              m_i = \\max\\bigl(m_{\\min},\\, \\lfloor T \\times r_i \\times r_{0} \\rfloor\\bigr)
           where:
           - \\(T\\) is the current temperature,
           - \\(r_0=\\) `self._initial_mutation_rate`,
           - \\(m_{\\min}=\\) `self._min_mutation_rate`.

        2. **Mutation loop**  
           For each structure \\(s_i^{(0)}\\) in `individuals`, apply \\(m_i\\)
           successive random mutations:  
           .. math::
              s_i^{(k+1)} = 
              \\begin{cases}
                \\text{mutation\_func}_j\\bigl(s_i^{(k)}\\bigr), & j\\sim \\mathrm{Categorical}(p),\\\\
                s_i^{(k)}, & \\text{if no mutations defined},
              \\end{cases}
              \\quad k=0,1,\\dots,m_i-1
           where the index \\(j\\) is drawn from the current
           `self._mutation_probabilities` distribution.  Each successful mutation is
           recorded and lineage metadata is updated.

        3. **Generate crossover pairs**  
           Let \\(N=|\\mathrm{individuals}|\\).  We form disjoint random pairs
           \\((i,j)\\) and include each pair in the crossover set \\(C\\) with
           probability \\(p_c\\) = `self._crossover_probability`.  If \\(C=\\varnothing\\),
           one random pair is forced to ensure at least one crossover.

        4. **Crossover loop**  
           For each \\((i,j)\\in C\\), apply a chosen crossover function:
           .. math::
              (c_i, c_j) = \\text{crossover\_func}_k\\bigl(s_i, s_j\\bigr),
              \\quad k\\sim \\mathrm{Categorical}(q)
           where \\(q\\)=`self._crossover_probabilities`.  Each offspring inherits
           lineage metadata from both parents.

        5. **Return**  
           - A list of **mutated** individuals (length \\(N\\)).  
           - A list of **crossed** offspring (may differ in length).  
           - The computed mutation count array \\([m_i]\\).

        :param individuals:
            Population of individuals to evolve.
        :type individuals: list[Any]
        :param generation:
            Current generation index (for lineage tracking).
        :type generation: int
        :param objectives:
            Array of objective values, shape \\((N, n_{obj})\\).  When multiple
            objectives are provided, they are internally combined (sum) for
            mutation‐rate calculation.
        :type objectives: numpy.ndarray
        :param temperature:
            Scalar temperature factor \\(T\\) modulating exploration.
        :type temperature: float
        :returns:
           - **mutated_structures** (*list[Any]*): the population after mutation.  
           - **crossed_structures** (*list[Any]*): newly generated offspring from crossover.  
           - **mutation_rate_array** (*numpy.ndarray*): integer mutation counts \\([m_i]\\).
        :rtype: tuple[list[Any], list[Any], numpy.ndarray]
        """

        # 1) Determine how many mutations to apply per structure
        mutation_rate_array = self._combined_rate(
            generation=generation, 
            objectives=objectives, 
            temperature=temperature, 
        )

        # 2) Mutation step (with objective-based probability adjustment)
        mutated_structures = self._mutate(individuals, mutation_rate_array, generation)

        # 3) Crossover step
        crossover_pairs = self._generate_crossover_indices(individuals, probability=self._crossover_probability)
        crossed_structures = self._cross_over(individuals, crossover_pairs, generation)
        
        return mutated_structures, crossed_structures, mutation_rate_array

    def _mutate(self, individuals, mutation_count_array, generation):
        r"""
        Apply a prescribed number of random mutations to each individual, updating lineage.

        This method perturbs each parent structure by performing multiple mutation operations,
        where each operation is selected randomly according to the current mutation probability
        distribution.  Post–mutation, lineage metadata is assigned to track ancestry and operations.

        **Workflow**:

        1. **Initialization**  
           For each parent structure \\(s_i\\), create a working copy  
           \\[
             s_i^{(0)} = \mathrm{deepcopy}(s_i),
           \\]  
           and reset any auxiliary attributes (e.g. magnetization, charge).

        3. **Determine mutation count**  
           Read the integer number of mutations \\(m_i\\) from `mutation_count_array[i]`.

        4. **Mutation loop**  
           For \\(k=1,\dots,m_i\\):  
           a. **Select operator**  
              Draw an index  
              \\(j_k\sim\mathrm{Categorical}(p_1,\dots,p_M)\\),  
              where  
              \\[
                p_j = \texttt{self.\_mutation\_probabilities}[j],
                \quad \sum_{j=1}^M p_j = 1.
              \\]  
           b. **Attempt mutation**  
              ```python
              candidate = mutation_funcs[j_k](s_i^{(k-1)})
              ```  
              - On success:  
                \\(s_i^{(k)} = candidate\\) and record \\(j_k\\) in `mutation_list`.  
              - On failure:  
                increment failure counter and set \\(s_i^{(k)} = s_i^{(k-1)}\\).

           c. **Count attempts**  
              `self._mutation_attempt_counts[j_k] += 1`.

        5. **Lineage assignment**  
           After all \\(m_i\\) steps, let  
           \\(\mathcal{J}_i = [j_1,\dots,j_{m_i}]\\).  Then  
           ```python
           self.lineage_tracker.assign_lineage_info(
               new_structure,
               generation,
               [parent.id],
               "mutation",
               mutation_list=mutation_list
           )
           ```

        **Mathematical summary**:  
        \\[
          s_i^{(k)} =
          \begin{cases}
            M_{j_k}(s_i^{(k-1)}), & j_k \sim \mathrm{Cat}(p), \\
            s_i^{(k-1)},          & \text{if mutation fails},
          \end{cases}
          \quad
          k=1,\dots,m_i.
        \\]

        :param individuals:
            List of original parent individuals \\([s_i]\\).
        :type individuals: list[Any]
        :param mutation_count_array:
            Integer array \\([m_i]\\) specifying how many mutations per parent.
        :type mutation_count_array: numpy.ndarray
        :param objectives:
            Array of objective values (shape (N,) or (N,*)).  Combined for logging.
        :type objectives: numpy.ndarray
        :param generation:
            Current generation index, used in lineage metadata.
        :type generation: int
        :returns:
            List of mutated individuals \\([s_i^{(m_i)}]\\).
        :rtype: list[Any]
        """
        mutated_structures = []

        for idx, parent in enumerate(individuals):
            # We copy the structure so as not to overwrite the parent
            new_structure = copy.deepcopy(parent)

            # Apply the requested number of mutations
            num_mutations = int(mutation_count_array[idx])
            mutation_list = []

            for _ in range(num_mutations):
                if len(self.mutation_funcs) == 0:
                    # No mutation functions are defined
                    break

                # Choose which mutation function to apply, weighted by _mutation_probabilities
                chosen_mut_idx = self._rng.choice(len(self.mutation_funcs), p=self._mutation_probabilities)
                chosen_mutation_func = self.mutation_funcs[chosen_mut_idx]

                # Attempt the mutation
                self._mutation_attempt_counts[chosen_mut_idx] += 1
                try:    
                    candidate_structure = chosen_mutation_func(new_structure)
                    mutation_list.append(chosen_mut_idx)
                except Exception as e:
                    self._mutation_fails_counts[chosen_mut_idx] += 1
                    candidate_structure = None
                    if True or self.debug:
                        import traceback
                        print(f"[DEBUG] An error occurred on mutation {chosen_mut_idx}:", e)
                        traceback.print_exc()

                # Update 'new_structure' to the mutated version
                if candidate_structure is None:
                    continue
                else:
                    new_structure = candidate_structure

            if self.debug:
                print(f'[DEBUG] Mutation ; Parent {parent.AtomPositionManager.metadata.get("id", -1) } Mutation list ({num_mutations}) {mutation_list}')

            if new_structure is None:
                continue           

            if self.lineage_tracker:
                # Store lineage information
                # Record who was mutated and which mutation was applied
                lineage_parents = [parent.AtomPositionManager.metadata.get("id", -1) ]
                self.lineage_tracker.assign_lineage_info(new_structure, generation, lineage_parents, "mutation", mutation_list=mutation_list)

            mutated_structures.append(new_structure)

        return mutated_structures

    def adjust_mutation_probabilities(self, population, ctx) -> np.ndarray:
        r"""
        Adapt the per‐operator mutation probabilities based on recent performance.

        This method compares each child’s objective value to its parent’s and
        adjusts the probabilities of the mutation (and crossover) operators that
        produced it. Improvements (negative delta) boost the corresponding operator
        probability; deteriorations reduce it.  Optionally, the adjustment magnitude
        is scaled by the size of the objective change.

        **Workflow**:

        1. **Input validation**  
           Ensure non‐empty `structures` and matching length of `objectives`.  
           Raises :exc:`ValueError` if violated.

        2. **Identify most recent generation**  
           Let \\(g^*\\) be the generation of the last entry in `structures`:  
           .. math::
              g^* = \max_{s\in\mathrm{structures}} s.metadata[\"generation\"]
           Only structures with \\(generation = g^*\\) are considered.

        3. **Build objective lookup**  
           Create mapping  
           \\(O: \text{id}\mapsto \text{objective}\\)  
           for all structures in the current generation.

        4. **Iterate over children**  
           For each structure \\(s\\) in reversed order with \\(generation=g^*\\):  
           a. Retrieve parent ID \\(p\\) and compute  
              \\[
                \Delta = O(s) - O(p).
              \\]  
           b. Convert to 1D array \\(\Delta\in\mathbb{R}^k\\).  
           c. **Scale adjustment**  
              Define base learning rate \\(\alpha\\) = ``self._alpha`` and optionally  
              compute magnitude factor  
              \\[
                \beta_i = 
                \begin{cases}
                  |\Delta_i / O(p)_i|, & |O(p)_i|>\varepsilon,\\
                  1, & \text{otherwise}
                \end{cases}
              \\]  
              then  
              \\[
                \hat\alpha_i = \mathrm{clip}\bigl(\alpha\,\beta_i,\;\alpha_{\min},\;\alpha_{\max}\bigr).
              \\]

           d. **Apply update rule**  
              For each mutation index \\(j\in s.metadata['mutation\_list']\\):  
              .. math::
                 p_j \;\leftarrow\;
                 \begin{cases}
                   p_j\,(1 + \hat\alpha_i), & \Delta_i < 0,\\\\
                   p_j\,(1 - \hat\alpha_i), & \Delta_i \ge 0.
                 \end{cases}
              Similarly for crossover indices in `s.metadata['crossover_idx']`.

        5. **Clamp and normalize**  
           After all updates, enforce  
           \\(p_j\in [p_{\min},p_{\max}]\\) and  
           \\(\sum_j p_j = 1\\)  
           via  
           .. code-block:: python
              self._mutation_probabilities = np.clip(self._mutation_probabilities, self._min_prob, self._max_prob)
              self._mutation_probabilities /= self._mutation_probabilities.sum()

        **Parameters**
        ----------
        structures : list[Any]
            List of recently generated structures, each with
            ``AtomPositionManager.metadata`` containing:
            - ``generation`` (int)
            - ``id`` (unique identifier)
            - ``parents`` (list, first element is parent id)
            - ``operation`` (“mutation” or “crossover”)
            - ``mutation_list`` or ``crossover_idx``
        objectives : list[float or np.ndarray]
            Corresponding objective values; lower is better.  Must match length of `structures`.
        features : Any
            Reserved for future extensions; currently unused.

        :returns:
            Updated and normalized mutation probability vector.
        :rtype: numpy.ndarray

        :raises ValueError:
            If `structures` is empty or `len(structures) != len(objectives)`.
        """
        structures = population.get_containers('dataset')
        objectives = ctx.get_objectives()
        features = ctx.get_features()

        # Validate input parameters
        if not structures:
            raise ValueError("The structures list is empty.")
        if objectives is None or len(structures) != len(objectives):
            raise ValueError("The number of structures must match the number of objectives.")

        # Retrieve the generation number of the most recent structure.
        last_gen = structures[-1].AtomPositionManager.metadata.get("generation", 0)

        if last_gen > 0:
            # Create a mapping from each structure's unique id to its corresponding objective value.
            objectives_dict = {
                s.AtomPositionManager.metadata.get("id", -1): obj
                for s, obj in zip(structures, objectives)
            }

            # Iterate over structures in reverse (most recent first) 
            for structure in reversed(structures):
                meta = structure.AtomPositionManager.metadata
                if meta.get("generation") == last_gen:
                    parents = meta.get("parents", [])
                    if not parents or meta.get("id", -1) == -1:
                        continue  # Skip if no parent

                    parent_id = parents[0]
                    current_obj = objectives_dict.get(meta.get("id", -1))
                    parent_obj = objectives_dict.get(parent_id, 0)
                    # Delta < 0 means the child is better (if minimizing the objective)
                    delta = np.atleast_1d(current_obj - parent_obj)

                    # Proceed only if the structure was generated via a mutation operation.
                    if meta.get("operation") == "mutation":
                        # Optionally log debug info
                        if self.debug:
                            if self.logger is not None:
                                self.logger.debug(meta)

                        # Possibly scale alpha by magnitude of the change (relative improvement/deterioration)
                        if np.ndim(self._alpha) == 0:
                            effective_alpha = np.full(delta.shape, float(self._alpha), dtype=float)
                        elif isinstance(self._alpha, np.ndarray) and self._alpha.shape == delta.shape:
                            effective_alpha = self._alpha.astype(float, copy=False)
                        else:
                            raise ValueError("alpha must be a scalar or an array shaped like the objective delta")

                        nonzero_mask = np.abs(parent_obj) > 1e-12
                        if self._use_magnitude_scaling and np.any(nonzero_mask):
                            # Compute a scaling factor for elements where the parent objective is non-negligible.
                            scaling_factor = np.ones_like(effective_alpha)

                            scaling_factor[nonzero_mask] = np.abs(delta[nonzero_mask] / parent_obj[nonzero_mask])
                            effective_alpha *= scaling_factor

                        effective_alpha = np.clip(effective_alpha, self.min_alpha, self.max_alpha)

                        # reescale normalize needeed
                        for ea, d in zip(effective_alpha, delta):
                            
                            # If delta < 0 => improvement => multiply probability by (1 + alpha).
                            # If delta >= 0 => no improvement => multiply probability by (1 - alpha).
                            # This follows the docstring's logic for "better is negative delta => increase probability."
                            if d < 0:
                                for mutation in meta.get("mutation_list", []):
                                    self._mutation_probabilities[mutation] *= (1.0 + ea)
                                    self._mutation_success_counts[mutation] += 1
                            else:
                                for mutation in meta.get("mutation_list", []):
                                    self._mutation_probabilities[mutation] *= (1.0 - ea)
                                    self._mutation_unsuccess_counts[mutation] += 1
                            
                    if meta.get("operation") == "crossover":
                        # Optionally log debug info
                        if self.debug:
                            if self.logger is not None:
                                self.logger.debug(meta)

                        # Possibly scale alpha by magnitude of the change (relative improvement/deterioration)
                        effective_alpha = np.atleast_1d(self._alpha)
                        nonzero_mask = np.abs(parent_obj) > 1e-12
                        if self._use_magnitude_scaling and np.any(nonzero_mask):
                            # Compute a scaling factor for elements where the parent objective is non-negligible.
                            scaling_factor = np.ones_like(effective_alpha)
                            scaling_factor[nonzero_mask] = np.abs(delta[nonzero_mask] / parent_obj[nonzero_mask])
                            effective_alpha *= scaling_factor

                        effective_alpha = np.clip(effective_alpha, self.min_alpha, self.max_alpha)

                        # reescale normalize needeed
                        for ea, d in zip(effective_alpha, delta):
                            # If delta < 0 => improvement => multiply probability by (1 + alpha).
                            # If delta >= 0 => no improvement => multiply probability by (1 - alpha).
                            # This follows the docstring's logic for "better is negative delta => increase probability."
                            if d < 0:
                                for crossover in meta.get("crossover_idx", []):
                                    self._crossover_probabilities[crossover] *= (1.0 + ea)
                                    self._crossover_success_counts[crossover] += 1
                            else:
                                for crossover in meta.get("crossover_idx", []):
                                    self._crossover_probabilities[crossover] *= (1.0 - ea)
                                    self._crossover_unsuccess_counts[crossover] += 1
                    
                else:
                    # Assuming structures are ordered by generation, stop at an older generation
                    break

        # (Optional) Enforce min and max probability bounds if desired
        self._mutation_probabilities = np.maximum(self._mutation_probabilities, self._min_prob)
        self._mutation_probabilities = np.minimum(self._mutation_probabilities, self._max_prob)

        # Re-normalize the mutation probabilities so they sum to 1
        total_probability = np.sum(self._mutation_probabilities)
        if total_probability > 1e-12:
            self._mutation_probabilities /= total_probability

        # Clamp & renormalize both heads
        self._mutation_probabilities  = self.clamp_and_renormalize(np.asarray(self._mutation_probabilities, dtype=float))
        self._crossover_probabilities = self.clamp_and_renormalize(np.asarray(self._crossover_probabilities, dtype=float))

        # Log the updated mutation probabilities if debugging is enabled
        if self.debug and self.logger is not None:
            self.logger.info(f"[DEBUG] Updated mutation probabilities: {self._mutation_probabilities}")

        return self._mutation_probabilities

    def _generate_crossover_indices(self, population, probability):
        r"""
        Select disjoint random index‐pairs for crossover, ensuring at least one pair.

        The goal is to partition the population into random pairs and then,
        for each pair, decide independently with probability \\(p_c\\) whether to
        perform crossover.  If no pairs are selected after the pass, one random
        pair is forced to guarantee at least one crossover event.

        **Procedure**:

        1. **Initialize index pool**  
           Let \\(N = |\\mathrm{population}|\\).  
           Build the list of available indices  
           \\[
             I = \{0,1,\dots,N-1\}.
           \\]

        2. **Form disjoint pairs**  
           While \\(|I| > 1\\):  
           a. Randomly draw two distinct indices  
              \\((i,j)\\sim\mathrm{UniformPair}(I)\\).  
           b. Remove them from \\(I\\):  
              \\[
                I \leftarrow I \setminus\{i,j\}.
              \\]
           c. Include \\((i,j)\\) in the crossover set \\(C\\) with probability \\(p_c\\):  
              .. math::
                 \Pr\bigl((i,j)\in C\bigr) = p_c.
           d. Otherwise, discard \\((i,j)\\).

        3. **Guarantee at least one crossover**  
           If \\(C=\\varnothing\\) and \\(N>1\\), select a single pair at random:
           \\[
             C \leftarrow \{(i,j)\},\quad (i,j)\sim\mathrm{UniformPair}(\{0,\dots,N-1\}).
           \\]

        **Parameters**
        ----------
        population : list
            Current generation’s list of structures.
        probability : float
            Crossover probability \\(p_c\\in[0,1]\\) for each disjoint pair.

        :returns:
            List of index‐tuples \\(C\\) selected for crossover.
        :rtype: list[tuple[int,int]]
        """

        ''' Legacy
        crossover_pairs = []
        indices = list(range(len(population)))

        while len(indices) > 1:
            i, j = self._rng.choice(indices, 2)
            indices.remove(i)
            indices.remove(j)
            if self._rng.random() < probability:
                crossover_pairs.append((i, j))

        # Ensure at least one crossover happens if possible
        if not crossover_pairs and len(population) > 1:
            i, j = self._rng.choice(range(len(population)), 2)
            crossover_pairs.append((i, j))

        return crossover_pairs
        '''

        pairs, indices = [], list(range(len(population)))
        self._rng.shuffle(indices)  # disjoint random pairing
        for a, b in zip(indices[::2], indices[1::2]):
            if self._rng.random() < probability:
                pairs.append((a, b))
        if not pairs and len(indices) > 1:
            pairs.append(tuple(self._rng.choice(indices, size=2, replace=False)))
        return pairs

    def _cross_over(self, containers, crossover_pairs, generation):
        r"""
        Execute crossover on specified index pairs to produce offspring, with lineage tracking.

        This method applies one of the available crossover operators to each selected pair
        of parent structures, generating two children per pair.  Each operator is chosen
        probabilistically according to `self._crossover_probabilities`, then lineage metadata
        is updated for each child.

        **Procedure**:

        1. **Guard clause**  
           If no crossover functions are provided (`len(self.crossover_funcs)==0`),
           immediately return an empty list.

        2. **Initialize offspring list**  
           Create an empty list to collect all resulting child structures:
           ```python
           offspring = []
           ```

        3. **Loop over selected pairs**  
           For each pair \\((i,j)\\) in `crossover_pairs`:
           
           a. **Identify parents**  
              \\[
                P_A = \mathrm{containers}[i], \quad
                P_B = \mathrm{containers}[j].
              \\]

           b. **Repeat for each allowed child per pair**  
              For \\(r=1,\ldots,R\\) where \\(R = \texttt{self.crossover_rate}\\):

              i. **Select operator index**  
                 Draw  
                 \\[
                   k \sim \mathrm{Categorical}\bigl(q_1,\dots,q_M\bigr),
                   \quad
                   q_m = \texttt{self._crossover_probabilities}[m].
                 \\]

              ii. **Apply crossover**  
                  ```python
                  C_A, C_B = crossover_funcs[k](P_A, P_B)
                  ```  
                  If either child is `None`, fallback to returning the original parents.

              iii. **Record attempt**  
                   Increment  
                   `self._crossover_attempt_counts[k] += 1`.

           c. **Lineage assignment**  
              Let  
              \\(\mathrm{ids} = [\,P_A.id, P_B.id]\\).  
              For each valid child \\(C\\):
              ```python
              self.lineage_tracker.assign_lineage_info(
                  C, generation, ids, "crossover"
              )
              ```

           d. **Collect children**  
              Append both \\(C_A, C_B\\) to `offspring`.

        4. **Return offspring**  
           The final list contains all new structures generated by crossover:
           ```python
           return offspring
           ```

        **Mathematical Summary**:

        For each selected pair \\((i,j)\\) and chosen operator \\(k\\):
        .. math::
           (C_i, C_j) = X_k(P_i, P_j), 
           \quad k \sim \mathrm{Categorical}(q),
        \\[
           q = \bigl[q_1,\dots,q_M\bigr],\quad \sum_{m} q_m = 1.
        \\]

        :param containers:
            List of parent structures.
        :type containers: list[Any]
        :param crossover_pairs:
            List of index tuples \\((i,j)\\) indicating which parents to cross.
        :type crossover_pairs: list[tuple[int,int]]
        :param generation:
            Current generation index for lineage metadata.
        :type generation: int
        :returns:
            List of all child structures produced by crossover.
        :rtype: list[Any]
        """
        if not self.crossover_funcs or len(self.crossover_funcs) == 0:
            # If no crossover functions exist, do nothing
            return []

        # Example: always use the first crossover function
        offspring = []

        for (i, j) in crossover_pairs:

            parentA, parentB = containers[i], containers[j]
            # start from parents for this pair, allow multiple offspring per pair

            for _ in range(self.crossover_rate):

                if self.debug and self.logger is not None:
                    self.logger.info(f"[DEBUG] Performing crossover on indices {i} and {j}.")

                # Choose which mutation function to apply, weighted by _mutation_probabilities
                chosen_co_idx = self._rng.choice(len(self.crossover_funcs), p=self._crossover_probabilities)
                chosen_co_func = self.crossover_funcs[chosen_co_idx]
                self._crossover_attempt_counts[chosen_co_idx] += 1

                # Attempt the mutation
                try:
                    childA_new, childB_new = chosen_co_func(parentA, parentB)
                except:
                    self._crossover_fails_counts[chosen_co_idx] += 1
                    childA_new, childB_new = None, None

                # fallback to cloning parents if operator failed
                if childA_new is None or childB_new is None:
                    childA_new, childB_new = copy.deepcopy(parentA), copy.deepcopy(parentB)

            if childA is None or childB is None:
                childA_new, childB_new = childA, childB

            else:
                # Assign lineage
                parents = [containers[i].AtomPositionManager.metadata.get("id", -1), containers[j].AtomPositionManager.metadata.get("id", -1) ]
                self.lineage_tracker.assign_lineage_info(childA_new, generation, parents, "crossover")
                self.lineage_tracker.assign_lineage_info(childB_new, generation, parents, "crossover")
                crossover_structures += [childA_new, childB_new]

        return crossover_structures

    def penalization(self, individuals, process='hash_collision'):
        r"""
        Apply a penalty to the mutation or crossover operator probabilities when a structure is invalid.

        When a generated structure `container` is rejected—either due to a hash‐collision
        (duplicate) or falling outside the design space—it is traced back to the operator(s)
        that produced it and those operators’ selection probabilities are reduced.

        **Workflow**:

        1. **Retrieve metadata**  
           Extract the operation type and operator indices from  
           ``individuals.AtomPositionManager.metadata``:  
           - ``operation`` ∈ {“mutation”, “crossover”}  
           - ``mutation_list`` or ``crossover_idx``

        2. **Select penalty factor**  
           Let \\(\alpha\\) = ``self._alpha``.  Then for each offending operator index \\(j\\),  
           apply  
           .. math::
              p_j \;\leftarrow\; p_j \,\times\, (1 - \alpha)
           where \\(p_j\\) is the prior probability of choosing operator \\(j\\).

        3. **Update counters**  
           Increment the corresponding collision count:  
           ```python
           self._mutation_hashcolition_counts[j] += 1
           # or
           self._crossover_hashcolition_counts[j] += 1
           ```

        4. **Clamp & renormalize**  
           Enforce bounds \\([p_{\min}, p_{\max}]\\) and renormalize so that  
           \\(\sum_k p_k = 1\\):  
           .. math::
              \hat p_j = \operatorname{clip}\bigl(p_j,\;p_{\min},\;p_{\max}\bigr),
              \quad
              p_j^{\mathrm{new}} = \frac{\hat p_j}{\sum_{k} \hat p_k}
           This is performed via  
           ```python
           self._mutation_probabilities = self.clamp_and_renormalize(self._mutation_probabilities)
           # similarly for _crossover_probabilities
           ```

        :param individuals:
            The structure that failed validation, containing metadata fields:
            - ``operation``: either "mutation" or "crossover"
            - ``mutation_list`` or ``crossover_idx``: list of operator indices responsible
        :type individuals: any
        :param process:
            Type of invalidation, either `'hash_collision'` (duplicate) or `'out_of_doe'`.
        :type process: str
        """
        # Retrieve metadata for operation type, mutation list, etc.
        
        if not isinstance(individuals, (list, tuple)):
            individuals = [individuals]

        process_to_attr = {
            'hash_collision': {
                'mutation': self._mutation_hashcolition_counts,
                'crossover': self._crossover_hashcolition_counts,
            },
            'out_of_doe': {
                'mutation': self._mutation_outofdoe_counts,
                'crossover': self._crossover_outofdoe_counts,
            },
            'selfcollision': {
                'mutation': self._mutation_fails_counts,
                'crossover': self._crossover_fails_counts,
            },            
        }
        if process not in process_to_attr:
            raise ValueError(f"Unknown process: {process}")

        for individual in individuals:
            meta = individual.AtomPositionManager.metadata

            operation = meta.get("operation", None)



            mutation_count_list = process_to_attr[process]['mutation']
            crossover_count_list = process_to_attr[process]['crossover']

            # We only apply penalties if the structure has a recorded operation
            if operation == "mutation":
                # The structure was generated by mutation
                mutation_indices = meta.get("mutation_list", [])
                for m_idx in mutation_indices:
                    # Track how many collisions this mutation function caused
                    mutation_count_list[m_idx] += 1

                    # Penalize by reducing the mutation probability by a factor (1 - alpha)
                    # If you use an array for alpha, you might do self._alpha[m_idx]
                    self._mutation_probabilities[m_idx] *= (1.0 - self._alpha)

                # Enforce minimum and maximum probability bounds
                # Re-normalize so probabilities sum to 1
                self._mutation_probabilities = self.clamp_and_renormalize(self._mutation_probabilities)

                if self.debug and self.logger is not None:
                    self.logger.info(
                        f"[DEBUG] Penalized mutation probabilities due to hash collision: "
                        f"{self._mutation_probabilities}"
                    )

            elif operation == "crossover":
                # The structure was generated by crossover
                # If you store which crossover function was used, penalize that index similarly
                # For example, let's assume there's a "crossover_idx" in metadata:
                co_idx = meta.get("crossover_idx", None)
                if co_idx is not None:
                    # Track collision count
                    crossover_count_list[co_idx] += 1

                    # Penalize the crossover probability
                    self._crossover_probabilities[co_idx] *= (1.0 - self._alpha)

                    # Enforce minimum and maximum probability bounds
                    # Re-normalize so probabilities sum to 1
                    self._crossover_probabilities = self.clamp_and_renormalize(self._crossover_probabilities)

                    if self.debug and self.logger is not None:
                        self.logger.info(
                            f"[DEBUG] Penalized crossover probabilities due to hash collision: "
                            f"{self._crossover_probabilities}"
                        )

    def evaluate_mutation_feature_change(
        self,
        structures,
        feature_func,
        n: int = 200,
        debug: bool = False
    ):
        r"""
        Estimate the per‐mutation impact on a feature via randomized trials and least squares.

        This method applies `n` successive random mutations to a copy of the provided
        structure, records the resulting feature changes, and then fits a linear model
        to quantify each mutation function’s average effect on the feature.

        **Procedure**:

        1. **Base feature computation**  
           Compute the original feature vector  
           .. math::
               \\boldsymbol\\phi^{(0)} = \\text{feature_func}(s_0),  
               \\quad s_0 = \\text{structures}[0].

        2. **Data matrix and response vector**  
           For each trial \\(i=1,\\dots,n\\):
           a. Select a mutation index \\(j_i\\) uniformly at random from  
              \\(\\{0,\\dots,M-1\\}\\) where \\(M=\\texttt{len(self.mutation_funcs)}\\).  
           b. Apply the mutation:  
              \\[
                s^{(i)} = M_{j_i}\\bigl(s^{(i-1)}\\bigr).
              \\]
           c. Compute the feature increment  
              \\[
                \\Delta\\boldsymbol\\phi^{(i)} = \\boldsymbol\\phi^{(i)} - \\boldsymbol\\phi^{(i-1)},
                \\quad \\boldsymbol\\phi^{(i)} = \\text{feature_func}(s^{(i)}).
              \\]
           d. Record in the design matrix and response:  
              .. math::
                 X_{i,k} = 
                 \\begin{cases}
                   1, & k = j_i,\\\\
                   0, & k \\neq j_i,
                 \\end{cases}
                 \\quad
                 y_i = \\Delta\\boldsymbol\\phi^{(i)}.

        3. **Linear least‐squares fit**  
           Solve for the effect vector \\(\\mathbf{w}\\in\\mathbb{R}^M\\) that minimizes  
           .. math::
              \\| X\,w - y \\|_2^2,
           whose closed‐form solution is  
           .. math::
              w = \\bigl(X^T X\\bigr)^{-1} X^T y.

        4. **Result assembly**  
           Store `w` in `self._mutation_feature_effects` and return a list of dicts:
           each dict contains the mutation index, its name, and the estimated effect.

        :param structures:
            List containing a single structure to be mutated.
        :type structures: list[Any]
        :param feature_func:
            Callable mapping a structure to a feature vector \\(\\boldsymbol\\phi\\in\\mathbb{R}^d\\).
        :type feature_func: callable
        :param n:
            Number of random mutation trials to perform.
        :type n: int
        :param debug:
            If True, emit intermediate debug information.
        :type debug: bool
        :returns:
            A list of dictionaries, each with keys:
            - `"mutation_index"`: int, index of the mutation function.  
            - `"mutation_name"`: str, its `__name__`.  
            - `"estimated_effect"`: float or array, the corresponding entry of \\(w\\).
        :rtype: list[dict]

        **Mathematical summary**:

        .. math::
           X \\in \\{0,1\\}^{n\\times M},\\quad
           y \\in \\mathbb{R}^{n\\times d},\\quad
           w = (X^T X)^{-1} X^T y.
        """

        if not self.mutation_funcs:
            if debug and self.logger is not None:
                self.logger.info("[DEBUG] No mutation functions found.")
            return []
            
        structure = structures[0]

        # 1) Compute the base (original) feature value
        base_feature_value = feature_func(structure)
        num_features = base_feature_value.shape[0]
        prev_feature_value = base_feature_value

        # 2) Prepare arrays to store random-mutation data
        #    data_mutation: one-hot for which mutation was chosen on each iteration
        #    data_delta_features: feature delta from the base after each iteration
        num_mutations = len(self.mutation_funcs)
        data_mutation = np.zeros((n, num_mutations), dtype=float)
        data_delta_features = np.zeros( (n, num_features), dtype=float)

        # Work on a deep copy of the original so we don't overwrite it
        test_struct = copy.deepcopy(structure)

        # 3) Apply random mutations n times and record data
        for i in range(n):
            # Randomly choose a mutation from the list
            mut_choice = self._rng.choice(num_mutations)
            chosen_mut_func = self.mutation_funcs[mut_choice]

            try:    
                candidate_structure = chosen_mut_func(test_struct)
                if candidate_structure is not None:
                    test_struct = candidate_structure 

                else:
                    continue

            except Exception as e:

                if self.debug:
                    import traceback
                    self.logger.info(f"[DEBUG] An error occurred on mutation {mut_choice}:", e)
                    traceback.print_exc()
                continue
            
            # Compute new feature after applying this mutation
            current_feature_value = feature_func(test_struct)

            # Record hot-encode for the chosen mutation
            data_mutation[i, mut_choice] = 1.0

            # Record the feature delta relative to the *original* structure
            data_delta_features[i] = current_feature_value - prev_feature_value
            prev_feature_value = current_feature_value

        # 4) Estimate the rate of change for each mutation using a linear fit
        #    data_delta_features = data_mutation @ effect_vector
        #    Solve for effect_vector in least squares sense
        X = data_mutation  # shape (n, num_mutations)
        y = data_delta_features  # shape (n,)
  
        # effect_vector will be the best-fit effect for each mutation
        effect_vector, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

        # 5) (Optional) Save raw data and the fitted effects in the class for later use
        #    You could store them in some persistent lists/dicts as needed.
        if not hasattr(self, "_feature_data_records"):
            self._feature_data_records = []
        self._feature_data_records.append({
            "data_mutation": data_mutation,
            "data_delta_features": data_delta_features,
            "base_feature_value": base_feature_value,
            "effect_vector": effect_vector
        })

        self._mutation_feature_effects = effect_vector  # e.g. store the final array

        # 6) Build a more user-friendly result list
        results = []
        for i, eff in enumerate(effect_vector):
            mut_name = getattr(self.mutation_funcs[i], "__name__", f"mutation_func_{i}")
            results.append({
                "mutation_index": i,
                "mutation_name": mut_name,
                "estimated_effect": eff
            })

        if self.logger is not None and False:
            # Build each row as "index | mutation_name | [effect1, effect2, …]"
            rows = []
            for entry in results:
                idx        = entry['mutation_index']
                name       = entry['mutation_name']
                effect_arr = entry['estimated_effect']
                effect_str = np.array2string(
                    effect_arr,
                    precision=2,             # two decimal places
                    separator=',',           # comma between values
                    max_line_width=1_000_000 # force single line
                )
                rows.append(f"{idx} | {name} | {effect_str}")

            body = "\n".join(rows)

            self.logger.info(
                "[DEBUG] Mutation effect estimates (LS fit):\n"
                "Index | Mutation Name | Estimated Effect\n%s",
                body
            )
            #self.logger.info(f"[DEBUG] Mutation effect estimates (LS fit): {results}")

        return results

    def foreigners_generation(
        self,
        structures,
        feature_func,
        design_points,
        tolerance: float = 0.01,
        max_iterations: int = 20,
        debug: bool = False
    ):
        r"""
        Generate candidate structures (“foreigners”) that achieve target feature values via directed mutation.

        This routine uses a previously estimated per‐mutation effect vector to iteratively steer
        a reference structure toward each desired design point in feature space.  If the feature
        deviates by more than `tolerance`, additional mutations are applied up to `max_iterations`.

        **Procedure**:

        1. **Ensure effect estimates**  
           Verify that `self._mutation_feature_effects` (\\(\\mathbf{w}\\in\\mathbb{R}^M\\)) is available.
           If not, call `evaluate_mutation_feature_change` with \\(n=100\\) to compute:
           .. math::
              X\,w = y,\quad
              w = (X^T X)^{-1} X^T y.

        2. **Setup**  
           - Let \\(\{s_k\}\\) = `structures` (template pool).  
           - Let \\(f(s) = \\texttt{feature_func}(s)\\) produce a feature vector \\(\\boldsymbol\\phi\\).  
           - For each design point \\(d_p\\in \\{\\texttt{design_points}\\}\\), we seek \\(s^*\\) such that  
             .. math::
                \\|f(s^*) - d_p\\|_\\infty \le \\texttt{tolerance}.

        3. **Iterative search per design point**  
           For each \\(d_p\\):
           a. **Initialize**  
              Select a random template \\(s^{(0)}\\) and compute  
              \\[
                \\boldsymbol\\phi^{(0)} = f\\bigl(s^{(0)}\\bigr),\quad
                \\Delta^{(0)} = d_p - \\boldsymbol\\phi^{(0)}.
              \\]
           b. **Repeat** for \\(t = 1,2,\\dots\\) until \\(\\|\\Delta^{(t-1)}\\|_\\infty \\le \\texttt{tolerance}\\)
              or \\(t > \\texttt{max\_iterations}\\):  
              i.  Compute integer coefficients via local solver:  
                  .. math::
                     \\mathbf{c} = \\mathrm{solver\\_integer\\_local}(\\mathbf{w}^T,\,\\Delta^{(t-1)}),
                     \\quad \\mathbf{c}\\in\\mathbb{Z}_{\\ge0}^M.  
              ii. Apply each mutation \\(M_j\\) exactly \\(c_j\\) times in sequence:  
                  .. math::
                     s^{(t)} = \\prod_{j=1}^M M_j^{c_j}\\bigl(s^{(0)}\\bigr).
                  Record new feature \\(\\boldsymbol\\phi^{(t)} = f(s^{(t)})\\).  
              iii. Update residual  
                  \\[
                    \\Delta^{(t)} = d_p - \\boldsymbol\\phi^{(t)}.
                  \\]

        4. **Acceptance**  
           If \\(\\|\\Delta^{(t)}\\|_\\infty \\le \\texttt{tolerance}\\), include \\(s^{(t)}\\)
           in the output list; otherwise, record a failure.

        5. **Summary**  
           Log or print statistics on successes, failures, max iteration counts,
           and maximal final deviation.

        :param structures:
            List of template structures to sample from.
        :type structures: list[Any]
        :param feature_func:
            Callable mapping a structure to a feature vector \\(\\boldsymbol\\phi\\).
        :type feature_func: callable
        :param design_points:
            Sequence of target feature vectors or scalars \\(d_p\\).
        :type design_points: list[float or array-like]
        :param tolerance:
            Maximum allowed infinity‐norm deviation  
            \\(\\|f(s) - d_p\\|_\\infty\\).
        :type tolerance: float
        :param max_iterations:
            Upper bound on mutation iterations per design point.
        :type max_iterations: int
        :param debug:
            If True, emit detailed diagnostic logs.
        :type debug: bool
        :returns:
            List of structures meeting the tolerance criterion for each design point.
        :rtype: list[Any]

        :raises RuntimeError:
            If no mutation feature effects are available and evaluation fails.
        """


        # 1) Ensure we have an up-to-date 'mutation_feature_effects' vector
        #    If not, run `evaluate_mutation_feature_change` once.
        if getattr(self, "_mutation_feature_effects", None) is None:
            # Example: evaluate on some "template" structure from partitions, or just on the passed-in structure
            self.evaluate_mutation_feature_change(
                structures=structures,              # Or a "template" structure if you prefer
                feature_func=feature_func,
                n=100,
                debug=debug
            )

        # Quick references
        effect_vector = self.mutation_feature_effects
        mutation_funcs = self.mutation_funcs
        if effect_vector is None or len(effect_vector) == 0 or len(mutation_funcs) == 0:
            if debug and self.logger is not None:
                self.logger.info(
                    "[DEBUG] No effect vector or mutation funcs available; returning empty list."
                )
            return []

        # 2) For collecting the resulting structures
        structures_recommend = []

        # Statistics to keep track of
        n_success = 0
        n_fail = 0
        max_final_diff = 0.0
        max_iterations = max_iterations
        max_iterations_count = 0

        # 3) For each desired design point, attempt to mutate toward that feature
        for dp_i, dp in enumerate(design_points):
            # Select a random structure from the template 
            structure = self._rng.choice(structures)

            # Make a fresh copy of the reference structure
            test_struct = copy.deepcopy(structure)
            current_feature = feature_func(test_struct)

            # We'll track how close we are
            diff = dp - current_feature
            iteration_count = 0

            # Iteratively apply mutations until close enough or max_iterations exceeded
            while np.any(np.abs(diff) > tolerance) and iteration_count < max_iterations:

                iteration_count += 1
                coefficient = solver_integer_local(effect_vector.T, diff)
                coeff = np.asarray(coefficient, dtype=int)
                coeff = np.maximum(coeff, 0)

                if np.sum(coeff) > 0:
                    for c_idx, c in enumerate(coeff):
                        
                        for _ in range(c):
                            try:    
                                test_struct_mutated = mutation_funcs[c_idx](test_struct)
                            except Exception:
                                test_struct_mutated = None

                            if test_struct_mutated is not None:
                                test_struct = test_struct_mutated  # If successful, update test_struct
                            else:
                                pass

                # Update our current feature and diff
                current_feature = feature_func(test_struct)
                diff = dp - current_feature

            max_iterations_count = max(max_iterations_count, iteration_count)
            # After the loop, see how close we got
            final_diff = float(np.max(np.abs(diff)))
            max_final_diff = max(max_final_diff, final_diff)

            if not np.abs(diff).any() > tolerance:
                # Accept this structure
                structures_recommend.append(test_struct)
                n_success += 1
            else:
                n_fail += 1

        # 4) Print or log summary if desired
        msg = (f"immigrants generation complete. "
               f"Design points: {len(design_points)} | "
               f"Success: {n_success} | Fail: {n_fail} | "
               f"Max final difference: {max_final_diff:.1g}"
               f"Max iterations: {max_iterations_count:.1f}")

        if debug and self.logger is not None:
            self.logger.info(f"[DEBUG] {msg}")
        else:
            print(msg)

        return structures_recommend

    def evaluate_mutation_rate_over_generations(self, temperature:list=None,) -> List[float]:
        r"""
        Simulate and visualize mutation rate dynamics as a function of temperature over generations.

        This utility predicts the integer mutation counts for each generation when
        subject to a predefined temperature schedule, isolating the effect of the
        thermostat and fitness factor without performing real mutations.

        **Procedure**:

        1. **Generate dummy objectives**  
           Create a placeholder objective array  
           \\[
             O = [o_1, o_2, \dots, o_N]^T,
             \quad o_i \sim \mathcal{U}(0,1),
             \; N = 100.
           \\]
           Stored as  
           ```python
           objectives_array = np.atleast_2d(np.random.rand(100)).T
           ```

        2. **Define generation indices**  
           Let \\(G = \operatorname{len}(\texttt{temperature})\\).  
           Compute  
           \\[
             g = 1,2,\dots,G.
           \\]
           via  
           ```python
           generations_array = np.arange(1, G+1)
           ```

        3. **Compute per‐generation mutation rates**  
           For each generation \\(g\\) with temperature \\(T_g\\), call the internal  
           `_combined_rate` method:  
           .. math::
              m_i(g) = \max\bigl(m_{\min}, \lfloor T_g\,r_i(T_g)\,r_{0}\rfloor\bigr),
              \quad i=1,\dots,N
           where:
           - \\(r_i(T) = \mathrm{fitness\_factor}(O_i, T)\\)
           - \\(r_{0} = \texttt{self._initial\_mutation\_rate}\\)
           - \\(m_{\min} = \texttt{self._min\_mutation\_rate}\\)

           Collected as  
           ```python
           mutation_rate_array = [
               self._combined_rate(g, objectives_array, T_g)
               for g, T_g in zip(generations_array, temperature)
           ]
           ```

        4. **Plot dynamics**  
           - Plot \\(m_i(g)\\) versus \\(g\\) to observe mutation‐rate evolution.  
           - Overlay normalized temperature curve for comparison:  
           .. math::
              T_{\mathrm{norm}}(g) = \frac{T_g}{\max(T)} \times \max(m_i).
           Implemented via Matplotlib.

        :param temperature:
            Sequence of temperature values \\([T_1,\dots,T_G]\\) for each generation.
        :type temperature: list[float]
        :returns:
            Tuple `(generations_array, mutation_rate_array)` where:
            - `generations_array`: numpy.ndarray of integers \\(1\ldots G\\).  
            - `mutation_rate_array`: list of numpy.ndarray, each containing \\([m_i(g)]\\).
        :rtype: (numpy.ndarray, List[numpy.ndarray])

        :raises ValueError:
            If `temperature` is None or not a one‐dimensional sequence.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        mutation_array = []
        objectives_array = np.atleast_2d(np.random.rand(100)).T

        generations_array = np.arange(1, temperature.shape[0]+1, 1)

        mutation_rate_array = [ self._combined_rate(
            generation=g, 
            objectives=objectives_array, 
            temperature=t, 
        ) for t, g in zip(temperature, generations_array) ]

        plt.plot( generations_array, mutation_rate_array )
        plt.plot( generations_array, temperature/np.max(temperature)*np.max(mutation_rate_array) )
        plt.show()

        return generations_array, mutation_rate_array
