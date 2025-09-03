import time
import numpy as np

from ..core.interfaces import (
    IEvaluator,
    IPopulation,
)

class Evaluator(IEvaluator):
    """
    """

    def __init__(self, 
        features_funcs:list = None, 
        objectives_funcs:list = None, 

        debug = False):
        """
        """

        self.features_funcs = features_funcs
        self.objectives_funcs = objectives_funcs
        self.debug = debug

    def evaluate_features_objectives(self, individuals:object):
        """
        Evaluates features and objectives for a list of structures.

        Parameters
        ----------
        structures : list
            List of structure containers.

        Returns
        -------
        features : np.ndarray
            Computed features for each structure.
        objectives : np.ndarray
            Computed objectives for each structure.
        """

        # Evaluate features
        features = self.get_features( individuals )
        

        # Evaluate objectives
        objectives = self.get_objectives( individuals )

        return features, objectives

    def get_features(self, individuals):
        return self._evaluate_features(individuals=individuals, features_funcs=self.features_funcs)

    def get_objectives(self, individuals):
        return self._evaluate_objectives(individuals=individuals, objectives_funcs=self.objectives_funcs)

    def _evaluate_features(self, individuals, features_funcs: callable = None):
        """
        Evaluates the given list of individuals using a user-supplied feature extractor function.

        Parameters
        ----------
        individuals : list
            List of individuals to evaluate.
        features_funcs : callable
            A function or callable that, given a list of individuals,
            returns an (N, D) array of features.

        Returns
        -------
        np.ndarray
            (N, D) array of feature vectors, one row per structure.
        """
        if not callable(features_funcs):
            # Return dummy feature: 1.0 for each individual
            return np.ones((len(individuals), 1), dtype=np.float64)

        return np.array([features_funcs(individual) for individual in individuals], dtype=np.float64)

    def _evaluate_objectives(self, individuals, objectives_funcs):
        r"""
        Compute multi-objective scores for a set of individuals.

        This function applies one or more user-supplied objective functions to an
        array of individuals and returns an (N, K) array of objective values,
        where N is the number of individuals and K is the number of objectives.

        **Procedure**:

        1. **Single callable**  
           If `objectives_funcs` is a single callable  
           .. math::
              f: \{\text{individuals}\} \;\to\; \mathbb{R}^{N \times K},
           then invoke  
           ```python
             results = objectives_funcs(individuals)
           ```
           and return it as a NumPy array.

        2. **List of K callables**  
           If `objectives_funcs = [f_1, f_2, \dots, f_K]`, each with signature  
           \\(f_k: \{\text{individuals}\} \to \mathbb{R}^N\\), then compute  
           .. math::
              \mathbf{o}_k = f_k(\text{individuals}), \quad k=1,\dots,K,
           stack them column-wise  
           .. math::
              O = [\,\mathbf{o}_1,\dots,\mathbf{o}_K\,] \in \mathbb{R}^{N\times K}.
           This is implemented as:
           ```python
           np.array([ func(individuals) for func in objectives_funcs ]).T
           ```

        3. **Return shape**  
           Always returns a NumPy array of shape \\((N,K)\\), suitable for downstream
           selection and analysis routines.

        :param individuals:
            List of N structure objects. Each object is passed to the objective functions.
        :type individuals: list[Any]
        :param objectives_funcs:
            Either a single callable returning an (N,K) array, or a list of K callables
            each returning an (N,) array of values.
        :type objectives_funcs: callable or list[callable]
        :returns:
            NumPy array of shape (N, K) containing objective values.
        :rtype: numpy.ndarray

        :raises ValueError:
            If `objectives_funcs` is a list but the returned shapes do not align, or
            if the inputs are not callable.
        """
        if isinstance(objectives_funcs, list):  
            return np.array([func(individuals) for func in objectives_funcs]).T
        else:
            return np.array([objectives_funcs(individuals)], dtype=np.float64)
