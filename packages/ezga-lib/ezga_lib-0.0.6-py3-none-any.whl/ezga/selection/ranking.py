"""
ranking.py
----------

Provides routines to filter the top structures in a population based on energy, anomaly,
and diversity. Implements a Pareto-based selection function.
"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import zscore
from scipy.spatial.distance import mahalanobis
from sklearn.linear_model import Ridge

def filter_top_structures(
    structures,
    N: int,
    atom_labels: list[str] | None = None,
    cluster_counts: np.ndarray | None = None,
    temperature: float = 0.3,
    inflection_point_shift: float = 2,
    energy_weight: float = 0.8,
    distance_weight: float = 0.1
    ):
    r"""
    Select the top N structures by combining formation energy, anomaly, and diversity.

    This routine ranks a candidate set of structures via:

    1. **Composition matrix**  
       Build  
       .. math::
          X_{i\ell} = \bigl\lvert\{\,a\in\mathrm{atoms}(s_i)\mid\mathrm{label}(a)=L_\ell\}\bigr\lvert  
       for each candidate structure \\(s_i\\) and each label \\(L_\ell\\).  

    2. **Linear fitting of chemical potentials**  
       Solve ridge regression  
       .. math::
          \boldsymbol\mu = \arg\min_\mu \|X\,\mu - \mathbf{y}\|^2 + \alpha\|\mu\|^2,  
       where  
       \\(\mathbf{y}_i = E(s_i)\\) is the raw per‐atom potential energy and  
       \\(\alpha=10^{-5}\\).  
       Compute **formation energy**  
       .. math::
          \varepsilon_i = y_i - X_{i:}\,\boldsymbol\mu.

    3. **Pareto‐anomalous‐diverse‐low‐energy selection**  
       Call `select_pareto_anomalous_diverse_low_energy` with inputs:
       - `data_matrix=cluster_counts`  
       - `energy_vector=\varepsilon`  
       - `M=N`, `temperature=0.2`, `inflection_point_shift=0.5`,  
         `energy_weight`, `distance_weight`.  

    4. **Return**  
       Map the selected indices back into the original `structures` list and return
       the top N `Structure` objects.

    :param structures:
        List of candidate structures, each exposing  
        ``structure.AtomPositionManager.atomLabelsList`` (array of labels) and  
        ``structure.AtomPositionManager.E`` (per‐atom potential energy).
    :type structures: list[Any]
    :param N:
        Number of top structures to return.
    :type N: int
    :param atom_labels:
        Ordered list of atomic labels defining columns of the composition matrix.  
        Defaults to ``['Fe','V','Ni','H','O','K']`` if None.
    :type atom_labels: list[str] or None
    :param cluster_counts:
        Optional NxD array for non‐energy features (e.g., cluster counts) passed
        downstream to Pareto selection.
    :type cluster_counts: numpy.ndarray or None
    :param temperature:
        Temperature‐like parameter controlling the inflection in the selection
        sigmoid, by default 0.3.
    :type temperature: float
    :param inflection_point_shift:
        Offset added to the minimal formation energy when computing the
        selection sigmoid inflection point, by default 2.
    :type inflection_point_shift: float
    :param energy_weight:
        Weight \\(w\in[0,1]\\) balancing energy vs. anomaly in final probability.
    :type energy_weight: float
    :param distance_weight:
        Weight \\(\delta\in[0,1]\\) for diversity penalty in iterative selection.
    :type distance_weight: float
    :returns:
        List of the top N structures (same order as selected by the underlying sampler).
    :rtype: list[Any]
    """


    if atom_labels is None:
        atom_labels = ['Fe', 'V', 'Ni', 'H', 'O', 'K']

    # Composition matrix X
    X = np.array([
        [
            np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
            for label in atom_labels
        ]
        for structure in structures
    ])

    # Extract energies
    y = np.array([structure.AtomPositionManager.E for structure in structures])

    # Fit a linear model for chemical potentials
    model = Ridge(alpha=1e-5, fit_intercept=False)
    model.fit(X, y)
    chemical_potentials = model.coef_
    formation_energies = y - X.dot(chemical_potentials)

    print('Chemical potentials:', ' '.join([f'{label}: {mu}' for label, mu in zip(atom_labels, chemical_potentials)]))

    # Select structures using a Pareto-based approach
    selected_indices, dominant_indices = select_pareto_anomalous_diverse_low_energy(
        data_matrix=cluster_counts,
        energy_vector=formation_energies,
        M=N,
        temperature=0.2,
        inflection_point_shift=0.5,
        energy_weight=energy_weight,
        distance_weight=distance_weight
    )

    return [structures[dominant_indices[i]] for i in selected_indices]


def select_pareto_anomalous_diverse_low_energy(
    data_matrix: np.ndarray,
    energy_vector: np.ndarray,
    M: int,
    temperature: float = 5.0,
    inflection_point_shift: float = 1.0,
    energy_weight: float = 0.8,
    distance_weight: float = 0.1
    ):
    r"""
    Probabilistically select M structures optimizing anomaly, diversity, and low energy.

    **1. Mahalanobis anomaly score**  
    Normalize  
    .. math::
       Z = \mathrm{zscore}(X),\quad \bar Z= \mathrm{mean}(Z),  
       \Sigma^{-1} = \bigl(\mathrm{cov}(Z)+\epsilon I\bigr)^{-1}.  
    Then for each row \\(z_i\\),  
    .. math::
       d_i = \sqrt{(z_i - \bar Z)\,\Sigma^{-1}\,(z_i-\bar Z)^T}.

    **2. Pareto non‐dominated set**  
    Partition candidates by unique composition, then within each group
    find indices \\(i\\) not dominated by any \\(j\\):  
    .. math::
      \neg\bigl[y_j\le y_i,\;d_j\ge d_i,\;(y_j<y_i\lor d_j>d_i)\bigr].

    **3. Compute base probabilities**  
    For each Pareto index \\(i\\):
      - Inflection energy:  
        .. math::
           \eta_i = \frac{1}{1 + \exp\bigl((\varepsilon_i - \xi)/T\bigr)},
           \quad\xi = \min(\varepsilon) + \mathrm{inflection\_point\_shift}.
      - Normalized anomaly:  
        .. math::
           a_i = \frac{d_i}{\sum_j d_j}.
      - Combined weight:  
        .. math::
           p_i \propto w\,\eta_i + (1-w)\,a_i,\quad w=\mathrm{energy\_weight}.

    **4. Iterative diversity‐aware sampling**  
    Repeat until M distinct picks:
      a. If some selected \\(S\\) nonempty, compute for each remaining
         Pareto candidate \\(i\\):  
         .. math::
            \delta_i = \min_{j\in S}\parallel X_i - X_j\parallel_2,
            \quad
            p'_i \propto (1-\delta_w)\,p_i + \delta_w\,\frac{\delta_i}{\sum\delta},
         with diversity weight \\(\delta_w=\mathrm{distance\_weight}\\).  
      b. Draw one index via  
         `np.random.choice` with probability vector \\(p'\\).  
      c. Zero out its probability and re‐normalize for the next draw.

    :param data_matrix:
        NxD array of non‐energy descriptors (e.g., cluster counts or composition
        histograms).
    :type data_matrix: numpy.ndarray
    :param energy_vector:
        Length‐N vector of formation energies \\(\varepsilon_i\\).
    :type energy_vector: numpy.ndarray
    :param M:
        Number of structures to select.
    :type M: int
    :param temperature:
        Controls sharpness of the logistic energy term, by default 5.0.
    :type temperature: float
    :param inflection_point_shift:
        Offset to shift the sigmoid inflection point relative to minimal energy.
    :type inflection_point_shift: float
    :param energy_weight:
        Weight balancing energy vs. anomaly in base probabilities.
    :type energy_weight: float
    :param distance_weight:
        Weight for diversity penalty when sampling sequentially.
    :type distance_weight: float
    :returns:
        - **selected_indices** (ndarray): Indices of the M chosen Pareto points.  
        - **dominant_indices** (list[int]): Indices of all non‐dominated points.
    :rtype: (numpy.ndarray, list[int])
    """

    # Step 1: Compute Mahalanobis distance for anomaly detection
    normalized_data = zscore(data_matrix, axis=0)
    normalized_data = np.nan_to_num(normalized_data, nan=0.0)
    mean_vector = np.mean(normalized_data, axis=0)
    cov_matrix_inv = inv(np.cov(normalized_data, rowvar=False) + 1e-6 * np.eye(normalized_data.shape[1]))

    mahalanobis_distances = np.array([
        mahalanobis(row, mean_vector, cov_matrix_inv) for row in normalized_data
    ])

    # Step 2: Identify non-dominated (Pareto) points
    unique_compositions, inverse_indices = np.unique(data_matrix, axis=0, return_inverse=True)
    dominant_indices = []

    for unique_idx in range(len(unique_compositions)):
        matching_indices = np.where(inverse_indices == unique_idx)[0]

        group_dominant = []
        for i in matching_indices:
            dominated = False
            for j in matching_indices:
                if (energy_vector[j] <= energy_vector[i] and
                    mahalanobis_distances[j] >= mahalanobis_distances[i] and
                    (energy_vector[j] < energy_vector[i] or mahalanobis_distances[j] > mahalanobis_distances[i])):
                    dominated = True
                    break
            if not dominated:
                group_dominant.append(i)
        dominant_indices.extend(group_dominant)

    # Step 3: Probabilistic selection
    pareto_energy = energy_vector[dominant_indices]
    pareto_anomaly = mahalanobis_distances[dominant_indices]
    pareto_data = data_matrix[dominant_indices]

    inflection_point = np.min(pareto_energy) + inflection_point_shift

    # Weighted combination of energy and anomaly
    energy_term = 1 / (1 + np.exp((pareto_energy - inflection_point) / temperature))
    energy_term /= np.sum(energy_term)

    anomaly_term = pareto_anomaly / np.sum(pareto_anomaly)

    probabilities = energy_weight * energy_term + (1 - energy_weight) * anomaly_term
    probabilities /= np.sum(probabilities)

    # Step 4: Iterative selection with diversity
    selected_indices = []
    for _ in range(M):
        if selected_indices:
            selected_data = pareto_data[selected_indices]
            distances_to_selected = np.min(
                np.linalg.norm(pareto_data[:, np.newaxis] - selected_data, axis=2), axis=1
            )

            # Normalize
            prob_norm = probabilities / np.sum(probabilities)
            distances_term = distances_to_selected / np.sum(distances_to_selected)

            probabilities_corrected = ((1 - distance_weight) * prob_norm
                                       + distance_weight * distances_term)
            probabilities_corrected /= np.sum(probabilities_corrected)
        else:
            probabilities_corrected = probabilities

        # If all probabilities vanish, reset to uniform
        probabilities_corrected_nan = np.nan_to_num(probabilities_corrected, nan=0.0)
        if np.sum(probabilities_corrected_nan) == 0:
            probabilities_corrected_nan = np.ones(len(dominant_indices)) / len(dominant_indices)

        chosen_idx = np.random.choice(len(dominant_indices), p=probabilities_corrected_nan)
        selected_indices.append(chosen_idx)
        probabilities[chosen_idx] = 0  # "Remove" this index from future draws
        probabilities /= np.sum(probabilities)

    return np.array(selected_indices), dominant_indices
