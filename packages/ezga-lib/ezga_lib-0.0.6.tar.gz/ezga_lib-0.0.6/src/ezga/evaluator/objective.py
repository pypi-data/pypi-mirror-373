import numpy as np
import logging
from numpy.linalg import norm, inv
from scipy.spatial.distance import cdist
from sage_lib.partition.Partition import Partition
from scipy.spatial import ConvexHull, QhullError
from scipy.stats import zscore
from sklearn.cluster import KMeans
from scipy.spatial.distance import mahalanobis
import warnings
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.linear_model import Ridge

def evaluate_objectives(structures, objectives_funcs):
    r"""
    Compute multi-objective scores for a set of structures.

    This function applies one or more user-supplied objective functions to an
    array of structures and returns an (N, K) array of objective values,
    where N is the number of structures and K is the number of objectives.

    **Procedure**:

    1. **Single callable**  
       If `objectives_funcs` is a single callable  
       .. math::
          f: \{\text{structures}\} \;\to\; \mathbb{R}^{N \times K},
       then invoke  
       ```python
         results = objectives_funcs(structures)
       ```
       and return it as a NumPy array.

    2. **List of K callables**  
       If `objectives_funcs = [f_1, f_2, \dots, f_K]`, each with signature  
       \\(f_k: \{\text{structures}\} \to \mathbb{R}^N\\), then compute  
       .. math::
          \mathbf{o}_k = f_k(\text{structures}), \quad k=1,\dots,K,
       stack them column-wise  
       .. math::
          O = [\,\mathbf{o}_1,\dots,\mathbf{o}_K\,] \in \mathbb{R}^{N\times K}.
       This is implemented as:
       ```python
       np.array([ func(structures) for func in objectives_funcs ]).T
       ```

    3. **Return shape**  
       Always returns a NumPy array of shape \\((N,K)\\), suitable for downstream
       selection and analysis routines.

    :param structures:
        List of N structure objects. Each object is passed to the objective functions.
    :type structures: list[Any]
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
        return np.array([func(structures) for func in objectives_funcs]).T
    else:
        return np.array([objectives_funcs(structures)])

def naive_objectives(structures, objectives_funcs):
    return np.ones( (self.partitions['dataset'].size, len(objectives_funcs)) )

def find_optimal_kmeans_k(data, max_k=10):
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


def objective_volume():
    """
    Returns a function that computes the volume of each structure based on its lattice vectors.
    
    Assumptions:
      - Each structure has an attribute 'AtomPositionManager' with an attribute 'latticeVectors'
        containing a 3x3 numpy array.
    
    Returns
    -------
    callable
        A function that accepts a list of structures and returns a numpy array of volumes.
    """
    def compute(structures):
        volumes = []
        for s in structures:
            if hasattr(s.AtomPositionManager, 'latticeVectors'):
                # Compute the absolute value of the determinant of the lattice vectors.
                vol = abs(np.linalg.det(s.AtomPositionManager.latticeVectors))
            else:
                vol = 0.0
            volumes.append(vol)
        return np.array(volumes)
    return compute

def objective_density(atomic_weights: dict = None):
    """
    Returns a function to compute the density of each structure.
    
    Density is defined as the total mass (sum of atomic weights) divided by the volume.
    If 'atomic_weights' is not provided, each atom is assumed to have unit mass.
    
    Parameters
    ----------
    atomic_weights : dict, optional
        Mapping from atomic symbol to atomic weight (e.g., {'Fe': 55.85, 'Ni': 58.69}).
    
    Returns
    -------
    callable
        A function that accepts a list of structures and returns a numpy array of densities.
    """
    def compute(structures):
        densities = []
        for s in structures:
            # Obtain volume from lattice vectors if available.
            if hasattr(s.AtomPositionManager, 'latticeVectors'):
                vol = abs(np.linalg.det(s.AtomPositionManager.latticeVectors))
            else:
                vol = 1.0  # Default volume to avoid division by zero.
            # Obtain the list of atomic labels.
            labels = s.AtomPositionManager.atomLabelsList
            if atomic_weights is None:
                total_mass = len(labels)
            else:
                total_mass = sum(atomic_weights.get(label, 1.0) for label in labels)
            density = total_mass / vol if vol != 0 else 0.0
            densities.append(density)

        return np.array(densities)
    return compute

def objective_average_interatomic_distance():
    """
    Returns a function that computes the average interatomic distance within each structure.
    
    Assumptions:
      - Each structure has an attribute 'AtomPositionManager' with an 'atomPositions'
        attribute that is a 2D numpy array of shape (N_atoms, 3).
    
    Returns
    -------
    callable
        A function that accepts a list of structures and returns a numpy array of the average 
        interatomic distance for each structure.
    """
    def compute(structures):
        avg_distances = []
        for s in structures:
            if hasattr(s.AtomPositionManager, 'atomPositions'):
                positions = s.AtomPositionManager.atomPositions
                # Ensure there are at least two atoms to compute distances.
                if positions.ndim == 2 and positions.shape[0] > 1:
                    distances = pdist(positions)
                    avg_distance = np.mean(distances)
                else:
                    avg_distance = 0.0
            else:
                avg_distance = 0.0
            avg_distances.append(avg_distance)
        return np.array(avg_distances)
    return compute

def objective_coordination_number(cutoff: float = 3.0):
    """
    Returns a function that computes the average coordination number of atoms in each structure.
    
    The coordination number is defined as the average number of neighboring atoms within a given
    cutoff distance. This metric can give insights into the local atomic environment.
    
    Parameters
    ----------
    cutoff : float, optional
        The distance cutoff to define neighboring atoms.
    
    Returns
    -------
    callable
        A function that accepts a list of structures and returns a numpy array of average 
        coordination numbers.
    """
    def compute(structures):
        avg_coordination = []
        for s in structures:
            if hasattr(s.AtomPositionManager, 'atomPositions'):
                positions = s.AtomPositionManager.atomPositions
                if positions.ndim == 2 and positions.shape[0] > 0:
                    dist_matrix = squareform(pdist(positions))
                    # Exclude self distances by setting diagonal entries to infinity.
                    np.fill_diagonal(dist_matrix, np.inf)
                    # Count neighbors for each atom within the cutoff.
                    coordination_numbers = np.sum(dist_matrix < cutoff, axis=1)
                    avg_coord = np.mean(coordination_numbers)
                else:
                    avg_coord = 0.0
            else:
                avg_coord = 0.0
            avg_coordination.append(avg_coord)
        return np.array(avg_coordination)
    return compute

def objective_symmetry():
    """
    Returns a function that computes a symmetry score for each structure based on the dispersion
    of atomic distances from the center of mass.
    
    A lower score (i.e., lower standard deviation) indicates a more symmetric distribution of atoms.
    
    Assumptions:
      - Each structure has an attribute 'AtomPositionManager' with an 'atomPositions'
        attribute that is a 2D numpy array of shape (N_atoms, 3).
    
    Returns
    -------
    callable
        A function that accepts a list of structures and returns a numpy array of symmetry scores.
    """
    def compute(structures):
        symmetry_scores = []
        for s in structures:
            if hasattr(s.AtomPositionManager, 'atomPositions'):
                positions = s.AtomPositionManager.atomPositions
                if positions.ndim == 2 and positions.shape[0] > 0:
                    # Compute the center of mass.
                    center_of_mass = np.mean(positions, axis=0)
                    # Calculate distances of each atom from the center.
                    distances = np.linalg.norm(positions - center_of_mass, axis=1)
                    # Use the standard deviation of these distances as a symmetry metric.
                    score = np.std(distances)
                else:
                    score = 0.0
            else:
                score = 0.0
            symmetry_scores.append(score)
        return np.array(symmetry_scores)
    return compute

def objective_energy(scale=1.0):
    """
    Returns a function that computes the (scaled) total energy of each structure.

    Parameters
    ----------
    scale : float
        Factor by which to scale the energy value.

    Returns
    -------
    callable
        A function that accepts a list of structures and returns an ndarray
        of shape (N, ), containing scaled energies.
    """
    def compute(structures):
        values = []
        for s in structures:
            # Suppose 'E' is the total energy stored in AtomPositionManager
            E = getattr(s.AtomPositionManager, 'E', 0.0)
            E = np.asarray(E, dtype=float)   
            E = np.nan_to_num(E, nan=0.0)  

            values.append(scale * E)
        return np.array(values)
    return compute

def objective_formation_energy(reference_potentials=None):
    """
    Returns a function to compute formation energy based on reference chemical potentials.

    Parameters
    ----------
    reference_potentials : dict or None
        Mapping from atom symbol to chemical potential value. For example:
        {'Fe': -3.72, 'Ni': -4.55, ...}
        If None, will return raw energies.

    Returns
    -------
    callable
        A function that accepts a list of structures and returns an ndarray
        of shape (N, ), representing formation energies.
    """
    def compute(structures):
        values = []

        partition = Partition()
        partition.add_container( structures )

        X = np.array([
            [
                np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
                for label in partition.uniqueAtomLabels
            ]
            for structure in structures
            ])
        y = np.array([getattr(s.AtomPositionManager, 'E', 0.0) for s in structures])
        y = np.asarray(y, dtype=float)   
        y = np.nan_to_num(y, nan=0.0)  

        if reference_potentials is not None:
            # Subtract the sum of reference potentials from total energy
            chemical_potentials = np.array([reference_potentials.get(ual, 0) for ual in partition.uniqueAtomLabels])
            formation_energies = y - X.dot(chemical_potentials)
        else:
            model = Ridge(alpha=1e-5, fit_intercept=False)
            model.fit(X, y)
            chemical_potentials = model.coef_
            formation_energies = y - X.dot(chemical_potentials)

        return np.array(formation_energies)

    return compute

def objective_min_distance_to_hull(reference_potentials:dict=None, variable_species:str=None, A:float=None, mu_range:list=None, steps:int=20):
    """
    """
    A_cte = isinstance(A, float)
        
    def compute(
        structures,
    ):
        """
        Computes the minimum distance to the convex hull for each structure while varying
        the chemical potential (mu) of exactly one species. All other species use fixed 
        (reference) chemical potentials. Formation-energy calculations are vectorized to
        improve efficiency.

        Parameters
        ----------
        structures : list
            A list of objects containing:
              - structure.AtomPositionManager.atomLabelsList (array of atomic labels)
              - structure.AtomPositionManager.E (float energy)
        reference_potentials : dict
            Reference chemical potentials keyed by species label, e.g. {'A': -3.0, 'B': -2.5}
        variable_species : str
            The species whose chemical potential is varied.
        mu_range : (float, float)
            The (start, end) range for the variable chemical potential.
        steps : int
            Number of discrete mu steps to sample in mu_range.

        Returns
        -------
        min_distances : np.ndarray, shape (N,)
            For each structure (out of N), the minimal distance to the hull found over all 
            tested mu values.
        """

        # 1) Collect structures and get unique labels
        partition = Partition()
        partition.add_container( structures )

        unique_labels = partition.uniqueAtomLabels
        if not variable_species in unique_labels:
            unique_labels.append(variable_species)

        # 2) Build composition matrix X and energy array y
        #    X[i, j] = # of atoms of species j in structure i
        #    y[i]    = total energy of structure i
        N_structs = len(structures)
        M_species = len(unique_labels)
        X = np.zeros((N_structs, M_species), dtype=float)
        y = np.zeros(N_structs, dtype=float)
        
        A_array = np.zeros_like( structures )  if not A_cte else A
        for i, struct in enumerate(structures):
            y[i] = getattr(struct.AtomPositionManager, 'E', 0.0)
            labels_array = struct.AtomPositionManager.atomLabelsList
            for j, lbl in enumerate(unique_labels):
                X[i, j] = np.count_nonzero(labels_array == lbl)

            if not A_cte:
                A_array[i] = abs(np.linalg.det(np.array([struct.AtomPositionManager.latticeVectors[0, :2], struct.AtomPositionManager.latticeVectors[1, :2]])))

        # 3) Identify index of the species we vary and prepare reference chemical potentials
        try:
            var_index = unique_labels.index(variable_species)
        except ValueError:
            raise ValueError(f"Species '{variable_species}' not found in unique labels {unique_labels}.")
        
        base_chem_pots = np.array([reference_potentials.get(lbl, 0.0) for lbl in unique_labels])
        
        # --- We will treat the variable species' chemical potential as an addition to 
        #     whatever reference value it has. If you want mu_range to represent the *entire* 
        #     potential (instead of just an offset), adjust accordingly. ---
        
        # 4) Precompute the formation energy offset for everything but the variable species
        #    so that we do not repeatedly recalculate the full dot product.
        #    formation_energy_if_mu_var_were_zero = y - X @ base_chem_pots_zeroed
        #    where base_chem_pots_zeroed has 0 for var_index, but reference values for others.
        base_chem_pots_zeroed = base_chem_pots.copy()
        base_chem_pots_zeroed[var_index] = 0.0
        fE_ref = y - X.dot(base_chem_pots_zeroed)  # shape: (N,)
        
        # 5) Prepare data structures for loop over mu
        min_distances = np.full(N_structs, np.inf, dtype=float)
        mu_values = np.linspace(mu_range[0], mu_range[1], steps)
        
        # 6) Define a function for distance above/below hull
        def distance_above_hull(compositions, energies):
            """
            Returns the 'above-hull' distance for each point in compositions+energies
            using a geometric approach. 
            In practice for materials, you'd typically compute 'energy above hull' at
            each composition. This geometric method is a demonstration for d-dimensional 
            hulls. 
            """
            # We treat compositions as shape (N, M), energies as shape (N,)
            # Points for hull: shape (N, M+1)
            points = np.hstack([compositions, energies[:, None]])
            hull = ConvexHull(points)
            
            # Prepare array for distances of each point from the lower hull
            above_hull_dist = np.zeros(len(points), dtype=float)
            
            # For each hull facet, we get an equation eq: (a_0, a_1, ..., a_(M+1)) 
            # so that eq[0]*x0 + eq[1]*x1 + ... + eq[M]*energy + eq[M+1] = 0
            # We'll check which side of the facet is 'above' vs 'below'. 
            # In principle, you'd filter for 'lower hull' facets. 
            for simplex in hull.simplices:
                eq = hull.equations[simplex]       # shape (M+2,) for M+1 dims
                norm_eq = np.linalg.norm(eq[:-1])  # ignoring the constant term eq[-1]
                
                # Evaluate signed distance for all points
                signed_dist = (points @ eq[:-1] + eq[-1]) / norm_eq
                
                # Determine orientation: if eq for the energy dimension is < 0, 
                # we treat it as a 'lower' facet. (You may need to adapt the sign test.)
                # eq[-2] is often the coefficient for the last 'energy' dimension
                # if you appended compositions first. Adjust as needed.
                if eq[-2] < 0.0:
                    # Keep only positive distances; negative means point is inside/under.
                    # For each point, track the maximum distance above any 'lower' facet.
                    # This effectively measures how far outside the hull the point sits.
                    mask_pos = signed_dist > above_hull_dist
                    above_hull_dist[mask_pos] = signed_dist[mask_pos]
            
            return above_hull_dist
        
        # 7) Main loop over sampled mu values (the new formation-energy computations are vectorized)
        #    The hull must be recomputed for each mu, but the formation-energy calculations are fast.
        fE_array = np.zeros( (N_structs, steps) )
        fE_hull = np.zeros( steps )
        for mu_var_i, mu_var in enumerate(mu_values):
            # If base_chem_pots[var_index] is the reference, then total mu for that species = 
            # base_chem_pots[var_index] + mu_var. 
            # => The variable part is mu_var itself.  
            
            # fE for each structure: 
            #    fE = [ precomputed reference part ] - X[:, var_index]*mu_var - [ reference contribution for var species ]
            # However, we already omitted var species from 'fE_ref'; 
            # so now just subtract (X[:, var_index]* (base_chem_pots[var_index] + mu_var)) 
            # if you want the entire potential; 
            # or subtract X[:, var_index]*mu_var if mu_values are offsets from reference, etc.
            
            total_var_pot = base_chem_pots[var_index] + mu_var
            fE = fE_ref - X[:, var_index] * total_var_pot  # shape: (N,)
            fE_array[:, mu_var_i] = fE / A_array
            fE_hull[mu_var_i] = np.min(fE_array[:, mu_var_i])
            # (Optional) Reintroduce the reference for the variable species if needed:
            #   fE -= X[:, var_index] * base_chem_pots[var_index]
            # but in this approach we've accounted for everything in fE_ref and total_var_pot.
            
            # Build the hull in composition+energy space. 
            # You can choose raw counts X or normalized fractions. 
        min_distances = np.min(fE_array - fE_hull[np.newaxis, :], axis=1)
        '''
        import matplotlib.pyplot as plt
        for n in range(N_structs):
            if n%1000:
                print(n)

            if n < 5:
                plt.plot(mu_values, fE_array[n,:], 'r') 

            elif n < 12:
                plt.plot(mu_values, fE_array[n,:], 'g') 
   
            else:
                plt.plot(mu_values, fE_array[n,:], 'b') 

        for n in range(12):
            if n%1000:
                print(n)

            if n < 5:
                plt.plot(mu_values, fE_array[n,:], 'r') 

            elif n < 12:
                plt.plot(mu_values, fE_array[n,:], 'g') 
        plt.show()
        '''
        return min_distances

    return compute


def objective_distance_to_composition_hull(reference_potentials: dict, A: float = None):
    """
    Builds a convex hull in composition-fraction vs formation-energy space
    with fixed chemical potentials, and returns the distance above hull
    for each input structure.

    Parameters
    ----------
    reference_potentials : dict
        Reference chemical potentials keyed by species label, e.g. {'A': -3.0, 'B': -2.5}
    A : float or None
        Constant area or volume factor. If None, energies are normalized per atom.

    Returns
    -------
    compute : function
        A function that accepts a list of structures and returns an array of distances
        above the hull for each structure.
    """
    def compute(structures):
        # Gather unique species labels
        partition = Partition()
        partition.add_container( structures )
        labels = partition.uniqueAtomLabels

        N = len(structures)
        M = len(labels)
        X = np.zeros((N, M), dtype=float)
        y = np.zeros(N, dtype=float)

        # Fill composition counts and energies
        for i, struct in enumerate(structures):
            y[i] = struct.AtomPositionManager.E
            lbls = struct.AtomPositionManager.atomLabelsList
            for j, lbl in enumerate(labels):
                X[i, j] = np.count_nonzero(lbls == lbl)

        # Determine normalization: per-area or per-atom
        if A is None:
            norm = X.sum(axis=1)
        else:
            norm = np.full(N, A, dtype=float)

        # Reference chemical potentials vector
        mu_vec = np.array([reference_potentials.get(lbl, 0.0) for lbl in labels])

        # Compute per-structure formation energy
        fE = (y - X.dot(mu_vec)) / norm

        # Compute composition fractions
        comp_frac = X / X.sum(axis=1)[:, None]

        # Build points for hull: (fractions..., formation energy)
        points = np.hstack([comp_frac, fE[:, None]])

        # Compute convex hull, with fallback joggle if necessary
        try:
            hull = ConvexHull(points)
        except QhullError:

            try:
                hull = ConvexHull(points, qhull_options='QJ')  # apply tiny random perturbation
            except:
                return np.zeros(N)
        # Distance above hull for each point
        d_above = np.zeros(N, dtype=float)
        eqs = hull.equations  # shape (num_facets, (M-1)+1+1)

        for eq in eqs:
            # eq[:M+1] are coefficients for fraction dims and energy
            # eq[-1] is constant term
            # Identify lower facets: energy coefficient < 0
            if eq[-2] < 0:
                norm_eq = np.linalg.norm(eq[:-1])
                signed = (points.dot(eq[:-1]) + eq[-1]) / norm_eq
                # Update distances
                mask = signed > d_above
                d_above[mask] = signed[mask]

        return d_above

    return compute

def objective_similarity(
    r_cut=4.0,
    n_max=2,
    l_max=2,
    sigma=0.5,
    n_components=3,
    compress_model='pca',  # or 'umap', etc.
    eps=0.6,
    min_samples=2,
    cluster_model='minibatch-kmeans',  # or 'dbscan'
    max_clusters=10
):
    """
    Returns a function that computes similarity scores for a list of structures based on the
    complement of their anomaly scores computed in the cluster space derived from SOAP descriptors.
    
    Similarity is defined as:
         similarity = 1 / (1 + anomaly)
    so that a lower anomaly (i.e., a more typical structure) yields a higher similarity,
    with similarity values in the range (0, 1].
    
    Parameters
    ----------
    r_cut : float
        Cutoff radius for the SOAP calculation.
    n_max : int
        Maximum number of radial basis functions.
    l_max : int
        Maximum spherical harmonic degree.
    sigma : float
        Gaussian width for the SOAP descriptors.
    n_components : int
        Number of components for dimensionality reduction.
    compress_model : str
        Compression model to use (e.g., 'pca' or 'umap').
    eps : float
        Epsilon parameter for the clustering algorithm.
    min_samples : int
        Minimum number of samples for clustering.
    cluster_model : str
        Identifier for the clustering method (e.g., 'dbscan' or 'minibatch-kmeans').
    max_clusters : int
        Maximum number of allowed clusters.
    
    Returns
    -------
    callable
         A function that accepts a list of structures and returns a NumPy array of similarity scores.
    
    See Also
    --------
    objective_anomality
         Function that calculates anomaly scores from the cluster space.
    """
    # Get the anomaly objective function using the provided parameters.
    anomaly_func = objective_anomality(
        r_cut=r_cut,
        n_max=n_max,
        l_max=l_max,
        sigma=sigma,
        n_components=n_components,
        compress_model=compress_model,
        eps=eps,
        min_samples=min_samples,
        cluster_model=cluster_model,
        max_clusters=max_clusters
    )
    
    def compute_similarity(structures):
        """
        Computes similarity scores for a list of structures.
        
        Parameters
        ----------
        structures : list
            List of atomic structures for which to compute similarity.
        
        Returns
        -------
        np.ndarray
            An array of similarity scores (one per structure), calculated as 1 / (1 + anomaly).
        """
        # Compute anomaly scores using the wrapped anomaly function.
        anomaly_scores = anomaly_func(structures)
        
        # Compute similarity scores as the inverse relation to anomaly:
        # similarity = 1 / (1 + anomaly)
        # This ensures that structures with low anomaly (i.e., more typical) have similarity near 1,
        # while structures with high anomaly have similarity scores near 0.
        similarity_scores = 1.0 / (1.0 + anomaly_scores)

        return similarity_scores

    return compute_similarity
    
def objective_anomality(
    r_cut=4.0,
    n_max=2,
    l_max=2,
    sigma=0.5,
    n_components=3,
    compress_model='pca', #'umap'
    eps=0.6,
    min_samples=2,
    cluster_model='minibatch-kmeans', #'dbscan'
    max_clusters=10
):
    """
    Returns a function that computes anomaly scores for a list of structures using the cluster space
    derived from SOAP descriptors.

    The process is as follows:
        1. Compute SOAP descriptors for each structure.
        2. Compress the descriptors using the specified dimensionality reduction method.
        3. Perform clustering on the compressed data for each atomic species.
        4. Generate a cluster count matrix representing the cluster space.
        5. Compute anomaly scores as the Mahalanobis distance in this space.

    Parameters:
        r_cut (float): Cutoff radius for SOAP calculation.
        n_max (int): Maximum number of radial basis functions.
        l_max (int): Maximum spherical harmonic degree.
        sigma (float): Gaussian width for the SOAP descriptors.
        n_components (int): Number of components for dimensionality reduction.
        compress_model (str): Compression model to use (e.g., 'pca', 'umap').
        eps (float): Epsilon parameter for the clustering algorithm.
        min_samples (int): Minimum samples for clustering.
        cluster_model (str): Identifier for the clustering method (e.g., 'dbscan').
        max_clusters (int): Maximum number of allowed clusters.

    Returns:
        callable: A function that accepts a list of structures and returns a NumPy array of anomaly scores.
    """
    def compute(
        structures,
        n_components=5,
        r_cut=5.0,
        n_max=3,
        l_max=3,
        sigma=0.5,
        max_clusters=10,
    ):
        """
        Computes anomaly scores per structure by:
          1. Generating SOAP descriptors per species
          2. Doing PCA + K-means (with an optimal number of clusters up to max_clusters)
          3. Counting cluster assignments to build a combined cluster-count matrix
          4. Using Mahalanobis distance in that cluster space as an anomaly metric

        Parameters
        ----------
        structures : list
            List of atomic structures.
        n_components : int
            Number of PCA components for dimensionality reduction per species.
        r_cut, n_max, l_max, sigma : float or int
            Parameters for the SOAP calculation.
        max_clusters : int
            The maximum possible number of clusters to try per species.

        Returns
        -------
        anomaly_scores : np.ndarray, shape (num_structures,)
            Mahalanobis-based anomaly scores for each structure.
        """

        # --------------------------------------------------------------------------
        # Step 0: Validate input
        # --------------------------------------------------------------------------
        n_structures = len(structures)
        if n_structures == 0:
            return np.array([])

        if n_structures < n_components:
            # If you cannot reliably do PCA because you have fewer structures than n_components
            return np.zeros(n_structures)

        # --------------------------------------------------------------------------
        # Step 1: SOAP Descriptors
        # --------------------------------------------------------------------------
        partition = Partition()
        partition.add_container( structures )
        descriptors_by_species, atom_info_by_species = partition.get_SOAP(
            r_cut=r_cut,
            n_max=n_max,
            l_max=l_max,
            sigma=sigma,
            save=False,
            cache=False
        )
        # descriptors_by_species: {species: (num_atoms_of_species, feature_dim)}
        # atom_info_by_species:   {species: [(structure_idx, atom_idx, ...), ...]}

        # If no descriptors at all, return zeros
        if not descriptors_by_species:
            return np.zeros(n_structures)

        # We will accumulate each species' cluster counts in a list.
        # Ultimately we'll stack them horizontally, so that each species
        # contributes a block of columns to the final (num_structures x total_num_clusters).
        cluster_counts_list = []

        # --------------------------------------------------------------------------
        # Step 2: For each species, do PCA + K-means and build cluster counts
        # --------------------------------------------------------------------------
        for species, desc_array in descriptors_by_species.items():
            # desc_array shape: (num_atoms_of_species, feature_dim)
            if desc_array.shape[0] == 0:
                # No atoms of this species
                continue

            # structure_indices[i] => a tuple (struc_idx, atom_idx, etc.)
            # We'll parse out the structure index from that tuple.
            structure_indices_full = atom_info_by_species[species]

            # Check descriptor dimension
            feature_dim = desc_array.shape[1]
            if feature_dim < n_components:
                # Not enough descriptor dimension => produce a zero matrix
                # or skip. We'll do zero matrix here, but you can adjust logic.
                zero_matrix = np.zeros((n_structures, 1), dtype=int)
                cluster_counts_list.append(zero_matrix)
                continue

            # 2A. PCA
            try:
                pca = PCA(n_components=n_components)
                compressed_data = pca.fit_transform(desc_array)  # shape: (num_atoms_of_species, n_components)
            except ValueError:
                # If PCA fails, skip or produce zeros
                zero_matrix = np.zeros((n_structures, 1), dtype=int)
                cluster_counts_list.append(zero_matrix)
                continue

            # 2B. Determine Optimal Cluster Count up to max_clusters
            #     Then run K-means for that cluster count.
            optimal_k = find_optimal_kmeans_k(compressed_data, max_k= np.min([compressed_data.shape[0], max_clusters]) ) 
            # If there's only 1 cluster (edge case), we skip KMeans or do a single cluster labeling:
            if optimal_k == 1:
                # All atoms in the same cluster => cluster_counts is shape (n_structures, 1)
                cluster_counts = np.zeros((n_structures, 1), dtype=int)
                for i_atom, c_data in enumerate(compressed_data):
                    # Single cluster => cluster index is 0
                    struc_idx = structure_indices_full[i_atom][0]
                    if 0 <= struc_idx < n_structures:
                        cluster_counts[struc_idx, 0] += 1
            else:
                kmeans = KMeans(n_clusters=optimal_k, random_state=42)
                atom_clusters = kmeans.fit_predict(compressed_data)  # shape: (num_atoms_of_species,)

                # 2C. Build cluster-count matrix
                # We want shape (n_structures, optimal_k).
                cluster_counts = np.zeros((n_structures, optimal_k), dtype=int)
                for i_atom, cluster_label in enumerate(atom_clusters):
                    struc_idx = structure_indices_full[i_atom][0]
                    # Guard against out-of-range structure indices
                    if 0 <= struc_idx < n_structures:
                        cluster_counts[struc_idx, cluster_label] += 1

            # Accumulate cluster counts for this species
            cluster_counts_list.append(cluster_counts)

        # If no species produced cluster counts, return zeros
        if not cluster_counts_list:
            return np.zeros(n_structures)

        # --------------------------------------------------------------------------
        # Step 3: Combine cluster counts from all species
        # --------------------------------------------------------------------------
        # We horizontally stack them. Example: species A => (n_structures, a_k),
        # species B => (n_structures, b_k). Combined => (n_structures, a_k + b_k).
        combined_cluster_counts = np.hstack(cluster_counts_list)  # shape: (n_structures, sum_of_clusters_all_species)

        # --------------------------------------------------------------------------
        # Step 4: Anomaly Scoring in cluster space (Mahalanobis)
        # --------------------------------------------------------------------------
        # 4A. Z-score normalization
        normalized_data = zscore(combined_cluster_counts, axis=0)
        normalized_data = np.nan_to_num(normalized_data, nan=0.0)

        # 4B. Mean / Covariance
        mean_vector = np.mean(normalized_data, axis=0)
        cov_matrix = np.cov(normalized_data, rowvar=False)

        # Regularize the covariance matrix to avoid singularities
        cov_matrix += 1e-6 * np.eye(cov_matrix.shape[0])
        cov_inv = inv(cov_matrix)

        # 4C. Mahalanobis distance => anomaly score
        anomaly_scores = []
        for row in normalized_data:
            try:
                dist = mahalanobis(row, mean_vector, cov_inv)
            except Exception:
                dist = np.nan
            anomaly_scores.append(dist)
        
        return np.array(anomaly_scores)

    return compute

def information_novelty(
    r_cut=4.0,
    n_max=2,
    l_max=2,
    sigma=0.5,
    n_components=3,
    compress_model='pca', #'umap'
    eps=0.6,
    min_samples=2,
    cluster_model='minibatch-kmeans', #'dbscan'
    max_clusters=10
):
    """
    """
    from ..classification.clustering import SOAPClusterAnalyzer
    from ..metric.information_ensemble_metrics import InformationEnsambleMetric

    def compute(       
        structures,
        n_components=5,
        r_cut=5.0,
        n_max=3,
        l_max=3,
        sigma=0.5,
        max_clusters=10,
        ):

        if len(structures) <= n_components:
            return np.ones(len(structures))

        analyzer = SOAPClusterAnalyzer()
        cluster_array = analyzer.get_cluster_counts(structures)

        IEM = InformationEnsambleMetric(
            metric = 'novelty',
        )

        information_novelty = IEM.compute(cluster_array)

        return np.array(information_novelty)
    
    return compute

def objective_min_distance_to_hull_pourbaix_diagram(pd:object, references_species:list):
    from collections import defaultdict
    from ..utils.pourbaix_diagram import Species 

    def objective(structures):
        partition = Partition()
        partition.add_container( structures )

        pd._candidate_species = {}
        pd._name_counts = defaultdict(int)

        for structure in structures:
            name = ''.join([f'{item}{key}' for item, key in structure.AtomPositionManager.atomCountDict.items()])
            pd.add_candidate_species( Species(name, G=structure.AtomPositionManager.E) )
            
        distances = pd.distance_convex_hull( reference_species=references_species, baseline_specie=None )

        return distances

    return objective
