# ============================================================
#   Extra peptide-specific mutations
#   (φ/ψ snap, Ramachandran sampler, ω flip, global spin, torsion pull by distance)
#   Requires the dihedral helpers already added: set_dihedral_graph, jitter_dihedral_graph, etc.
# ============================================================
import math
import numpy as np

# --------- 1) Snap φ/ψ to known basins -----------------------
# NOTE: adjust centers to your reference (approximate typical values).
_RAMACHANDRAN_CENTERS = {
    "beta":   (-135.0, 135.0),
    "C7eq":   (-80.0,   80.0),
    "C7ax":   (  60.0, -60.0),
}

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
def mutation_ramachandran_snap(
    phi: tuple, psi: tuple,
    basin: str = "C7eq",
    jitter_deg: float = 10.0,
    constraints: list = []
):
    """
    Fixes (φ,ψ) near the center of the chosen basin (+/- jitter).
    phi, psi: tuples (a,b,c,d) for each dihedral.
    """
    phi = tuple(map(int, phi)); psi = tuple(map(int, psi))
    cx, cy = _RAMACHANDRAN_CENTERS[basin]
    def func(structure):
        # φ
        if constraints and not (validate(phi[1], structure, constraints) and validate(phi[2], structure, constraints)):
            return None
        target_phi = cx + float(np.random.uniform(-jitter_deg, jitter_deg))
        ok1 = set_dihedral_graph(structure, *phi, target_phi)
        if not ok1: 
            return None
        # ψ
        if constraints and not (validate(psi[1], structure, constraints) and validate(psi[2], structure, constraints)):
            return None
        target_psi = cy + float(np.random.uniform(-jitter_deg, jitter_deg))
        ok2 = set_dihedral_graph(structure, *psi, target_psi)
        return structure if ok2 else None
    return func

# --------- 2) Ramachandran mixture sampler -------------------
def mutation_ramachandran_sample(
    phi: tuple, psi: tuple,
    centers: dict = None,
    widths_deg: dict = None,
    probs: dict = None,
    constraints: list = []
):
    """
    Samples (φ,ψ) from a mixture {center: N(μ,σ)} with weights 'probs'.
    """
    phi = tuple(map(int, phi)); psi = tuple(map(int, psi))
    centers = centers or _RAMACHANDRAN_CENTERS
    widths_deg = widths_deg or {"beta": 20.0, "C7eq": 20.0, "C7ax": 20.0}
    probs = probs or {"beta": 0.30, "C7eq": 0.35, "C7ax": 0.35}
    keys = sorted(centers.keys())
    p = np.array([probs[k] for k in keys], float); p /= p.sum()

    def func(structure):
        k = np.random.choice(keys, p=p)
        mu_phi, mu_psi = centers[k]
        s = widths_deg.get(k, 20.0)
        tphi = float(np.random.normal(mu_phi, s))
        tpsi = float(np.random.normal(mu_psi, s))
        if constraints and not (validate(phi[1], structure, constraints) and validate(phi[2], structure, constraints)):
            return None
        if not set_dihedral_graph(structure, *phi, tphi):
            return None
        if constraints and not (validate(psi[1], structure, constraints) and validate(psi[2], structure, constraints)):
            return None
        ok = set_dihedral_graph(structure, *psi, tpsi)
        return structure if ok else None
    return func

# --------- 3) ω flip/planarization (peptide bond) ------------
def mutation_omega_flip(
    omega: tuple,                     # e.g., (C_i, N_{i+1}, CA_{i+1}, C_{i+1})
    prefer_trans: bool = True,
    flip_prob: float = 0.05,          # very low: cis is rare
    constraints: list = []
):
    """
    With probability flip_prob: ω -> ω ± 180° (cis/trans). 
    Otherwise, planarize (ω -> ±180° if prefer_trans, or 0° if not).
    """
    omega = tuple(map(int, omega))
    def func(structure):
        # Decide target
        if np.random.rand() < flip_prob:
            target = 0.0 if prefer_trans else 180.0
        else:
            target = 180.0 if prefer_trans else 0.0
        # rotate the downstream part of the N–CA bond (b–c of dihedral a–b–c–d)
        if constraints and not (validate(omega[1], structure, constraints) and validate(omega[2], structure, constraints)):
            return None
        ok = set_dihedral_graph(structure, *omega, target)
        return structure if ok else None
    return func

# --------- 4) Rigid-body spin of the whole molecule ----------
def mutation_global_spin(angle_max_deg: float = 180.0, seed: int = None):
    """
    Rigid rotation of the whole molecule around a random axis (does not change energy).
    """
    rng = np.random.RandomState(seed)
    def func(structure):
        P = np.asarray(structure.AtomPositionManager.atomPositions, float)
        axis = rng.normal(size=3); axis /= (np.linalg.norm(axis) + 1e-12)
        ang  = float(rng.uniform(-angle_max_deg, angle_max_deg))
        R = _R_axis_angle(axis, math.radians(ang))
        com = P.mean(0)
        Q = (P - com) @ R.T + com
        structure.AtomPositionManager.atomPositions = Q
        return structure
    return func

# --------- 5) Torsion pull towards target distance -----------
def mutation_torsion_pull_distance(
    dihedral: tuple,                   # (a,b,c,d) to rotate (c-side)
    pair: tuple,                       # (i,j) distance to improve
    target_dist: float = 2.2,          # Å (e.g., H···O hydrogen bond)
    step_deg: float = 5.0,
    iters: int = 8,
    constraints: list = []
):
    """
    Adjusts a dihedral in small steps, trying to bring |ri-rj| closer to 'target_dist'.
    Useful to induce/preform H-bonds without distorting bonds.
    """
    a,b,c,d = map(int, dihedral)
    i,j = map(int, pair)
    def func(structure):
        P = np.asarray(structure.AtomPositionManager.atomPositions, float)
        if constraints and not (validate(b, structure, constraints) and validate(c, structure, constraints)):
            return None
        best = np.linalg.norm(P[i]-P[j])
        direction = 1.0
        improved = False
        for _ in range(iters):
            _rotate_about_bond_inplace(structure, b, c, direction*step_deg, group=None)  # group computed inside
            P2 = np.asarray(structure.AtomPositionManager.atomPositions, float)
            dnow = np.linalg.norm(P2[i]-P2[j])
            if abs(dnow - target_dist) < abs(best - target_dist):
                best = dnow; improved = True
            else:
                # revert & try opposite
                _rotate_about_bond_inplace(structure, b, c, -direction*step_deg, group=None)
                direction *= -1.0
        return structure if improved else None
    return func
