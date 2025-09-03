"""
helper_functions.py
-------------------

Provides various helpers for checking convergence, generating random factors,
and other related tasks.
"""

import numpy as np
from sklearn.linear_model import Ridge
from scipy.optimize import lsq_linear
from typing import Optional

def solver_integer_local(X: np.ndarray, y: np.ndarray, regularization: float = 0.01, max_iter: int = 1000) -> np.ndarray:
    """
    Solves the regularized least squares problem with non-negative integer coefficients
    using a continuous relaxation followed by a simple local search (hill climbing).
    
    The optimization problem is defined as:
        minimize   || (X.T @ X + regularization * I) c - X.T @ y ||^2
        subject to c >= 0 and c is an integer vector.
    
    This method first computes a continuous solution using lsq_linear, rounds it to obtain an initial
    integer solution, and then iteratively improves it by checking local perturbations of each coefficient.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix with dimensions (n_samples, n_features).
    y : np.ndarray
        Response vector with dimensions (n_samples,).
    regularization : float, optional
        Regularization parameter (default is 0.01).
    max_iter : int, optional
        Maximum number of iterations for the local search (default is 1000).
    
    Returns
    -------
    np.ndarray
        Array of integer coefficients resulting from the optimization.
    """
    n_features = X.shape[1]
    
    # Construct matrix A and vector b for the formulation:
    # A = X.T @ X + regularization * I, and b = X.T @ y.
    A = X.T @ X + regularization * np.eye(n_features)
    b = X.T @ y

    # Define the objective function: f(c) = ||A*c - b||^2.
    def objective(c):
        return np.linalg.norm(A @ c - b)**2

    # Solve the continuous relaxation using lsq_linear.
    cont_sol = lsq_linear(A, b, bounds=(0, np.inf)).x
    
    # Round the continuous solution to obtain an initial integer solution.
    c_int = np.round(cont_sol).astype(int)
    # Ensure non-negative values.
    c_int = np.maximum(c_int, 0)
    
    current_value = objective(c_int)
    improved = True
    iterations = 0
    
    # Perform a simple local search (hill climbing).
    while improved and iterations < max_iter:
        improved = False
        for i in range(n_features):
            # Try adjusting the i-th coefficient by -1 and +1.
            for delta in [-1, 1]:
                candidate = c_int.copy()
                candidate[i] += delta
                # Skip if candidate becomes negative.
                if candidate[i] < 0:
                    continue
                candidate_value = objective(candidate)
                # If the candidate improves the objective, accept it.
                if candidate_value < current_value:
                    c_int = candidate
                    current_value = candidate_value
                    improved = True
                    break  # Exit inner loop if improvement is found.
            if improved:
                break  # Restart search from the new solution.
        iterations += 1

    return c_int

def oscillation_factor(generation, period, amplitude=0.5):
    """
    Computes an oscillation factor for the current generation using a cosine-based cycle.

    Parameters
    ----------
    generation : int
        Current generation index.
    period : int
        Number of generations per oscillation cycle.
    amplitude : float, optional
        Maximum amplitude of the oscillation. By default 1.0.

    Returns
    -------
    float
        A cyclical factor that varies between 0 and `amplitude * 2`.
        Example formula: amplitude * (1 + cos(2π * generation / period)).
    """
    return amplitude * (1.0 + np.cos(2.0 * np.pi * generation / period))

def decay_factor(generation, decay_rate):
    """
    Calculates an exponential decay factor from 1 down to near 0.

    Parameters
    ----------
    generation : int
        Current generation index.
    decay_rate : float
        Decay rate constant. Higher -> faster decay.

    Returns
    -------
    float
        Decay factor e^(-decay_rate * generation).
    """
    return np.exp(-decay_rate * generation)

def fitness_factor(
    objectives: np.ndarray,
    weights: Optional[np.ndarray] = None,
    temperature: float = 1.0,
    inflection_point: float = 1.0,
    min_fitness: float = 0.0,
    max_fitness: float = 1.0
    ) -> np.ndarray:
    r"""
    Compute a normalized fitness factor for each candidate from multi-objective scores.

    The computation follows these steps:

    1. **Weight determination**:
       Let \(K\) be the number of objectives. Define weights:
       .. math::
          w_k = \begin{cases}
            \frac{1}{K}, & \text{if } weights \text{ is None};\\
            weights_k / \sum_{j=1}^K weights_j, & \text{otherwise.}
          \end{cases}

    2. **Min-max normalization** of each objective column \(f_{ik}\) to \([0,1]\):
       .. math::
          f'_{ik} = \frac{f_{ik} - \min_i f_{ik}}{\max_i f_{ik} - \min_i f_{ik} + \epsilon}
       where \(\epsilon = 10^{-12}\) avoids division by zero.

    3. **Weighted cost** per candidate \(C_i\):
       .. math::
          C_i = \sum_{k=1}^K w_k \, f'_{ik},
          \quad C_i \in [0,1].

    4. **Logistic scaling** to compress cost into \((0,1)\):
       .. math::
          z_i = \frac{C_i - \phi}{T + \epsilon},
          \quad L_i = \frac{1}{1 + e^{z_i}},

       where:
       - \(T = \text{temperature}\) (steepness control),
       - \(\phi = \text{inflection_point}\).

    5. **Clipping** of logistic output:
       .. math::
          L_i \leftarrow \min\bigl(\max(L_i, \text{min_fitness}), \text{max_fitness}\bigr).

    6. **Inversion** so that better candidates (low cost) map to higher fitness:
       .. math::
          F_i = 1 - L_i,
          \quad F_i \in [0,1].

    :param objectives:
        Array of shape \((N,K)\) with objective values ("lower is better").
    :type objectives: numpy.ndarray

    :param weights:
        Optional array of length \(K\) for objective weighting. Equal weights used if None.
    :type weights: array-like or None

    :param temperature:
        Logistic temperature \(T > 0\), controlling sharpness of transition.
    :type temperature: float

    :param inflection_point:
        Logistic midpoint \(\phi\) for cost-to-logistic mapping.
    :type inflection_point: float

    :param min_fitness:
        Minimum allowed fitness \(F_i\) after clipping.
    :type min_fitness: float

    :param max_fitness:
        Maximum allowed fitness \(F_i\) after clipping.
    :type max_fitness: float

    :returns:
        Array of shape \((N,)\) containing fitness factors \(F_i\in[0,1]\).
    :rtype: numpy.ndarray
    """
    # Retrieve parameters with defaults
    N, K = objectives.shape

    # 1) Determine weights
    if weights is None:
        w = np.ones(K) / K
    else:
        w = np.array(weights, dtype=float)
        if w.shape[0] != K:
            raise ValueError("Length of self.weights must match # of objectives (K).")

    # 2) Min-max normalize each objective to 0..1 => 0 is best, 1 is worst
    eps = 1e-12
    norm_obj = np.zeros_like(objectives)
    for j in range(K):
        col = objectives[:, j]
        cmin, cmax = col.min(), col.max()
        spread = cmax - cmin
        if spread < eps:
            norm_obj[:, j] = 0.0
        else:
            norm_obj[:, j] = (col - cmin) / (spread + eps)

    # 3) Weighted sum => cost in [0..1]
    cost = np.dot(norm_obj, w)  # shape (N,)

    # 4) Convert cost -> logistic scale => 0..1
    #    If cost is lower, logistic => smaller => we might invert it.
    scaled = (cost - inflection_point) / (temperature + eps)
    logistic_values = 1.0 / (1.0 + np.exp(scaled))
    
    # 5) Cap them if desired
    logistic_values = np.minimum(logistic_values, max_fitness)
    logistic_values = np.maximum(logistic_values, min_fitness)

    # 6) Invert so that 1 => "best", 0 => "worst"
    #    i.e. cost=0 => logistic ~ a bit > 0 => fitness => close to 1
    fitness = 1.5 - logistic_values

    return fitness

def has_converged(series, N, tolerance):
    """
    Checks if a time series has converged based on the last N values' standard deviation.

    Parameters
    ----------
    series : list or np.ndarray
        The time series data.
    N : int
        Number of last values to check.
    tolerance : float
        The threshold for standard deviation below which we consider convergence.

    Returns
    -------
    bool
        True if converged, False otherwise.
    """
    if len(series) < N:
        return False
    last_values = np.array(series[-N:])
    return np.std(last_values) <= tolerance
