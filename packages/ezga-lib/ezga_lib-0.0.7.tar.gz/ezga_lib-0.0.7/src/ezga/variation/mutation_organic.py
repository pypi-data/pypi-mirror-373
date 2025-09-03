
# ============================================================
#  Molecular-graph based torsion mutations for organics
#  (distance-derived bonds, ring-aware rotors, dihedral set/jitter)
# ============================================================
import math
import numpy as np

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
    labels_focus             = None,
    indices_focus            = None,
    require_mode             = 'any',          # 'any' | 'central'
    side                     = 'k',            # 'k' | 'j' | 'l_only'
    angle                    = None,
    angle_range              = (-120.0, 120.0),# wider range → easier to escape RDF bins
    degrees                  = True,
    radius_scale             = 1.15,
    cutoff_max               = None,
    pbc                      = True,
    wrap_after               = True,
    collision_tolerance      = 1.00,
    max_attempts             = 12,
    constraints              = [],
    seed                     = None,
    verbose                  = False,
    # bias controls
    allowed_central_pairs    = None,
    forbidden_central_pairs  = None,
    exclude_end_labels       = {'H'},
    min_degree_end           = 2,
    sample_mode              = 'weighted',
    w_heavy_end              = 4.0,
    w_backbone_pair          = 6.0,
    w_default                = 1.0,
    # --- new robustness knobs ---
    ensure_change            = True,           # enforce effective change
    min_dihedral_delta_deg   = 10.0,           # minimum |Δφ| (deg)
    min_rmsd_moved           = 1e-3,           # Å; RMSD on moved subgraph
    relax_if_empty           = True            # progressively relax filters if no candidates
):
    r"""
    Create a mutation operator that **auto-discovers and rotates dihedral angles**
    based on element-aware connectivity, with robust handling of molecular (no cell)
    and periodic (PBC) systems.

    The factory returns a callable ``func(structure)`` that:

    1) builds a covalent neighbor graph from coordinates (PBC minimum-image when a
       valid 3×3 lattice is available),
    2) enumerates all torsions ``(i, j, k, l)`` with edges ``i–j``, ``j–k``, ``k–l``,
    3) filters candidates using label/index focus and additional chemistry-aware
       criteria (e.g., central bond element pairs, exclusion of terminal H),
    4) samples one torsion (uniformly or via importance weighting),
    5) rotates the selected **side** of the molecule around the central axis ``j→k``,
       checking optional collision tolerances and wrapping fractional coordinates
       when PBC is active.

    This operator is intended for **backbone/rotor sampling** in organic molecules,
    surfaces, and bulk systems, and includes controls to **avoid methyl-only bias**.

    **Requirements on ``structure``**:
    ``structure.AtomPositionManager`` must provide:
    - ``atomLabelsList``: sequence of atomic symbols (e.g., ``['C','H','N',...]``),
    - ``atomPositions``: ``(N, 3)`` float array of Cartesian positions in Å,
    - ``latticeVectors``: ``(3, 3)`` cell matrix (Å) or ``None``/invalid for molecules,
    - assignment to ``atomPositions`` must update the geometry.

    :param labels_focus:
        Optional set/list of element symbols. If provided, torsions must satisfy:
        - ``require_mode='any'`` (default): at least one of ``i,j,k,l`` has a label in
          ``labels_focus``.
        - ``require_mode='central'``: **both** central atoms ``j`` and ``k`` have labels
          in ``labels_focus``.
    :type labels_focus: set[str] | list[str] | None
    :param indices_focus:
        Optional set/list of atom indices. If provided, torsions must include at least
        one of these indices among ``(i,j,k,l)``. Useful to localize sampling to a region
        or to ensure inclusion of specific atoms.
    :type indices_focus: set[int] | list[int] | None
    :param require_mode:
        Focus logic when ``labels_focus`` is given. Options:
        - ``'any'`` (default): any of ``i,j,k,l`` matches,
        - ``'central'``: **both** ``j`` and ``k`` match.
    :type require_mode: {'any', 'central'}
    :param side:
        Which side of the central bond to rotate:
        - ``'k'``: rotate the connected component on the *k* side when the ``j–k`` edge
          is virtually cut (typical for torsion scans),
        - ``'j'``: rotate the *j* side component,
        - ``'l_only'``: rotate only atom ``l`` (useful for delicate adjustments).
    :type side: {'k', 'j', 'l_only'}
    :param angle:
        Fixed rotation angle. If ``None`` (default), an angle is sampled uniformly from
        ``angle_range``.
    :type angle: float | None
    :param angle_range:
        Inclusive range for random angles when ``angle is None``. Units controlled by
        ``degrees``. Default ``(-30.0, 30.0)``.
    :type angle_range: tuple[float, float]
    :param degrees:
        If ``True`` (default), interpret ``angle`` and ``angle_range`` in degrees; else
        in radians.
    :type degrees: bool
    :param radius_scale:
        Connectivity cutoff multiplier. Two atoms ``p`` and ``q`` are considered bonded
        if distance ``d(p,q) ≤ radius_scale * (r_cov(p) + r_cov(q))`` where the covalent
        radii are element-aware (internal table; fallback 1.20 Å). Default ``1.15``.
    :type radius_scale: float
    :param cutoff_max:
        Optional hard cap (Å) on the bonding cutoff computed from covalent radii. If
        provided, the effective cutoff is ``min(cutoff_max, radius_scale * sum_r_cov)``.
    :type cutoff_max: float | None
    :param pbc:
        Enable periodic minimum-image distances and fractional wrapping **when a valid
        3×3 lattice exists**. The implementation automatically falls back to Cartesian
        (non-PBC) if the cell is missing/invalid/singular. Default ``True``.
    :type pbc: bool
    :param wrap_after:
        When PBC is active, wrap fractional coordinates back into ``[0,1)`` after the
        rotation. Ignored if PBC is not used. Default ``True``.
    :type wrap_after: bool
    :param collision_tolerance:
        Minimum allowed interatomic distance (Å) for the **proposed** geometry. If any
        moved atom comes closer than this to any atom (moved or not), the proposal is
        rejected and another angle is sampled (up to ``max_attempts``). Set ``None`` to
        disable collision checks. Default ``1.05`` Å.
    :type collision_tolerance: float | None
    :param max_attempts:
        Maximum resampling attempts of the angle before giving up and returning ``None``.
        Default ``8``.
    :type max_attempts: int
    :param constraints:
        List of callables ``constraint(idx, structure) -> bool``. All **moved** atoms
        must satisfy **all** constraints; otherwise the candidate torsion is rejected.
        This integrates with your existing ``validate`` helper.
    :type constraints: list[Callable[[int, Any], bool]]
    :param seed:
        RNG seed for reproducible sampling (torsion choice and random angles). Default
        ``None`` (system randomness).
    :type seed: int | None
    :param verbose:
        If ``True``, print a concise message upon successful rotation (indices, central
        pair, angle, side). Default ``False``.
    :type verbose: bool

    # --- Selection controls to mitigate methyl bias ---
    :param allowed_central_pairs:
        Optional set of **unordered** element pairs for the central bond ``{label_j, label_k}``.
        When provided, only torsions whose central pair is a member are eligible. Example
        for peptide backbone bias: ``{frozenset({'N','C'}), frozenset({'C','C'})}``.
    :type allowed_central_pairs: set[frozenset[str]] | None
    :param forbidden_central_pairs:
        Optional set of unordered element pairs that are **not** allowed as central bonds.
        Useful to exclude specific chemistries (e.g., ``{frozenset({'C','H'})}``).
    :type forbidden_central_pairs: set[frozenset[str]] | None
    :param exclude_end_labels:
        Labels disallowed on the terminal torsion atoms ``i`` and ``l``. Default ``{'H'}``
        to suppress terminal-hydrogen and many methyl dihedrals.
    :type exclude_end_labels: set[str]
    :param min_degree_end:
        Minimum graph degree required for both ends ``i`` and ``l``. ``2`` (default)
        suppresses terminal atoms and many CH₃ end cases.
    :type min_degree_end: int
    :param sample_mode:
        Torsion sampling scheme among the filtered candidates:
        - ``'uniform'``: all candidates equiprobable,
        - ``'weighted'`` (default): importance sampling using weights below.
    :type sample_mode: {'uniform', 'weighted'}
    :param w_heavy_end:
        Weight bonus added when **both** ends ``i`` and ``l`` are *not* in
        ``exclude_end_labels`` (i.e., heavy-atom ends). Only used when
        ``sample_mode='weighted'``. Default ``4.0``.
    :type w_heavy_end: float
    :param w_backbone_pair:
        Weight bonus added when the central pair is in ``allowed_central_pairs``.
        Only used when ``sample_mode='weighted'``. Default ``6.0``.
    :type w_backbone_pair: float
    :param w_default:
        Base weight for each candidate prior to bonuses. Only used when
        ``sample_mode='weighted'``. Default ``1.0``.
    :type w_default: float

    :returns:
        A callable ``func(structure)`` that attempts one dihedral rotation and returns:
        - the **mutated** ``structure`` on success, or
        - ``None`` if no eligible torsion was found or all proposals failed collision/constraint checks.

    :rtype:
        Callable[[Any], Any]

    :notes:
        - **PBC autodetection**: PBC math is used only when a valid 3×3 lattice with non-zero
          determinant is present; otherwise Cartesian distances are used and wrapping is skipped.
        - **Complexity**: neighbor graph construction is ``O(N²)``; acceptable for small/medium
          molecules and unit cells typical in GA steps. For very large systems, consider providing
          a bonded topology to avoid ``O(N²)`` detection.
        - **Reproducibility**: pass a fixed ``seed`` to stabilize both candidate selection and
          random angles; structural duplicates and collision rejections can still affect outcomes.
        - **Chemistry control**: combine ``allowed_central_pairs`` with ``exclude_end_labels`` and
          ``min_degree_end`` to favor backbone torsions (φ/ψ/ω) over methyl rotors.

    :examples:
        Prefer peptide backbone torsions (φ/ψ) in an XYZ molecule (no cell), while avoiding H ends:
        
        >>> BACKBONE = {frozenset({'N','C'}), frozenset({'C','C'})}
        >>> mut = mutation_rotate_dihedral_by_connectivity(
        ...     pbc=False, wrap_after=False,
        ...     allowed_central_pairs=BACKBONE,
        ...     exclude_end_labels={'H'}, min_degree_end=2,
        ...     sample_mode='weighted',
        ...     angle_range=(-25.0, 25.0),
        ...     side='k',
        ...     collision_tolerance=1.0,
        ...     max_attempts=10,
        ...     seed=73,
        ... )
        >>> new_structure = mut(structure)  # returns None if no acceptable move

        Target only torsions that involve specific atoms (e.g., indices around a functional group):

        >>> mut = mutation_rotate_dihedral_by_connectivity(
        ...     indices_focus={12, 13, 22},  # must appear somewhere in (i,j,k,l)
        ...     exclude_end_labels={'H'},
        ... )

    :seealso:
        - ``random_rattle`` for Gaussian Cartesian perturbations under constraints.
        - ``mutation_random_strain`` for symmetric cell/position strains (bulk/surfaces).
    """
    rng = random.Random(seed)

    def _dihedral(a,b,c,d):
        # returns radians in (-pi, pi]
        v1 = b - a; v2 = c - b; v3 = d - c
        n1 = np.cross(v1, v2); n2 = np.cross(v2, v3)
        n1 /= (np.linalg.norm(n1) + 1e-15)
        n2 /= (np.linalg.norm(n2) + 1e-15)
        m1 = np.cross(n1, v2/ (np.linalg.norm(v2)+1e-15))
        x = np.dot(n1, n2)
        y = np.dot(m1, n2)
        return np.arctan2(y, x)

    def _angular_diff(a, b):
        # wrap to (-pi, pi]
        d = a - b
        d = (d + np.pi) % (2*np.pi) - np.pi
        return d

    def _choose_candidates(structure,
                           allowed_pairs, forbidden_pairs,
                           ex_end_labels, min_deg):
        labels = np.asarray(structure.AtomPositionManager.atomLabelsList)
        pos    = np.asarray(structure.AtomPositionManager.atomPositions, dtype=float)

        cell    = _get_cell(structure)
        use_pbc = bool(pbc and (cell is not None))
        neigh   = _build_connectivity(structure, radius_scale=radius_scale, pbc=use_pbc, cutoff_max=cutoff_max)
        torsions = _enumerate_torsions(neigh)

        if not torsions:
            return [], [], neigh, pos, labels, cell, use_pbc

        lab_focus = set(labels_focus) if labels_focus is not None else None
        idx_focus = set(indices_focus) if indices_focus is not None else None
        allowed_pairs_set   = set(allowed_pairs)   if allowed_pairs   is not None else None
        forbidden_pairs_set = set(forbidden_pairs) if forbidden_pairs is not None else None

        def deg(u): return len(neigh[u])

        cand, wts = [], []
        for (i,j,k,l) in torsions:
            # focus by labels/indices
            if lab_focus is not None:
                if require_mode == 'central':
                    if not (labels[j] in lab_focus and labels[k] in lab_focus):
                        continue
                else:
                    if not any(lbl in lab_focus for lbl in (labels[i],labels[j],labels[k],labels[l])):
                        continue
            if idx_focus is not None and not ({i,j,k,l} & idx_focus):
                continue

            # central-pair chemistry
            pair = frozenset({labels[j], labels[k]})
            if allowed_pairs_set   is not None and pair not in allowed_pairs_set:
                continue
            if forbidden_pairs_set is not None and pair in  forbidden_pairs_set:
                continue

            # avoid H/terminal ends
            if (labels[i] in ex_end_labels) or (labels[l] in ex_end_labels):
                continue
            if (deg(i) < min_deg) or (deg(l) < min_deg):
                continue

            # precompute moved side for constraints/weights
            if side == 'k':
                moved = _component_of(neigh, start=k, blocked=j)
            elif side == 'j':
                moved = _component_of(neigh, start=j, blocked=k)
            elif side == 'l_only':
                moved = [l]
            else:
                continue

            if constraints and not all(validate(int(u), structure, constraints) for u in moved):
                continue

            # weights
            w = w_default
            if allowed_pairs_set is not None and pair in allowed_pairs_set:
                w += w_backbone_pair
            if (labels[i] not in ex_end_labels) and (labels[l] not in ex_end_labels):
                w += w_heavy_end

            cand.append((i,j,k,l,moved))
            wts.append(max(1e-6, float(w)))

        return cand, wts, neigh, pos, labels, cell, use_pbc

    def func(structure):
        # try with user filters; optionally relax if empty
        tries = [
            (allowed_central_pairs, forbidden_central_pairs, exclude_end_labels, min_degree_end),
        ]
        if relax_if_empty:
            # progressively relax: drop degree, then allow H ends, then drop pair filter
            tries += [
                (allowed_central_pairs, forbidden_central_pairs, exclude_end_labels, 1),
                (allowed_central_pairs, forbidden_central_pairs, set(),              1),
                (None,                  forbidden_central_pairs, set(),              1),
            ]

        for (acp, fcp, exlab, mindeg) in tries:
            cand, wts, neigh, pos, labels, cell, use_pbc = _choose_candidates(
                structure, acp, fcp, exlab, mindeg
            )
            if not cand:
                continue

            # sample a torsion
            if sample_mode == 'weighted':
                total = sum(wts); r = rng.uniform(0.0, total); acc = 0.0; pick = 0
                for idx, w in enumerate(wts):
                    acc += w
                    if r <= acc:
                        pick = idx; break
            else:
                pick = rng.randrange(len(cand))

            i,j,k,l,moved = cand[pick]

            # axis through j→k; origin at j
            axis_vec = _pbc_delta(cell if use_pbc else None, pos[j], pos[k])
            n = np.linalg.norm(axis_vec)
            if n < 1e-12:
                continue
            axis   = axis_vec / n
            origin = pos[j].copy()

            # reference dihedral (use original positions, Cartesian)
            phi0 = _dihedral(pos[i], pos[j], pos[k], pos[l])

            # attempt rotations
            for _ in range(max(1, int(max_attempts))):
                ang = (rng.uniform(*angle_range) if angle is None else float(angle))
                ang = np.deg2rad(ang) if degrees else ang
                R = _rotation_matrix(axis, ang)

                pos_trial = pos.copy()
                v = pos_trial[moved] - origin
                pos_trial[moved] = (R @ v.T).T + origin

                if wrap_after and use_pbc:
                    frac = _cart_to_frac(cell, pos_trial)
                    frac = _wrap_frac(frac)
                    pos_trial = _frac_to_cart(cell, frac)

                # ensure change: dihedral delta + RMSD on moved subgraph
                ok_change = True
                if ensure_change:
                    phi1   = _dihedral(pos_trial[i], pos_trial[j], pos_trial[k], pos_trial[l])
                    dphi   = abs(_angular_diff(phi1, phi0))
                    if degrees:
                        dphi = np.degrees(dphi)
                    rmsd = np.sqrt(np.mean(np.sum((pos_trial[moved] - pos[moved])**2, axis=1)))
                    ok_change = (dphi >= min_dihedral_delta_deg) and (rmsd >= min_rmsd_moved)

                if not ok_change:
                    continue

                # collision check
                if not _min_separation_after_move(cell if use_pbc else None,
                                                  pos, pos_trial, moved,
                                                  collision_tolerance, pbc=use_pbc):
                    continue

                # accept
                structure.AtomPositionManager.atomPositions = pos_trial
                if verbose:
                    pair = frozenset({labels[j], labels[k]})
                    print(f"[torsion] ({i}-{j}-{k}-{l}) Δφ≥{min_dihedral_delta_deg}"
                          f"{'°' if degrees else 'rad'}; central={set(pair)}; side={side}; moved={len(moved)} atoms")
                return structure

        # nothing accepted
        return None

    return func