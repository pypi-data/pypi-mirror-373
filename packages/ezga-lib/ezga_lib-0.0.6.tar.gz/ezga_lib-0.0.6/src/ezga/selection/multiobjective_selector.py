from __future__ import annotations

"""probabilistic_pareto_sampler.py

Stochastic Pareto‑aware selector with:
- Independent objective fusion temperature (`objective_temperature`)
- Separate sampling temperature (`sampling_temperature`)
- Optional objective normalization
- Diversity promotion and repetition penalization

Key formulas:
  • Shift: f'_ik = f_ik − min_k(f_ik) ≥ 0
  • Normalize (optional): \tilde f = (f' − mean_k)/std_k
  • Boltzmann fusion:
        Z_i = ∑_k w_k·exp(−fusion_k / T_obj)
        F_i = −T_obj·ln(Z_i + ε)
  • Cost before sampling:
        C_i = F_i − λ·R_i + κ·c_i
  • Sampling with T_samp:
        p_i ∝ exp(−C_i / T_samp)

Unit tests validate shape, distribution smearing, and diversity repulsion.
"""

from dataclasses import dataclass, field
from typing import Optional
import unittest

import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.special import logsumexp

__all__ = ["Selector"]

_EPS = 1e-12

def _repulsion_score(
    cand_feat: np.ndarray,
    sel_feat: np.ndarray,
    metric: str,
    mode: str,
    eps: float = _EPS,
) -> np.ndarray:
    if sel_feat.size == 0:
        return np.zeros(cand_feat.shape[0])
    dmat = pairwise_distances(cand_feat, sel_feat, metric=metric)
    if mode == "avg":
        dvals = dmat.mean(axis=1)
    elif mode == "min":
        dvals = dmat.min(axis=1)
    elif mode == "max":
        dvals = dmat.max(axis=1)
    else:
        raise ValueError("repulsion_mode must be 'avg', 'min', or 'max'.")

    dmin, dmax = dvals.min(), dvals.max()
    #return (dvals - dmin) / (dmax - dmin + eps)
    return np.log(1.0 / (dvals + eps))

@dataclass
class Selector:
    """Probabilistic selector for multi‑objective optimisation.

    Parameters
    ----------
    weights : Optional[np.ndarray]
        Importance of each objective (sum to 1). Default equal.
    repulsion_weight : float
        λ ≥ 0, diversity strength.
    objective_temperature : float
        T_obj ≥ 0, acts on objectives (same units as f).
    sampling_temperature : float
        T_samp ≥ 0, scales sampling sharpness.
    normalize_objectives : bool
        If True, apply zero‑mean, unit‑variance normalization after shift.
    repetition_penalty : bool
        γ ∈ (0,1], multiplicative penalty per repeat.
    size : int
        Number of structures to select.
    repulsion_mode : str
        'avg', 'min', or 'max'.
    metric : str
        Distance metric for pairwise_distances.
    random_seed : Optional[int]
        For reproducibility.
    """
    # —————————————————————————————————————————————
    # Public API fields hyper‑parameters (all optional, with defaults)
    # —————————————————————————————————————————————
    weights: Optional[np.ndarray]   = None
    repulsion_weight: float         = 1.0
    objective_temperature: float    = 1.0
    sampling_temperature: float     = 1.0
    normalize_objectives: bool      = False
    repetition_penalty: bool        = True
    size: int                       = 1
    repulsion_mode: str             = "min"
    metric: str                     = "manhattan"
    selection_method: str           = "stochastic"  # 'stochastic'|'roulette'|'nondominated_sorted'|'nsga3'
    random_seed: Optional[int]      = None

    # Repetition‑penalty controls
    steepness: float                = 10.0
    counts: Optional[np.ndarray]    = None
    max_count: int                  = 100
    cooling_rate: float             = 0.1

    # NSGA‑III controls
    divisions: int                  = 12

    # —————————————————————————————————————————————
    # Internal state (not passed by user)
    # —————————————————————————————————————————————
    _rng: np.random.Generator       = field(init=False, repr=False)

    # ==========================================================================
    #                         Life‑cycle helpers
    # ==========================================================================
    def __post_init__(self):
        if self.objective_temperature < 0:
            raise ValueError("objective_temperature must be non‑negative")
        if self.sampling_temperature < 0:
            raise ValueError("sampling_temperature must be non‑negative")
        if not isinstance(self.repetition_penalty, bool):
            raise ValueError("repetition_penalty must be in (0,1]")
        self._rng = np.random.default_rng(self.random_seed)

    # ----------------------------------------------------------------------
    #                          Utility functions
    # ----------------------------------------------------------------------
    @staticmethod
    def _normalize_objectives(objectives, eps=_EPS):
        """
        Min-max normalize each objective column to [0, 1].

        Parameters
        ----------
        objectives : np.ndarray, shape (N, K)
            Raw objective scores (lower is better).
        eps : float
            Small value to avoid division by zero.

        Returns
        -------
        np.ndarray
            Normalized objectives in [0, 1].
        """
        normed = np.zeros_like(objectives)
        for j in range(objectives.shape[1]):
            col = objectives[:, j]
            cmin, cmax = col.min(), col.max()
            span = cmax - cmin
            if span < eps:
                normed[:, j] = 0.0
            else:
                normed[:, j] = (col - cmin) / span
        return normed

    #@staticmethod
    def _penalty( self, counts: np.ndarray ) -> np.ndarray:
        """
        Returns for each index i a penalty p_i ∈ [0,1], where
          p_i = 0 → no change,
          p_i = 1 → zero probability.
        """
        # your existing “steepness” shape
        raw = (np.tanh(self.steepness * (0.5 - counts/self.max_count)) + 1.0)  / (np.tanh(self.steepness * 0.5) + 1.0)  
        # raw ∈ (–1, +1); map it so that:
        #   raw = +1 → p = 0
        #   raw = –1 → p = 1
        p = (1.0 - raw) / 1.0
        # ensure strict bounds
        return np.clip(p, 0.0, 1.0)

    # ==========================================================================
    #                               API
    # ==========================================================================
    def select(
        self,
        objectives: np.ndarray,
        features: np.ndarray,
        size: Optional[int] = None,
    ) -> np.ndarray:
        r"""
        Stochastically select a Pareto‐aware subset of candidates.

        This method implements a two‐temperature probabilistic Pareto sampler with
        optional diversity repulsion and repetition penalization.  The selection
        probability is computed in three stages:

        1. **Objective fusion**  
           Given raw objectives \\(f_{ik}\\) for candidates \\(i=1,\dots,N\\), \\(k=1,\dots,K\\):
           a. **Shift** to non‐negative:  
              .. math::
                 f'_{ik} = f_{ik} \;-\; \min_{i}(f_{ik}),
                 \quad f'_{ik}\ge0.
           b. **Optional normalization** (zero‐mean, unit‐variance per objective):  
              .. math::
                 \tilde f_{ik} = \frac{f'_{ik} - \mu_k}{\sigma_k}.
           c. **Boltzmann fusion** at objective‐temperature \\(T_{\rm obj}\\):  
              .. math::
                 F_i = -T_{\rm obj}\,\ln\!\Bigl(\sum_{k=1}^K w_k \,\exp\bigl(\,-\,\tfrac{f'_{ik}}{T_{\rm obj}}\bigr)\Bigr),
              where \\(w_k\\) are objective weights (\\(\sum_k w_k=1\\)).

        2. **Cost assembly**  
           Starting from fused scores \\(F_i\\), add:
           - **Diversity repulsion** (if \\(\lambda>0\\)):  
             .. math::
               R_i = \mathrm{repulsion\_score}\bigl(\mathbf{x}_i,\,X_{\rm sel}\bigr),
               \quad
               C_i = F_i \;-\;\lambda\,R_i,
           - **Repetition penalty** (if enabled, with per‐candidate count \\(c_i\\)):  
             in log‐space by adding  
             .. math::
               \Delta \ell_i = \ln(1 - p(c_i)),
             so that final sampling logit is  
             \\(\ell_i = -C_i/T_{\rm samp} + \Delta \ell_i.\\)

        3. **Sampling**  
           Draw without replacement via the Gumbel–Max trick at sampling temperature
           \\(T_{\rm samp}\\):  
           .. math::
             g_i \sim \mathrm{Gumbel}(0,1),\quad
             \hat \ell_i = \frac{-C_i}{T_{\rm samp}} + g_i + \ln(1-p(c_i)),
             \quad
             \text{select }i^* = \arg\max_i \hat \ell_i.
           Repeat until `size` distinct indices are chosen, updating repetition counts
           and repulsion set after each pick. Finally, apply a “cooling” step:
           .. math::
             c_i \leftarrow \max\{c_i - \gamma,\,0\}.

        :param objectives:
            Array of shape \\((N,K)\\) with raw objective values (minimization).
        :type objectives: numpy.ndarray
        :param features:
            Array of shape \\((N,D)\\) with feature vectors used for diversity repulsion.
        :type features: numpy.ndarray
        :param size:
            Number of distinct candidates to select; defaults to `self.size`.
        :type size: int, optional
        :returns:
            Array of length `size` containing the selected candidate indices.
        :rtype: numpy.ndarray

        :raises ValueError:
            If inputs are not 2-D, shapes mismatch, `size` not in \\([1,N]\\), or contain non-finite values.
        """

        # ---------- Input validation ----------
        # Ensure float64 precision
        # Ensure correct dtype and shapes
        objectives = np.asarray(objectives, dtype=np.float64)
        features   = np.asarray(features,   dtype=np.float64)

        # Sanity checks
        size = int(size or self.size)
        self._sanity_check(objectives, features, size)
        N, K = objectives.shape
        if not (1 <= size <= N):
            raise ValueError("size must be between 1 and N")

        # ===================================================================
        #                         Mode: NSGA‑III
        # ===================================================================
        # ===== NSGA-III selection: non-dominated sort + reference-point niching =====
        if self.selection_method == 'nsga3':
            fronts = self._non_dominated_sort(objectives)
            selected: list[int] = []
            # fill entire fronts until last
            for front in fronts:
                if len(selected) + len(front) <= size:
                    selected.extend(front)
                    continue
                # need to fill remaining via niching
                rem = size - len(selected)
                ref_dirs = self._generate_reference_dirs(K, self.divisions)
                niche_sel = self._reference_point_niching(objectives, front, ref_dirs, rem)
                selected.extend(niche_sel)
                break

            return np.asarray(selected, dtype=int)

        # ===================================================================
        #                         Mode: Non‑dominated sort only
        # ===================================================================
        # ===== Simple non-dominated sort =====
        if self.selection_method == 'nondominated_sorted':
            fronts = self._non_dominated_sort(objectives)
            selected: list[int] = []
            for front in fronts:
                for idx in front:
                    if len(selected) < size:
                        selected.append(idx)
                    else:
                        break
                if len(selected) >= size:
                    break

            return np.asarray(selected, dtype=int)

        # ---------- ---------- Pre‑compute common terms ---------- ----------
        # Otherwise: stochastic two-temperature Pareto sampler
        # ===== original code continues =====
        # 2) Prepare weights
        # weights
        w = np.ones(K, dtype=np.float64) / K if self.weights is None else np.asarray(self.weights, dtype=np.float64)
        if w.size != K:
            raise ValueError("weights length mismatch")
        w /= w.sum()
        log_w = np.log(w)

        # 3) Zero‐baseline and optional normalization
        # Shift to zero baseline and optionally normalize
        f_min = objectives.min(axis=0)
        f_adj = objectives - f_min
        # optional normalization
        if self.normalize_objectives:
            f_adj = self._normalize_objectives(f_adj)

        # 4) Initialize or pad counts
        if isinstance(self.counts, np.ndarray):
            self.counts = np.pad(self.counts, (0, max(0, N - self.counts.size)), mode='constant')
        else:
            self.counts = np.zeros(N, dtype=np.float32)
        self.counts[self.counts<0] = 0

        sel_idx: list[int] = []
        sel_feat = np.empty((0, features.shape[1]))

        # ===================================================================
        #                         Mode: *Roulette‑wheel*
        # ===================================================================
        if self.selection_method == 'roulette':

            for _ in range(size):
                cost = np.sum(f_adj, axis=1)
                # Diversity repulsion term
                if self.repulsion_weight > 0 and sel_feat.size:
                    cost += self.repulsion_weight * _repulsion_score(
                        features, sel_feat, self.metric, self.repulsion_mode)

                # Convert to fitness (higher‑is‑better)
                
                fitness = -cost
                if fitness.ndim > 1:  # Safety: ensure 1‑D for broadcasting
                    fitness = fitness.ravel()

                # Repetition penalty (multiplicative on fitness)
                if self.repetition_penalty:
                    penalty_mask = 1.0 - self._penalty(self.counts)
                    fitness *= penalty_mask

                # Zero out already picked indices
                if sel_idx:
                    fitness[sel_idx] = 0.0

                probs = self._probs_sanity_check(fitness)

                idx = int(self._rng.choice(N, p=probs))
                sel_idx.append(idx)
                self.counts[idx] += 1
                if self.repulsion_weight > 0:
                    sel_feat = np.vstack((sel_feat, features[idx]))

            # Cooling
            self.counts[self.counts > self.cooling_rate] -= self.cooling_rate
            return np.asarray(sel_idx, dtype=int)

        # ===================================================================
        #                         Mode: *stochastic* / *boltzmann selection*
        # ===================================================================
        for _ in range(size):
            # 1) objective fusion
            T_obj = self.objective_temperature + _EPS
            '''
            # will underflow (every entry in exps becomes zero) so that all fused‐objective 
            # scores collapse to essentially the same constant. Once your costs are all identical, 
            # sampling (even with a “softmax‐style” np.exp(logits - logits.max())) will be 
            # effectively uniform––hence the completely random picks you observe.
            exps = np.exp(-f_adj / T_obj)  [! Direct]
            Z = exps.dot(w)  [! Direct]
            F = -T_obj * np.log(Z + _EPS) [! Direct]
            cost = F.copy() [! Direct]
            '''
            # 5) Objective fusion via stable log-sum-exp
            log_w = np.log(w)
            F = -T_obj * logsumexp((-f_adj / T_obj) + log_w[None, :], axis=1)
            cost = F.copy()

            # 6) Diversity repulsion
            if self.repulsion_weight > 0 and sel_feat.size:
                rep = _repulsion_score(features, sel_feat, self.metric, self.repulsion_mode)
                cost += self.repulsion_weight * rep

            # 7) Build sampling logits
            T_s = self.sampling_temperature + _EPS
            logits = -cost / T_s
            #probs = np.exp(logits - logits.max()) [! Direct]

            # 8) Repetition penalty in log‐space
            if self.repetition_penalty:
                p = self._penalty(self.counts)            # shape (N,)
                '''
                Why this works
                Exact zeroing: whenever your penalty function returns 1.0, log1p(-1.0) is -inf. 
                An -inf logit will always lose in the Gumbel–Max arg-max, so that candidate’s 
                probability is exactly zero.
                Smooth down-weighting: for in-between values 0<p<1, you’re effectively multiplying 
                the unnormalized weight by (1−p), which reduces but does not entirely kill off that item.
                No buried epsilon: by not adding + _EPS inside the log, you allow true log(0)-> -inf
                '''
                penalty_logit = np.log1p(-p)
                logits += penalty_logit
                #logits += np.log(1.0 - p )

            #probs = self._probs_sanity_check(probs)

            # 9) Sample via Gumbel–Max
            # Draw one index via Gumbel–Max
            # Gumbel(0,1) samples = -log(-log(U))
            #idx = self._rng.choice(N, p=probs)  [! Direct]
            u = self._rng.random(size=N)
            gumbels = -np.log(-np.log(u + _EPS) + _EPS)
            idx = int(np.argmax(logits + gumbels))

            # 10) Without replacement
            while idx in sel_idx:
                #probs[idx] = 0.0  [! Direct]
                #probs = self._probs_sanity_check(probs) [! Direct]
                #idx = self._rng.choice(N, p=probs) [! Direct]
                logits[idx] = -np.inf
                u = self._rng.random(size=N)
                gumbels = -np.log(-np.log(u + _EPS) + _EPS)
                idx = int(np.argmax(logits + gumbels))

            # 11) Record selection
            sel_idx.append(idx)
            self.counts[idx] += 1
            if self.repulsion_weight > 0:
                sel_feat = np.vstack((sel_feat, features[idx]))

        # 12) Cooling step
        self.counts[self.counts>self.cooling_rate] -= self.cooling_rate

        return np.asarray(sel_idx, dtype=int)

    # ----------------------------------------------------------------------
    #                            Sanity checks
    # ----------------------------------------------------------------------
    def _sanity_check(
        self,
        obj: np.ndarray,
        feat: np.ndarray,
        size: int,
    ) -> None:
        if obj.ndim != 2 or feat.ndim != 2:
            raise ValueError("`objectives` and `features` must be 2-D arrays")
        if obj.shape[0] != feat.shape[0]:
            raise ValueError("Number of rows in objectives and features must match")
        if not np.isfinite(obj).all() or not np.isfinite(feat).all():
            raise ValueError("Inputs contain NaN or infinite values")
        if not (1 <= size <= obj.shape[0]):
            raise ValueError("`size` must be between 1 and N")

    @staticmethod
    def _probs_sanity_check(probs: np.ndarray) -> np.ndarray:
        """Force a 1‑D probability vector into a valid simplex.

        * Replace NaNs with 0
        * Clamp negatives to 0 (can arise from round‑off in fitness)
        * If the vector is all‑zeros, revert to a uniform distribution
        * Finally, normalise so that `probs.sum() == 1`
        """
        probs = np.nan_to_num(probs, nan=0.0, copy=False)
        probs[probs < 0.0] = 0.0
        total = probs.sum()
        if np.isclose(total, 0.0):
            probs.fill(1.0 / probs.size)
        else:
            probs /= total
        return probs

    # ----------------------------------------------------------------------
    #                        Non‑dominated sorting helpers
    # ----------------------------------------------------------------------
    def _non_dominated_sort(self, objectives: np.ndarray) -> list[list[int]]:
        """
        Perform non-dominated sorting on a set of objective vectors.

        This method assigns each candidate a Pareto-front rank by iteratively
        identifying non-dominated points and peeling them off.

        :param objectives: Array of shape (N, K) containing objective values for N candidates.
                           Lower values are considered better.
        :type objectives: numpy.ndarray
        :returns: A list of Pareto fronts; each front is a list of candidate indices.
                  Front 0 contains non-dominated points (rank 1), front 1 contains points
                  dominated only by those in front 0, etc.
        :rtype: List[List[int]]
        """
        N, K = objectives.shape
        domination_counts = np.zeros(N, dtype=int)
        dominated_sets = [set() for _ in range(N)]
        fronts: list[list[int]] = []

        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                if np.all(objectives[i] <= objectives[j]) and np.any(objectives[i] < objectives[j]):
                    dominated_sets[i].add(j)
                elif np.all(objectives[j] <= objectives[i]) and np.any(objectives[j] < objectives[i]):
                    domination_counts[i] += 1

        current_front = [i for i in range(N) if domination_counts[i] == 0]
        while current_front:
            fronts.append(current_front)
            next_front: list[int] = []
            for p in current_front:
                for q in dominated_sets[p]:
                    domination_counts[q] -= 1
                    if domination_counts[q] == 0:
                        next_front.append(q)
            current_front = next_front

        return fronts

    # ----------------------------------------------------------------------
    #                          NSGA‑III helpers
    # ----------------------------------------------------------------------
    def _generate_reference_dirs(self, M: int, H: int) -> np.ndarray:
        """
        Generate reference directions on the M-objective simplex using the Das–Dennis method.

        :param M: Number of objectives (dimensionality of the simplex).
        :type M: int
        :param H: Number of divisions along each axis for constructing the reference grid.
                  Total reference directions = comb(H + M - 1, M - 1).
        :type H: int
        :returns: Array of shape (num_dirs, M) with each row a reference direction vector.
        :rtype: numpy.ndarray
        """
        def gen(curr: list[int], left: int, dims: int):
            if dims == 1:
                yield curr + [left]
            else:
                for k in range(left + 1):
                    yield from gen(curr + [k], left - k, dims - 1)

        dirs = np.array(list(gen([], H, M)), dtype=float)
        dirs /= (H + _EPS)
        return dirs

    def _reference_point_niching(
        self,
        objectives: np.ndarray,
        front: list[int],
        ref_dirs: np.ndarray,
        rem: int
    ) -> list[int]:
        """
        Perform reference-point niching selection on a Pareto front.

        Each candidate in the given front is associated with the closest reference
        direction, and up to `rem` candidates are chosen to maximize diversity.

        :param objectives: Full objective matrix of shape (N, K) for normalization.
        :type objectives: numpy.ndarray
        :param front: List of indices belonging to the target Pareto front.
        :type front: List[int]
        :param ref_dirs: Array of reference directions of shape (num_dirs, K).
        :type ref_dirs: numpy.ndarray
        :param rem: Number of candidates to select from this front.
        :type rem: int
        :returns: List of selected candidate indices of length `rem`.
        :rtype: List[int]
        """
        # Normalize objectives to [0,1]
        f_min = objectives.min(axis=0)
        f_max = objectives.max(axis=0)
        f_norm = (objectives - f_min) / (f_max - f_min + _EPS)

        # Unit ref_dirs
        r_norm = ref_dirs / (np.linalg.norm(ref_dirs, axis=1, keepdims=True) + _EPS)

        # Compute perpendicular distances
        dists = np.full((len(front), len(r_norm)), np.inf)
        for i, idx in enumerate(front):
            for j, r in enumerate(r_norm):
                proj = np.dot(f_norm[idx], r) * r
                dists[i, j] = np.linalg.norm(f_norm[idx] - proj)

        # Associate each front member to nearest direction
        assoc = np.argmin(dists, axis=1)

        niche_count = np.zeros(len(r_norm), dtype=int)
        selected: list[int] = []
        candidates = list(range(len(front)))

        for _ in range(rem):
            # find directions with minimal niche count among candidates
            avail_dirs = set(assoc[c] for c in candidates)
            min_count = min(niche_count[list(avail_dirs)])
            best_dirs = [d for d in avail_dirs if niche_count[d] == min_count]
            # pick first best direction
            d_sel = best_dirs[0]
            # candidates in that niche
            niche_cands = [c for c in candidates if assoc[c] == d_sel]
            # choose the one with smallest distance
            c_star = min(niche_cands, key=lambda idx: dists[idx, d_sel])
            selected.append(front[c_star])
            niche_count[d_sel] += 1
            candidates.remove(c_star)

        return selected


    def plot_diagnostics(
        self,
        objectives: np.ndarray,
        features: np.ndarray,
        obj_temps: Sequence[float] = (0.0001, 0.001, 0.01, 0.1, 1),
        samp_temps: Sequence[float] = (0.0001, 0.001, 0.01, 0.1, 1),
    ) -> None:
        """
        Show diagnostics grid:
        Top row: varying objective temperatures.
        Bottom row: varying sampling temperatures.
        """
        import matplotlib.pyplot as plt
        # Prepare base kwargs for clone
        base_kwargs = dict(
            weights=self.weights,
            repulsion_weight=self.repulsion_weight,
            normalize_objectives=self.normalize_objectives,
            repetition_penalty=self.repetition_penalty,
            size=self.size,
            repulsion_mode=self.repulsion_mode,
            metric=self.metric,
            random_seed=self.random_seed,
            sampling_temperature=self.sampling_temperature,
        )
        fig, axes = plt.subplots(
            2,
            max(len(obj_temps), len(samp_temps)),
            figsize=(5 * max(len(obj_temps), len(samp_temps)), 8),
        )
        # Objective temp row
        for i, T in enumerate(obj_temps):
            sampler = ProbabilisticParetoSampler(
                **{**base_kwargs, 'sampling_temperature': T}
            )
            sampler.repulsion_weight = 0.0
            sampler.max_count = 10
            ax = axes[0, i]
            ax.scatter(objectives[:,0], objectives[:,1], alpha=0.6, s=2)

            for n in range(10):
                idx = sampler.select(objectives, features, size=40)
                ax.scatter(objectives[idx,0], objectives[idx,1], marker='x', s=30, label=f"T_obj={T}", alpha=0.1)

            ax.set_title(f"Objective Temp = {T}")
            #ax.legend()

        # Sampling temp row
        for i, T in enumerate(samp_temps):
            print(T)  
            sampler = ProbabilisticParetoSampler(
                **{**base_kwargs, 'objective_temperature': self.objective_temperature,
                   'sampling_temperature': T}
            )
            sampler.repulsion_weight = 0.0001
            idx = sampler.select(objectives, features, size=10)
            ax = axes[1, i]
            ax.scatter(features[:,0], features[:,1], alpha=0.3)
            ax.scatter(features[idx,0], features[idx,1], marker='x', s=100, label=f"T_samp={T}")
            ax.set_title(f"Sampling Temp = {T}")
            #ax.legend()
        fig.suptitle("Sampler Diagnostics", fontsize=16)
        plt.tight_layout()
        #plt.show()

# ----------------------------------------------------------------------
# Unit tests
# ----------------------------------------------------------------------
class _SamplerTest(unittest.TestCase):
    def setUp(self):

        def generate_pareto_front(    
            N: int,
            df1: float = 2.0,
            df2: Optional[float] = None
            ) -> tuple[np.ndarray, np.ndarray]:
            """
            Generate N synthetic points from Chi-squared distributions for objectives.
            """
            rng = np.random.default_rng()
            f1 = rng.chisquare(df1, size=N)
            df2 = df1 if df2 is None else df2
            f2 = rng.chisquare(df2, size=N)
            objectives = np.vstack((f1, f2)).T
            features = objectives.copy()
            return objectives, features

        self.N, self.K, self.D = 1000, 2, 5
        rng = np.random.default_rng(7)
        #self.obj = rng.normal(loc=-5.0, scale=2.0, size=(self.N, self.K))
        #self.feat = rng.normal(size=(self.N, self.K))
        self.obj, self.feat = generate_pareto_front(self.N)


        rng = np.random.default_rng(7)
        self.N, self.K = 1000, 2
        self.obj = rng.gamma(shape=2.0, scale=1.0, size=(self.N, self.K))
        self.feat = self.obj + rng.normal(scale=0.1, size=(self.N, self.K))


    def test_shape_and_uniqueness(self):
        sampler = ProbabilisticParetoSampler(size=10, random_seed=0)
        idx = sampler.select(self.obj, self.feat)
        self.assertEqual(idx.size, 10)
        self.assertEqual(len(np.unique(idx)), 10)

    def test_diagnostics_runs(self):
        sampler = ProbabilisticParetoSampler(size=5, random_seed=0)
        # Should produce plots without error
        sampler.plot_diagnostics(self.obj, self.feat)

    def test_objective_normalization(self):
        sampler = ProbabilisticParetoSampler(normalize_objectives=True, size=5, random_seed=3)
        idx = sampler.select(self.obj, self.feat)
        self.assertEqual(len(idx), 5)

    def test_sampling_temperature_smears_distribution(self):
        phys_T = 1.0
        low_ts = ProbabilisticParetoSampler(
            objective_temperature=phys_T,
            sampling_temperature=0.1,
            size=1,
            random_seed=1
        )
        high_ts = ProbabilisticParetoSampler(
            objective_temperature=phys_T,
            sampling_temperature=10.0,
            size=1,
            random_seed=1
        )
        f_min = self.obj.min(axis=0)
        f_adj = self.obj - f_min
        T_obj = phys_T + _EPS
        exps = np.exp(-f_adj / T_obj)
        Z = exps.dot(np.ones(self.K)/self.K)
        F = -T_obj * np.log(Z + _EPS)
        def p_dist(ts):
            logits = -F / (ts + _EPS)
            p = np.exp(logits - logits.max())
            return p / p.sum()
        p_low = p_dist(low_ts.sampling_temperature)
        p_high = p_dist(high_ts.sampling_temperature)
        self.assertGreater(p_low.max(), p_high.max())

    def test_repulsion_increases_diversity(self):
        no_rep = ProbabilisticParetoSampler(repulsion_weight=0.0, size=5, random_seed=2)
        rep = ProbabilisticParetoSampler(repulsion_weight=1.0, size=5, random_seed=2)
        idx_n = no_rep.select(self.obj, self.feat)
        idx_r = rep.select(self.obj, self.feat)
        d_n = pairwise_distances(self.feat[idx_n]).mean()
        d_r = pairwise_distances(self.feat[idx_r]).mean()
        self.assertGreaterEqual(d_r, d_n)

    def test_shape_and_uniqueness(self):
        sampler = ProbabilisticParetoSampler(size=10, random_seed=0)
        idx = sampler.select(self.obj, self.feat)
        self.assertEqual(idx.size, 10)
        self.assertEqual(len(np.unique(idx)), 10)

    def test_roulette_runs(self):
        sampler = ProbabilisticParetoSampler(size=15, selection_method='roulette', random_seed=1)
        idx = sampler.select(self.obj, self.feat)
        self.assertEqual(idx.size, 15)
        self.assertEqual(len(np.unique(idx)), 15)


if __name__ == "__main__":
    unittest.main()
