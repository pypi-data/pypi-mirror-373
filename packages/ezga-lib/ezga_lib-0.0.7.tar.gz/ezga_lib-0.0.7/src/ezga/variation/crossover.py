"""
crossover.py
------------

Provides several default crossover functions that can be used in conjunction
with the GA framework. Each crossover function takes two parent structures
(structureA and structureB) and returns two resulting child structures
(childA, childB).

Integration:
    - You can add these functions to your 'crossover_funcs' list in
      'MutationCrossoverHandler'.
    - The main GA loop will randomly pick one of these crossover
      functions based on assigned probabilities, similarly to how
      mutations are handled.
    - Each crossover function should either return two new structures,
      or (None, None) if the crossover fails or is not feasible.

Constraints:
    - By default, these examples do not strictly filter or check constraints
      except for a minimal example in `swap_random_atoms`. If you want
      to replicate the approach from the mutation constraints, adapt the
      `validate(...)` function as needed to handle pairs of atoms or other
      conditions.
"""
import numpy as np
import copy
import random

def align_and_crossover(parentA, parentB, crossover_func=None):
    r"""
    Align two parent structures in 3D space and perform a genetic crossover.

    This routine carries out the following sequence of operations:

    1. **Deep copy** of the input structures to avoid mutating the originals.
    2. **Translation to centroid** for each parent:
       .. math::
          \mathbf{c} = \frac{1}{N}\sum_{i=1}^{N} \mathbf{x}_i,\quad
          \tilde{\mathbf{x}}_i = \mathbf{x}_i - \mathbf{c}.
    3. **PCA-based rotation** to align principal axes with the canonical axes:
       - Compute the covariance matrix
         .. math::
            \Sigma = \frac{1}{N-1}\sum_{i=1}^{N} (\tilde{\mathbf{x}}_i)(\tilde{\mathbf{x}}_i)^\top.
       - Eigen-decompose :math:`\Sigma \mathbf{v}_j = \lambda_j \mathbf{v}_j`.
       - Rotate positions via
         .. math::
            \mathbf{x}^\prime_i = V^\top \tilde{\mathbf{x}}_i,
         where :math:`V = [\mathbf{v}_1,\mathbf{v}_2,\mathbf{v}_3]`.
    4. **Fine RMSD minimization** by:
       a. Pairing atoms in the smaller structure to nearest neighbours in the larger:
          .. math::
             j^*(i) = \arg\min_{j}\,\|\,\mathbf{a}_i - \mathbf{b}_j\|_2.
       b. Applying the **Kabsch algorithm** to find
          .. math::
             R = \arg\min_{R\in SO(3)} \sum_{i=1}^{m}\|R\mathbf{u}_i - \mathbf{v}_i\|^2,
             \quad \mathbf{t} = \bar{\mathbf{v}} - R\,\bar{\mathbf{u}}.
    5. **Crossover** using `crossover_func`, which takes the aligned parents
       and returns two children. If None, a default single-cut plane crossover
       (`single_cut_crossover`) is used.

    :param parentA: First parent structure, with attributes:
        - `.AtomPositionManager.atomPositions`: :math:`(N,3)` array of coordinates.
        - `.AtomPositionManager.atomLabelsList`: length-N array of labels.
        - Methods `.remove_atom(indices)` and `.add_atom(atomLabels, atomPosition)`.
    :param parentB: Second parent structure (same interface as `parentA`).
    :param crossover_func: Optional callable:
        ``(alignedA, alignedB) -> (childA, childB)``.
    :returns: Tuple `(childA, childB)` of new structures.
    """

    # 1) Copy the parents so we do not modify them directly
    A = copy.deepcopy(parentA)
    B = copy.deepcopy(parentB)

    # 2) Translate to center of mass and apply PCA rotation (for each structure independently)
    A = translate_to_center(A)
    B = translate_to_center(B)
    A = align_principal_axes(A)
    B = align_principal_axes(B)

    # 3) Fine alignment to minimize RMSD by pairing the smaller structure's atoms
    #    with nearest neighbors in the larger structure, then applying Kabsch.
    A, B = fine_align_by_minimizing_rmsd(A, B)

    # 4) Perform the actual crossover. If the user didn’t supply a crossover function,
    #    use a simple single-plane (single-cut) crossover as an example.
    if crossover_func is None:
        crossover_func = single_cut_crossover  # fallback default
    childA, childB = crossover_func(A, B)

    return childA, childB


# ------------------------------------------------------------------
# Step A: Translate a structure so that its center (mean position) is at the origin.
def translate_to_center(container):
    r"""
    Translate a structure so that its centroid lies at the origin.

    Given positions :math:`\{\mathbf{x}_i\}_{i=1}^N`, compute the centroid
    .. math::
       \mathbf{c} = \frac{1}{N}\sum_{i=1}^N \mathbf{x}_i,
       \quad
       \mathbf{x}_i^\text{new} = \mathbf{x}_i - \mathbf{c}.
    This centers the cloud of atoms at the origin.

    :param container: Structure with `.AtomPositionManager.atomPositions`.
    :returns: The same container with updated positions.
    """
    positions = container.AtomPositionManager.atomPositions
    centroid = np.mean(positions, axis=0)
    container.AtomPositionManager.atomPositions = positions - centroid
    return container

# ------------------------------------------------------------------
# Step B: Align a structure's principal axes to the Cartesian axes via PCA.
def align_principal_axes(container):
    r"""
    Rotate a structure so its principal axes align with the Cartesian coordinate axes.

    1. Compute the covariance matrix of centered positions
       .. math::
          \Sigma = \frac{1}{N-1}\sum_{i=1}^N (\mathbf{x}_i - \bar{\mathbf{x}})
                                          (\mathbf{x}_i - \bar{\mathbf{x}})^\top.
    2. Perform eigen-decomposition
       .. math::
          \Sigma \mathbf{v}_j = \lambda_j \mathbf{v}_j,\quad
          V = [\mathbf{v}_1,\mathbf{v}_2,\mathbf{v}_3].
    3. Rotate each position
       .. math::
          \mathbf{x}_i^\prime = V^\top (\mathbf{x}_i - \bar{\mathbf{x}}).
    This aligns the direction of greatest variance with the x-axis, etc.

    :param container: Structure with `.AtomPositionManager.atomPositions`.
    :returns: The same container with rotated positions.
    """
    positions = container.AtomPositionManager.atomPositions

    # Compute covariance
    cov = np.cov(positions, rowvar=False)  # shape (3,3)

    # Eigen-decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort eigenvectors by descending eigenvalue
    sort_idx = np.argsort(eigenvalues)[::-1]
    principal_axes = eigenvectors[:, sort_idx]  # shape (3,3)

    # Rotate positions
    positions_aligned = positions.dot(principal_axes)
    container.AtomPositionManager.atomPositions = positions_aligned
    return container


# ------------------------------------------------------------------
# Step C: Fine alignment to minimize RMSD between the “smaller” structure's atoms
# and a matched subset in the “larger” structure.
def fine_align_by_minimizing_rmsd(containerA, containerB):
    r"""
    Perform fine alignment by minimizing RMSD between two structures.

    - Identify the smaller structure (fewest atoms) and the larger one.
    - Pair each atom :math:`\mathbf{u}_i` in the smaller set with its nearest
      neighbour :math:`\mathbf{v}_i` in the larger.
    - Compute the optimal rotation :math:`R\in SO(3)` and translation
      :math:`\mathbf{t}` solving
      .. math::
         \min_{R,\mathbf{t}}\sum_{i=1}^{m}\bigl\|R\,\mathbf{u}_i + \mathbf{t} - \mathbf{v}_i\bigr\|_2^2,
      using the Kabsch algorithm.

    :param containerA: First structure.
    :param containerB: Second structure.
    :returns: Tuple `(alignedA, alignedB)` with the smaller structure transformed.
    """
    A = copy.deepcopy(containerA)
    B = copy.deepcopy(containerB)
    posA = A.AtomPositionManager.atomPositions
    posB = B.AtomPositionManager.atomPositions

    # Determine which container is smaller
    nA = posA.shape[0]
    nB = posB.shape[0]

    if nA <= nB:
        # A is smaller or equal in size => align A onto B
        matchedA, matchedB = pair_atoms_nearest(posA, posB)
        R, t = kabsch_transform(matchedA, matchedB)
        # Apply to all positions in A
        posA_new = (posA - matchedA.mean(axis=0)).dot(R) + matchedB.mean(axis=0)
        A.AtomPositionManager.atomPositions = posA_new
        return A, B
    else:
        # B is smaller => align B onto A
        matchedB, matchedA = pair_atoms_nearest(posB, posA)
        R, t = kabsch_transform(matchedB, matchedA)
        # Apply to all positions in B
        posB_new = (posB - matchedB.mean(axis=0)).dot(R) + matchedA.mean(axis=0)
        B.AtomPositionManager.atomPositions = posB_new
        return A, B


def pair_atoms_nearest(smallPos, largePos):
    r"""
    Pair each point in `smallPos` with its nearest neighbour in `largePos`.

    For each :math:`\mathbf{u}\in\text{smallPos}`, find
    .. math::
      j^* = \arg\min_j \|\mathbf{u} - \mathbf{v}_j\|_2.
    This yields two arrays of matched coordinates for Kabsch input.

    :param smallPos: :math:`(m,3)` array of points.
    :param largePos: :math:`(n,3)` array of points, with :math:`n\ge m`.
    :returns: Tuple `(matched_small, matched_large)`, each :math:`(m,3)`.
    """
    matched_small = []
    matched_large = []

    for vec in smallPos:
        # Find the index j in largePos that is closest to vec
        diffs = largePos - vec
        dists = np.sum(diffs**2, axis=1)
        jmin = np.argmin(dists)
        matched_small.append(vec)
        matched_large.append(largePos[jmin])

    return np.array(matched_small), np.array(matched_large)


def kabsch_transform(X, Y):
    r"""
    Compute the Kabsch rotation and translation aligning point sets X→Y.

    Given paired sets :math:`X,Y\in\mathbb{R}^{m\times3}`, let centroids
    .. math::
       \bar{X} = \frac{1}{m}\sum_i X_i,\quad
       \bar{Y} = \frac{1}{m}\sum_i Y_i,
       \quad
       X' = X - \bar{X},\; Y' = Y - \bar{Y}.
    Form the covariance
    .. math::
       H = (X')^\top Y',
    perform SVD :math:`H = U\Sigma V^\top`, and set
    .. math::
       R = VU^\top,\quad \mathbf{t} = \bar{Y} - R\,\bar{X}.
    Ensures :math:`R\in SO(3)` (no reflection).

    :param X: :math:`(m,3)` source points.
    :param Y: :math:`(m,3)` target points.
    :returns: Tuple `(R, t)` where `R` is a 3×3 rotation matrix and `t` is a 3-vector.
    """
    # 1) Center is typically subtracted outside this function,
    #    but let's do the standard approach with the data as-is.
    Xc = X.mean(axis=0)
    Yc = Y.mean(axis=0)
    Xp = X - Xc
    Yp = Y - Yc

    # 2) Covariance matrix
    #    H = Xp^T * Yp
    H = Xp.T.dot(Yp)

    # 3) SVD of H
    U, S, Vt = np.linalg.svd(H)

    # 4) Compute rotation
    #    Potential reflection fix if det < 0
    R_ = Vt.T.dot(U.T)
    if np.linalg.det(R_) < 0:
        # Flip the sign of the last row of Vt
        Vt[-1, :] *= -1
        R_ = Vt.T.dot(U.T)

    # 5) Translation
    t_ = Yc - R_.dot(Xc)
    return R_, t_


# ------------------------------------------------------------------
#  ------------          CrossOver functions              ---------
# ------------------------------------------------------------------
def crossover_planes_exchange():
    r"""
    Generate a crossover function that exchanges entire crystallographic planes
    between two parent structures.

    The returned function `func(A, B)` will:
      1. Identify planar “layers” of atoms in each parent along some axis.
      2. Randomly decide, for each plane index \(n\), whether to swap that plane.
      3. Remove swapped atoms from each child and insert the exchanged atoms
         from the other parent.

    Mathematically, if
    \[
      L_A = \{\,\ell_i^A\}_{i=1}^N,\quad
      L_B = \{\,\ell_j^B\}_{j=1}^M
    \]
    are the sets of plane IDs for parents \(A\) and \(B\), then for each plane
    index \(n\) we flip a fair coin and, if heads, perform
    \[
      A' \gets (A \setminus \ell_n^A)\;\cup\;\ell_n^B,\quad
      B' \gets (B \setminus \ell_n^B)\;\cup\;\ell_n^A.
    \]

    :returns: A function `func(A, B) -> (childA, childB)` performing the exchange.
    :rtype: Callable[[Structure, Structure], Tuple[Structure, Structure]]
    """
    def func(containers_A, containers_B):
        """
        Perform crossover between pairs of containers by exchanging layers of atoms.

        Parameters
        ----------
        containers_A, containers_B 

        Returns
        -------
        list
            The modified list of containers after performing crossover.
        """
        
        # Identify planes in container i
        indices_A, plane_ids_A = identify_planes(
            containers_A.AtomPositionManager.atomLabelsList,
            containers_A.AtomPositionManager.atomPositions
        )

        # Identify planes in container j
        indices_B, plane_ids_B = identify_planes(
            containers_B.AtomPositionManager.atomLabelsList,
            containers_B.AtomPositionManager.atomPositions
        )

        max_planes_A = np.max(plane_ids_A) + 1
        max_planes_B = np.max(plane_ids_B) + 1
        max_planes = max(max_planes_A, max_planes_B)

        # Sort planes by mean y-coordinate (example approach)
        layer_order_index_A = []
        layer_order_index_B = []
        for n in range(max_planes_A):
            coords_plane = containers_A.AtomPositionManager.atomPositions[indices_A[plane_ids_A == n]]
            layer_order_index_A.append(np.mean(coords_plane[:, 1]) if len(coords_plane) > 0 else float('inf'))

        for n in range(max_planes_B):
            coords_plane = containers_B.AtomPositionManager.atomPositions[indices_B[plane_ids_B == n]]
            layer_order_index_B.append(np.mean(coords_plane[:, 1]) if len(coords_plane) > 0 else float('inf'))

        as_A = np.argsort(layer_order_index_A)
        as_B = np.argsort(layer_order_index_B)

        exchanged_layers = 0
        remove_index_store_A = []
        remove_index_store_B = []
        atom_position_store_A = np.empty((0, 3))
        atom_position_store_B = np.empty((0, 3))
        atom_label_store_A = []
        atom_label_store_B = []

        for n in range(max_planes):
            if n < max_planes_A and n < max_planes_B:
                # Randomly decide whether to swap plane n
                if np.random.randint(2) == 1:
                    selA = indices_A[plane_ids_A == as_A[n]]
                    selB = indices_B[plane_ids_B == as_B[n]]

                    coordsA = containers_A.AtomPositionManager.atomPositions[selA]
                    coordsB = containers_B.AtomPositionManager.atomPositions[selB]
                    labelsA = containers_A.AtomPositionManager.atomLabelsList[selA]
                    labelsB = containers_B.AtomPositionManager.atomLabelsList[selB]

                    remove_index_store_A = np.concatenate((remove_index_store_A, selA))
                    remove_index_store_B = np.concatenate((remove_index_store_B, selB))

                    atom_position_store_A = np.concatenate((atom_position_store_A, coordsB), axis=0)
                    atom_position_store_B = np.concatenate((atom_position_store_B, coordsA), axis=0)

                    atom_label_store_A = np.concatenate((atom_label_store_A, labelsB))
                    atom_label_store_B = np.concatenate((atom_label_store_B, labelsA))
                    exchanged_layers += 1

        # Ensure at least one layer is exchanged
        if exchanged_layers == 0 and max_planes_A > 0 and max_planes_B > 0:
            n = np.random.randint(min(max_planes_A, max_planes_B))
            selA = indices_A[plane_ids_A == as_A[n]]
            selB = indices_B[plane_ids_B == as_B[n]]
            coordsA = containers_A.AtomPositionManager.atomPositions[selA]
            coordsB = containers_B.AtomPositionManager.atomPositions[selB]
            labelsA = containers_A.AtomPositionManager.atomLabelsList[selA]
            labelsB = containers_B.AtomPositionManager.atomLabelsList[selB]

            remove_index_store_A = np.concatenate((remove_index_store_A, selA))
            remove_index_store_B = np.concatenate((remove_index_store_B, selB))

            atom_position_store_A = np.concatenate((atom_position_store_A, coordsB), axis=0)
            atom_position_store_B = np.concatenate((atom_position_store_B, coordsA), axis=0)

            atom_label_store_A = np.concatenate((atom_label_store_A, labelsB))
            atom_label_store_B = np.concatenate((atom_label_store_B, labelsA))

        # Remove old atoms and add the swapped ones
        containers_A.AtomPositionManager.remove_atom(remove_index_store_A)
        containers_B.AtomPositionManager.remove_atom(remove_index_store_B)

        containers_A.AtomPositionManager.add_atom(atomLabels=atom_label_store_A,
                                                   atomPosition=atom_position_store_A)
        containers_B.AtomPositionManager.add_atom(atomLabels=atom_label_store_B,
                                                   atomPosition=atom_position_store_B)

        return containers_A, containers_B

    return func

# Example: Single-plane (single-cut) crossover
def crossover_single_cut(containerA, containerB):
    r"""
    Perform a single‐plane cut crossover along a random Cartesian axis.

    Procedure:
      1. Choose axis \(d\in\{0,1,2\}\).
      2. Compute
         \[
           \min_d = \min(\min A_d, \min B_d),\quad
           \max_d = \max(\max A_d, \max B_d).
         \]
      3. Sample cut position
         \(
           c \sim \mathcal{U}(\min_d, \max_d).
         \)
      4. Define masks
         \[
           M_A^- = \{i: x_{i,d} \le c\},\quad M_A^+ = \{i: x_{i,d} > c\},
         \]
         similarly for \(B\).
      5. Child A inherits \(A\) below the cut plus \(B\) above:
         \[
           A' = A[M_A^-]\;\cup\;B[\neg M_B^-],
         \]
         and child B inherits the complement.

    :param containerA: Parent structure \(A\).
    :param containerB: Parent structure \(B\).
    :returns: Tuple `(childA, childB)` with atoms recombined.
    :rtype: Tuple[Structure, Structure]
    """
    import copy
    # Copy the parents
    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # 1) Choose random axis
    axis = np.random.choice([0, 1, 2])

    # 2) Determine global min/max along this axis (so the cut is guaranteed within range)
    min_coord = min(posA[:, axis].min(), posB[:, axis].min())
    max_coord = max(posA[:, axis].max(), posB[:, axis].max())

    # 3) Pick a random cut position
    cut_position = np.random.uniform(min_coord, max_coord)

    # 4) Identify “below” and “above” for each parent
    maskA_below = posA[:, axis] <= cut_position
    maskB_below = posB[:, axis] <= cut_position

    # 5) Remove old atoms in children
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # 6) Reconstruct childA
    # A below + B above
    new_positions_A = np.concatenate([posA[maskA_below], posB[~maskB_below]])
    new_labels_A = np.concatenate([labelsA[maskA_below], labelsB[~maskB_below]])
    childA.AtomPositionManager.add_atom(atomLabels=new_labels_A, atomPosition=new_positions_A)

    # 7) Reconstruct childB
    # B below + A above
    new_positions_B = np.concatenate([posB[maskB_below], posA[~maskA_below]])
    new_labels_B = np.concatenate([labelsB[maskB_below], labelsA[~maskA_below]])
    childB.AtomPositionManager.add_atom(atomLabels=new_labels_B, atomPosition=new_positions_B)

    return childA, childB

def crossover_two_cut(containerA, containerB):
    r"""
    Perform a two‐plane cut crossover along a random axis.

    1. Choose axis \(d\) and two sorted cut positions \(c_1<c_2\) in that dimension.
    2. Define regions:
       \[
         R^- = \{x_d < c_1\},\quad
         R^0 = \{c_1 \le x_d \le c_2\},\quad
         R^+ = \{x_d > c_2\}.
       \]
    3. Child A inherits \(A\) in \(R^-\cup R^+\) and \(B\) in \(R^0\);
       child B does the opposite.

    :param containerA: Parent structure \(A\).
    :param containerB: Parent structure \(B\).
    :returns: Tuple `(childA, childB)` after recombination.
    :rtype: Tuple[Structure, Structure]
    """
    import copy
    import numpy as np

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Pick an axis
    axis = np.random.choice([0, 1, 2])

    # Choose two cut positions along that axis
    min_coord = min(posA[:, axis].min(), posB[:, axis].min())
    max_coord = max(posA[:, axis].max(), posB[:, axis].max())
    cut1, cut2 = np.sort(np.random.uniform(min_coord, max_coord, size=2))

    # Identify below, middle, above for parent A
    belowA = posA[:, axis] < cut1
    middleA = (posA[:, axis] >= cut1) & (posA[:, axis] <= cut2)
    aboveA = posA[:, axis] > cut2

    # Identify below, middle, above for parent B
    belowB = posB[:, axis] < cut1
    middleB = (posB[:, axis] >= cut1) & (posB[:, axis] <= cut2)
    aboveB = posB[:, axis] > cut2

    # Remove old atoms in children
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # childA = A(below + above) + B(middle)
    newA_positions = np.concatenate([posA[belowA], posA[aboveA], posB[middleB]])
    newA_labels = np.concatenate([labelsA[belowA], labelsA[aboveA], labelsB[middleB]])
    childA.AtomPositionManager.add_atom(atomLabels=newA_labels, atomPosition=newA_positions)

    # childB = B(below + above) + A(middle)
    newB_positions = np.concatenate([posB[belowB], posB[aboveB], posA[middleA]])
    newB_labels = np.concatenate([labelsB[belowB], labelsB[aboveB], labelsA[middleA]])
    childB.AtomPositionManager.add_atom(atomLabels=newB_labels, atomPosition=newB_positions)

    return childA, childB


def crossover_spherical(containerA, containerB):
    r"""
    Perform a spherical‐region crossover.

    1. Sample a random center \(\mathbf{c}\) within the bounding box of \(A\cup B\).
    2. Choose radius \(r\) uniformly up to half the diagonal:
       \[
         r \sim \mathcal{U}\bigl(0,\,\tfrac12\|\max\!-\!\min\|_2\bigr).
       \]
    3. Define inside‐sphere masks
       \[
         I_A = \{\|\mathbf{x}_i^A - \mathbf{c}\| \le r\},\quad
         I_B = \{\|\mathbf{x}_j^B - \mathbf{c}\| \le r\}.
       \]
    4. Child A = \(A[I_A]\cup B[\neg I_B]\), Child B = \(B[I_B]\cup A[\neg I_A]\).

    :param containerA: Parent structure \(A\).
    :param containerB: Parent structure \(B\).
    :returns: Tuple `(childA, childB)` after spherical exchange.
    :rtype: Tuple[Structure, Structure]
    """
    import copy
    import numpy as np

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Random sphere center from extremes of both parents
    all_pos = np.vstack([posA, posB])
    mins = all_pos.min(axis=0)
    maxs = all_pos.max(axis=0)
    center = np.array([
        np.random.uniform(mins[0], maxs[0]),
        np.random.uniform(mins[1], maxs[1]),
        np.random.uniform(mins[2], maxs[2])
    ])

    # Random radius in a range (e.g., 1/4 of bounding box diagonal)
    diag = np.linalg.norm(maxs - mins)
    radius = np.random.uniform(0.0, 0.5 * diag)

    # Distances of each atom from the center
    distA = np.linalg.norm(posA - center, axis=1)
    distB = np.linalg.norm(posB - center, axis=1)

    insideA = distA < radius
    insideB = distB < radius

    # Remove old
    childA.AtomPositionManager.remove_atom(np.arange(posA.shape[0]))
    childB.AtomPositionManager.remove_atom(np.arange(posB.shape[0]))

    # ChildA = A-inside + B-outside
    newA_positions = np.concatenate([posA[insideA], posB[~insideB]])
    newA_labels = np.concatenate([labelsA[insideA], labelsB[~insideB]])
    childA.AtomPositionManager.add_atom(atomLabels=newA_labels, atomPosition=newA_positions)

    # ChildB = B-inside + A-outside
    newB_positions = np.concatenate([posB[insideB], posA[~insideA]])
    newB_labels = np.concatenate([labelsB[insideB], labelsA[~insideA]])
    childB.AtomPositionManager.add_atom(atomLabels=newB_labels, atomPosition=newB_positions)

    return childA, childB


def crossover_uniform_atom_level(containerA, containerB):
    r"""
    Perform per‐atom uniform crossover.

    Assumes both parents have the same atom count \(N\).
    For each index \(i=1,\dots,N\), with probability \(p=0.5\) swap atoms:
    \[
      A'_i = \begin{cases}B_i,&U_i<0.5\\A_i,&\text{otherwise}\end{cases},\quad
      B'_i = \begin{cases}A_i,&U_i<0.5\\B_i,&\text{otherwise}\end{cases},
    \]
    where \(U_i\sim\mathcal{U}(0,1)\).

    :param containerA: Parent structure \(A\).
    :param containerB: Parent structure \(B\).
    :returns: Tuple `(childA, childB)` after per‐atom swapping.
    :rtype: Tuple[Structure, Structure]
    """
    import copy
    import numpy as np

    # If parents differ in number of atoms, adapt accordingly
    nA = containerA.AtomPositionManager.atomPositions.shape[0]
    nB = containerB.AtomPositionManager.atomPositions.shape[0]
    if nA != nB:
        raise ValueError("Parents must have the same number of atoms for uniform crossover!")

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Remove existing atoms
    childA.AtomPositionManager.remove_atom(np.arange(nA))
    childB.AtomPositionManager.remove_atom(np.arange(nB))

    # Build lists for the children
    new_positions_A = []
    new_labels_A = []
    new_positions_B = []
    new_labels_B = []

    for i in range(nA):
        if np.random.rand() < 0.5:
            # childA inherits A[i], childB inherits B[i]
            new_positions_A.append(posA[i])
            new_labels_A.append(labelsA[i])
            new_positions_B.append(posB[i])
            new_labels_B.append(labelsB[i])
        else:
            # childA inherits B[i], childB inherits A[i]
            new_positions_A.append(posB[i])
            new_labels_A.append(labelsB[i])
            new_positions_B.append(posA[i])
            new_labels_B.append(labelsA[i])

    # Convert to arrays
    new_positions_A = np.array(new_positions_A)
    new_labels_A = np.array(new_labels_A)
    new_positions_B = np.array(new_positions_B)
    new_labels_B = np.array(new_labels_B)

    childA.AtomPositionManager.add_atom(atomLabels=new_labels_A, atomPosition=new_positions_A)
    childB.AtomPositionManager.add_atom(atomLabels=new_labels_B, atomPosition=new_positions_B)

    return childA, childB


def crossover_species_proportion(containerA, containerB, proportions=None):
    r"""
    Perform species‐fraction crossover.

    For each chemical species \(s\), let \(n^A_s,n^B_s\) be the counts
    in \(A,B\). Choose fraction \(0\le p_s\le1\). Then child A receives
    \(\lfloor p_s\,n^A_s\rfloor\) atoms of species \(s\) from \(A\) and
    \(\lfloor p_s\,(n^A_s + n^B_s)\rfloor - \lfloor p_s\,n^A_s\rfloor\)
    from \(B\). Child B receives the complementary atoms.

    :param containerA: Parent structure \(A\).
    :param containerB: Parent structure \(B\).
    :param proportions: Mapping \(\{s\mapsto p_s\}\). Defaults to \(p_s=0.5\).
    :returns: Tuple `(childA, childB)` after species‐based mixing.
    :rtype: Tuple[Structure, Structure]
    """
    import copy
    import numpy as np

    if proportions is None:
        proportions = {}  # default: 0.5 each species

    childA = copy.deepcopy(containerA)
    childB = copy.deepcopy(containerB)

    posA = containerA.AtomPositionManager.atomPositions
    posB = containerB.AtomPositionManager.atomPositions
    labelsA = containerA.AtomPositionManager.atomLabelsList
    labelsB = containerB.AtomPositionManager.atomLabelsList

    # Combine all species from both parents to ensure we handle everything
    all_species = set(labelsA).union(set(labelsB))

    # We will collect positions/labels for each child in lists, then remove+add
    new_posA = []
    new_labA = []
    new_posB = []
    new_labB = []

    # Remove old
    childA.AtomPositionManager.remove_atom(np.arange(len(labelsA)))
    childB.AtomPositionManager.remove_atom(np.arange(len(labelsB)))

    for sp in all_species:
        p = proportions.get(sp, 0.5)

        # Indices of species sp in parent A
        idxA = np.where(labelsA == sp)[0]
        # Indices of species sp in parent B
        idxB = np.where(labelsB == sp)[0]

        # Shuffle them so we pick random subsets
        np.random.shuffle(idxA)
        np.random.shuffle(idxB)

        # Number from parent A to child A
        nA_to_A = int(np.floor(p * len(idxA)))
        # Number from parent B to child A
        # We want to keep childA's total count for sp = (some fraction) * (lenA + lenB)
        # but a simpler approach is: childA takes nA_to_A from A, plus some fraction from B.
        total_sp = len(idxA) + len(idxB)
        # overall fraction for sp: 
        total_A_need = int(np.floor(p * total_sp))
        # so from B, we want total_A_need - nA_to_A 
        nB_to_A = max(0, total_A_need - nA_to_A)

        # The rest go to childB
        # from A => len(idxA) - nA_to_A
        # from B => len(idxB) - nB_to_A

        # Take these atoms from A to childA
        a_selA = idxA[:nA_to_A]
        # Take these atoms from B to childA
        b_selA = idxB[:nB_to_A]

        # The leftover
        a_selB = idxA[nA_to_A:]
        b_selB = idxB[nB_to_A:]

        # Add to new arrays
        new_posA.append(posA[a_selA])
        new_labA.append(labelsA[a_selA])
        new_posA.append(posB[b_selA])
        new_labA.append(labelsB[b_selA])

        new_posB.append(posA[a_selB])
        new_labB.append(labelsA[a_selB])
        new_posB.append(posB[b_selB])
        new_labB.append(labelsB[b_selB])

    # Concatenate
    new_posA = np.concatenate(new_posA) if len(new_posA) else np.zeros((0,3))
    new_labA = np.concatenate(new_labA) if len(new_labA) else np.array([])
    new_posB = np.concatenate(new_posB) if len(new_posB) else np.zeros((0,3))
    new_labB = np.concatenate(new_labB) if len(new_labB) else np.array([])

    # Now add them
    childA.AtomPositionManager.add_atom(atomLabels=new_labA, atomPosition=new_posA)
    childB.AtomPositionManager.add_atom(atomLabels=new_labB, atomPosition=new_posB)

    return childA, childB

def validate_crossover(structureA, structureB, constraints: list, logic: str = "all"):
    """
    Example of a "pairwise" validation approach. This function
    can be adapted to check constraints that depend on both
    structureA and structureB simultaneously.

    Parameters
    ----------
    structureA : object
        First parent structure.
    structureB : object
        Second parent structure.
    constraints : list
        List of callable constraints to check.
    logic : str, optional
        "all" or "any", controlling how constraints are combined.

    Returns
    -------
    bool
        True if constraints pass, False otherwise.
    """
    if not constraints:
        return True

    # Ejemplo mínimo: asumiendo constraints del estilo constraint(structureA, structureB)
    if logic == "all":
        return all(constraint(structureA, structureB) for constraint in constraints)
    elif logic == "any":
        return any(constraint(structureA, structureB) for constraint in constraints)
    return False


# -----------------------------------------------------------------------------
# 1) Single-Point Crossover
# -----------------------------------------------------------------------------
def crossover_one_point(structureA, structureB, constraints=None):
    """
    Perform a 'single-point' crossover by splitting the array of atoms in each
    parent structure at the same index, and swapping the segments to produce
    two children.

    Parameters
    ----------
    structureA : object
        First parent structure (must have AtomPositionManager with lists/arrays).
    structureB : object
        Second parent structure (must have AtomPositionManager with lists/arrays).
    constraints : list, optional
        Optional constraints to validate. If validation fails, returns (None, None).

    Returns
    -------
    (childA, childB) : tuple
        Two new structures. If an error or invalid condition arises, returns (None, None).
    """
    # Optional: check constraints at the pair level
    if constraints and not validate_crossover(structureA, structureB, constraints):
        return None, None

    # 1) Deepcopy the parents
    childA = copy.deepcopy(structureA)
    childB = copy.deepcopy(structureB)

    # 2) We require that both parents have the same number of atoms for a direct index-based crossover.
    nA = len(childA.AtomPositionManager.atomLabelsList)
    nB = len(childB.AtomPositionManager.atomLabelsList)
    if nA != nB or nA == 0:
        # We can't do single-point crossover if the structures differ in size or are empty.
        return None, None

    # 3) Choose a random index for the crossover 'cut'
    cut_index = random.randint(1, nA - 1)

    # 4) Swap all atoms from 'cut_index' to end
    #    in childA with those in childB
    labelsA = childA.AtomPositionManager.atomLabelsList
    labelsB = childB.AtomPositionManager.atomLabelsList
    coordsA = childA.AtomPositionManager.atomPositions
    coordsB = childB.AtomPositionManager.atomPositions

    # Segment swap
    labelsA[cut_index:], labelsB[cut_index:] = labelsB[cut_index:].copy(), labelsA[cut_index:].copy()
    coordsA[cut_index:], coordsB[cut_index:] = coordsB[cut_index:].copy(), coordsA[cut_index:].copy()

    return childA, childB


# -----------------------------------------------------------------------------
# 2) Uniform Crossover
# -----------------------------------------------------------------------------
def crossover_uniform(structureA, structureB, constraints=None, swap_probability=0.5):
    """
    Perform a 'uniform' crossover by iterating over each atom index
    and randomly deciding whether to swap or not.

    Parameters
    ----------
    structureA : object
        First parent structure.
    structureB : object
        Second parent structure.
    constraints : list, optional
        Optional constraints to validate. If validation fails, returns (None, None).
    swap_probability : float, optional
        Probability of swapping an atom between the two parents
        (default=0.5 means ~50% chance to swap each atom).

    Returns
    -------
    (childA, childB) : tuple
        Two new structures or (None, None) if not feasible.
    """
    if constraints and not validate_crossover(structureA, structureB, constraints):
        return None, None

    childA = copy.deepcopy(structureA)
    childB = copy.deepcopy(structureB)

    nA = len(childA.AtomPositionManager.atomLabelsList)
    nB = len(childB.AtomPositionManager.atomLabelsList)

    # For uniform crossover, we again need matching numbers of atoms
    if nA != nB or nA == 0:
        return None, None

    labelsA = childA.AtomPositionManager.atomLabelsList
    labelsB = childB.AtomPositionManager.atomLabelsList
    coordsA = childA.AtomPositionManager.atomPositions
    coordsB = childB.AtomPositionManager.atomPositions

    for i in range(nA):
        # Decide randomly if we swap index i
        if random.random() < swap_probability:
            labelsA[i], labelsB[i] = labelsB[i], labelsA[i]
            coordsA[i], coordsB[i] = coordsB[i].copy(), coordsA[i].copy()

    return childA, childB


# -----------------------------------------------------------------------------
# 3) Random-Atom Exchange
# -----------------------------------------------------------------------------
def crossover_random_atom_exchange(structureA, structureB, constraints=None, fraction=0.3):
    """
    Randomly pick a subset of atoms from each parent and exchange them.

    Parameters
    ----------
    structureA : object
        First parent structure.
    structureB : object
        Second parent structure.
    constraints : list, optional
        Optional constraints to validate. If validation fails, returns (None, None).
    fraction : float, optional
        Fraction of total atoms to exchange (default=0.3). Must be between 0 and 1.

    Returns
    -------
    (childA, childB) : tuple
        Two new structures or (None, None) if not feasible.
    """
    if constraints and not validate_crossover(structureA, structureB, constraints):
        return None, None

    childA = copy.deepcopy(structureA)
    childB = copy.deepcopy(structureB)

    nA = len(childA.AtomPositionManager.atomLabelsList)
    nB = len(childB.AtomPositionManager.atomLabelsList)
    if nA != nB or nA == 0:
        return None, None

    labelsA = childA.AtomPositionManager.atomLabelsList
    labelsB = childB.AtomPositionManager.atomLabelsList
    coordsA = childA.AtomPositionManager.atomPositions
    coordsB = childB.AtomPositionManager.atomPositions

    # Number of atoms to exchange
    k = int(fraction * nA)
    if k <= 0:
        return childA, childB

    # Choose k random indices from [0..nA-1]
    idx_to_swap = random.sample(range(nA), k)

    for i in idx_to_swap:
        labelsA[i], labelsB[i] = labelsB[i], labelsA[i]
        coordsA[i], coordsB[i] = coordsB[i].copy(), coordsA[i].copy()

    return childA, childB


# -----------------------------------------------------------------------------
# 4) Fractional Mixing (Position Interpolation) 
# -----------------------------------------------------------------------------
def crossover_fractional_mixing(structureA, structureB, alpha=0.5, constraints=None):
    """
    Create children by linearly interpolating atomic positions
    while preserving the atomic labels. This can be useful if
    the structures are identical in the number/order of atoms
    but slightly different in geometry.

    childA = alpha * coordsA + (1-alpha) * coordsB
    childB = alpha * coordsB + (1-alpha) * coordsA

    Parameters
    ----------
    structureA : object
        First parent structure.
    structureB : object
        Second parent structure.
    alpha : float, optional
        Fraction that controls the interpolation. Defaults to 0.5
        (i.e. halfway between the two positions).
    constraints : list, optional
        Optional constraints to validate. If validation fails, returns (None, None).

    Returns
    -------
    (childA, childB) : tuple
        Two new structures or (None, None) if mismatch or failure.
    """
    if constraints and not validate_crossover(structureA, structureB, constraints):
        return None, None

    childA = copy.deepcopy(structureA)
    childB = copy.deepcopy(structureB)

    nA = len(childA.AtomPositionManager.atomLabelsList)
    nB = len(childB.AtomPositionManager.atomLabelsList)
    if nA != nB or nA == 0:
        return None, None

    # Interpolate positions
    coordsA = childA.AtomPositionManager.atomPositions
    coordsB = childB.AtomPositionManager.atomPositions

    # childA is a blend of A and B
    coordsA_new = alpha * coordsA + (1.0 - alpha) * coordsB
    # childB is the complementary blend
    coordsB_new = alpha * coordsB + (1.0 - alpha) * coordsA

    # Assign back
    childA.AtomPositionManager.atomPositions = coordsA_new
    childB.AtomPositionManager.atomPositions = coordsB_new

    return childA, childB


# -----------------------------------------------------------------------------
# EJEMPLO de una constraint que podrías usar:
# (Para que sirva como referencia en el caso "validate_crossover")
# -----------------------------------------------------------------------------
def constraint_check_same_size(structA, structB):
    r"""
    Example constraint: ensure both parents have the same atom count.

    :returns: `True` if \(\#A=\#B\).
    """
    return (
        len(structA.AtomPositionManager.atomLabelsList)
        == len(structB.AtomPositionManager.atomLabelsList)
    )

# ---------------------------------------------------------------
# 0.  Helper: tag atoms by geometric "layer" along the surface
# ---------------------------------------------------------------
def _layer_index(z_coords, layer_thickness=1.2):
    r"""
    Assign integer layer IDs by sorting \(z\)-coordinates and
    incrementing when gap \(>\) `layer_thickness`.

    :param z_coords: Array of shape \((N,)\).
    :param layer_thickness: Max gap within a layer.
    :returns: Integer array of layer IDs.
    """
    order = np.argsort(z_coords)
    layers = np.zeros_like(z_coords, dtype=int)
    current_layer = 0
    last_z = z_coords[order[0]]
    for idx in order:
        if z_coords[idx] - last_z > layer_thickness:
            current_layer += 1
        layers[idx] = current_layer
        last_z = z_coords[idx]
    return layers


# ---------------------------------------------------------------
# 1.  Top-Layer Swap
# ---------------------------------------------------------------
def crossover_top_layer_swap(structA, structB, n_layers=1, constraints=None):
    r"""
    Swap the top \(n\) atomic layers of two slabs.

    Let \(\ell_{\max}\) be the highest layer index. Define
    \(\mathrm{mask}_A = \{\ell_i^A\ge\ell_{\max}-(n-1)\}\).
    Exchange those atoms between \(A\) and \(B\).

    :param n_layers: Number of top layers to swap.
    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)

    zA = childA.AtomPositionManager.atomPositions[:, 2]
    zB = childB.AtomPositionManager.atomPositions[:, 2]
    layA = _layer_index(zA)
    layB = _layer_index(zB)

    selA = np.where(layA >= layA.max() - (n_layers - 1))[0]
    selB = np.where(layB >= layB.max() - (n_layers - 1))[0]

    # store and remove
    posA, labA = (childA.AtomPositionManager.atomPositions[selA],
                  childA.AtomPositionManager.atomLabelsList[selA])
    posB, labB = (childB.AtomPositionManager.atomPositions[selB],
                  childB.AtomPositionManager.atomLabelsList[selB])

    childA.AtomPositionManager.remove_atom(selA)
    childB.AtomPositionManager.remove_atom(selB)

    childA.AtomPositionManager.add_atom(atomLabels=labB, atomPosition=posB)
    childB.AtomPositionManager.add_atom(atomLabels=labA, atomPosition=posA)

    return childA, childB


# ---------------------------------------------------------------
# 2.  Terrace-Width Interchange
# ---------------------------------------------------------------
def crossover_terrace_interchange(structA, structB, terrace_height=2.5, constraints=None):
    """
    Cut each parent at a random z equal to an integer multiple of
    'terrace_height' and swap the upper parts.  Preserves registry
    of deep layers while perturbing the outer terrace morphology.
    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)
    zA = childA.AtomPositionManager.atomPositions[:, 2]
    zB = childB.AtomPositionManager.atomPositions[:, 2]

    zmin = min(zA.min(), zB.min())
    zmax = max(zA.max(), zB.max())
    n_steps = int((zmax - zmin) / terrace_height)
    if n_steps < 1:
        return None, None

    step = random.randint(1, n_steps)  # at least one full terrace
    z_cut = zmin + step * terrace_height

    maskA_up = zA >= z_cut
    maskB_up = zB >= z_cut

    posA, labA = (childA.AtomPositionManager.atomPositions[maskA_up],
                  childA.AtomPositionManager.atomLabelsList[maskA_up])
    posB, labB = (childB.AtomPositionManager.atomPositions[maskB_up],
                  childB.AtomPositionManager.atomLabelsList[maskB_up])

    childA.AtomPositionManager.remove_atom(np.where(maskA_up)[0])
    childB.AtomPositionManager.remove_atom(np.where(maskB_up)[0])

    childA.AtomPositionManager.add_atom(atomLabels=labB, atomPosition=posB)
    childB.AtomPositionManager.add_atom(atomLabels=labA, atomPosition=posA)

    return childA, childB


# ---------------------------------------------------------------
# 3.  Surface-Normal Rotation Merge
# ---------------------------------------------------------------
def crossover_surface_rotation(structA, structB, angle_max=60.0, constraints=None):
    r"""
    Rotate the top half‐slab about surface normal by random angle
    \(\theta\in[-\theta_{\max},+\theta_{\max}]\).

    1. Split at mid‐\(z\): \(\{z\ge \tfrac{z_{\min}+z_{\max}}2\}\).
    2. Rotate upper by \(\mathbf{R}(\theta)\) in \(xy\)‐plane.
    3. Exchange rotated regions.

    :param angle_max: Max rotation in degrees.
    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    deg2rad = np.pi / 180.0
    θ = random.uniform(-angle_max, angle_max) * deg2rad

    def _split_and_rotate(parent, θ):
        pos = parent.AtomPositionManager.atomPositions
        z = pos[:, 2]
        z_mid = (z.min() + z.max()) / 2
        upper = z >= z_mid
        R = np.array([[np.cos(θ), -np.sin(θ), 0.0],
                      [np.sin(θ),  np.cos(θ), 0.0],
                      [0.0,        0.0,       1.0]])
        rotated = pos[upper].dot(R.T)
        return upper, rotated

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)
    maskA, rotA = _split_and_rotate(childA, θ)
    maskB, rotB = _split_and_rotate(childB, -θ)

    labsA = childA.AtomPositionManager.atomLabelsList[maskA]
    labsB = childB.AtomPositionManager.atomLabelsList[maskB]

    childA.AtomPositionManager.remove_atom(np.where(maskA)[0])
    childB.AtomPositionManager.remove_atom(np.where(maskB)[0])

    childA.AtomPositionManager.add_atom(atomLabels=labsB, atomPosition=rotB)
    childB.AtomPositionManager.add_atom(atomLabels=labsA, atomPosition=rotA)

    return childA, childB


# ---------------------------------------------------------------
# 4.  Adsorbate-Only Swap
# ---------------------------------------------------------------
def crossover_adsorbate_swap(structA, structB, adsorbate_set, constraints=None):
    r"""
    Swap only atoms whose labels lie in `adsorbate_set`.

    Keep slab backbone fixed; exchange adsorbate subsets.

    :param adsorbate_set: e.g. \{\('H','O','CO'\)\}.
    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)

    labA = childA.AtomPositionManager.atomLabelsList
    labB = childB.AtomPositionManager.atomLabelsList

    selA = np.isin(labA, list(adsorbate_set))
    selB = np.isin(labB, list(adsorbate_set))

    posA, labA_sel = (childA.AtomPositionManager.atomPositions[selA],
                      labA[selA])
    posB, labB_sel = (childB.AtomPositionManager.atomPositions[selB],
                      labB[selB])

    childA.AtomPositionManager.remove_atom(np.where(selA)[0])
    childB.AtomPositionManager.remove_atom(np.where(selB)[0])

    childA.AtomPositionManager.add_atom(atomLabels=labB_sel, atomPosition=posB)
    childB.AtomPositionManager.add_atom(atomLabels=labA_sel, atomPosition=posA)

    return childA, childB


# ---------------------------------------------------------------
# 5.  Vacancy-Insertion Exchange
# ---------------------------------------------------------------
def crossover_surface_vacancies(structA, structB, vac_prob=0.3, constraints=None):
    r"""
    Creates complementary surface vacancies: with probability \(p\)
    'vac_prob' an atom present in parent A's top layer is *removed*
    in childA and *duplicated* in childB, and vice versa.  Emulates
    Schwoebel-type point-defect cross breeding.

    For each top‐layer atom, with chance \(p\) remove it in one child
    and insert it into the other.

    :param vac_prob: Vacancy probability.


    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)

    for child in (childA, childB):
        z = child.AtomPositionManager.atomPositions[:, 2]
        lay = _layer_index(z)
        top = lay == lay.max()
        if not np.any(top):
            continue
        idx_top = np.where(top)[0]
        to_vacate = [i for i in idx_top if random.random() < vac_prob]
        # save copies before deleting
        pos_vac = child.AtomPositionManager.atomPositions[to_vacate]
        lab_vac = child.AtomPositionManager.atomLabelsList[to_vacate]
        child.AtomPositionManager.remove_atom(to_vacate)
        # store for opposite child via closure
        if child is childA:
            vacA_pos, vacA_lab = pos_vac, lab_vac
        else:
            vacB_pos, vacB_lab = pos_vac, lab_vac

    # add vacancies to opposite children
    if len(vacA_pos):
        childB.AtomPositionManager.add_atom(atomLabels=vacA_lab,
                                            atomPosition=vacA_pos)
    if len(vacB_pos):
        childA.AtomPositionManager.add_atom(atomLabels=vacB_lab,
                                            atomPosition=vacB_pos)

    return childA, childB


# ---------------------------------------------------------------
# 6.  In-Plane Shuffle-and-Relax
# ---------------------------------------------------------------
def crossover_inplane_shuffle(structA, structB, shuffle_sigma=0.35, top_n_layers=2, constraints=None):
    r"""
    Apply a small 2D Gaussian shuffle to the top \(n\) layers:

    \[
      \Delta x,y \sim \mathcal{N}(0,\sigma^2),
      \quad
      \text{only for atoms with layer}\ge\ell_{\max}-(n-1).
    \]

    :param shuffle_sigma: Std dev of Gaussian.
    :param top_n_layers: Number of top layers.
    """
    if constraints and not validate_crossover(structA, structB, constraints):
        return None, None

    def _shuffle(parent, sign):
        z = parent.AtomPositionManager.atomPositions[:, 2]
        lay = _layer_index(z)
        mask = lay >= lay.max() - (top_n_layers - 1)
        delta = np.zeros_like(parent.AtomPositionManager.atomPositions)
        delta[mask, :2] = sign * np.random.normal(0.0, shuffle_sigma,
                                                  size=(mask.sum(), 2))
        return parent.AtomPositionManager.atomPositions + delta

    childA, childB = copy.deepcopy(structA), copy.deepcopy(structB)
    childA.AtomPositionManager.atomPositions = _shuffle(childA, +1)
    childB.AtomPositionManager.atomPositions = _shuffle(childB, -1)
    return childA, childB
