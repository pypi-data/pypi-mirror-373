"""
planes.py
---------

Provides functions for identifying atomic planes in a structure and distributing atoms
across layers.
"""

import numpy as np

def identify_planes(atom_labels, coordinates, atom_types=['Ni', 'Fe', 'V'],
                    tolerance=3.3, include_close=False, container=None):
    """
    Identifies planes of specified atom types and assigns IDs starting from 0.

    Parameters
    ----------
    atom_labels : list
        List of atom labels.
    coordinates : np.ndarray
        Coordinates of the atoms (Nx3).
    atom_types : list, optional
        List of atom types to consider, by default ['Ni', 'Fe', 'V'].
    tolerance : float, optional
        Tolerance for differentiating planes in the y-direction, by default 3.3.
    include_close : bool, optional
        Whether to include atoms close to the identified planes, by default False.
    container : Container, optional
        If needed to find neighbors or additional geometry methods.

    Returns
    -------
    tuple
        (indices, plane_ids), where:
        - indices is a 1D array of atom indices for the given `atom_types`.
        - plane_ids is a 1D array of the same length, containing plane ID for each atom.
    """
    indices = np.where(np.isin(atom_labels, atom_types))[0]
    selected_coordinates = coordinates[indices]

    sorted_order = np.argsort(selected_coordinates[:, 1])
    selected_coordinates = selected_coordinates[sorted_order]
    indices = indices[sorted_order]  # Align indices with sorted coords

    plane_id = 0
    current_plane_y = selected_coordinates[0, 1]
    plane_ids = np.zeros(len(indices), dtype=int)

    for i, coord in enumerate(selected_coordinates):
        if np.abs(coord[1] - current_plane_y) > tolerance:
            plane_id += 1
            current_plane_y = coord[1]
        plane_ids[i] = plane_id

    # If include_close is True, incorporate a neighbor-based approach
    # This can be implemented if your code requires merging nearby layers
    if include_close and container is not None:
        pass

    return indices, plane_ids


def distribute_atoms_evenly(num_Ni, num_Fe, num_V, num_planes=4):
    """
    Distributes Ni, Fe, V evenly among the specified number of planes.

    Parameters
    ----------
    num_Ni : int
        Number of Ni atoms.
    num_Fe : int
        Number of Fe atoms.
    num_V : int
        Number of V atoms.
    num_planes : int, optional
        Number of planes for distribution, by default 4.

    Returns
    -------
    dict
        A dictionary with plane_index -> [Ni_count, Fe_count, V_count].
    """
    def distribute_single_element_evenly(total, planes):
        base = total // planes
        remainder = total % planes
        dist = [base] * planes
        for i in range(remainder):
            dist[i % planes] += 1
        return dist

    total_atoms = num_Ni + num_Fe + num_V
    ni_distribution = distribute_single_element_evenly(num_Ni, num_planes)
    fe_distribution = distribute_single_element_evenly(num_Fe, num_planes)
    v_distribution = distribute_single_element_evenly(num_V, num_planes)

    # Example: you might swap certain planes, etc.
    distribution = {}
    for i in range(num_planes):
        distribution[i] = [ni_distribution[i], fe_distribution[i], v_distribution[i]]

    return distribution


def print_distribution_info(distribution):
    """
    Prints details of the distribution of Ni, Fe, V across planes.

    Parameters
    ----------
    distribution : dict
        A dictionary mapping plane_index -> [Ni_count, Fe_count, V_count].
    """
    for plane, counts in distribution.items():
        print(f"Plane {plane}: Ni={counts[0]}, Fe={counts[1]}, V={counts[2]}")
