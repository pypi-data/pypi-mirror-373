"""
soap_cluster_analyzer_refactored.py
==================================
A pythonic rewrite of the original *SOAPClusterAnalyzer* utility that

* Computes Smooth Overlap of Atomic Positions (SOAP) descriptors for a list
  of **ase**-compatible containers.
* Performs dimensionality reduction (PCA) followed by K‑means clustering
  (with a simple *elbow* placeholder for *k* optimisation).
* Consolidates per‑structure cluster populations into a matrix and evaluates
  Mahalanobis distances as an anomaly score.

The public interface stays **backwards‑compatible** with the original script:

>>> analyzer = SOAPClusterAnalyzer()
>>> scores   = analyzer.compute(structures)
>>> counts   = analyzer.get_cluster_counts(structures)

A convenience *extract_cluster_counts* function is provided for quick access
from procedural code.

Unit tests are included at the bottom of the file – they can be executed
with

    python soap_cluster_analyzer_refactored.py

or via *pytest* / *unittest discover*.
"""

from __future__ import annotations

###############################################################################
# Standard‑library imports
###############################################################################
import logging
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple, Optional
from collections.abc import Sequence

###############################################################################
# Third‑party imports – grouped by provider
###############################################################################
import numpy as np
from numpy.linalg import LinAlgError, inv
from scipy.spatial.distance import mahalanobis
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import silhouette_score

# *sage_lib* is an external dependency shipped with SAGE‑Lab.
from sage_lib.partition.Partition import Partition  # type: ignore

###############################################################################
# Library‑wide configuration
###############################################################################
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence scikit‑learn convergence spam in unit tests.
import warnings

warnings.filterwarnings("ignore", category=ConvergenceWarning)

__all__ = [
    "SOAPClusterAnalyzer",
    "extract_cluster_counts",
]

###############################################################################
# Helper utilities
###############################################################################

def find_optimal_kmeans_k(data: np.ndarray, max_k: int=15) -> int:
    """
    Finds an optimal number of clusters (between 2..max_k) using silhouette score.
    If data has fewer samples than 2, returns 1 cluster by default.
    """
    if data.shape[0] < 2:
        return 1

    best_k = 2
    best_silhouette = -1

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(data)
            # If fewer than 2 distinct clusters are found, skip this iteration.
            if len(set(labels)) < 2:
                continue

            try:
                score = silhouette_score(data, labels)
                if score > best_silhouette:
                    best_silhouette = score
                    best_k = k
            except Exception:
                # If silhouette_score fails, skip to the next value of k.
                pass

    return best_k


def _safe_inverse(cov: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Return *cov*⁻¹, falling back to *Tikhonov* regularisation when singular."""

    try:
        return inv(cov)
    except LinAlgError:
        return inv(cov + np.eye(cov.shape[0]) * eps)


###############################################################################
# Main public API
###############################################################################


@dataclass
class SOAPClusterAnalyzer:
    """Analyse structural anomalies in a *SOAP* feature space.

    Parameters
    ----------
    n_components
        Number of principal components (PCA) to keep per species.
    r_cut, n_max, l_max, sigma
        Hyper‑parameters forwarded to :py:meth:`Partition.get_SOAP`.
    max_clusters
        Upper bound on *k* for the *k*‑means stage.
    """

    n_components: int = 5
    r_cut: float = 4.0
    n_max: int = 2
    l_max: int = 2
    sigma: float = 0.5
    max_clusters: int = 10

    # ---------------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------------

    def compute(self, structures: Sequence) -> np.ndarray:
        r"""
        Compute a per-structure Mahalanobis anomaly score using SOAP descriptors, PCA, and K-means clustering.

        The algorithm proceeds in eight stages:

        1. **Input validation**  
           Ensure `structures` is a `Sequence` and let  
           :math:`n = |\text{structures}|`.  
           Return an empty array if :math:`n=0`.  
           If \[n < \texttt{n_components}\], there is insufficient data for a stable covariance estimate, so return zeros:

           .. math::
           
              \mathbf{s} = \mathbf{0} \in \mathbb{R}^n.

        2. **SOAP descriptor computation**  
           Invoke the external `Partition.get_SOAP` to obtain:
           - A mapping of species to descriptor arrays  
             :math:`D^{(s)} \in \mathbb{R}^{n_{\text{atoms},s}\times F}`  
           - A mapping of species to per-atom index lists  
             :math:`I^{(s)} = \{(j,i)\}` indicating atom ‌i belongs to structure j.  
           If no descriptors are returned, return zeros.

        3. **Dimensionality reduction per species**  
           For each species ⁠:math:`s`, apply PCA with :math:`d = \texttt{n_components}`:
           .. math::
              Z^{(s)} = \mathrm{PCA}_{d}\bigl(D^{(s)}\bigr),
              \quad Z^{(s)} \in \mathbb{R}^{n_{\text{atoms},s}\times d}.
           If PCA fails or :math:`F<d`, fall back to a zero matrix of shape 
           :math:`(n,1)`.

        4. **Optimal cluster count**  
           Determine the number of clusters :math:`k^{(s)}` for each species via
           `find_optimal_kmeans_k`, i.e.  
           .. math::
              k^{(s)} = \arg\max_{2 \le k \le \min(n_{\text{atoms},s},\,\texttt{max_clusters})}
                        \text{silhouette\_score}\bigl(Z^{(s)},\,k\bigr),
           with a lower bound of 1.

        5. **K-means clustering**  
           Fit `KMeans(n_clusters=k^{(s)})` to :math:`Z^{(s)}`, producing labels  
           :math:`\ell^{(s)}_i \in \{0,\dots,k^{(s)}-1\}` for each atom.

        6. **Per-structure cluster count matrix**  
           Build a count matrix 
           :math:`C^{(s)} \in \mathbb{N}^{n\times k^{(s)}}` with
           .. math::
              C^{(s)}_{j,c} \;=\; \sum_{(j,i)\in I^{(s)}} \mathbf{1}\bigl(\ell^{(s)}_i = c\bigr).
           Concatenate across species:
           .. math::
              C = \bigl[\,C^{(s_1)} \mid C^{(s_2)} \mid \dots\bigr]
              \in \mathbb{N}^{n \times K_{\mathrm{total}}}.

        7. **Covariance estimation**  
           Compute the sample mean and covariance of the rows of :math:`C`:
           .. math::
              \mu = \frac{1}{n}\sum_{j=1}^n C_{j,\cdot}, 
              \quad
              \Sigma = \frac{1}{n-1}\bigl(C - \mu\bigr)^\top \bigl(C - \mu\bigr).
           Invert with Tikhonov regularisation if necessary.

        8. **Mahalanobis anomaly score**  
           For each structure :math:`j`, compute
           .. math::
              d_j = \sqrt{\,\bigl(C_{j,\cdot} - \mu\bigr)\,\Sigma^{-1}\,
                          \bigl(C_{j,\cdot} - \mu\bigr)^\top\,}\,.
           Return the vector 
           :math:`\mathbf{d} = [d_1,\dots,d_n]^\top \in \mathbb{R}^n`.

        Parameters
        ----------
        structures : Sequence
            ASE‐compatible containers for which to compute SOAP descriptors.

        Returns
        -------
        np.ndarray, shape (n,)
            Mahalanobis anomaly scores per structure.

        Raises
        ------
        TypeError
            If `structures` is not a list or tuple.
        """

        """Return one Mahalanobis anomaly score per structure."""

        n_structures = self._validate_input(structures)
        if n_structures == 0:
            return np.empty(0)
        if n_structures < self.n_components:
            # Not enough data for a stable covariance estimate – return zeros.
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 1. Compute species‑resolved SOAP descriptors.
        # ------------------------------------------------------------------
        partition = Partition()
        partition.containers = list(structures)  # *Partition* expects a list.
        desc_by_species, idx_by_species = partition.get_SOAP(
            r_cut=self.r_cut,
            n_max=self.n_max,
            l_max=self.l_max,
            sigma=self.sigma,
            save=False,
            cache=False,
        )
        if not desc_by_species:
            # No atoms – return zeros.
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 2. Reduce dimensionality + cluster per species.
        # ------------------------------------------------------------------
        cluster_matrices: List[np.ndarray] = []

        for specie, descriptors in desc_by_species.items():
            if descriptors.size == 0:
                continue  # No atoms of this species.

            atom_indices = idx_by_species[specie]
            feature_dim = descriptors.shape[1]

            if feature_dim < self.n_components:
                # Degenerate case – one column fit.
                cluster_matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            # *PCA* can throw if rank < n_components; catch and skip gracefully.
            try:
                compressed = PCA(n_components=self.n_components).fit_transform(
                    descriptors
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("PCA failed for %s: %s", specie, exc)
                cluster_matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            k_max = min(compressed.shape[0], self.max_clusters)
            k_opt = find_optimal_kmeans_k(compressed, k_max)

            cluster_counts = np.zeros((n_structures, max(k_opt, 1)), dtype=int)

            if k_opt <= 1:
                # All atoms belong to a single cluster – just count per structure.
                for atom_idx in range(compressed.shape[0]):
                    struct_idx = atom_indices[atom_idx][0]
                    cluster_counts[struct_idx, 0] += 1
            else:
                labels = KMeans(n_clusters=k_opt, random_state=42).fit_predict(
                    compressed
                )
                for atom_idx, lbl in enumerate(labels):
                    struct_idx = atom_indices[atom_idx][0]
                    cluster_counts[struct_idx, lbl] += 1

            cluster_matrices.append(cluster_counts)

        if not cluster_matrices:
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 3. Stack species matrices → shape = (n_structures, total_clusters).
        # ------------------------------------------------------------------
        combined = np.hstack(cluster_matrices)
        if combined.shape[1] == 0:
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 4. Mahalanobis anomaly score per row.
        # ------------------------------------------------------------------
        mean_vec = combined.mean(axis=0)
        cov = np.cov(combined, rowvar=False)
        inv_cov = _safe_inverse(cov)

        return np.array(
            [mahalanobis(row, mean_vec, inv_cov) for row in combined]
        )

    # ------------------------------------------------------------------

    def get_cluster_counts_classic(self, structures: Sequence) -> np.ndarray:
        r"""
        Compute and return the per-structure cluster-count matrix obtained from species-wise SOAP descriptors.

        The procedure consists of six steps:

        1. **Input validation**  
           Verify `structures` is a list or tuple and let  
           :math:`n = |\text{structures}|`.  
           If :math:`n = 0`, return an empty matrix of shape :math:`(0,0)`.

        2. **SOAP descriptor extraction**  
           Use the external `Partition.get_SOAP` call to obtain for each species :math:`s`:
           - Descriptor array  
             :math:`D^{(s)} \in \mathbb{R}^{N_s \times F}`, where :math:`N_s` is the total number of atoms of species :math:`s` and :math:`F` is the per-atom SOAP feature dimension.
           - Index mapping  
             :math:`I^{(s)} = \{(j,i)\}` indicating atom :math:`i` belongs to structure :math:`j`.

        3. **Dimensionality check and PCA**  
           For each :math:`D^{(s)}`:
           - If :math:`F < d` (with :math:`d = \texttt{n_components}`), substitute a zero-column count matrix of shape :math:`(n,1)`.
           - Otherwise, apply PCA to reduce to :math:`d` components:
             .. math::
                Z^{(s)} = \mathrm{PCA}_{d}\bigl(D^{(s)}\bigr), 
                \quad Z^{(s)} \in \mathbb{R}^{N_s \times d}.
           PCA exceptions are not expected here since :math:`F \ge d`.

        4. **Optimal cluster number selection**  
           Determine the number of clusters :math:`k^{(s)}` for species :math:`s` by:
           .. math::
              k^{(s)} = \arg\max_{2 \le k \le \min(N_s,\;\texttt{max_clusters})}
                         \text{silhouette\_score}\bigl(Z^{(s)}, k\bigr),
           with a lower bound of 1 resulting from `find_optimal_kmeans_k`.

        5. **K-means clustering and count assembly**  
           - Fit `KMeans(n_clusters=k^{(s)})` on :math:`Z^{(s)}` to obtain labels :math:`\ell^{(s)}_i` for each atom index :math:`i`.  
           - Build a count matrix  
             :math:`C^{(s)} \in \mathbb{N}^{n \times k^{(s)}}` where
             .. math::
                C^{(s)}_{j,c} \;=\; \sum_{(j,i)\in I^{(s)}} \mathbf{1}\bigl(\ell^{(s)}_i = c\bigr).
           - If :math:`k^{(s)} = 0` (no atoms), skip species :math:`s`.

        6. **Concatenation and return**  
           Horizontally stack all species count matrices:
           .. math::
              C = \bigl[\,C^{(s_1)} \mid C^{(s_2)} \mid \dots \bigr]
              \in \mathbb{N}^{n \times K_{\mathrm{total}}}.
           If no species produced counts, return a zero matrix of shape :math:`(n,0)`.

        Parameters
        ----------
        structures : Sequence
            ASE-compatible atomic containers to process via SOAP.

        Returns
        -------
        np.ndarray, shape (n, K_{\mathrm{total}})
            Concatenated cluster counts per structure across all species.

        Raises
        ------
        TypeError
            If `structures` is not a list or tuple.
        """
        
        """Return the concatenated cluster count matrix."""

        n_structures = self._validate_input(structures)
        if n_structures == 0:
            return np.empty((0, 0), dtype=int)

        partition = Partition()
        partition.add_container( structures )

        desc_by_species, idx_by_species = partition.get_SOAP(
            r_cut=self.r_cut,
            n_max=self.n_max,
            l_max=self.l_max,
            sigma=self.sigma,
            save=False,
            cache=False,
        )

        matrices: List[np.ndarray] = []
        for specie, descriptors in desc_by_species.items():
            if descriptors.size == 0:
                continue
            atom_indices = idx_by_species[specie]
            feature_dim = descriptors.shape[1]

            if feature_dim < self.n_components:
                matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            compressed = PCA(n_components=self.n_components).fit_transform(
                descriptors
            )
            k_max = min(compressed.shape[0], self.max_clusters)
            k_opt = find_optimal_kmeans_k(compressed, k_max)

            counts = np.zeros((n_structures, max(k_opt, 1)), dtype=int)
            if k_opt <= 1:
                for atom_idx in range(compressed.shape[0]):
                    struct_idx = atom_indices[atom_idx][0]
                    counts[struct_idx, 0] += 1
            else:
                labels = KMeans(n_clusters=k_opt, random_state=42).fit_predict(
                    compressed
                )
                for atom_idx, lbl in enumerate(labels):
                    struct_idx = atom_indices[atom_idx][0]
                    counts[struct_idx, lbl] += 1
            matrices.append(counts)

        return np.hstack(matrices) if matrices else np.zeros((n_structures, 0))

    # ──────────────────────────────────────────────────────────────────────────────
    #  Speed-optimised cluster-count routine
    # ──────────────────────────────────────────────────────────────────────────────
    def get_cluster_counts(
        self,
        structures: Sequence,
        *,
        max_atoms_per_species: int = 800,
        batch_size_km: int = 1024,
        silhouette_k_grid: Tuple[int, ...] = (2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20),
    ) -> np.ndarray:
        r"""
        Return a **matrix of per-structure cluster counts** obtained from SOAP
        descriptors, but with several **speed optimisations**:

        1. *Random sub-sampling*  
           For each chemical species, at most ``max_atoms_per_species`` atoms are
           processed.  This caps the PCA and clustering cost to :math:`\mathcal{O}`
           (``max_atoms_per_species``).

        2. *Mini-Batch k-means*  
           ``MiniBatchKMeans`` converges quickly on large samples while offering
           results very close to full k-means.

        3. *Coarse silhouette scan*  
           Instead of testing every ``k = 2…k_max``, only the values listed in
           ``silhouette_k_grid`` are evaluated to pick the optimal number of
           clusters.  Adjust the tuple if finer granularity is required.

        4. *Vectorised accumulation*  
           ``np.add.at`` is used to fill the count matrix without explicit Python
           loops.

        Parameters
        ----------
        structures
            Iterable of ASE‐compatible atomic containers.
        max_atoms_per_species
            Maximum number of atoms per species used for PCA / clustering.  Set
            to ``None`` to disable sub-sampling.
        batch_size_km
            Mini-batch size for ``MiniBatchKMeans``.  Irrelevant if
            ``k_opt == 1`` or if you replace the solver with the classic
            ``KMeans``.
        silhouette_k_grid
            Candidate *k* values evaluated when searching the optimal number of
            clusters by silhouette score.  Must contain integers ≥ 2.

        Returns
        -------
        np.ndarray, shape ``(n_structures, K_total)``
            Horizontally concatenated cluster-count matrix.  If no atoms are found
            return a zero-width matrix ``(n_structures, 0)``.

        Notes
        -----
        * All objectives in the GA are *minimisation*; no changes here.
        * The new offspring of the current generation are not included when
          ranking old structures (they automatically survive one generation).
        """
        # ───────────────────────────────────────────────────────────────────
        # 0. Light-weight validation
        # ───────────────────────────────────────────────────────────────────
        n_structures = self._validate_input(structures)
        if n_structures == 0:
            return np.empty((0, 0), dtype=int)

        # ───────────────────────────────────────────────────────────────────
        # 1. SOAP descriptor extraction (unchanged)
        # ───────────────────────────────────────────────────────────────────
        part = Partition()
        part.add_container( structures )
        desc_by_sp, idx_by_sp = part.get_SOAP(
            r_cut=self.r_cut, n_max=self.n_max, l_max=self.l_max, sigma=self.sigma,
            save=False, cache=False,
        )

        matrices: List[np.ndarray] = []

        # ───────────────────────────────────────────────────────────────────
        # 2. Loop over species
        # ───────────────────────────────────────────────────────────────────
        for specie, descriptors in desc_by_sp.items():
            if descriptors.size == 0:           # no atoms of this specie
                continue

            atom_idx_map = idx_by_sp[specie]    # list/ndarray, shape (N_s, 2)
            N_s, feature_dim = descriptors.shape

            # ── 2A. Quick exit if dimensionality too low ──────────────────
            if feature_dim < self.n_components:
                matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            # ── 2B. Random sub-sampling (Layer A) ─────────────────────────
            if (max_atoms_per_species is not None) and (N_s > max_atoms_per_species):
                sel = np.random.choice(N_s, max_atoms_per_species, replace=False)
                descriptors_sub  = descriptors[sel]
                atom_idx_map_sub = np.asarray(atom_idx_map)[sel]   # -- ndarray!
            else:
                descriptors_sub  = descriptors
                atom_idx_map_sub = np.asarray(atom_idx_map)        # ensure ndarray

            # ── 2C. PCA dimensionality reduction ─────────────────────────
            Z = PCA(n_components=self.n_components).fit_transform(descriptors_sub)

            # ── 2D. Pick optimal *k* with a coarse silhouette grid ────────
            k_max = min(Z.shape[0], self.max_clusters)
            if k_max < 2:
                k_opt = 1
            else:
                # Restrict grid to valid candidates ≤ k_max
                k_grid = [k for k in silhouette_k_grid if 2 <= k <= k_max] or [2]
                best_k, best_sil = 1, -1.0
                for k in k_grid:
                    labels_tmp = MiniBatchKMeans(
                        n_clusters=k, batch_size=batch_size_km, random_state=42
                    ).fit_predict(Z)
                    sil = silhouette_score(Z, labels_tmp) if k > 1 else -1.0
                    if sil > best_sil:
                        best_k, best_sil = k, sil
                k_opt = best_k

            # ── 2E. Final clustering (Mini-Batch k-means) ─────────────────
            if k_opt > 1:
                labels = MiniBatchKMeans(
                    n_clusters=k_opt, batch_size=batch_size_km, random_state=42
                ).fit_predict(Z)
            else:
                labels = np.zeros(Z.shape[0], dtype=int)   # single cluster

            # ── 2F. Build the per-structure count matrix (vectorised) ─────
            counts = np.zeros((n_structures, max(k_opt, 1)), dtype=int)
            struct_ids = atom_idx_map_sub[:, 0]            # (N_s_sub,)
            np.add.at(counts, (struct_ids, labels), 1)     # fast accumulation
            matrices.append(counts)

        # ───────────────────────────────────────────────────────────────────
        # 3. Concatenate and return
        # ───────────────────────────────────────────────────────────────────
        return np.hstack(matrices) if matrices else np.zeros((n_structures, 0))


    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_input(structures: Sequence) -> int:
        """Validate *structures* and return *len(structures)*."""

        if not isinstance(structures, (list, tuple)):
            raise TypeError("'structures' must be a list or tuple of containers.")
        return len(structures)


###############################################################################
# Procedural helper – kept for backward compatibility
###############################################################################

def extract_cluster_counts(containers: Sequence, **kwargs) -> np.ndarray:
    """Return the cluster‑count matrix for *containers* using keyword overrides."""

    return SOAPClusterAnalyzer(**kwargs).get_cluster_counts(containers)


###############################################################################
# Unit‑tests (can be run with `python soap_cluster_analyzer_refactored.py`)
###############################################################################

if __name__ == "__main__":
    # Register under canonical name so *unittest.mock.patch* works in scripts.
    sys.modules["soap_cluster_analyzer"] = sys.modules[__name__]

    import unittest
    from unittest.mock import patch

    import matplotlib.pyplot as plt

    # ------------------------------------------------------------------
    # Test‑helpers
    # ------------------------------------------------------------------

    def _synthetic_containers(n: int) -> List[str]:
        """Return dummy identifiers – SOAP will be patched in tests."""

        return [f"structure_{i}" for i in range(n)]

    # ------------------------------------------------------------------
    # Test‑suite
    # ------------------------------------------------------------------

    class TestSOAPClusterAnalyzer(unittest.TestCase):
        """Minimal non‑exhaustive smoke tests – extend as required."""

        def setUp(self) -> None:  # noqa: D401 – short description style.
            self.n_structures = 5
            self.structures = _synthetic_containers(self.n_structures)

        # -------------------------- compute() ---------------------------
        @patch("soap_cluster_analyzer.Partition")
        def test_empty_input(self, mock_partition):  # noqa: ANN001
            analyzer = SOAPClusterAnalyzer()
            result = analyzer.compute([])
            self.assertEqual(result.size, 0)
            mock_partition.assert_not_called()

        @patch("soap_cluster_analyzer.Partition")
        def test_synthetic_scores(self, mock_partition):  # noqa: ANN001
            n_atoms, n_features = 50, 10
            descriptors = np.random.rand(n_atoms, n_features)
            atom_info = [(i % self.n_structures, i) for i in range(n_atoms)]

            mock_inst = mock_partition.return_value
            mock_inst.get_SOAP.return_value = ({"A": descriptors}, {"A": atom_info})

            analyzer = SOAPClusterAnalyzer(n_components=3, max_clusters=4)
            scores = analyzer.compute(self.structures)
            self.assertEqual(scores.shape, (self.n_structures,))

        # ----------------- plotting & cluster matrix -------------------
        @patch("soap_cluster_analyzer.Partition")
        def test_plot_and_matrix(self, mock_partition):  # noqa: ANN001
            n_atoms, n_features = 30, 8
            descriptors = np.random.rand(n_atoms, n_features)
            atom_info = [(i % self.n_structures, i) for i in range(n_atoms)]

            mock_inst = mock_partition.return_value
            mock_inst.get_SOAP.return_value = ({"B": descriptors}, {"B": atom_info})

            analyzer = SOAPClusterAnalyzer(n_components=2, max_clusters=3)
            scores = analyzer.compute(self.structures)

            # Quick plot – verifies nothing crashes during I/O.
            plt.figure()
            plt.plot(range(len(scores)), scores)
            plt.xlabel("Structure Index")
            plt.ylabel("Anomaly Score")
            plt.title("Synthetic Anomaly Scores")
            plt.close()

            counts = extract_cluster_counts(
                self.structures, n_components=2, max_clusters=3
            )
            self.assertEqual(counts.shape[0], self.n_structures)

    # ------------------------------------------------------------------
    # Execute tests when the module is run directly.
    # ------------------------------------------------------------------
    unittest.main()
