import numpy as np
from scipy.spatial.distance import jensenshannon
from typing import Dict, Any, Optional, List

class InformationEnsambleMetric:
    r"""
    Stateful calculator for generation‐to‐generation information gains in a GA population.

    Four information metrics are supported:

    1. **Entropy Gain**  
       Denote by  
       :math:`\mathbf{v}_{i}\in\mathbb{Z}_{\ge0}^d`  
       the count vector for feature cluster frequencies of individual :math:`i`.  Define
       .. math::
          p_k = \frac{1}{N}\sum_{i=1}^N \mathbf{1}\bigl(v_{i,k} > 0\bigr),
       and the Shannon entropy
       .. math::
          H = -\sum_{k=1}^d \bigl[p_k\log p_k + (1-p_k)\log(1-p_k)\bigr].
       The **entropy gain** at generation :math:`t` is  
       :math:`\Delta H = H^{(t)} - H^{(t-1)}`.

    2. **Jensen–Shannon Divergence Gain**  
       Let :math:`P_k^{(t-1)}` and :math:`P_k^{(t)}` be discrete distributions of counts
       in cluster :math:`k` at generations :math:`t-1` and :math:`t`.  The JS divergence
       is
       .. math::
          \mathrm{JS}(P,Q) = \tfrac12\,\mathrm{KL}\bigl(P\big\|M\bigr)
                             + \tfrac12\,\mathrm{KL}\bigl(Q\big\|M\bigr),
       where :math:`M = \tfrac12(P+Q)`.  We square the output of `scipy.jensenshannon`
       (base 2) and average over all :math:`d` clusters to obtain the **JS gain**.

    3. **Novelty Score (k‐NN Distance)**  
       For each current vector :math:`v_i^{(t)}` and the set of previous‐generation
       vectors :math:`\{v_j^{(t-1)}\}`, compute the average distance to its :math:`k` nearest
       neighbors in the previous generation:
       .. math::
          n_i = \frac{1}{k}\sum_{j\in\mathcal{N}_k(i)} \lVert v_i^{(t)} - v_j^{(t-1)}\rVert_p.
       The global **novelty** is the maximum :math:`\max_i n_i`.

    4. **Covariance‐Volume Gain**  
       Let :math:`\Sigma^{(t)} = \mathrm{Cov}(\{v_i^{(t)}\})` and stabilize with
       :math:`\Sigma_\epsilon = \Sigma + \epsilon I`.  The **covariance volume**
       is :math:`\log\det(\Sigma_\epsilon)`.  The gain is the difference between
       consecutive generations.

    The chosen metric (via the `metric` attribute) determines which of the above
    is computed and compared to thresholds for improvement.

    Attributes
    ----------
    novelty_k : int
        Number of neighbors for novelty score.
    entropy_thresh : float
        Minimum required entropy gain (nats) to count as improvement.
    js_thresh : float
        Minimum required JS‐divergence gain (bits) to count as improvement.
    cov_thresh : float
        Minimum required covariance‐volume gain (log‐det) to count as improvement.
    novelty_thresh : float or None
        Absolute threshold for novelty; if None, computed at the specified percentile.
    epsilon : float
        Small constant added to covariance diagonal for numerical stability.
    p_norm : float
        Minkowski‐norm order for novelty distance.
    auto_adjust : bool
        If True, adjust `novelty_thresh` automatically based on past percentiles.
    auto_percentile : float
        Percentile used for auto‐adjusting `novelty_thresh`.
    metric : str
        Which metric to compute by default: 'all', 'entropy', 'js', 'novelty', 'covariance'.

    Histories
    ---------
    prev_presence : np.ndarray
        Presence‐vector from the previous generation.
    prev_full_distributions : list of np.ndarray
        Full count distributions from the previous generation.
    prev_vectors : np.ndarray
        Feature‐count matrix from the previous generation.
    prev_cov_vol : float
        Covariance volume (log‐det) from the previous generation.
    novelty_history : list of float
        Max novelty per generation.
    novelty_thresh_history : list of float
        Threshold used per generation.
    novelty_scores_history : list of np.ndarray
        Raw novelty scores per generation.
    """
    def __init__(
        self,
        novelty_k: int = 5,
        entropy_thresh: float = 1e-3,
        js_thresh: float = 0.01,
        cov_thresh: float = 0.1,
        novelty_thresh: float = None,
        epsilon: float = 1e-8,
        p_norm: float = 2.0,
        auto_adjust: bool = True,
        auto_percentile: float = 15.0,
        metric : str = 'novelty',
    ):
        r"""
        Initialize information‐gain thresholds and internal state.

        Parameters
        ----------
        novelty_k : int
            Number of nearest neighbors for k‐NN novelty.
        entropy_thresh : float
            Entropy‐gain threshold in nats.
        js_thresh : float
            JS‐divergence threshold in bits.
        cov_thresh : float
            Covariance‐volume gain threshold (log‐det).
        novelty_thresh : float or None
            Absolute novelty threshold; if None, set via percentile.
        epsilon : float
            Regularization constant for covariance matrix.
        p_norm : float
            p‐norm order for novelty distance (Minkowski).
        auto_adjust : bool
            Automatically adjust `novelty_thresh` based on past history.
        auto_percentile : float
            Percentile (0–100) for auto‐adjusting novelty threshold.
        metric : {'all','entropy','js','novelty','covariance'}
            Default metric to compute in `compute`.
        """
        self.novelty_k = novelty_k
        self.entropy_thresh = entropy_thresh
        self.js_thresh = js_thresh
        self.cov_thresh = cov_thresh
        self.novelty_thresh = novelty_thresh
        self.epsilon = epsilon
        self.p_norm = p_norm
        self.auto_adjust = auto_adjust
        self.auto_percentile = auto_percentile
        self.metric = metric

        self.prev_presence = None
        self.prev_full_distributions = None
        self.prev_cov_vol = None
        self.prev_vectors = None
        self.dim = None
        # record history of max novelty scores for auto threshold
        self.novelty_history = []
        self.novelty_thresh_history = []
        self.novelty_scores_history = []

    def get_latest_novelty(self) -> float:
        """
        Retrieve the most recent novelty .

        Returns
        -------
        float
            The last value in novelty_history, or 0.0 if history is empty.
        """
        if not self.novelty_history:
            return 0.0
        return float(self.novelty_history[-1])

    def get_latest_novelty_thresh(self) -> float:
        """
        Retrieve the most recent novelty threshold.

        Returns
        -------
        float
            The last value in novelty_thresh_history, or 0.0 if history is empty.
        """
        if not self.novelty_thresh_history:
            return 0.0
        return float(self.novelty_thresh_history[-1])

    def get_latest_novelty_scores(self):
        """
        Retrieve the most recent novelty scores.

        Returns
        -------
        numpy.ndarray or float
            The last entry in novelty_scores_history, or 0.0 if history is empty.
        """
        if not self.novelty_scores_history:
            return 0.0
        return self.novelty_scores_history[-1]

    def sanity_check(self, vectors):
        r"""
        Validate input matrix shape and nonnegativity.

        Ensures `vectors` is a 2D array of non‐negative integers
        with consistent column dimension across calls, and
        at least `novelty_k` rows for novelty computation.

        Parameters
        ----------
        vectors : array‐like
            Population count matrix of shape :math:`(N, d)`.

        Returns
        -------
        arr : np.ndarray, shape (N, d)
            Validated integer array.

        Raises
        ------
        ValueError
            If `vectors` is not 2D, contains negatives, has inconsistent
            width, or has fewer than `novelty_k` rows.
        """
        arr = np.asarray(vectors)

        if arr.ndim != 2:
            raise ValueError(f"Expected 2D array, got {arr.ndim}D")
        #if not np.issubdtype(arr.dtype, (np.integer, np.float64) ):
        #    raise ValueError("All vector entries must be integers or float.")
        if np.any(arr < 0):
            raise ValueError("Vector entries must be non-negative.")

        N, d = arr.shape
        if self.dim is None:
            self.dim = d
        elif d != self.dim:
            raise ValueError(f"Dimension mismatch: expected {self.dim}, got {d}.")
        if N < 1:
            raise ValueError("At least one individual is required.")
        if N < self.novelty_k:
            raise ValueError(f"At least {self.novelty_k} individuals are required for novelty score.")

        return arr.astype(int)

    def compute_entropy_gain(self, vectors) -> float:
        r"""
        Compute the Shannon‐entropy gain between successive generations.

        Let presence‐probabilities
        :math:`p_k = N^{-1}\sum_i \mathbf{1}(v_{i,k}>0)`.  Define
        .. math::
           H = -\sum_{k=1}^d \bigl[p_k\ln p_k + (1-p_k)\ln(1-p_k)\bigr].
        Returns :math:`\Delta H = H^{(t)} - H^{(t-1)}` (zero on first call).

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.

        Returns
        -------
        float
            Entropy gain in nats.
        """
        arr = vectors#  self.sanity_check(vectors)
        curr_p = np.mean(arr > 0, axis=0)
        def entropy(p):
            mask = (p > 0) & (p < 1)
            return -np.sum(p[mask] * np.log(p[mask]) + (1 - p[mask]) * np.log(1 - p[mask]))

        H_curr = entropy(curr_p)
        if self.prev_presence is None:
            self.prev_presence = curr_p
            return 0.0
        H_prev = entropy(self.prev_presence)
        gain = H_curr - H_prev
        self.prev_presence = curr_p
        return float(gain)

    def _compute_distributions(self, arr: np.ndarray) -> list:
        N, d = arr.shape
        dists = []
        for k in range(d):
            col = arr[:, k]
            max_c = int(col.max())
            counts = np.bincount(col, minlength=max_c + 1)
            dists.append(counts.astype(float) / N)
        return dists

    def compute_js_gain(self, vectors:np.ndarray) -> float:
        r"""
        Compute the average Jensen–Shannon divergence gain across features.

        For each column distribution :math:`P` (prev) and :math:`Q` (curr),
        JS‐divergence is squared (base 2).  The **JS gain** is the mean
        of these squared divergences:
        .. math::
           \mathrm{gain} = \frac1d \sum_{k=1}^d \mathrm{JS}(P_k,Q_k)^2.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.

        Returns
        -------
        float
            Mean squared JS‐divergence.
        """
        arr = self.sanity_check(vectors)
        curr_dists = self._compute_distributions(arr)
        if self.prev_full_distributions is None:
            self.prev_full_distributions = curr_dists
            return 0.0
        js_vals = []
        for P_prev, P_curr in zip(self.prev_full_distributions, curr_dists):
            L = max(len(P_prev), len(P_curr))
            Pp = np.pad(P_prev, (0, L - len(P_prev)), constant_values=0)
            Pc = np.pad(P_curr, (0, L - len(P_curr)), constant_values=0)
            js_vals.append(jensenshannon(Pp, Pc, base=2.0) ** 2)
        gain = float(np.mean(js_vals))
        self.prev_full_distributions = curr_dists
        return gain

    def compute_novelty_scores(self, vectors: np.ndarray) -> np.ndarray:
        r"""
        Compute k‐NN novelty scores relative to the previous generation.

        For each vector :math:`v_i`, compute
        .. math::
           n_i = \frac{1}{k}\sum_{j\in\mathcal{N}_k(i)} \lVert v_i - v_j\rVert_p,
        storing the raw :math:`n_i` and updating
        `novelty_history` with :math:`\max_i n_i`.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.

        Returns
        -------
        np.ndarray, shape (N,)
            Novelty scores per individual.
        """
        from scipy.spatial import distance

        arr = np.asarray(vectors)# self.sanity_check(vectors)
        N, d = arr.shape
        if self.prev_vectors is None:
            scores = np.zeros(N)
        else:
            D = distance.cdist(arr, self.prev_vectors, metric='minkowski', p=self.p_norm)
            k = min(self.novelty_k, self.prev_vectors.shape[0])
            nearest = np.partition(D, k, axis=1)[:, :k]
            scores = np.mean(nearest, axis=1)
        self.prev_vectors = arr
        max_score = float(np.max(scores))
        self.novelty_scores_history.append( scores )
        self.novelty_history.append(max_score)
        self.novelty_thresh_history.append( self.compute_novelty_thresh() )

        # default novelty_thresh
        #if self.novelty_thresh is None:
        #    C_max = max(int(arr.max()), 1)
        #    self.novelty_thresh = self.compute_novelty_thresh()
        return scores

    def compute_covariance_volume_gain(self, vectors:np.ndarray) -> float:
        r"""
        Compute the log‐determinant volume gain of the covariance.

        Let :math:`\Sigma = \mathrm{Cov}(v)` and
        :math:`\Sigma_\epsilon = \Sigma + \epsilon I`.  Then
        .. math::
           V = \log\det(\Sigma_\epsilon),\quad
           \Delta V = V^{(t)} - V^{(t-1)}.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.

        Returns
        -------
        float
            Covariance‐volume gain.
        """
        arr = self.sanity_check(vectors)
        cov = np.cov(arr, rowvar=False)
        d = cov.shape[0]
        cov_stable = cov + self.epsilon * np.eye(d)
        sign, logdet = np.linalg.slogdet(cov_stable)
        vol = float(logdet)
        if self.prev_cov_vol is None:
            self.prev_cov_vol = vol
            return 0.0
        gain = vol - self.prev_cov_vol
        self.prev_cov_vol = vol
        return gain

    def compute_all(self, vectors: np.ndarray) -> Dict[str, Any]:
        r"""
        Compute all four metrics and return them in a dictionary.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.

        Returns
        -------
        dict
            {
              'entropy_gain': float,
              'js_gain': float,
              'novelty_scores': np.ndarray,
              'covariance_volume_gain': float
            }
        """
        return {
            'entropy_gain': self.compute_entropy_gain(vectors),
            'js_gain': self.compute_js_gain(vectors),
            'novelty_scores': self.compute_novelty_scores(vectors),
            'covariance_volume_gain': self.compute_covariance_volume_gain(vectors)
        }

    def compute(self, vectors: np.ndarray, metric: Optional[str] = None):
        r"""
        Compute the selected metric or all metrics.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.
        metric : str, optional
            One of 'all','entropy','js','novelty','covariance'.  
            Defaults to the instance `metric` attribute.

        Returns
        -------
        float or np.ndarray or dict
            Single metric value or array, or dict if 'all'.

        Raises
        ------
        ValueError
            If `metric` is unrecognized.
        """
        metric = metric if metric is not None else self.metric
        m = metric.lower() 

        if m == 'all':
            return self.compute_all(vectors)
        elif m in ('entropy', 'entropy_gain'):
            return self.compute_entropy_gain(vectors)
        elif m in ('js', 'js_gain', 'jensen_shannon'):
            return self.compute_js_gain(vectors)
        elif m in ('novelty', 'novelty_scores'):
            return self.compute_novelty_scores(vectors)
        elif m in ('covariance', 'covariance_volume', 'covariance_volume_gain'):
            return self.compute_covariance_volume_gain(vectors)
        else:
            raise ValueError(
                f"Unknown metric '{metric}'. Valid options are 'all', 'entropy', 'js', 'novelty', 'covariance'."
            )

    def compute_novelty_thresh(self, ) -> float:
        r"""
        Compute the novelty threshold as the :math:`p`th percentile of past maxima.

        .. math::
           \tau_{\mathrm{novel}} = \mathrm{percentile}\bigl(\{\max_i n_i^{(s)}\}_{s<t},\,p\bigr).

        Returns
        -------
        float
            Auto‐adjusted novelty threshold.
        """
        return float(np.percentile(self.novelty_history, self.auto_percentile))

    def has_improved(self, vectors: np.ndarray, metric: Optional[str] = None) -> bool:
        r"""
        Determine if the chosen metric has improved beyond its threshold.

        For `metric='all'`, all four gains must exceed their respective thresholds.
        For a single metric, return whether
        .. math::
           \Delta m \;\ge\; \mathrm{threshold}_m.

        Parameters
        ----------
        vectors : array‐like
            Current generation count matrix.
        metric : str, optional
            Which metric to check (see `compute`).

        Returns
        -------
        bool
            True if improvement criterion is met.
        """
        metric = metric if metric is not None else self.metric
        m = metric.lower() 

        if m == 'all':
            res = self.compute_all(vectors)

            if res['entropy_gain'] <= self.entropy_thresh:
                return False
            if res['js_gain'] <= self.js_thresh:
                return False
            if res['covariance_volume_gain'] <= self.cov_thresh:
                return False
            if np.max(res['novelty_scores']) <= self.novelty_thresh:
                return False
            return True

        elif m in ('entropy', 'entropy_gain'):
            return self.compute_entropy_gain(vectors) <= self.entropy_thresh

        elif m in ('js', 'js_gain', 'jensen_shannon'):
            return self.compute_js_gain(vectors) <= self.js_thresh
        elif m in ('novelty', 'novelty_scores'):
            self.compute_novelty_scores(vectors=vectors)
            return len(self.novelty_history) < 2 or self.novelty_history[-1] <= self.novelty_history[-2]
        elif m in ('covariance', 'covariance_volume', 'covariance_volume_gain'):
            return self.compute_covariance_volume_gain(vectors) <= self.cov_thresh
        else:
            raise ValueError(
                f"Unknown metric '{metric}'. Valid options are 'all', 'entropy', 'js', 'novelty', 'covariance'."
            )

        return True

    def plot_metrics(self, 
                     history: List[Dict[str, Any]],
                     sizes: Optional[List[int]] = None,
                     raw_history: Optional[List[np.ndarray]] = None):
        r"""
        Plot time‐series of all metrics and, if available, data histograms.

        - Entropy gain vs. generation.  
        - JS gain vs. generation.  
        - Covariance‐volume gain vs. generation.  
        - Max novelty vs. generation (with threshold line).  
        - (Optional) Histograms of raw feature‐counts for the final generation.
        - (Optional, if d=2) Scatter plot of the two variables.

        Parameters
        ----------
        history : list of dict
            Metric dicts as returned by `compute_all` for each generation.
        sizes : list of int, optional
            Population sizes per generation (x‐axis).
        raw_history : list of np.ndarray, optional
            Raw count matrices per generation; last entry used for histograms.

        Returns
        -------
        matplotlib.figure.Figure
            Figure containing the assembled subplots.
        """
        import matplotlib.pyplot as plt
        # ensure novelty_thresh is set before plotting
        has_data = raw_history is not None
        last = raw_history[-1] if has_data else np.array([])

        entropy = [h['entropy_gain'] for h in history]
        js_gain = [h['js_gain'] for h in history]
        cov_vol = [h['covariance_volume_gain'] for h in history]
        novelty_max = [np.max(h['novelty_scores']) for h in history]
        xs = list(sizes) if sizes is not None else list(range(1, len(history)+1))

        # layout
        d = last.shape[1] if has_data else 0
        rows = 2 + int(has_data) + int(has_data and d==2)
        fig, axes = plt.subplots(rows, 2 if rows>1 else 1, figsize=(10, 4*rows))
        axes = np.array(axes).flatten()

        # plot metrics
        axes[0].plot(xs, entropy)
        axes[0].axhline(self.entropy_thresh, color='red', linestyle='--')
        axes[0].set_title('Entropy Gain')

        axes[1].plot(xs, js_gain)
        axes[1].axhline(self.js_thresh, color='red', linestyle='--')
        axes[1].set_title('JS Gain')

        axes[2].plot(xs, cov_vol)
        axes[2].axhline(self.cov_thresh, color='red', linestyle='--')
        axes[2].set_title('Cov Volume Gain')

        axes[3].plot(xs, novelty_max)
        axes[3].plot(xs, self.novelty_thresh_history, color='r', linestyle='--')
        axes[3].set_title('Novelty Max')

        idx = 4
        if has_data:
            for k in range(d):
                axes[idx].hist(last[:, k], bins=range(int(last[:, k].max())+2))
                axes[idx].set_title(f'Var{k} Hist')
                idx += 1
            if d == 2:
                axes[idx].scatter(last[:, 0], last[:, 1])
                axes[idx].set_title('Var0 vs Var1')

        # remove extra axes
        total = 4 + (d if has_data else 0) + (1 if has_data and d==2 else 0)
        for ax in axes[total:]:
            fig.delaxes(ax)

        fig.tight_layout()
        plt.show()
        return fig

# ---------------------- UNIT TESTS ----------------------
import unittest

class TestInformationEnsambleMetric(unittest.TestCase):
    def setUp(self):
        self.calc = InformationEnsambleMetric(novelty_k=2, )

    def test_sanity_check(self):
        with self.assertRaises(ValueError):
            self.calc.sanity_check([1, 2, 3])
        with self.assertRaises(ValueError):
            self.calc.sanity_check(np.array([[1.0]]))
        with self.assertRaises(ValueError):
            self.calc.sanity_check(np.array([[-1, 0], [1, 0]]))
        # fewer individuals than novelty_k
        with self.assertRaises(ValueError):
            InformationEnsambleMetric(novelty_k=5).sanity_check(np.zeros((3,3), int))

    def test_metrics_initial_and_subsequent(self):
        # create simple constant-population datasets
        base = np.ones((5, 3), int)
        hist = []
        hist.append(self.calc.compute_all(base))
        hist.append(self.calc.compute_all(base * 2))
        # metrics dict structure
        for h in hist:
            self.assertIn('entropy_gain', h)
            self.assertIn('js_gain', h)
            self.assertIn('novelty_scores', h)
            self.assertIn('covariance_volume_gain', h)
        # entropy gain should be zero then zero
        self.assertEqual(hist[0]['entropy_gain'], 0.0)
        self.assertEqual(hist[1]['entropy_gain'], 0.0)

    def test_synthetic_datasets_increasing_size(self):
        # generate datasets of increasing size
        sizes = [5, 10, 20, 40, 80]
        history = []
        for n in sizes:
            data = np.random.randint(0, 4, size=(n, 3))
            history.append(self.calc.compute_all(data))
        # verify history length and metric shapes
        self.assertEqual(len(history), len(sizes))
        for h in history:
            self.assertIsInstance(h['entropy_gain'], float)
            self.assertIsInstance(h['js_gain'], float)
            self.assertIsInstance(h['covariance_volume_gain'], float)
            self.assertEqual(h['novelty_scores'].shape[0], sizes[history.index(h)])

    def test_synthetic_datasets_cumulative(self):
        sizes = [5, 10, 20, 40]
        history = []
        raw_history = []
        current_data = np.random.randint(0, 4, size=(sizes[0], 3))
        raw_history.append(current_data.copy())
        history.append(self.calc.compute_all(current_data))
        for prev_size, new_size in zip(sizes, sizes[1:]):
            add_n = new_size - prev_size
            new_samples = np.random.randint(0, 4, size=(add_n, 3))
            current_data = np.vstack([current_data, new_samples])
            raw_history.append(current_data.copy())
            history.append(self.calc.compute_all(current_data))
        self.assertEqual(len(history), len(sizes))
        for idx, h in enumerate(history):
            self.assertEqual(h['novelty_scores'].shape[0], sizes[idx])
            self.assertIsInstance(h['entropy_gain'], float)
            self.assertIsInstance(h['js_gain'], float)
            self.assertIsInstance(h['covariance_volume_gain'], float)

    def test_plot_metrics_runs(self):
        sizes = np.arange(10, 1000, 10)
        history = []
        raw_history = []
        current_data = np.random.randint(0, 40, size=(sizes[0], 3))
        raw_history.append(current_data.copy())
        history.append(self.calc.compute_all(current_data))
        for prev_size, new_size in zip(sizes, sizes[1:]):
            add_n = new_size - prev_size
            new_samples = np.random.randint(0, 40, size=(add_n, 3))
            current_data = np.vstack([current_data, new_samples])
            raw_history.append(current_data.copy())
            history.append(self.calc.compute_all(current_data))
        self.assertEqual(len(history), len(sizes))
        for idx, h in enumerate(history):
            self.assertEqual(h['novelty_scores'].shape[0], sizes[idx])
            self.assertIsInstance(h['entropy_gain'], float)
            self.assertIsInstance(h['js_gain'], float)
            self.assertIsInstance(h['covariance_volume_gain'], float)

    def test_plot_metrics_runs(self):
        sizes = np.arange(20, 3000, 50)
        history = []
        raw_history = []
        current_data = np.random.randint(0, 40, size=(sizes[0], 2))
        raw_history.append(current_data.copy())
        history.append(self.calc.compute_all(current_data))
        for i, (prev_size, new_size) in enumerate(zip(sizes, sizes[1:])):
            add_n = new_size - prev_size
            if i < 30:
                new_samples = np.random.randint(0, 400, size=(add_n, 2))
            elif i < 60:
                new_samples = np.random.randint(400, 800, size=(add_n, 2))
            else:
                new_samples = np.random.randint(700, 850, size=(add_n, 2))

            current_data = np.vstack([current_data, new_samples])
            raw_history.append(current_data.copy())
            history.append(self.calc.compute_all(current_data))

        fig = self.calc.plot_metrics(history, sizes, raw_history=raw_history)
        self.assertTrue(hasattr(fig, 'axes'))

if __name__ == '__main__':
    unittest.main()