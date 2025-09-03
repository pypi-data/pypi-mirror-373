import numpy as np
from scipy.spatial.distance import pdist
from scipy.spatial import ConvexHull

def evaluate_features(structures, features_funcs):
    """
    Evaluates the given list of structures using a user-supplied feature extractor function.

    Parameters
    ----------
    structures : list
        List of structures to evaluate.
    features_funcs : callable
        A function or callable that, given a list of structures,
        returns an (N, D) array of features.

    Returns
    -------
    np.ndarray
        (N, D) array of feature vectors, one row per structure.
    """
    return np.array([features_funcs(structure) for structure in structures])

def feature_composition_vector(IDs):
    """
    Returns a function that computes the composition vector for a given structure.
    The vector contains counts for each unique atom label present in the structure.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns a 1D numpy array with the atom counts.
    """
    def get_feature_index_map():
        return { label: idx for idx, label in enumerate(IDs) }

    def compute(structure):
        counts = np.array([np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label) for label in IDs], dtype=float)
        return counts

    compute.get_feature_index_map = get_feature_index_map

    return compute

def feature_total_atoms():
    """
    Returns a function that computes the total number of atoms in a structure.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns a float representing the total atom count.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        return float(len(structure.AtomPositionManager.atomLabelsList))

    compute.get_feature_index_map = get_feature_index_map

    return compute

def feature_unique_atom_count():
    """
    Returns a function that computes the number of unique atom types in a structure.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the count of unique atom labels.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        labels = structure.AtomPositionManager.atomLabelsList
        unique_labels = np.unique(labels)
        return float(len(unique_labels))

    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_average_interatomic_distance():
    """
    Returns a function that computes the average interatomic distance within a structure.
    It uses pairwise Euclidean distances among all atoms.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the average distance.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        coords = structure.AtomPositionManager.atomPositions
        if coords.shape[0] < 2:
            return 0.0
        dists = pdist(coords, metric='euclidean')
        return float(np.mean(dists))
    
    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_radius_of_gyration():
    """
    Returns a function that computes the radius of gyration of a structure.
    The radius of gyration is defined as the root-mean-square distance of the atoms from the center of mass.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the radius of gyration.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        coords = structure.AtomPositionManager.atomPositions
        if coords.shape[0] == 0:
            return 0.0
        center_of_mass = np.mean(coords, axis=0)
        rg = np.sqrt(np.mean(np.sum((coords - center_of_mass)**2, axis=1)))
        return float(rg)

    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_center_of_mass():
    """
    Returns a function that computes the center of mass of a structure.
    The result is a 3D vector representing the average position of the atoms.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns a numpy array of shape (3,).
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        coords = structure.AtomPositionManager.atomPositions
        if coords.shape[0] == 0:
            return np.array([0.0, 0.0, 0.0])
        return np.mean(coords, axis=0)
    
    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_minimum_interatomic_distance():
    """
    Returns a function that computes the minimum interatomic distance in a structure.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the smallest pairwise distance.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        coords = structure.AtomPositionManager.atomPositions
        if coords.shape[0] < 2:
            return 0.0
        dists = pdist(coords, metric='euclidean')
        return float(np.min(dists))
    
    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_convex_hull_volume():
    """
    Returns a function that computes the volume of the convex hull formed by the atomic positions.
    If the points are coplanares o colineales, returns 0.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the convex hull volume.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        coords = structure.AtomPositionManager.atomPositions
        if coords.shape[0] < 4:
            return 0.0
        try:
            hull = ConvexHull(coords)
            return float(hull.volume)
        except Exception:
            return 0.0

    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_cell_volume():
    """
    Returns a function that computes the volume of the simulation cell.
    Assumes that the cell is a 3x3 matrix stored in structure.AtomPositionManager.cell.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the cell volume.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        cell = structure.AtomPositionManager.cell
        try:
            vol = np.abs(np.linalg.det(cell))
            return float(vol)
        except Exception:
            return 0.0

    compute.get_feature_index_map = get_feature_index_map
    
    return compute

def feature_density():
    """
    Returns a function that computes an approximate density of a structure,
    defined as the number of atoms divided by the cell volume.
    
    Returns
    -------
    callable
        A function that accepts a structure and returns the density.
    """
    def get_feature_index_map():
        return { 'N': 0 }

    def compute(structure):
        total_atoms = len(structure.AtomPositionManager.atomLabelsList)
        cell = structure.AtomPositionManager.cell
        try:
            vol = np.abs(np.linalg.det(cell))
        except Exception:
            vol = 1.0
        if vol == 0:
            return 0.0
        return float(total_atoms) / vol

    compute.get_feature_index_map = get_feature_index_map
    
    return compute
