import numpy as np
import time
from ..core.interfaces import IConvergence

class Convergence(IConvergence):
    r"""
    A convergence monitor for generational optimization that tracks both objective-value improvements
    and, optionally, information-driven novelty.

    Convergence criterion
    ---------------------
    Let :math:`M` be the ``stall_threshold``. For each generation :math:`t`, define

    .. math::
       I_{\mathrm{obj}}(t) =
         \begin{cases}
           1, & \text{if any new objective value } o_t(i)
                 \text{ strictly improves the previously recorded best for feature } f_i, \\
           0, & \text{otherwise.}
         \end{cases}

    If :paramref:`information_driven` is ``True``, define similarly

    .. math::
       I_{\mathrm{info}}(t) =
         \begin{cases}
           1, & \text{if information novelty has improved at generation } t, \\
           0, & \text{otherwise.}
         \end{cases}

    Convergence is declared when (for ``convergence_type=='and'``)

    .. math::
       \underbrace{\sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{obj}}(k)\bigr)}_{\ge M}
       \;\wedge\;
       \underbrace{\sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{info}}(k)\bigr)}_{\ge M}

    or (for ``convergence_type=='or'``) when either of the above sums alone satisfies

    .. math::
       \sum_{k=t-M+1}^t \bigl(1 - I_{\mathrm{obj or info}}(k)\bigr) \;\ge\; M.

    Parameters
    ----------
    logger : logging.Logger or None
        Optional logger for informational messages.
    detailed_record : bool
        If True, stores the full per-generation history of objective vectors.
    stall_threshold : int
        Number of consecutive generations without improvement before declaring convergence.
    information_driven : bool
        If True, uses a parallel stall counter for information-driven novelty.

    Attributes
    ----------
    _objectives_for_features_history : dict[tuple, dict]
        Maps each feature-tuple to a dict containing:
        - ``"best_objective"`` (np.ndarray): the best objective seen so far.
        - ``"history"`` (dict[int, list[np.ndarray]]): per-generation records if ``detailed_record``.
    _no_improvement_count_objectives : int
        Number of consecutive generations with no objective improvement.
    _no_improvement_count_information : int
        Number of consecutive generations with no information improvement.
    _convergence_type : str
        Logical operator for combining criteria; either ``'and'`` or ``'or'``.
    """
    def __init__(self, 
        logger=None, 
        objective_threshold: float = 1e-4,
        feature_threshold: float = 1e-4,
        detailed_record : bool = False, 
        stall_threshold : int = 5, 
        information_driven : bool = True,
        convergence_type: str = 'and',
        ):
        """
        Initializes the ConvergenceChecker with optional logging and a flag to maintain detailed records.

        Parameters
        ----------
        logger : logging.Logger, optional
            A logger instance to record events.
        detailed_record : bool, optional
            If True, a detailed history of objective values is stored.
        """
        self.logger = logger
        self.detailed_record = detailed_record
        self._objectives_for_features_history = {}
        self._no_improvement_count_objectives = 0
        self._no_improvement_count_information = 0
        self._no_improvement_count = 0

        self._stall_threshold = stall_threshold
        self._information_driven = information_driven
        self._convergence_type = 'and'

        self._objective_threshold = objective_threshold
        self._feature_threshold = feature_threshold

        self._converge = False

    def _record_objective_for_feature(self, feature_key, generation, current_obj):
        """
        Update the per‐feature best‐objective record and optionally the full history.

        This routine ensures that for each feature combination:
        \[
          b_{t}(f) = \min\bigl(b_{t-1}(f), \, o_t(f)\bigr)
        \]
        and if `detailed_record` is enabled,
        appends \(o_t(f)\) into the history at index `generation`.

        :param feature_key: Immutable tuple representing the feature vector \(f\).
        :type feature_key: tuple
        :param generation: Current generation index \(t\).
        :type generation: int
        :param current_obj: Objective vector \(o_t(f)\) for the structure.
        :type current_obj: np.ndarray
        :returns: None
        """
        if feature_key not in self._objectives_for_features_history:
            self._objectives_for_features_history[feature_key] = {
                "best_objective": current_obj.copy(),
            }
        record = self._objectives_for_features_history[feature_key]
        if self.detailed_record:
            if 'history' not in record:
                record['history'] = {}
            if generation not in record['history']:
                record['history'][generation] = []
            record['history'][generation].append(current_obj)
        prev_best = record["best_objective"]
        if np.any(current_obj < prev_best):
            record["best_objective"] = np.minimum(prev_best, current_obj)

    def check(self, generation, objectives, features):
        r"""information_novelty_has_improved
        """
        # Ensure objectives and features are at least 1D arrays
        objectives_arr = np.atleast_1d(objectives)
        features_arr = np.atleast_1d(features)

        n_structures = objectives_arr.shape[0]

        # Reshape arrays if necessary
        if objectives_arr.ndim == 1:
            objectives_arr = objectives_arr.reshape(-1, 1)
        if features_arr.ndim == 1:
            features_arr = features_arr.reshape(-1, 1)

        improvement_found = False

        for i in range(n_structures):
            feature_key = tuple(features_arr[i, :])
            current_obj = objectives_arr[i, :]
            if feature_key in self._objectives_for_features_history:
                prev_best = self._objectives_for_features_history[feature_key]["best_objective"]
                if np.any(current_obj < prev_best - self._objective_threshold):
                    improvement_found = True
            else:
                improvement_found = True
            self._record_objective_for_feature(feature_key, generation, current_obj)

        # Update objective stall count
        self._no_improvement_count_objectives = (
            0 if improvement_found 
            else self._no_improvement_count_objectives + 1
        )
        self._no_improvement_count_objectives = min( self._no_improvement_count_objectives, self._stall_threshold )

        # If using information-driven convergence, update info stall count
        if self._information_driven:
            self._no_improvement_count_information = (
                0 if not information_novelty_has_improved
                else self._no_improvement_count_information + 1
            )
            self._no_improvement_count_information = min( self._no_improvement_count_information, self._stall_threshold )

        # Determine convergence
        conv_type = self._convergence_type.lower()
        if self._information_driven:
            # Pair counts for [objectives, information]
            counts = (
                self._no_improvement_count_objectives,
                self._no_improvement_count_information
            )
            # Map 'and' → all, 'or' → any; default to any if unrecognized
            op = {'and': all, 'or': any}.get(conv_type, any)
            converge = op(count >= self._stall_threshold for count in counts)
        else:
            converge = self._no_improvement_count_objectives >= self._stall_threshold
            counts = self._no_improvement_count_objectives
        
        self._converge = converge
        self._no_improvement_count = np.min( counts ) 
        self._improvement_found = improvement_found

        return {
            'converge': converge,
            'improvement_found': improvement_found,
            'stall_count_objetive': self._no_improvement_count_objectives,
            'stall_count_information': self._no_improvement_count_information,
        }

    def get_stagnation(self, ):
        """
        """
        return self._no_improvement_count


    def improvement_found(self, ):
        """
        """
        return self._improvement_found


    def is_converge(self, ):
        """
        """
        return self._converge
