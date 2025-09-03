"""
mutation.py
-----------

Implements functions that mutate structures by changing atom types, adding or removing
solvents, etc.
"""

import copy
import random
import numpy as np
from sage_lib.partition.Partition import Partition
from typing import List, Callable, Tuple, Any, Optional

# ------------------------------------------------------------------
#  ------------             constraints                 ---------
# ------------------------------------------------------------------

def component_greater_than( component:int, threshold: float ):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly greater than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] >= threshold
    return _check

def component_less_than(component: int, threshold: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly less than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] < threshold
    return _check

def component_in_range(component: int, min_val: float, max_val: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position falls within the provided [min_val, max_val] range.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param min_val: Lower bound of the allowed range.
    :param max_val: Upper bound of the allowed range.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return min_val <= value <= max_val
    return _check


def distance_from_origin_less_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is less than a specified threshold.

    :param threshold: The maximum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared < threshold**2
    return _check

def distance_from_origin_greater_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is greater than a specified threshold.

    :param threshold: The minimum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared > threshold**2
    return _check

def component_close_to_value(component: int, target: float, tolerance: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is within a certain tolerance of a target value.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param target: The desired coordinate value.
    :param tolerance: Allowed deviation from the target value.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return abs(value - target) <= tolerance
    return _check

def label_is(label: str):
    """
    Returns a constraint function that checks if the atom’s label matches
    the specified label exactly.

    :param label: Desired atomic label (e.g., 'C', 'H', 'O', 'Fe').
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] == label
    return _check

def label_in(label_set: set):
    """
    Returns a constraint function that checks if the atom’s label is a member
    of the given set of labels.

    :param label_set: A set of valid labels (e.g., {'H', 'He', 'Li'}).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] in label_set
    return _check

def component_ratio_less_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is less than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:  # Avoid division by zero
            return False
        return (pos[x_component] / pos[y_component]) < ratio
    return _check

def component_ratio_greater_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is greater than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:
            return False
        return (pos[x_component] / pos[y_component]) > ratio
    return _check


def distance_between_atoms_less_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is less than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared < threshold**2
    return _check

def distance_between_atoms_greater_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is greater than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared > threshold**2
    return _check


def z_greater_than_fraction_of_lattice(fraction: float):
    """
    Returns a constraint function that checks if the z-component of an atom's position
    is greater than a specified fraction of the c-lattice vector length.

    :param fraction: Fraction of the c-lattice vector (structure.AtomPositionManager.latticeVectors[2,2]).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        c_length = structure.AtomPositionManager.latticeVectors[2, 2]
        z_pos = structure.AtomPositionManager.atomPositions[idx, 2]
        return z_pos > fraction * c_length
    return _check


def x_plus_y_less_than(threshold: float):
    """
    Returns a constraint function that checks if the sum of x- and y-components of
    an atom's position is less than the given threshold.

    :param threshold: Sum threshold for x + y.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[0] + pos[1]) < threshold
    return _check


def y_minus_z_greater_than(threshold: float):
    """
    Returns a constraint function that checks if the difference (y - z) for an atom's
    position exceeds the specified threshold.

    :param threshold: The minimum allowed value for (y - z).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[1] - pos[2]) > threshold
    return _check

def component_sum_greater_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [0, 1] for x+y) of an atom's position is greater than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The minimum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total > threshold
    return _check


def component_sum_less_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [1, 2] for y+z) of an atom's position is less than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The maximum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total < threshold
    return _check


def fixed_positions():
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [1, 2] for y+z) of an atom's position is less than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The maximum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """

    def _check(idx, structure):
        """
        True if the atom is marked as fixed.

        Works with:
          • atomicConstraints: shape (N,)  -> per-atom bool/int
          • atomicConstraints: shape (N,3) -> per-component bools (x,y,z)
        """
        ac = getattr(structure.AtomPositionManager, "atomicConstraints", None)

        if ac is None:
            # No info → don't block anything
            return True

        try:
            v = ac[idx]
        except Exception:
            return True

        # Scalar case (Python bool/int or NumPy scalar)
        if np.isscalar(v) or isinstance(v, (bool, np.bool_, int, np.integer, float, np.floating)):
            return not bool(v)

        # Vector/array-like case
        try:
            arr = np.asarray(v)
            if arr.ndim == 0:
                return not bool(arr)
            # Consider the atom "fixed" if ANY component is fixed
            return not bool(np.any(arr))
        except Exception:
            # Fallback: best-effort cast to bool
            return not bool(v)

    return _check

# from sage_lib.partition.Partition import Partition
# from your_code.utils import get_element_counts, ...
def validate(idx, structure, constraints:list, logic:str = "all") -> bool:
    """
    Checks whether the provided feature vector satisfies
    the constraints according to the specified logic.
    
    Returns
    -------
    bool
        True if constraints pass, False otherwise.
    """

    def _as_bool(x) -> bool:
        # Accept Python bool, numpy.bool_, 0-D arrays, or vectors
        if isinstance(x, (bool, np.bool_)):
            return bool(x)
        a = np.asarray(x)
        if a.shape == ():        # numpy scalar
            return bool(a.item())
        return bool(np.all(a))   # vectors: require all components True

    if not constraints:
        return True
    vals = (_as_bool(constraint(idx, structure)) for constraint in constraints)

    if logic == "all":
        return all(vals)
    elif logic == "any":
        return any(vals)
        
    return False

# ------------------------------------------------------------------
#  ------------                HELPERS                      ---------
# ------------------------------------------------------------------
# ==================== Symmetry-Projection Mutation (CI mode) ====================
# --- internal helpers (minimal, no external deps) --------------------------------
def _kabsch(P, Q):
    """Return rotation R that best aligns P->Q (both centered)."""
    C = P.T @ Q
    V, _, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1.0, 1.0, d])
    return V @ D @ Wt

def _wrap_frac(frac):
    """Wrap fractional coords to [0,1)."""
    return frac - np.floor(frac)

def _cart2frac(cell, xyz):
    """xyz (N,3); cell rows are lattice vectors."""
    return np.linalg.solve(cell.T, xyz.T).T

def _frac2cart(cell, frac):
    return (cell.T @ frac.T).T

def _pairwise_sqdist(A, B):
    """Squared distances between rows of A and B (no PBC)."""
    AA = np.sum(A*A, axis=1)[:, None]
    BB = np.sum(B*B, axis=1)[None, :]
    return AA + BB - 2.0 * (A @ B.T)

def _best_perm_specieswise(X_ref, X_can, species):
    """
    Species-wise assignment: map rows of X_can onto X_ref within each species.
    Tries SciPy Hungarian; falls back to a greedy nearest-neighbor mapping.
    Returns an index array 'perm' so that X_can[perm] ~ X_ref.
    """
    perm = np.arange(len(X_ref))
    try:
        from scipy.optimize import linear_sum_assignment
        out = np.empty_like(perm)
        for sp in np.unique(species):
            I = np.where(species == sp)[0]
            C = _pairwise_sqdist(X_ref[I], X_can[I])
            r, c = linear_sum_assignment(C)
            out[I] = I[c]
        return out
    except Exception:
        # Greedy fallback per species
        out = perm.copy()
        for sp in np.unique(species):
            I = np.where(species == sp)[0]
            if len(I) <= 1:
                continue
            C = _pairwise_sqdist(X_ref[I], X_can[I])
            used = set()
            for j_local, j in enumerate(I):
                # pick nearest unused k in I
                row = C[j_local]
                candidates = [(row[k_local], I[k_local]) for k_local in range(len(I)) if I[k_local] not in used]
                k = min(candidates, key=lambda z: z[0])[1]
                used.add(k)
                out[j] = k
        return out

def _orbit_average_cart(X0, ops, species, max_ops=None):
    """
    Orbit-average in Cartesian space (no PBC).
    For each op: apply, rigidly realign to X0, species-wise permute, then average.
    """
    use_ops = ops if (max_ops is None or max_ops >= len(ops)) else ops[:max_ops]
    com = X0.mean(axis=0)
    X = X0 - com
    acc = np.zeros_like(X)
    for Rop in use_ops:
        Y = X @ Rop.T
        R = _kabsch(Y, X)
        Y_al = Y @ R.T
        perm = _best_perm_specieswise(X, Y_al, species)
        acc += Y_al[perm]
    Xsym = acc / float(len(use_ops))
    return Xsym + com

def _orbit_average_frac(cell, X0, ops, species, max_ops=None):
    """
    Orbit-average in fractional space (PBC-aware wrapping).
    """
    use_ops = ops if (max_ops is None or max_ops >= len(ops)) else ops[:max_ops]
    frac0 = _wrap_frac(_cart2frac(cell, X0))
    acc = np.zeros_like(frac0)
    for Rop in use_ops:
        # apply op in Cartesian, map to frac, wrap
        Yc = X0 @ Rop.T
        Yf = _wrap_frac(_cart2frac(cell, Yc))
        # align in Cartesian to decide permutation (more stable)
        Yc_wrapped = _frac2cart(cell, Yf)
        R = _kabsch(Yc_wrapped - Yc_wrapped.mean(0), X0 - X0.mean(0))
        Yc_al = (Yc_wrapped - Yc_wrapped.mean(0)) @ R.T + X0.mean(0)
        perm = _best_perm_specieswise(X0, Yc_al, species)
        acc += Yf[perm]
    fracsym = _wrap_frac(acc / float(len(use_ops)))
    return _frac2cart(cell, fracsym)

# ----------------- small helper: common operator sets -----------------
def random_rattle(structure, species:list=[], std:float=1, constraints:list=[], seed:int=42, verbose:bool=False, components:list=[0,1,2]):
    r"""
    Apply a constrained random displacement ("rattle") to selected atoms.

    This mutation perturbs the positions of a subset of atoms by adding Gaussian 
    noise only along specified Cartesian components, subject to user-provided constraints.

    **Steps**:

    1. **Build component mask**  
       Convert any string labels in ``components`` to their integer indices  
       (``0\!\to\!x``, ``1\!\to\!y``, ``2\!\to\!z``).  
       ```python
       components = [comp_map[c] if isinstance(c, str) else c for c in components]
       ```

    2. **Select target atoms**  
       Let \\(L_i\\) be the list of all atomic labels, and \\(S\\subseteq\\{1,\\dots,N\\}\\) be
       the indices matching ``species``.  If ``species`` is empty, \\(S=\\{1,\\dots,N\\}\\).  
       ```math
         S = 
         \begin{cases}
           \{\,i : L_i \in \texttt{species}\}, & |\texttt{species}|>0,\\
           \{1,\dots,N\}, & |\texttt{species}|=0.
         \end{cases}
       ```

    3. **Filter by constraints**  
       From \\(S\\), build  
       \\(F = \{\,i\in S ~|~ \texttt{validate}(i,\!structure,\!constraints)\}\\).  
       If \\(F\\) is empty, abort with ``None, None``.

    4. **Generate mask array**  
       Construct a Boolean mask \\(M\in\{0,1\}^{N\times 3}\\) where  
       \\(M_{i,c}=1\\) iff \\(i\in F\\) and \\(c\in\texttt{components}\\).  

    5. **Apply Gaussian displacement**  
       For each atom index \\(i\\) and component \\(c\\) with \\(M_{i,c}=1\\), update  
       ```math
         x_{i,c} \;\leftarrow\; x_{i,c} + \epsilon_{i,c}, 
         \quad \epsilon_{i,c}\sim \mathcal{N}(0,\sigma^2),
         \quad \sigma = \texttt{std}
       ```  
       holding other coordinates fixed.  Implementation uses  
       ``structure.AtomPositionManager.rattle(stdev=std, seed=seed, mask=mask_array)``.

    :param structure:
        Object with ``AtomPositionManager`` providing ``atomLabelsList``,
        ``atomPositions``, and a ``rattle`` method.
    :type structure: any
    :param species:
        Single label or list of labels to perturb; if empty, all atoms are considered.
    :type species: list[str]
    :param std:
        Standard deviation \\(\sigma\\) of the Gaussian noise.
    :type std: float
    :param constraints:
        List of callables ``(idx,structure)→bool``; only atoms passing **all**
        constraints are rattled.
    :type constraints: list[callable]
    :param seed:
        Pseudorandom seed for reproducibility.
    :type seed: int
    :param verbose:
        If ``True``, emit detailed diagnostic messages.
    :type verbose: bool
    :param components:
        Subset of Cartesian components (0,1,2 or 'x','y','z') along which to apply noise.
    :type components: list[int|str]
    :returns:
        A tuple ``(modified_structure, mask_array)`` where
        ``mask_array`` is the \\(N\times3\\) Boolean mask used; or
        ``(None, None)`` if no atoms qualified.
    :rtype: tuple[any, numpy.ndarray] or (None, None)
    """
    comp_map = {'x': 0, 'y': 1, 'z': 2}
    components = [comp_map[c] if isinstance(c, str) else c for c in components]
    
    labels = np.array(structure.AtomPositionManager.atomLabelsList)
    N_atoms = len(labels)

    if isinstance(species, str):     
        atom_indices = np.nonzero(labels == species)[0]
    elif isinstance(species, (list, np.ndarray)):
        species = np.array(species)
        if species.size == 0:
            atom_indices = np.arange(N_atoms)
        else:
            atom_indices = np.nonzero(np.isin(labels, species))[0]
    else:
        raise ValueError("species must be either a string or a list of strings.")
    atom_indices_filtered = [idx for idx in atom_indices if validate(idx, structure, constraints)]

    if not atom_indices_filtered:
        return None, None

    atom_indices_filtered = np.array(atom_indices_filtered)
    mask_array = np.zeros((N_atoms, 3), dtype=bool)
    mask_array[np.ix_(atom_indices_filtered, components)] = True
    structure.AtomPositionManager.rattle(stdev=std, seed=seed, mask=mask_array)

    return structure, mask_array

def change_atom_type(structure, ID_initial, ID_final, N:int=1, constraints:list=[], verbose:bool=False, ):
    r"""
    Change the chemical identity of one randomly chosen atom.

    This mutation selects a single atom whose current label is in `ID_initial`,
    validates it against optional constraints, and replaces its label with `ID_final`.

    **Procedure**:

    1. **Gather candidates**  
       Let \\(L = [L_i]_{i=1}^N\\) be the list of atomic labels.  
       Define the index set  
       \\[
         C = \{\,i \mid L_i \in \texttt{ID\_initial}\}.
       \\]

    2. **Constraint filtering**  
       From \\(C\\), build  
       \\[
         F = \{\,i \in C \mid \forall\,\varphi\in\texttt{constraints}: \varphi(i,\text{structure}) = \text{True}\}.
       \\]  
       If \\(F\\) is empty, abort and return `(None, None)`.

    3. **Random selection**  
       Draw  
       \\[
         i^* \sim \text{Uniform}(F).
       \\]

    4. **Perform relabeling**  
       Encapsulate the structure in a temporary `Partition`, then call  
       `partition.handleAtomIDChange(...)` to execute  
       \\(L_{i^*}\!\leftarrow\!\texttt{ID\_final}\\)  
       exactly \\(N\\) times.

    :param structure:
        Structure object with `AtomPositionManager.atomLabelsList`.
    :type structure: any
    :param ID_initial:
        Single label or list of labels from which to choose.
    :type ID_initial: str or list[str]
    :param ID_final:
        New atomic label to assign.
    :type ID_final: str
    :param N:
        Number of identical relabel operations to perform.
    :type N: int
    :param constraints:
        List of callables `(idx, structure) -> bool`; only indices passing **all** 
        constraints are eligible.
    :type constraints: list[callable]
    :param verbose:
        If True, enables detailed logging within `handleAtomIDChange`.
    :type verbose: bool
    :returns:
        A tuple `(modified_structure, selected_index)`, or `(None, None)` if no atom qualified.
    :rtype: tuple[any, int] or (None, None)
    """

    # ------------------------------------------------------------------ 1. gather
    labels = np.asarray(structure.AtomPositionManager.atomLabelsList)

    # ---- resolve ID_initial → candidate indices ---------------------------
    if isinstance(ID_initial, (int, np.integer)):
        candidate_indices = np.asarray([int(ID_initial)], dtype=int)

    elif isinstance(ID_initial, str):
        candidate_indices = np.where(labels == ID_initial)[0]

    elif isinstance(ID_initial, (list, tuple, np.ndarray)):
        arr = np.asarray(ID_initial)

        if np.issubdtype(arr.dtype, np.integer):
            candidate_indices = arr.astype(int)

        elif np.issubdtype(arr.dtype, np.str_):
            candidate_indices = np.where(np.isin(labels, arr))[0]

        else:
            raise ValueError(
                "ID_initial sequence must contain either all integers or all strings."
            )
    else:
        raise ValueError(
            "ID_initial must be an int, str, or an iterable of ints or strs."
        )


    # ------------------------------------------------------------------ 2. constrain
    atom_indices_filtered = []

    for idx in candidate_indices:
        if validate(idx, structure, constraints):
            atom_indices_filtered.append( idx )

    candidate_indices = atom_indices_filtered

    if len(candidate_indices) == 0:
        return None, None

    # ------------------------------------------------------------------ 3. select
    selected_atom_index = random.choice(candidate_indices)

    # ------------------------------------------------------------------ 4. relabel
    partition = Partition()
    partition.add_container( structure )

    partition.handleAtomIDChange({
     'atom_index': {
         'search': 'exact',
         'atom_index': 'atom_index',
         'atom_ID': [selected_atom_index],
         'new_atom_ID': [ID_final],
         'N': N,
         'weights': [1],
         'seed': 1,
         'verbose': verbose
     }
    })
    return partition.containers[0], selected_atom_index

def remove_atom_groups(structure, species, N=1, constraints: list=[]):
    r"""
    Remove one or more atoms or groups from the structure.

    This function supports two modes:
    - **Single-species removal**: randomly delete one atom of label `species`.
    - **Multi-group removal**: generate new configurations via `Partition.generate_configurational_space`.

    **Single-species**:
    1. Identify indices \\(C = \{\,i \mid L_i = \texttt{species}\}\\).
    2. Filter by constraints:  
       \\(F = \{\,i\in C \mid \forall\varphi: \varphi(i,\text{structure})\}\\).
    3. Choose \\(i^*\sim\mathrm{Uniform}(F)\\) and call  
       `structure.AtomPositionManager.remove_atom(i^*)`.

    **Multi-group**:
    1. Wrap `structure` in a `Partition`.
    2. Call  
       ```python
       partition.generate_configurational_space(
           values={
               'iterations': N,
               'atom_groups': species,
               ...
           }
       )
       ```
       which returns a list of new structures with groups removed.

    :param structure:
        Structure containing `AtomPositionManager.atomLabelsList`.
    :type structure: any
    :param species:
        Label (str) or list of atom‐group identifiers to remove.
    :type species: str or list
    :param N:
        Number of removal iterations (only used in multi‐group mode).
    :type N: int
    :param constraints:
        Callables `(idx, structure)->bool` to filter candidates in single-species mode.
    :type constraints: list[callable]
    :returns:
        Modified structure after removal.
    :rtype: any
    """
    species = species[0] if isinstance(species, list) and len(species)==1 else species

    if structure.AtomPositionManager.atomCount == 1:
        return structure
        
    if isinstance(species, str):

        atom_indices = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == species)[0]
        
        atom_indices_filtered = []
        for idx in atom_indices:
            if validate(idx, structure, constraints):
                atom_indices_filtered.append( idx )

        atom_indices = atom_indices_filtered
        if len(atom_indices) > 0:
            structure.AtomPositionManager.remove_atom( random.choice(atom_indices) )

    else:
        partition = Partition()
        partition.add_container( copy.deepcopy([structure]) )
        values = {
            'iterations': N,
            'repetitions': 1,
            'distribution': 'uniform',
            'fill': False,
            'atom_groups': species,
            'group_numbers': None,
        }

        partition.set_container( partition.generate_configurational_space(values=values, verbose=False) )
        structure = partition.containers[0]
        
    return structure

def add_species(structure, species, bound:list =None, collision_tolerance:float=2.0, slab:bool=False, constraints: list=[], verbose:bool=False ):
    r"""
    Add adsorbates or solvent molecules to a structure.

    Two modes, determined by `bound`:

    1. **Bound‐site addition**:  
       - Compute candidate indices  
         \\(C = \{\,i: i\in\texttt{bound}\\}\cup\{\,i: L_i\in\texttt{bound}\}.\\)  
       - Filter by constraints to form \\(F\\).  
       - Assemble parameter dictionary  
         \\(\texttt{ADD_ADSOBATE}\mapsto\{\dots\}\\)  
         and call `partition.handleCLUSTER(...)`.

    2. **Solvent filling**:  
       - Use uniform placement in the unit cell, with density and tolerance settings,  
         via `{'ADD_SOLVENT': {...}}`.

    :param structure:
        Structure with `AtomPositionManager` supporting lattice and removal/insertion.
    :type structure: any
    :param species:
        Single species or list of species to add.
    :type species: list[str]
    :param bound:
        Optional list of anchor indices or labels for bound‐site addition.
    :type bound: list[int|str] or None
    :param collision_tolerance:
        Minimum allowed interatomic distance.
    :type collision_tolerance: float
    :param constraints:
        Filters applied to `bound` indices (if provided).
    :type constraints: list[callable]
    :param verbose:
        If True, passes verbose flag into cluster handlers.
    :type verbose: bool
    :returns:
        New `structure` with added species, or `None` if addition failed.
    :rtype: any or None
    """
    species = species if isinstance(species, list) else [species]

    partition = Partition()
    partition.add_container( copy.deepcopy([structure]) )

    if isinstance(bound, (list, np.ndarray)):
        # Convert elements that are int or float to integers
        atom_indices = [int(x) for x in bound if isinstance(x, (int, float))]

        # Append indices from container.AtomPositionManager.atomLabelsList where the label is present in ID_label_list
        atom_indices.extend(
            i for i, label in enumerate(structure.AtomPositionManager.atomLabelsList)
            if label in bound
        )

        atom_indices_filtered = []
        for idx in atom_indices:
            if validate(idx, structure, constraints):
                atom_indices_filtered.append( idx )

        assert len(atom_indices_filtered) > 0, "Error: atom_indices_filtered list is empty"
        
        values = {
            'adsobate': species,
            'padding':1.,
            'resolution':40,
            'd':collision_tolerance*1.06,
            'ID': atom_indices_filtered,
            'collision_tolerance': collision_tolerance*0.95,
            'molecules_number':np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':100,
            'slab':slab,
            'seed':None,
            'prioritize_connectivity':True,
            'verbose':verbose,
        }
        ans = partition.handleCLUSTER( values= {'ADD_ADSOBATE':values}  )

    else:
        values = {
            'density': None,
            'solvent': species,
            'slab': slab,
            'shape': 'cell',
            'size': None,
            'vacuum_tolerance': None,
            'collision_tolerance': collision_tolerance,
            'molecules_number': np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':100,
            'seed':None,
            'verbose':verbose
        }
        ans = partition.handleCLUSTER( values= {'ADD_SOLVENT':values}  )

    if ans == False:
        return None
    else:
        return partition.containers[0]

# ------------------------------------------------------------------
#  ------------          Mutations functions              ---------
# ------------------------------------------------------------------
def mutation_swap(ID1: str, ID2: str, constraints: list=[], N: int=1):
    def func(structure):
        idx1_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID1)[0]
        idx2_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID2)[0]

        if len(idx1_list) > 0 and len(idx2_list) > 0:

            structure, idx = change_atom_type(structure=structure, ID_initial=ID1, ID_final=ID2, N=N, constraints=constraints)
            structure, idx = change_atom_type(structure=structure, ID_initial=idx2_list, ID_final=ID1, N=N, constraints=constraints)
        else: return None

        return structure

    return func

def mutation_change_ID(ID_initial: str, ID_final: str, constraints: list=[], N: int=1):
    
    def func(structure):
        structure, _ = change_atom_type(structure=structure, ID_initial=ID_initial, ID_final=ID_final, N=N, constraints=constraints)
        return structure

    return func


def mutation_change_all_ID_random(
    ID_initial_list: List[str],
    ID_final_list:   List[str],
    verbose:         bool = False
) -> Callable[[Any], Any]:
    """
    Returns a callable that, given a structure, will:
      1. Identify all atom‐indices whose label ∈ ID_initial_list.
      2. Randomly pick one such index.
      3. Randomly pick a replacement label ∈ ID_final_list (according to `weights`).
      4. Delegate to Config_builder.handleAtomIDChange to perform the change N times.
      5. Return the mutated structure (or the original if no viable atom was found).

    :param ID_initial_list: list of labels to choose from in the structure.
    :param ID_final_list:   list of candidate replacement labels.
        If None, uniform sampling is used.
    :param verbose:         passed through to handleAtomIDChange.
    """
    ID_initial_list = np.array(ID_initial_list, ndmin=1)
    ID_final_list   = np.array(ID_final_list,   ndmin=1)

    def func(structure: Any) -> Any:

        atomLabelsList = structure.AtomPositionManager.atomLabelsList
        common = np.intersect1d(atomLabelsList, ID_initial_list)

        ID_initial_pick = random.choice(common)
        ID_final_pick = random.choice(ID_final_list)

        selected_atomLabels = np.where(structure.AtomPositionManager.atomLabelsList == ID_initial_pick)[0]
        structure.AtomPositionManager.set_ID(atom_index=np.where(selected_atomLabels)[0], ID=ID_final_pick)

        return structure[0]

    return func

def mutation_remove(species: str, constraints: list=[], N:int=1):
    def func(structure):
        structure = remove_atom_groups(structure, species=species, N=N, constraints=constraints)
        return structure

    return func

def mutation_add(species: list, bound:list =None, collision_tolerance:float=2.0, constraints: list=[], slab:bool=False):
    def func(structure):
        structure = add_species(structure=structure, species=species, bound=bound, collision_tolerance=collision_tolerance, slab=slab, constraints=constraints)
        return structure

    return func

def mutation_remove_add(species_add: list, species_remove: list, bound:list =None, collision_tolerance:float=2.0, constraints: list=[], N:int=1, slab:bool=False):
    def func(structure):
        structure = remove_atom_groups(structure=structure, species=species_remove, N=N, constraints=constraints)
        structure = add_species(structure=structure, species=species_add, bound=bound, collision_tolerance=collision_tolerance, slab=slab, constraints=constraints)

        return structure

    return func

def mutation_rattle(std: str, constraints: list=[], species:list=[], components:list=[0,1,2], seed:int=42 ):
    def func(structure):
        structure, _ = random_rattle(structure=structure, species=species, std=std,  constraints=constraints, components=components, seed=seed )
        return structure
    return func

def mutation_compress(compress_factor: float, constraints: list=[]):
    def func(structure):
        structure.AtomPositionManager.compress(compress_factor=compress_factor, verbose=False)
        return structure
    return func

def mutation_shear(gamma_max: float, plane: str = 'xy', verbose: bool = False):
    """
    Apply a simple shear γ in the specified coordinate plane up to ±gamma_max.

    :param gamma_max: Maximum shear magnitude.
    :param plane:     One of 'xy', 'xz', or 'yz'.
    :param verbose:   If True, print the applied shear component.
    :returns:         A function(structure) -> structure
    """
    axes_map = {
        'xy': (0, 1),
        'xz': (0, 2),
        'yz': (1, 2),
    }
    if plane not in axes_map:
        raise ValueError(f"Invalid plane '{plane}'. Choose from 'xy', 'xz', or 'yz'.")

    i, j = axes_map[plane]

    def _mutate(structure):
        # 1) Original cell
        C = np.array(structure.AtomPositionManager.latticeVectors, dtype=float)

        # 2) Random shear in the chosen plane
        gamma = np.random.uniform(-gamma_max, gamma_max)
        shear = np.eye(3, dtype=float)
        shear[i, j] = gamma

        # 3) New cell and fractional coords
        C_new = shear.dot(C)
        frac = np.linalg.solve(C.T, structure.AtomPositionManager.atomPositions.T).T

        # 4) Assign back
        structure.AtomPositionManager.latticeVectors = C_new
        structure.AtomPositionManager.atomPositions = (C_new.T.dot(frac.T)).T

        if verbose:
            print(f"Applied shear γ_{plane} = {gamma:.3f}")

        return structure

    return _mutate

def mutation_random_strain(max_strain: float, constraints: list = [], seed: int = None, verbose: bool = False):
    """
    Apply a random symmetric strain tensor (up to ±max_strain) 
    to both the lattice vectors and atomic positions.

    :param max_strain: Maximum absolute strain component (e.g. 0.02 for ±2%).
    :param constraints: List of callables (idx, structure)->bool; if non-empty,
                        the strain is only applied if all atoms pass.
    :param seed:       RNG seed for reproducibility.
    :param verbose:    If True, prints the applied strain tensor.
    :returns:          A function(structure) -> structure
    """
    rng = np.random.RandomState(seed)

    def _mutate(structure):
        # 1) Optionally check constraints on every atom
        if constraints:
            N = len(structure.AtomPositionManager.atomPositions)
            ok = all(
                all(c(idx, structure) for c in constraints)
                for idx in range(N)
            )
            if not ok:
                return None

        # 2) Fetch original cell & positions
        C0 = np.array(structure.AtomPositionManager.latticeVectors, dtype=float)
        pos = np.array(structure.AtomPositionManager.atomPositions, dtype=float)

        # 3) Build a small symmetric strain tensor
        eps = rng.uniform(-max_strain, max_strain, size=(3,3))
        eps = 0.5*(eps + eps.T)

        # 4) Compute new cell and positions
        C1 = (np.eye(3) + eps).dot(C0)
        # fractional coords w.r.t. original cell
        frac = np.linalg.solve(C0.T, pos.T).T
        new_pos = (C1.T.dot(frac.T)).T

        # 5) Assign back
        structure.AtomPositionManager.latticeVectors = C1
        structure.AtomPositionManager.atomPositions = new_pos

        if verbose:
            print("Applied strain tensor:\n", eps)
        return structure

    return _mutate

def mutation_symmetry_project(
    ops: list,
    alpha: float = 0.5,
    tol: float = 1e-6,
    max_iter: int = 30,
    max_ops: int = 50,
    periodic: bool = False,
    apply_prob: float = 1.0,
    species_subset: list = None,
    index_mask: np.ndarray = None,   # optional: faster than species_subset if you have it
    # repulsion-related parameters
    repulsion: bool = True,
    repulsion_strength: float = 0.1,
    repulsion_min_distance: float = 1.0,
    repulsion_steps: int = 3,
):
    """
    Symmetry-projection (continuous iteration) mutation.
    - ops: list of 3x3 orthogonal matrices (rotations/reflections/inversion).
    - alpha: relaxation factor (0<alpha<=1).
    - tol: per-atom RMS movement threshold (Å) to stop the CI loop.
    - max_iter: max CI iterations.
    - max_ops: cap number of symmetry ops used per call.
    - periodic: if True, operate in fractional coords with wrapping.
    - apply_prob: probability to apply the mutation (for diversity control).
    - species_subset: list of labels to move (others kept fixed). If None, move all.
    - index_mask: boolean array (N,) to select moved atoms (overrides species_subset if given).

    Returns: function(structure) -> structure
    """
    def _mutate(structure):
        if np.random.rand() > apply_prob or len(ops) == 0:
            return structure

        cell   = np.array(structure.AtomPositionManager.latticeVectors, float)
        X      = np.array(structure.AtomPositionManager.atomPositions, float)
        labels = np.array(structure.AtomPositionManager.atomLabelsList)

        # choose which atoms to move
        if index_mask is not None:
            mask = np.array(index_mask, dtype=bool)
        elif species_subset is None or len(species_subset) == 0:
            mask = np.ones(len(labels), dtype=bool)
        else:
            mask = np.isin(labels, np.array(species_subset))

        I = np.where(mask)[0]
        if I.size == 0:
            return structure

        # CI loop on the participating subset only
        Xw = X.copy()
        it = 0
        while it < max_iter:
            Xprev = Xw[I].copy()
            if periodic:
                Xsym = _orbit_average_frac(cell, Xw[I], ops, labels[I], max_ops=max_ops)
            else:
                Xsym = _orbit_average_cart(Xw[I], ops, labels[I], max_ops=max_ops)
            Xw[I] = (1.0 - alpha) * Xw[I] + alpha * Xsym
            rms = np.linalg.norm(Xw[I] - Xprev) / np.sqrt(I.size)

            # --- optional repulsion term ---
            if repulsion:
                for _ in range(repulsion_steps):
                    com = Xw.mean(axis=0)

                    # Pull atoms toward center of mass (soft confinement)
                    disp = com - Xw
                    Xw += repulsion_strength * disp

                    # Rigid-sphere repulsion (pairwise)
                    N = len(Xw)
                    for i in range(N):
                        for j in range(i+1, N):
                            rij = Xw[j] - Xw[i]
                            dist = np.linalg.norm(rij)
                            if dist < repulsion_min_distance and dist > 1e-12:
                                corr = 0.5 * (repulsion_min_distance - dist) * rij / dist
                                Xw[i] -= corr
                                Xw[j] += corr
            it += 1
            if rms < tol:
                break

        structure.AtomPositionManager.atomPositions = Xw
        return structure

    return _mutate

def mutation_compact_to_com(strength: float = 0.1, min_distance: float = 1.0, steps: int = 5, seed: int = None):
    """
    Mutation: Compact atoms toward the center of mass (CoM), treating them as rigid spheres.
    
    Parameters
    ----------
    strength : float
        Force constant toward CoM. Larger = stronger compaction.
    min_distance : float
        Minimum allowed interatomic distance (sphere radius constraint).
    steps : int
        Number of iterative updates.
    seed : int
        RNG seed for reproducibility.
    """
    rng = np.random.RandomState(seed)

    def func(structure):
        pos = np.array(structure.AtomPositionManager.atomPositions, dtype=float)
        N = len(pos)
        if N == 0:
            return structure

        # Iterative relaxation
        for _ in range(steps):
            com = pos.mean(axis=0)

            # Pull each atom toward CoM
            disp = com - pos
            pos += strength * disp

            # Enforce rigid-sphere constraint (no overlap)
            for i in range(N):
                for j in range(i+1, N):
                    rij = pos[j] - pos[i]
                    dist = np.linalg.norm(rij)
                    if dist < min_distance and dist > 1e-8:
                        # Push atoms apart equally
                        corr = 0.5 * (min_distance - dist) * rij / dist
                        pos[i] -= corr
                        pos[j] += corr

        structure.AtomPositionManager.atomPositions = pos

        return structure

    return func






# ============================================================
#      ORGANIC-SPECIFIC HELPERS & MUTATIONS (torsions, etc.)
# ============================================================
import numpy as np
import random

# ---- Helpers (safe to redefine) ---------------------------------------------
def _as_axis_vector(axis):
    if isinstance(axis, str):
        v = {'x': np.array([1.0, 0.0, 0.0]),
             'y': np.array([0.0, 1.0, 0.0]),
             'z': np.array([0.0, 0.0, 1.0])}[axis.lower()]
    else:
        v = np.array(axis, dtype=float)
    n = np.linalg.norm(v)
    if n < 1e-15:
        raise ValueError("Axis vector has near-zero norm.")
    return v / n

def _rotation_matrix(axis_vec, angle_rad):
    k = axis_vec / np.linalg.norm(axis_vec)
    K = np.array([[    0, -k[2],  k[1]],
                  [ k[2],     0, -k[0]],
                  [-k[1],  k[0],     0]], dtype=float)
    I = np.eye(3)
    return I + np.sin(angle_rad)*K + (1 - np.cos(angle_rad))*(K @ K)

# --- Helpers: robust cell handling ------------------------------------------
def _get_cell(structure):
    """Return a valid 3x3 cell or None if absent/invalid/singular."""
    try:
        C = np.array(structure.AtomPositionManager.latticeVectors, dtype=float)
    except Exception:
        return None
    if C.ndim != 2 or C.shape != (3, 3) or not np.isfinite(C).all():
        return None
    try:
        det = float(np.linalg.det(C))
    except Exception:
        return None
    if abs(det) < 1e-12:
        return None
    return C

def _cart_to_frac(cell, cart):
    cart = np.atleast_2d(np.array(cart, dtype=float))
    if cell is None:
        raise ValueError("_cart_to_frac called with cell=None")
    return np.linalg.solve(cell.T, cart.T).T

def _frac_to_cart(cell, frac):
    frac = np.atleast_2d(np.array(frac, dtype=float))
    if cell is None:
        raise ValueError("_frac_to_cart called with cell=None")
    return (cell.T @ frac.T).T

def _wrap_frac(frac):
    return frac - np.floor(frac)

def _pbc_delta(cell, ri, rj):
    """Minimum-image vector rj - ri; if cell is None, plain Cartesian difference."""
    ri = np.array(ri, dtype=float)
    rj = np.array(rj, dtype=float)
    if cell is None:
        return rj - ri
    fi = _cart_to_frac(cell, [ri])[0]
    fj = _cart_to_frac(cell, [rj])[0]
    df = fj - fi
    df -= np.round(df)
    return _frac_to_cart(cell, [df])[0]

# Covalent radii (Å); extend as needed. Fallback = 1.2 Å.
_COV_RAD = {
    'H':0.31,'C':0.76,'N':0.71,'O':0.66,'F':0.57,'P':1.07,'S':1.05,'Cl':1.02,'Br':1.20,'I':1.39,
    'Ni':1.24,'Fe':1.24,'V':1.22,'K':2.03,'Na':1.66,'Li':1.28
}

def _rcov(sym):
    return _COV_RAD.get(sym, 1.20)

# --- Connectivity uses PBC only if the cell is valid -------------------------
def _build_connectivity(structure, radius_scale=1.15, pbc=True, cutoff_max=None):
    labels = np.array(structure.AtomPositionManager.atomLabelsList)
    pos    = np.array(structure.AtomPositionManager.atomPositions, dtype=float)
    if pos.ndim != 2 or pos.shape[1] != 3:
        return [set() for _ in range(len(pos).item() if pos.ndim == 1 else 0)]  # safe fallback

    cell = _get_cell(structure)
    use_pbc = bool(pbc and (cell is not None))

    N = pos.shape[0]
    neigh = [set() for _ in range(N)]
    for i in range(N):
        for j in range(i+1, N):
            rc = radius_scale * (_rcov(labels[i]) + _rcov(labels[j]))
            if cutoff_max is not None:
                rc = min(rc, cutoff_max)
            rij = _pbc_delta(cell if use_pbc else None, pos[i], pos[j])
            if np.dot(rij, rij) <= rc*rc:
                neigh[i].add(j); neigh[j].add(i)
    return neigh


def _enumerate_torsions(neigh):
    """
    Generate torsions (i,j,k,l) where i-j, j-k, k-l are edges; j<k to avoid duplicates.
    """
    torsions = []
    N = len(neigh)
    for j in range(N):
        for k in neigh[j]:
            if j < k:
                for i in (neigh[j] - {k}):
                    for l in (neigh[k] - {j}):
                        torsions.append((i, j, k, l))
    return torsions

def _component_of(neigh, start, blocked):
    """Return the connected component reached from 'start' when the edge to 'blocked' is cut."""
    seen = set([blocked])  # pretend 'blocked' is removed
    out  = []
    stack = [start]
    while stack:
        u = stack.pop()
        if u in seen: 
            continue
        seen.add(u)
        out.append(u)
        for v in neigh[u]:
            if v not in seen:
                stack.append(v)
    return out

def _min_separation_after_move(cell, pos_old, pos_new, moved_idx, tol, pbc=True):
    """
    Quick collision check: ensure all moved atoms are at least 'tol' from all atoms.
    """
    if tol is None:
        return True
    moved = set(moved_idx)
    N = pos_new.shape[0]
    for a in moved:
        ra = pos_new[a]
        for b in range(N):
            if b == a: 
                continue
            rb = pos_new[b] if b in moved else pos_old[b]  # others unchanged
            dv = _pbc_delta(cell, ra, rb) if pbc else (rb - ra)
            if np.dot(dv, dv) < tol*tol:
                return False
    return True

# ---- Public factory ----------------------------------------------------------
# --- Dihedral mutation: auto-fallback to non-PBC for molecules ---------------
def mutation_rotate_dihedral_by_connectivity(
    labels_focus           = None,
    indices_focus          = None,
    require_mode           = 'any',     # 'any' or 'central'
    side                   = 'k',       # 'k' | 'j' | 'l_only'
    angle                  = None,
    angle_range            = (-30.0, 30.0),
    degrees                = True,
    radius_scale           = 1.15,
    cutoff_max             = None,
    pbc                    = True,
    wrap_after             = True,
    collision_tolerance    = 1.05,
    max_attempts           = 8,
    constraints            = [],
    seed                   = None,
    verbose                = False
):
    rng = random.Random(seed)

    def func(structure):
        labels = np.array(structure.AtomPositionManager.atomLabelsList)
        pos    = np.array(structure.AtomPositionManager.atomPositions, dtype=float)
        if pos.ndim != 2 or pos.shape[1] != 3 or pos.shape[0] < 4:
            return None  # nothing to do / malformed positions

        cell = _get_cell(structure)
        use_pbc = bool(pbc and (cell is not None))

        # 1) connectivity & torsions
        neigh = _build_connectivity(structure, radius_scale=radius_scale,
                                    pbc=use_pbc, cutoff_max=cutoff_max)
        torsions = _enumerate_torsions(neigh)
        if not torsions:
            return None

        # 2) filters
        lab_focus = set(labels_focus) if labels_focus is not None else None
        idx_focus = set(indices_focus) if indices_focus is not None else None

        filtered = []
        for (i,j,k,l) in torsions:
            ok = True
            if lab_focus is not None:
                ok = ((labels[j] in lab_focus and labels[k] in lab_focus)
                      if require_mode == 'central'
                      else any(lbl in lab_focus for lbl in (labels[i], labels[j], labels[k], labels[l])))
            if ok and idx_focus is not None:
                ok = (i in idx_focus or j in idx_focus or k in idx_focus or l in idx_focus)
            if ok:
                filtered.append((i,j,k,l))
        if not filtered:
            return None

        (i,j,k,l) = rng.choice(filtered)

        # 3) axis, side, constraints
        axis_vec = _pbc_delta(cell if use_pbc else None, pos[j], pos[k])
        n = np.linalg.norm(axis_vec)
        if n < 1e-12:
            return None
        axis = axis_vec / n
        origin = pos[j].copy()

        if side == 'k':
            side_atoms = _component_of(neigh, start=k, blocked=j)
        elif side == 'j':
            side_atoms = _component_of(neigh, start=j, blocked=k)
        elif side == 'l_only':
            side_atoms = [l]
        else:
            return None

        if constraints and not all(validate(int(u), structure, constraints) for u in side_atoms):
            return None

        # 4) try rotations (collision-checked if requested)
        for _ in range(max(1, int(max_attempts))):
            ang = (rng.uniform(*angle_range) if angle is None else float(angle))
            ang = np.deg2rad(ang) if degrees else ang
            R = _rotation_matrix(axis, ang)

            pos_trial = pos.copy()
            v = pos_trial[side_atoms] - origin
            pos_trial[side_atoms] = (R @ v.T).T + origin

            if wrap_after and use_pbc:
                frac = _cart_to_frac(cell, pos_trial)
                frac = _wrap_frac(frac)
                pos_trial = _frac_to_cart(cell, frac)

            if _min_separation_after_move(cell if use_pbc else None,
                                          pos, pos_trial, side_atoms,
                                          collision_tolerance, pbc=use_pbc):
                structure.AtomPositionManager.atomPositions = pos_trial
                if verbose:
                    print(f"Rotated dihedral ({i}-{j}-{k}-{l}); side={side}")
                return structure
        return None

    return func

























# ============================================================
#  Molecular-graph based torsion mutations for organics
#  (distance-derived bonds, ring-aware rotors, dihedral set/jitter)
# ============================================================
import math
import numpy as np

# --- Covalent radii (Å). Extend as needed.
_COV_RAD = {
    "H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57,
    "P": 1.07, "S": 1.05, "Cl": 1.02, "Br": 1.20, "I": 1.39
}

# ---------------- Graph construction & utilities ----------------
def _bond_table_from_distances(structure, scale: float = 1.15):
    """
    Heuristic bonds as pairs (i,j) if ||ri-rj|| <= scale*(r_cov[i]+r_cov[j]).
    No PBC; intended for gas-phase molecules.
    """
    P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    L = np.asarray(structure.AtomPositionManager.atomLabelsList)
    n = len(P)
    pairs = []
    for i in range(n-1):
        Ri = _COV_RAD.get(L[i], 0.77)
        pi = P[i]
        for j in range(i+1, n):
            Rj = _COV_RAD.get(L[j], 0.77)
            if np.linalg.norm(P[j]-pi) <= scale*(Ri+Rj):
                pairs.append((i, j))
    return pairs

def _adj_from_pairs(pairs, n):
    adj = [[] for _ in range(n)]
    for i, j in pairs:
        adj[i].append(j)
        adj[j].append(i)
    return adj

def _edge_is_in_cycle(adj, i, j):
    """
    Edge (i,j) is in a cycle iff removing it keeps i connected to j.
    """
    n = len(adj)
    seen = [False]*n
    stack = [i]
    seen[i] = True
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if (u == i and v == j) or (u == j and v == i):
                continue
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return seen[j]

def _downstream_from_bond(adj, b, c):
    """
    Vertices reachable from c when the edge (b,c) is removed.
    """
    n = len(adj)
    blocked = {(b, c), (c, b)}
    seen = [False]*n
    out = []
    stack = [c]
    seen[c] = True
    while stack:
        u = stack.pop()
        out.append(u)
        for v in adj[u]:
            if (u, v) in blocked:
                continue
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return np.array(sorted(set(out)), dtype=int)

def _local_planarity_score(P, center, neighbors):
    """
    Cheap sp2/planarity heuristic: fit plane to neighbors of 'center' and
    measure max deviation angle among neighbor normals. Small → planar.
    """
    if len(neighbors) < 3:
        return 180.0  # not enough points → treat as non-planar
    Q = P[neighbors] - P[center]
    # PCA normal:
    U, S, Vt = np.linalg.svd(Q, full_matrices=False)
    n = Vt[-1]
    # angles of neighbor bonds vs plane normal:
    ang = np.degrees(np.abs(np.arcsin((Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)) @ n)))
    return float(np.max(ang))  # small ≈ coplanar

def _bond_is_planar_like(P, adj, b, c, tol_deg=12.0):
    """
    True if either end looks 'planar-like' (sp2/amide-like) per neighbor geometry.
    """
    nb_b = [k for k in adj[b] if k != c]
    nb_c = [k for k in adj[c] if k != b]
    if len(nb_b) >= 2:
        if _local_planarity_score(P, b, nb_b) < tol_deg:
            return True
    if len(nb_c) >= 2:
        if _local_planarity_score(P, c, nb_c) < tol_deg:
            return True
    return False

# ---------------- Geometry helpers ----------------
def _torsion_deg(P, a, b, c, d):
    p = P[[a, b, c, d]]
    b1, b2, b3 = p[1]-p[0], p[2]-p[1], p[3]-p[2]
    n1 = np.cross(b1, b2)
    n2 = np.cross(b2, b3)
    x = np.dot(n1, n2)
    y = np.dot(np.cross(n1, n2), b2/(np.linalg.norm(b2) + 1e-15))
    return float(np.degrees(np.arctan2(y, x)))

def _R_axis_angle(axis, theta):
    axis = np.asarray(axis, float)
    n = np.linalg.norm(axis)
    if n < 1e-15:
        return np.eye(3)
    axis = axis / n
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d),     2*(b*d+a*c)],
                     [2*(b*c+a*d),     a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                     [2*(b*d-a*c),     2*(c*d+a*b),     a*a+d*d-b*b-c*c]], float)

def _rotate_about_bond_inplace(structure, b, c, angle_deg, group, P=None):
    """
    Rotate 'group' atom indices around axis (b→c) by angle_deg (degrees).
    """
    if P is None:
        P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    axis = P[c] - P[b]
    if np.linalg.norm(axis) < 1e-12:
        return False
    R = _R_axis_angle(axis, math.radians(angle_deg))
    origin = P[b]
    Q = P.copy()
    idx = np.asarray(group, dtype=int)
    Q[idx] = (Q[idx] - origin) @ R.T + origin
    structure.AtomPositionManager.atomPositions = Q
    return True

# ---------------- Public dihedral ops (graph-aware) ----------------
def set_dihedral_graph(structure, a, b, c, d, target_deg, cov_scale=1.15):
    """
    Set dihedral a–b–c–d to 'target_deg' by rotating the c-side downstream of b–c.
    """
    P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    pairs = _bond_table_from_distances(structure, scale=cov_scale)
    adj   = _adj_from_pairs(pairs, len(P))
    group = _downstream_from_bond(adj, b, c)
    if group.size == 0:
        return False
    cur = _torsion_deg(P, a, b, c, d)
    delta = ((target_deg - cur + 180.0) % 360.0) - 180.0
    return _rotate_about_bond_inplace(structure, b, c, delta, group, P=P)

def jitter_dihedral_graph(structure, a, b, c, d, max_delta_deg=25.0, cov_scale=1.15):
    """
    Jitter dihedral a–b–c–d by a random Δ∈[−max,+max] rotating the c-side.
    """
    P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    pairs = _bond_table_from_distances(structure, scale=cov_scale)
    adj   = _adj_from_pairs(pairs, len(P))
    group = _downstream_from_bond(adj, b, c)
    if group.size == 0:
        return False
    delta = float(np.random.uniform(-max_delta_deg, max_delta_deg))
    return _rotate_about_bond_inplace(structure, b, c, delta, group, P=P)

# ---------------- Rotor discovery & methyl rotors ----------------
def _rotatable_bonds(structure, cov_scale=1.15, avoid_terminal=True, avoid_rings=True, avoid_planar=True, planarity_tol_deg=12.0):
    """
    Heuristic rotor list: degree≥2 on both ends; optionally skip ring or planar-like (sp2/amide) bonds.
    """
    P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    pairs = _bond_table_from_distances(structure, scale=cov_scale)
    adj   = _adj_from_pairs(pairs, len(P))
    rotors = []
    for (i, j) in pairs:
        if avoid_terminal and (len(adj[i]) < 2 or len(adj[j]) < 2):
            continue
        if avoid_rings and _edge_is_in_cycle(adj, i, j):
            continue
        if avoid_planar and _bond_is_planar_like(P, adj, i, j, tol_deg=planarity_tol_deg):
            continue
        rotors.append((i, j))
    return rotors, adj, pairs

def _methyl_groups(structure, cov_scale=1.15):
    """
    Return list of (center_C, anchor_X, [H,H,H]) for –CH3 groups.
    """
    P = np.asarray(structure.AtomPositionManager.atomPositions, float)
    L = np.asarray(structure.AtomPositionManager.atomLabelsList)
    pairs = _bond_table_from_distances(structure, scale=cov_scale)
    adj   = _adj_from_pairs(pairs, len(P))
    out = []
    for i, lab in enumerate(L):
        if lab != "C":
            continue
        nbrs = adj[i]
        Hs = [k for k in nbrs if L[k] == "H"]
        Xs = [k for k in nbrs if L[k] != "H"]
        if len(Hs) == 3 and len(Xs) == 1:
            out.append((i, Xs[0], Hs))
    return out, adj, pairs

# ------------------------------------------------------------------
#  ------------          Mutations functions              ---------
# ------------------------------------------------------------------
def mutation_dihedral_set_graph(dihedral: tuple, target_deg: float, cov_scale: float = 1.15, constraints: list = []):
    """
    Set a specific dihedral (a,b,c,d) to 'target_deg' by rotating the c-side
    of bond b–c. Returns None if the move is not applicable.
    """
    a,b,c,d = map(int, dihedral)
    def func(structure):
        # respect your constraint hook on the b/c pivot if provided
        if constraints and not (validate(b, structure, constraints) and validate(c, structure, constraints)):
            return None
        ok = set_dihedral_graph(structure, a, b, c, d, float(target_deg), cov_scale=cov_scale)
        return structure if ok else None
    return func

def mutation_dihedral_jitter_graph(dihedral: tuple, max_delta_deg: float = 25.0, cov_scale: float = 1.15, constraints: list = []):
    """
    Randomly jitter a specific dihedral (a,b,c,d) by ±max_delta_deg (degrees).
    """
    a,b,c,d = map(int, dihedral)
    def func(structure):
        if constraints and not (validate(b, structure, constraints) and validate(c, structure, constraints)):
            return None
        ok = jitter_dihedral_graph(structure, a, b, c, d, max_delta_deg=max_delta_deg, cov_scale=cov_scale)
        return structure if ok else None
    return func

def mutation_rotor_jitter_graph(
    max_delta_deg: float = 30.0,
    avoid_terminal: bool = True,
    avoid_rings: bool = True,
    avoid_planar: bool = True,
    planarity_tol_deg: float = 12.0,
    cov_scale: float = 1.15,
    constraints: list = [],
    seed: int = None
):
    """
    Pick a random rotatable bond (heuristic) and rotate its downstream side by
    a random ±Δ. Skips terminal, ring, and planar-like (sp2/amide) bonds by default.
    """
    rng = np.random.RandomState(seed)
    def func(structure):
        rotors, adj, pairs = _rotatable_bonds(
            structure,
            cov_scale=cov_scale,
            avoid_terminal=avoid_terminal,
            avoid_rings=avoid_rings,
            avoid_planar=avoid_planar,
            planarity_tol_deg=planarity_tol_deg
        )
        if not rotors:
            return None
        b, c = rotors[rng.randint(len(rotors))]
        if constraints and not (validate(b, structure, constraints) and validate(c, structure, constraints)):
            return None
        group = _downstream_from_bond(adj, b, c)
        if group.size == 0:
            return None
        delta = float(rng.uniform(-max_delta_deg, max_delta_deg))
        ok = _rotate_about_bond_inplace(structure, b, c, delta, group)
        return structure if ok else None
    return func

def mutation_methyl_rotor_graph(step_deg: float = 120.0, jitter: float = 10.0, cov_scale: float = 1.15, seed: int = None):
    """
    Rotate one –CH3 group about its C–X bond by (step_deg ± jitter) degrees,
    moving only the three H atoms (rigid top).
    """
    rng = np.random.RandomState(seed)
    def func(structure):
        mets, adj, pairs = _methyl_groups(structure, cov_scale=cov_scale)
        if not mets:
            return None
        c, x, Hs = mets[rng.randint(len(mets))]
        angle = float(step_deg + rng.uniform(-jitter, jitter))
        ok = _rotate_about_bond_inplace(structure, x, c, angle, group=Hs)
        return structure if ok else None
    return func

def mutation_rotate_bond_graph(bc: tuple, delta_deg: float, cov_scale: float = 1.15, avoid_rings: bool = True, avoid_planar: bool = True, planarity_tol_deg: float = 12.0, constraints: list = []):
    """
    Low-level utility: rotate the downstream side of a specific bond (b,c) by delta_deg.
    Useful when you already know the pivot and want deterministic moves.
    """
    b, c = map(int, bc)
    def func(structure):
        P = np.asarray(structure.AtomPositionManager.atomPositions, float)
        pairs = _bond_table_from_distances(structure, scale=cov_scale)
        adj   = _adj_from_pairs(pairs, len(P))
        if avoid_rings and _edge_is_in_cycle(adj, b, c):
            return None
        if avoid_planar and _bond_is_planar_like(P, adj, b, c, tol_deg=planarity_tol_deg):
            return None
        if constraints and not (validate(b, structure, constraints) and validate(c, structure, constraints)):
            return None
        group = _downstream_from_bond(adj, b, c)
        if group.size == 0:
            return None
        ok = _rotate_about_bond_inplace(structure, b, c, float(delta_deg), group, P=P)
        return structure if ok else None
    return func

