"""
design_space_constraints.py
---------------------------

Provides classes and utility functions to define and manage feature-based constraints
for design space exploration. These constraints can be used to filter out candidate
individuals (e.g., structures or parameter sets) that do not meet certain user-defined
criteria. Typical use-cases include feature-based restrictions, ratio checks,
upper/lower bounds, and custom logic to ensure the population remains within feasible
design regions.

Overview
--------
- ConstraintGenerator: A collection of static methods returning *callable* objects
  that verify whether a given individual's features satisfy a specified condition
  (e.g., "feature[i] > 0", "ratio of feature[i]/feature[j] < 2", etc.).

- FeatureConstraint: Encapsulates a single constraint (i.e., check_func) with an
  optional name and description. This allows for easier introspection, logging,
  and debugging.

- DesignSpaceConstraintManager: A manager class to collect multiple constraints,
  apply logical modes ("all" or "any"), and check if a candidate's features meet
  the overall constraints.

Usage Example
-------------
1) Define your constraints:
    from design_space_constraints import ConstraintGenerator, FeatureConstraint

    # Create a constraint that ensures feature[0] >= 5.0
    c1 = FeatureConstraint(
        check_func=ConstraintGenerator.greater_or_equal(feature_idx=0, threshold=5.0),
        name="C1_feature0_GE_5",
        description="Ensures feature[0] is >= 5.0"
    )

    # Create a ratio constraint that ensures feature[1]/feature[2] is between 0.3 and 0.7
    c2 = FeatureConstraint(
        check_func=ConstraintGenerator.ratio_in_range(
            numerator_idx=1, denominator_idx=2, min_ratio=0.3, max_ratio=0.7
        ),
        name="C2_ratio_in_range",
        description="Ensures ratio(feature[1]/feature[2]) is between 0.3 and 0.7"
    )

2) Create a manager and add constraints:
    from design_space_constraints import DesignSpaceConstraintManager

    manager = DesignSpaceConstraintManager(logic="all")  # all constraints must be satisfied
    manager.add_constraint(c1)
    manager.add_constraint(c2)

3) In your evolutionary loop, filter individuals:
    for individual in population:
        feat_vector = compute_features(individual)  # shape (D, )
        if manager.validate(feat_vector):
            # keep or process this individual
        else:
            # discard this individual

This approach cleanly separates the definition of constraints from the logic that
applies them to candidate solutions, enabling a flexible mechanism for restricting
the design space.
"""
import numpy as np
import itertools
import random
import warnings
from typing import Callable, List, Tuple, Optional, Dict, Union
from ezga.core.interfaces import IDoE
from ezga.DoE.constraint import ConstraintFactory

# =============================================================================
# DesignOfExperiments
# =============================================================================
class DesignOfExperiments(IDoE):
    """
    Manage multiple FeatureConstraints under logical modes.

    Attributes
    ----------
    constraints : List[callable]
    logic : str
        Either 'all' (conjunction) or 'any' (disjunction).
    """

    def __init__(   
        self, 
        design: str = None, 
        logic: str = "all", 
        constraints: Optional[List[callable]] = None,
        candidate_generator:callable = None,
        ):
        """
        Initialize with logic mode.

        Parameters
        ----------
        logic : {'all','any'}
        """
        valid_modes = ["all", "any"]
        if logic not in valid_modes:
            raise ValueError(
                f"Invalid logic='{logic}'. Must be one of {valid_modes}."
            )
        self.constraints: List[callable] = constraints if constraints else []
        self._name_map = {}

        self.candidate_generator = None

        self.logic = logic
        self.design = design
        
    def set_name_mapping(self, mapping: Dict[str, int]) -> "DesignOfExperiments":
        """
        Register a feature-name → index mapping for all constraints.
        This calls ConstraintGenerator.set_name_mapping(...) under the hood,
        so any ConstraintGenerator methods that take string keys will resolve correctly.
        Returns self to allow chaining.
        """
        # Validate mapping shape
        if not isinstance(mapping, dict):
            raise TypeError(f"Expected dict for mapping, got {type(mapping).__name__}")
        for name, idx in mapping.items():
            if not isinstance(name, str):
                raise ValueError(f"Feature name must be str, got {type(name).__name__!r}")
            if not isinstance(idx, int):
                raise ValueError(f"Feature index must be int, got {type(idx).__name__!r}")

        self._name_map = dict(mapping)
        # propagate to the central registry
        ConstraintFactory.set_name_mapping(self._name_map)
        return self

    def add(self, constraint: callable):
        """
        Add a callable.

        Parameters
        ----------
        constraint : callable
        """
        self.add_constraint(constraint)

    def add_constraint(self, constraint: callable):
        """
        Adds a callable to the DOE manager.

        Parameters
        ----------
        constraint : callable
        """
        if not callable(constraint):
            raise TypeError("Only callable functions can be added.")

        # On first use, ensure constraints is a fresh list
        if self.constraints is None:
            self.constraints = []

        self.constraints.append(constraint)

    def validate(self, features: np.ndarray) -> bool:
        """
        Check if features satisfy combined constraints.

        Returns
        -------
        bool
            - 'all': True if all constraints hold.  
            - 'any': True if at least one holds.
        """
        if self.logic == "all":
            return all(c(features) for c in self.constraints)
        else:
            return any(c(features) for c in self.constraints)

        return False

    def generate(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        *,
        n_candidates: int,
        T: float,
    ) -> np.ndarray:
        """
        Propose new design points either via a Bayesian optimizer or via the
        static DOE generator.

        Steps:
        1. If no candidate_generator exists and n_candidates > 0, automatically
           instantiate a BayesianOptimization using this DoE’s bounds and constraints.
        2. Fit the optimizer on (X, Y).
        3. Call its generate(...) to obtain new points.
        4. Otherwise, fall back to calling self.design(self.validate) and trim
           to n_candidates.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Feature matrix from the previous generation.
        Y : np.ndarray, shape (n_samples,) or (n_samples, n_objectives)
            Objective values from the previous generation.
        n_candidates : int
            Number of new points to propose.
        T : float
            Temperature parameter for acquisition (only used by BO).

        Returns
        -------
        np.ndarray, shape (<= n_candidates, n_features)
            The proposed design points.

        Raises
        ------
        ValueError
            If n_candidates is negative or T is not numeric.
        RuntimeError
            If automatic BO creation or generation fails.
        """
        # 1. Early exit for no candidates requested
        if n_candidates is None or n_candidates == 0:
            return []

        # 2. Validate inputs
        if not isinstance(n_candidates, int) or n_candidates < 0:
            raise ValueError(f"n_candidates must be a non-negative integer or None, got {n_candidates}")
        if not isinstance(T, (int, float)):
            raise ValueError(f"T must be numeric, got {type(T).__name__}")

        # 3) Ensure Y is two‐dimensional
        Y_arr = np.asarray(Y)
        if Y_arr.ndim == 1:
            # single‐objective: reshape to (n_samples, 1)
            Y_arr = Y_arr.reshape(-1, 1)
        elif Y_arr.ndim != 2:
            raise ValueError(f"Y must be 1D or 2D array, got ndim={Y_arr.ndim}")

        # 4. Lazy‐instantiation of a Bayesian optimizer if needed
        if self.candidate_generator is None:
            from bansga.bayesian_optimization.bayesian_optimization import BayesianOptimization
            try:
                self.candidate_generator = BayesianOptimization(
                    weights=np.ones(Y_arr.shape[1]),
                    bounds=self.bounds,
                    constraints=self.constraints,
                    n_objectives=Y_arr.shape[1],
                    logic=self.logic,
                    random_state=0
                )
            except Exception as e:
                raise RuntimeError("Failed to instantiate BayesianOptimization") from e

        # 5. Delegate to BO
        try:
            points = self.candidate_generator.generate(
                X=X,
                Y=Y,
                n_candidates=n_candidates,
                T=T
            )
        except Exception as e:
            raise RuntimeError("Error in candidate_generator.generate()") from e

        # 6. Return at most n_candidates points
        return list(points[:n_candidates])




        # 1) If a BO instance is attached, use it
        if self.candidate_generator is not None:
            # make sure it's been fitted
            try:
                return self.candidate_generator.generate(
                    X=X,
                    Y=Y,
                    n_candidates=n_candidates,
                    T=T
                )
            except Exception as e:
                raise RuntimeError("Error in candidate_generator.generate") from e

    def initialization(self, ): 
        r"""
        Generate design points via design_func and filter by constraints.

        Parameters
        ----------
        design_func : Callable[[Callable], np.ndarray]
            A function that accepts a validator and returns candidate points.

        Returns
        -------
        np.ndarray
            Valid design points \(D\).  
            After generation, \(D = \{\mathbf{x}: validate(\mathbf{x})=True\}\).
        """
        if self.design is None:
            return []

        design_points = self.design( self.validate )
        self.design_points = design_points

        return self.design_points

    def __repr__(self):
        return (f"<DesignOfExperiments(logic={self.logic}, "
                f"num_constraints={len(self.constraints)})>")

# -------------------------------------------------------------------------
# 1. Full Factorial Design
# -------------------------------------------------------------------------
def design_full_factorial(levels_per_factor: List[List[float]], discrete_design: bool=True) -> np.ndarray:
    r"""
    Full factorial design: Cartesian product of levels.

    Let factor i have levels \(L_i\).  The design is
    .. math::
       D = L_1 \times L_2 \times \cdots \times L_n,
       \quad |D| = \prod_{i=1}^n |L_i|.

    Parameters
    ----------
    levels_per_factor : List[List[float]]
        Levels for each factor.
    discrete_design : bool

    Returns
    -------
    Callable
    """
    from itertools import product
    def func(validate):
        # Cartesian product to get all combinations
        raw_design = list(product(*levels_per_factor))

        # Convert to numpy array
        all_points = np.array(raw_design, dtype=int if discrete_design else float)
        # Filter out points that do not meet constraints
        valid_points = []
        for point in all_points:
            if validate(point):
                valid_points.append(point)

        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 2. Fractional Factorial Design (Basic 2-level example)
# -------------------------------------------------------------------------
def generate_fractional_factorial(n_factors: int, 
                                  fraction: float = 0.5, 
                                  discrete_design: bool=True) -> np.ndarray:
    """
    Generates a simple 2-level fractional factorial design for n_factors.
    By default, it takes only a fraction (e.g., 1/2) of the full factorial 
    to reduce the number of runs. (This is a simplistic approach; real 
    fractional factorial designs often use aliasing structures or 
    orthogonal arrays.)

    The 2-level design is assumed to be [-1, +1] for each factor.

    Parameters
    ----------
    n_factors : int
        Number of factors (dimensions).
    fraction : float, optional
        Fraction of the full factorial to keep. Must be between 0 and 1.
        Default is 0.5 (i.e., half-fraction).

    Returns
    -------
    np.ndarray
        Valid points in the fractional design that pass the constraints.
    """
    def func(validate):
        if not (0 < fraction <= 1):
            raise ValueError("fraction must be between 0 and 1.")

        from itertools import product
        
        # Full factorial 2^n: [-1, +1]
        levels = [-1.0, 1.0]
        full_design = list(product(levels, repeat=n_factors))
        full_design = np.array(full_design, dtype=int if discrete_design else float)

        # Shuffle and pick only a subset (the fraction)
        np.random.shuffle(full_design)
        n_subset = int(len(full_design) * fraction)
        subset_design = full_design[:n_subset]

        # Filter out points that do not meet constraints
        valid_points = [pt for pt in subset_design if validate(pt)]
        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 3. Central Composite Design (CCD)
# -------------------------------------------------------------------------
def generate_central_composite(n_factors: int,
                               alpha: float = None,
                               center_points: int = 1, 
                               discrete_design: bool=True) -> np.ndarray:
    """
    Generates a Central Composite Design (CCD) for n_factors using:
      - A 2-level factorial portion
      - Axial (star) points at ±alpha
      - Center points repeated 'center_points' times
      
    Typically, alpha is chosen such that the design is rotatable. 
    For a full-factorial of 2^n, a common choice is 
        alpha = (2^(n_factors/4)) 
    but it can vary depending on the design objective.

    Parameters
    ----------
    n_factors : int
        Number of design factors.
    alpha : float, optional
        The distance of the axial points from the center. If None, 
        uses 2^(n_factors/4) for approximate rotatability.
    center_points : int, optional
        How many times to replicate the center point. Default is 1.

    Returns
    -------
    np.ndarray
        Valid points from the CCD that satisfy constraints.
    """
    def func(validate):
        if alpha is None:
            alpha = 2 ** (n_factors / 4.0)  # approximate rotatable design

        from itertools import product
        # 1) Factorial portion (±1 for each factor)
        factorial_pts = list(product([-1.0, 1.0], repeat=n_factors))
        
        # 2) Axial points: one factor at ±alpha, rest are 0
        axial_pts = []
        for i in range(n_factors):
            for sign in [-1, 1]:
                pt = [0.0] * n_factors
                pt[i] = sign * alpha
                axial_pts.append(pt)

        # 3) Center points: all zeros, repeated
        center_pts = [[0.0] * n_factors for _ in range(center_points)]

        # Combine into a single array
        design = np.array(factorial_pts + axial_pts + center_pts, dtype=int if discrete_design else float)

        # Filter by constraints
        valid_points = [pt for pt in design if validate(pt)]

        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 4. Box-Behnken Design
# -------------------------------------------------------------------------
def generate_box_behnken(n_factors: int,
                        discrete_design: bool=True) -> np.ndarray:
    """
    Generates a Box-Behnken design (BBD) for n_factors. 
    This design is formed by combinations of middle levels 
    in the faces of an n-dimensional cube, plus the center point.
    
    In general, a Box-Behnken design does not include corners (±1, ±1, etc.),
    so it is useful when extreme points are infeasible. This simplified 
    version uses three levels: -1, 0, +1.
    
    For n_factors >= 3, the number of runs is 2n(n - 1) + center. 
    In practice, one might replicate the center point, but for 
    simplicity, we'll include a single center point here.

    Parameters
    ----------
    n_factors : int
        Number of factors.

    Returns
    -------
    np.ndarray
        Valid design points that satisfy constraints.
    """
    def func(validate):
        if n_factors < 2:
            raise ValueError("Box-Behnken typically requires n_factors >= 2.")

        # For a basic demonstration, we will:
        # 1) Generate all permutations of [-1, 0, +1] for each pair of factors.
        # 2) Ensure exactly two factors are at ±1 and all others are at 0, for each "block".
        # 3) Add the center point (0,0,...,0) once.

        # This is a simplified approach. 
        # A general Box-Behnken is typically built systematically for each pair of factors.

        design = []
        levels = [-1.0, 0.0, +1.0]

        # For each pair of factors (i, j), vary those two in [-1, +1, 0], 
        # while the rest are 0
        for i in range(n_factors):
            for j in range(i+1, n_factors):
                # Each combination for (i, j) with others = 0
                # We only take combinations where i and j are not both 0 
                # at the same time, to avoid duplicating center 
                # or missing edge combos. For Box-Behnken, 
                # typically factor pairs cycle through combos.
                for level_i in [-1.0, +1.0]:
                    for level_j in [-1.0, +1.0]:
                        pt = [0.0]*n_factors
                        pt[i] = level_i
                        pt[j] = level_j
                        design.append(pt)

        # Add center point
        center_pt = [0.0]*n_factors
        design.append(center_pt)

        design = np.array(design, dtype=int if discrete_design else float)

        # Filter by constraints
        valid_points = [pt for pt in design if validate(pt)]
        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 5. Plackett-Burman Design (Simplified Approach)
# -------------------------------------------------------------------------
def generate_plackett_burman(n_factors: int,
                            discrete_design: bool=True) -> np.ndarray:
    """
    Generates a simplified Plackett-Burman design for main effects screening.
    Typically, these designs come in multiples of 4 (e.g., 4, 8, 12, 16 factors).
    A full general solution requires a specific set of orthogonal arrays. 
    Here, we implement a minimal approach for demonstration only.

    Parameters
    ----------
    n_factors : int
        Number of factors. Usually a multiple of 4 for a proper 
        Plackett-Burman array.

    Returns
    -------
    np.ndarray
        Valid points from the design that pass constraints.
    """
    # For demonstration, let's do a basic approach if n_factors == 4 or 8.
    # In real usage, you'd either implement or import a specialized 
    # function for general PB designs.

    # Minimal set for n_factors=4:
    #  1   1   1  -1
    #  1  -1   1   1
    #  1   1  -1   1
    # -1   1   1   1
    # This is 4 runs for 4 factors.

    # Minimal set for n_factors=8 (example):
    # A standard 12-run array is often used. For simplicity, we do 8 runs for 8 factors.
    
    # If not recognized n_factors, raise an error or degrade to a full factorial approach.
    def func(validate):
        if n_factors == 4:
            design = np.array([
                [ 1,  1,  1, -1],
                [ 1, -1,  1,  1],
                [ 1,  1, -1,  1],
                [-1,  1,  1,  1]
            ], dtype=int if discrete_design else float)
        elif n_factors == 8:
            design = np.array([
                [ 1,  1,  1,  1, -1, -1, -1,  1],
                [ 1,  1, -1, -1,  1,  1, -1,  1],
                [ 1, -1,  1, -1,  1, -1,  1,  1],
                [ 1, -1, -1,  1, -1,  1,  1,  1],
                [-1,  1,  1, -1,  1, -1,  1,  1],
                [-1,  1, -1,  1, -1,  1,  1,  1],
                [-1, -1,  1,  1,  1,  1, -1,  1],
                [-1, -1, -1, -1, -1, -1, -1,  1]
            ], dtype=int if discrete_design else float)
        else:
            raise NotImplementedError(
                f"No example Plackett-Burman design implemented for {n_factors} factors."
            )

        # Filter by constraints
        valid_points = [pt for pt in design if validate(pt)]
        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 6. Taguchi Orthogonal Design (Illustrative)
# -------------------------------------------------------------------------
def generate_taguchi_orthogonal(array_name: str = "L4",
                                discrete_design: bool=True) -> np.ndarray:
    """
    Generates a simplified Taguchi orthogonal array design. 
    Common arrays are L4, L8, L9, L12, L16, L18, L32, etc. 
    This function provides only a minimal demonstration.

    Parameters
    ----------
    array_name : str, optional
        Name of a known Taguchi array. Defaults to "L4".
    
    Returns
    -------
    np.ndarray
        Valid points that pass constraints.
    """
    # Example: L4(2^3) Orthogonal Array
    # Typically used for up to 3 factors at 2 levels each.
    # Runs: 4. Factors: up to 3. 
    # Array structure (factors in columns):
    #   run | f1 | f2 | f3
    #   1   |  1 |  1 |  1
    #   2   |  1 | -1 | -1
    #   3   | -1 |  1 | -1
    #   4   | -1 | -1 |  1
    def func(validate):
        if array_name.upper() == "L4":
            design = np.array([
                [ 1,  1,  1],
                [ 1, -1, -1],
                [-1,  1, -1],
                [-1, -1,  1]
            ], dtype=int if discrete_design else float)
        else:
            raise NotImplementedError(
                f"Taguchi array '{array_name}' not implemented in this example."
            )

        # Filter by constraints
        valid_points = [pt for pt in design if validate(pt)]
        return np.array(valid_points)

    return func

# -------------------------------------------------------------------------
# 7. Mixture Design (Simplex-Lattice)
# -------------------------------------------------------------------------
def generate_mixture_design(n_components: int, 
                            grid_resolution: int = 3,
                            discrete_design: bool=True) -> np.ndarray:
    """
    Generates a simple simplex-lattice mixture design for n_components,
    where each factor corresponds to the proportion of a component.
    The sum of all n_components must be 1.0 for each point.
    
    This design discretizes the simplex with a given grid resolution.
    For instance, if grid_resolution=2 and n_components=3, 
    you get points at increments of 1/2 in the simplex (triangle).

    Parameters
    ----------
    n_components : int
        Number of mixture components (factors).
    grid_resolution : int
        Number of increments per component in [0,1] 
        subject to sum(component_i)=1.

    Returns
    -------
    np.ndarray
        Valid mixture points (each row sums to 1) that satisfy constraints.
    """
    # We can systematically generate all integer combinations 
    # of length n_components that sum to grid_resolution, 
    # then normalize by grid_resolution to get fractions that sum to 1.
    def func(validate):
        from itertools import product

        valid_points = []

        for combo in product(range(grid_resolution+1), repeat=n_components):
            if sum(combo) == grid_resolution:
                pt = np.array(combo, dtype=float) / float(grid_resolution)
                pt = np.array(pt, dtype= int if discrete_design else float)
                # Check constraints
                if validate(pt):
                    valid_points.append(pt)

        return np.array(valid_points)

# -------------------------------------------------------------------------
# 8. Latin Hypercube Sampling (LHS)
# -------------------------------------------------------------------------
def generate_latin_hypercube(n_factors: int, 
                             n_samples: int,
                             low: float = 0.0, 
                             high: float = 1.0,
                             max_iterations: int = 10000,
                             discrete_design: bool=True) -> np.ndarray:
    """
    Generates a Latin Hypercube Sample (LHS) in n_factors dimensions,
    returning n_samples points, each factor within [low, high].
    
    LHS attempts to sample the space so that each factor is 
    stratified into n_samples intervals, guaranteeing coverage 
    along each dimension.

    Parameters
    ----------
    n_factors : int
        Number of factors (dimensions).
    n_samples : int
        Number of LHS points to generate.
    low : float, optional
        Lower bound for each factor. Defaults to 0.0
    high : float, optional
        Upper bound for each factor. Defaults to 1.0
    max_iterations : int, optional
        Maximum trials to get valid points after constraint filtering.

    Returns
    -------
    np.ndarray
        Valid LHS points that meet constraints.
    """
    # Start with a basic LHS procedure
    # 1) Divide each dimension into n_samples intervals.
    # 2) Shuffle the order in each dimension.
    # 3) Pick a random point in each interval along that dimension.
    def func(validate):

        def lhs(dim, samples):
            # Basic LHS logic: each dimension is divided into 'samples' intervals
            # We'll shuffle them to ensure random positioning
            result = np.zeros((samples, dim))
            temp = np.zeros((samples))
            for i in range(dim):
                # Create random perm of [0..samples-1]
                perm = np.random.permutation(samples)
                # For each sample, choose a random location within the interval
                for j in range(samples):
                    temp[j] = (perm[j] + random.random()) / samples
                result[:, i] = temp
            return result

        attempts = 0
        valid_points = []
        while len(valid_points) < n_samples and attempts < max_iterations:
            # Generate a new LHS set
            lhs_samples = lhs(n_factors, n_samples)
            # Scale from [0,1] to [low, high]
            scaled_samples = low + lhs_samples * (high - low)
            scaled_samples = np.array(scaled_samples, dtype= int if discrete_design else float)
            # Filter points with constraints
            candidate_points = [pt for pt in scaled_samples if validate(pt)]
            valid_points.extend(candidate_points)
            attempts += 1

        if len(valid_points) < n_samples:
            print(f"Warning: Only generated {len(valid_points)} valid points "
                  f"out of requested {n_samples} after {attempts} attempts.")

        return np.array(valid_points[:n_samples])
    
    return func

# -------------------------------------------------------------------------
# 9. Space Filling Design (Greedy Maximin Approach)
# -------------------------------------------------------------------------
def generate_space_filling(n_factors: int,
                           n_points: int,
                           bounds: Optional[List[Tuple[float, float]]] = None,
                           candidate_multiplier: int = 50,
                           discrete_design: bool=True,
                           avoid_repetitions: bool=True,
                             ) -> Callable[[Callable[[np.ndarray], bool]], np.ndarray]:
    r"""
    Generate a space-filling design using a greedy maximin algorithm.

    The algorithm proceeds in three phases:

    1. **Candidate Pool Sampling**  
       Sample an initial pool of
       :math:`N = C \times n\_points`
       points uniformly from the hyper-rectangle
       :math:`\prod_{i=1}^d [b_i^{\min}, b_i^{\max}]`,
       where :math:`d = n\_factors` and
       :math:`C = \texttt{candidate_multiplier}`.  
       If `bounds` is `None`, defaults to :math:`[0,1]^d`.

    2. **Feasibility Filtering**  
       Retain only those points satisfying the user-supplied validator
       :math:`v(\mathbf{x})`, i.e.
       .. math::
          X = \{\mathbf{x}\in\mathbb{R}^d : v(\mathbf{x}) = 1\}.

    3. **Greedy Maximin Selection**  
       From :math:`X`, iteratively build the final set
       :math:`S = \{s_1, \dots, s_{n\_points}\}` by:
       .. math::
          s_1 \;\text{is arbitrary},\quad
          s_{k+1} = \arg\max_{x \in X\setminus S_k}
                     \min_{s\in S_k} \|x - s\|_2,
       until :math:`|S| = n\_points`.  This maximizes the minimum pairwise
       distance among selected points.

    Parameters
    ----------
    n_factors : int
        Dimensionality :math:`d` of the design space.
    n_points : int
        Number of final points to select.
    bounds : list of (float, float), optional
        Lower and upper bounds for each dimension; length must equal `n_factors`.
        Defaults to `[(0.0, 1.0)] * d`.
    candidate_multiplier : int
        Pool size factor :math:`C` (so pool size = `C * n_points`).
    discrete_design : bool
        If True, sample integer points in each interval; otherwise sample continuous.
    avoid_repetitions : bool
        If True, enforce uniqueness when building the candidate pool.

    Returns
    -------
    Callable[[Callable[[np.ndarray], bool]], np.ndarray]
        A function `f(v)` that, given a boolean validator `v(x)`, returns
        the selected design points as an array of shape `(n_points, d)`.

    Raises
    ------
    ValueError
        If `bounds` is provided and its length ≠ `n_factors`.
    """
    if bounds is None:
        bounds = [(0.0, 1.0)] * n_factors
    elif len(bounds) != n_factors:
        raise ValueError("Length of 'bounds' must equal n_factors.")
        
    def func(validate):
        candidate_count = candidate_multiplier * n_points
        candidates = []
        max_attempts = candidate_count * 10
        attempts = 0

        # Generate candidate pool of valid points
        unique_candidates = set()
        while len(candidates) < candidate_count and attempts < max_attempts:
            if discrete_design:
                candidate = np.array([random.randint(low, high) for (low, high) in bounds], dtype=int)
            else:
                candidate = np.array([random.uniform(low, high) for (low, high) in bounds], dtype=float)

            if validate(candidate):
                if avoid_repetitions:
                    candidate_tuple = tuple(candidate)  
                    if candidate_tuple not in unique_candidates:
                        unique_candidates.add(candidate_tuple)
                        candidates.append(candidate)
                else:
                    candidates.append(candidate)

            attempts += 1

        if len(candidates) < n_points:
            warnings.warn("Not enough valid candidate points were generated.")
            #raise RuntimeError("Not enough valid candidate points were generated.")

        candidates = np.array(candidates)

        # Greedy maximin selection: iteratively select the candidate 
        # that maximizes the minimum distance to the already selected points.
        selected = [candidates[0]]
        remaining = list(candidates[1:])
        
        while len(selected) < n_points and len(remaining)>0 :
            best_candidate = None
            best_distance = -1
            for candidate in remaining:
                distances = [np.linalg.norm(candidate - s) for s in selected]
                min_distance = min(distances)
                if min_distance > best_distance:
                    best_distance = min_distance
                    best_candidate = candidate

            if best_distance > 0:
                selected.append(best_candidate)
            remaining = [candidate for candidate in remaining if not np.array_equal(candidate, best_candidate)]

        return np.array(selected)

    return func

# =============================================================================
# Example Usage
# =============================================================================
if __name__ == "__main__":
    # Define constraints
    constraint1 = FeatureConstraint(
        check_func=ConstraintGenerator.greater_or_equal(0, 5.0),
        name="Feature0 >= 5",
        description="The first variable must be at least 5."
    )
    constraint2 = FeatureConstraint(
        check_func=ConstraintGenerator.sum_in_range( [0,1,2], 128, 128),
        name="Feature1 < 10",
        description="The second variable must be less than 10."
    )

    # Create a ConstraintManager with 'all' logic
    DoE = DesignOfExperiments(design=generate_space_filling(
                n_factors=5, 
                n_points=100, 
                bounds=[    [80,120], 
                            [0,20], 
                            [0,20], 
                            [40,80], 
                            [90,100], ] ), 
                logic="all", )
    
    DoE.add(constraint1)
    DoE.add(constraint2)

    # Instantiate DesignSpace without fixed bounds; feasibility is determined solely by the constraints.
    s = DoE.initialization()

    # Generate 20 valid design points
    try:
        valid_design_points = DoE.initialization()
        print("Valid design points:")
        for point in valid_design_points:
            print(point)
    except RuntimeError as e:
        print(str(e))
