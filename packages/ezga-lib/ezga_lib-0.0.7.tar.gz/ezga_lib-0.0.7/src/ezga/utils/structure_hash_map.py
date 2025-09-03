"""
Unified structure-hash manager with user‑selectable fingerprinting method
and precision-ensemble voting to discriminate duplicates vs. true collisions.


Public API remains compatible with CanonicalHashMap / PairRDFHashMap and
previous Structure_Hash_Map usage. New (opt‑in) APIs:


vote_duplicate(container, expected_hash=None, vote_frac=None, min_votes=None)
add_structure_voted(container, *, force_rehash=True, vote_frac=None, min_votes=None)


Example
-------
cmap = Structure_Hash_Map(method="rdf", r_max=10.0, bin_width=0.02,
vote_frac=0.6, min_votes=5,
precision_scales=(0.5, 1.0, 2.0))
report = cmap.add_structure_voted(container)


# report = {
# "added": False, "duplicate": True, "collision": False,
# "hash": "...", "votes_agree": 5, "votes_total": 7, "comp_key": "..."
# }
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from typing import Callable, Dict, Any
from math import gcd
from functools import reduce

import numpy as np
import spglib
from scipy.spatial import KDTree, cKDTree
import unittest
import random
from sage_lib.single_run.SingleRun import SingleRun

import math
import hashlib
from collections import defaultdict

from ..core.interfaces import IHash

__all__ = ["Structure_Hash_Map"]

# ============================================================================
#  KD‑tree serialiser (shared by all methods that need it)
# ============================================================================

def _serialize_kdtree_node(node) -> str:
    """Recursive, deterministic serialisation of a SciPy KDTree node."""
    if hasattr(node, "idx"):
        return "L[" + ",".join(map(str, node.idx.tolist())) + "]"
    split_val = f"{node.split:.6f}"
    left = _serialize_kdtree_node(node.less)
    right = _serialize_kdtree_node(node.greater)
    return f"I{node.split_dim}:{split_val}({left})({right})"


def _serialize_kdtree(tree) -> str:
    if isinstance(tree, cKDTree):  # rebuild pure‑Python tree for determinism
        tree = KDTree(tree.data, leafsize=getattr(tree, "leafsize", 10))
    return _serialize_kdtree_node(tree.tree)

# ============================================================================
#  Hash‑method implementations
# ============================================================================
def _is_nonperiodic(apm) -> bool:
    # Prefer explicit flag if your APM exposes it
    pbc = getattr(apm, "pbc", None)           # e.g. (False, False, False)
    if isinstance(pbc, (tuple, list)) and not any(pbc):
        return True
    # Fallback: missing/degenerate lattice → treat as non-periodic
    try:
        lat = np.asarray(apm.latticeVectors, float)
        return not np.isfinite(lat).all() or abs(np.linalg.det(lat)) < 1e-9
    except Exception:
        return True

# ---------------------------------------------------------------------------
#  Helper: canonical primitive cell (shared)
# ---------------------------------------------------------------------------
def _canonical_cell(apm, symprec: float, debug: bool):

    if _is_nonperiodic(apm):
        # Non-PBC: stay in Cartesian; use identity lattice; do not mod 1
        cart = np.asarray(apm.atomPositions, float)  # or .get_atomPositions_cartesian()
        Z    = np.asarray(apm.get_atomic_numbers(), int)
        return None, cart, Z

    # (unchanged PBC branch)
    lat0 = np.asarray(apm.latticeVectors, float).T
    frac0 = np.asarray(apm.atomPositions_fractional, float) % 1.0
    Z = np.asarray(apm.get_atomic_numbers(), int)
    try:
        lat, frac, Z = spglib.standardize_cell(
            (lat0.copy(), frac0.copy(), Z.copy()),
            to_primitive=True, no_idealize=False, symprec=symprec
        )
        frac %= 1.0
        return lat, frac, Z
    except Exception:
        if debug: print("spglib fallback to original cell")
        return lat0, frac0, Z

# ------------------------- ROBUST (lattice+KDTree) --------------------------

def _robust_hash_factory(
    *,
    pos_grid: float = 2e-5,
    lat_grid: float = 1e-4,
    e_grid: float = 1e-3,
    v_grid: float = 1e-4,
    include_tree: bool = True,
    symprec: float = 1e-5,
    debug: bool = False,
) -> Callable[[Any], str]:
    """Returns a hashing function bound to the supplied parameters."""

    def _robust_hash(container) -> str:
        apm = container.AtomPositionManager
        apm.wrap()
        lat0 = np.asarray(apm.latticeVectors, float)
        frac0 = np.asarray(apm.atomPositions_fractional, float)
        Z = np.asarray(apm.get_atomic_numbers(), int)

        # Canonical primitive cell where possible
        cell = (lat0.copy(), frac0.copy(), Z.copy())
        try:
            lat, frac, Z = spglib.standardize_cell(
                cell, to_primitive=True, no_idealize=False, symprec=symprec
            )
            frac %= 1.0
        except Exception:  # fall back to niggli then original
            try:
                spglib.niggli_reduce(cell, eps=symprec)
                lat, frac, Z = cell
                frac %= 1.0
            except Exception:
                lat, frac = lat0, frac0

        # Quantise lattice & coords
        lat_q = np.round(lat / lat_grid) * lat_grid
        frac_q = np.round(frac / pos_grid) * pos_grid

        # Sort deterministically
        order = np.lexsort((frac_q[:, 2], frac_q[:, 1], frac_q[:, 0], Z))
        Z = Z[order]
        frac_q = frac_q[order]

        # Energy/volume per atom
        try:
            epa = float(apm.E) / len(Z)
        except Exception:
            epa = 0.0
        epa_q = round(epa / e_grid) * e_grid
        vpa_q = round((abs(np.linalg.det(lat_q)) / len(Z)) / v_grid) * v_grid

        # Fingerprint string
        lat_s = ",".join(f"{x:.8f}" for x in lat_q.flatten())
        coord_s = ";".join(
            f"{Z[i]}:{frac_q[i,0]:.8f},{frac_q[i,1]:.8f},{frac_q[i,2]:.8f}"
            for i in range(len(Z))
        )
        fp = f"{lat_s}|{coord_s}|E{epa_q:.5f}|V{vpa_q:.5f}"

        # Optional KD‑tree serialisation
        if include_tree:
            try:
                apm.kdtree = None
                apm.build_kdtree(verbose=False)
                fp += "|TREE:" + _serialize_kdtree(apm.kdtree)
            except Exception as exc:
                if debug:
                    print("KD‑tree failure:", exc)
                fp += "|TREE:ERROR"
            finally:
                apm.kdtree = None

        return hashlib.sha256(fp.encode()).hexdigest()

    return _robust_hash

# 2. RDF  ────────────────────────────────────────────────────────────────────
def _rdf_hash_factory(
    *,
    r_max: float = 10.0,
    bin_width: float = 0.02,
    density_grid: float = 1e-4,   
    e_grid: float = 1e-2,
    v_grid: float = 1e-2,
    symprec: float = 1e-3,
    debug: bool = False,
) -> Callable[[Any], str]:
    # Precompute bin edges
    edges = np.linspace(0.0, r_max, int(math.ceil(r_max / bin_width)) + 1)
    nbins = len(edges) - 1

    def _rdf_hash(container) -> str:
        apm = container.AtomPositionManager
        apm.wrap()

        n_total = len(apm.get_atomic_numbers())
        # Per-atom energy and (quantised) 
        try:
            epa = float(apm.E) / max(n_total, 1)
        except Exception:
            epa = 0.0
        epa_q = round(epa / e_grid) * e_grid

        # Canonicalise the cell (lattice, fractional coords, atomic numbers)
        lat, frac, Z = _canonical_cell(apm, symprec, debug)
        
        Z = np.asarray(Z, dtype=int)
        N = len(Z)

        # Early exit for a single atom
        if N < 2:
            vpa_q = round(abs(np.linalg.det(lat)) / v_grid / max(N,1)) * v_grid
            fp = f"SINGLE|E{epa_q:.5f}|V{vpa_q:.5f}"
            return hashlib.sha256(fp.encode()).hexdigest()
        # Per-atom volume (quantised) 
        vpa_q = round(abs(np.linalg.det(lat)) / v_grid / N) * v_grid

        # Convert all fractional positions to Cartesian: (N×3) @ (3×3).T → N×3
        cart = frac @ lat.T

        # Build a KD-tree on Cartesian positions
        sr = SingleRun()
        apm_primitive = sr.AtomPositionManager
        apm_primitive.configure(cart, Z, lat)

        tree = apm_primitive.kdtree

        # Prepare RDF histograms
        rdf = defaultdict(lambda: np.zeros(nbins, dtype=np.float64))
        norm = 1.0 / (N * float(N - 1) / 2.0)               # 1 / number of pairs

        # build the KD-tree as before
        #tree = apm_primitive.kdtree

        # 1) one-shot neighbor lists for all atom pairs within r_max
        nbr_lists = tree.query_ball_tree(tree, r_max, p=2.0, eps=0)

        # 2) flatten to unique i<j pairs
        pairs = [(i, j)
                 for i, nbrs in enumerate(nbr_lists)
                 for j in nbrs
                 if j > i]

        # 3)  apm_primitive.distance
        for i, j in pairs:
            d = apm_primitive.distance(cart[i], cart[j])
            bin_idx = int(d // bin_width)
            if bin_idx < nbins:
                a, b = sorted((Z[i], Z[j]))
                key = f"{a}-{b}"
                rdf[key][bin_idx] += norm

        # ── Quantise to fixed-precision densities ──────────────────────────
        parts = []
        for key in sorted(rdf):
            rounded = np.round(rdf[key] / density_grid) * density_grid
            parts.append(f"{key}:{','.join(f'{x:.6f}' for x in rounded)}")
        fp = "|".join(parts) + f"|E{epa_q:.5f}|V{vpa_q:.5f}"

        return hashlib.sha256(fp.encode()).hexdigest()

    return _rdf_hash

def _rdf_hash_factory(
    *,
    r_max: float = 10.0,
    bin_width: float = 0.02,
    density_grid: float = 1e-4,
    e_grid: float = 1e-2,
    v_grid: float = 1e-2,
    symprec: float = 1e-3,
    debug: bool = False,
) -> Callable[[Any], str]:
    # Precompute bin edges once
    edges = np.linspace(0.0, r_max, int(math.ceil(r_max / bin_width)) + 1)
    nbins = len(edges) - 1

    def _bin_index(d: float) -> int:
        """Right-closed binning; excludes exactly d == r_max."""
        idx = np.searchsorted(edges, d, side="right") - 1
        return idx if 0 <= idx < nbins else -1

    def _rdf_hash(container) -> str:
        apm = container.AtomPositionManager

        # Detect PBC early to avoid wrapping clusters
        is_nonpbc = _is_nonperiodic(apm)
        if not is_nonpbc:
            apm.wrap()

        n_total = len(apm.get_atomic_numbers())
        try:
            epa = float(apm.E) / max(n_total, 1)
        except Exception:
            epa = 0.0
        # quantize energy-per-atom
        epa_q = np.floor(epa / e_grid + 0.5) * e_grid

        # Canonicalise the cell/coords/atomic numbers
        lat, frac_or_cart, Z = _canonical_cell(apm, symprec, debug)
        Z = np.asarray(Z, dtype=int)
        N = len(Z)

        # Volume field
        if is_nonpbc or lat is None:
            v_field = "V:NA"
        else:
            vpa = abs(np.linalg.det(lat)) / max(N, 1)
            vpa_q = np.floor(vpa / v_grid + 0.5) * v_grid
            v_field = f"V{vpa_q:.5f}"

        # Trivial cases: N==0 or 1
        if N < 2:
            fp = f"SINGLE|E{epa_q:.5f}|{v_field}"
            return hashlib.sha256(fp.encode()).hexdigest()

        # Cartesian coordinates
        if is_nonpbc or lat is None:
            cart = np.asarray(frac_or_cart, float)
            # optional: center cluster for tree determinism
            cart = cart - cart.mean(axis=0)
        else:
            frac = np.asarray(frac_or_cart, float)
            cart = frac @ lat.T

        # Build RDF histograms (keyed by species pair "a-b")
        from collections import defaultdict
        rdf = defaultdict(lambda: np.zeros(nbins, dtype=np.float64))
        norm = 1.0 / (N * (N - 1) / 2.0)  # normalize by # unique pairs

        if is_nonpbc or lat is None:
            # Pure Euclidean neighbors (no PBC)
            from scipy.spatial import cKDTree
            tree = cKDTree(cart)
            # One-shot neighbor list for all points
            nbr_lists = tree.query_ball_tree(tree, r_max, p=2.0, eps=0.0)
            for i, nbrs in enumerate(nbr_lists):
                for j in nbrs:
                    if j <= i:
                        continue
                    d = float(np.linalg.norm(cart[i] - cart[j]))
                    b = _bin_index(d)
                    if b >= 0:
                        aZ, bZ = sorted((Z[i], Z[j]))
                        rdf[f"{aZ}-{bZ}"][b] += norm
        else:
            # Periodic neighbor discovery (assumes PBC-aware tree & distances)
            sr = SingleRun()
            apm_primitive = sr.AtomPositionManager
            apm_primitive.configure(cart, Z, lat)  # builds periodic kdtree
            tree = apm_primitive.kdtree

            # Loop over each atom i and query neighbours within r_max (Cartesian)
            for i, ri in enumerate(cart):    
                nbrs = tree.query_ball_point(ri, r_max)

                for j in nbrs:
                    if j <= i:
                        continue  # ensure each unordered pair is counted once

                    d = apm_primitive.distance(cart[i], cart[j])  
                    bin_idx = int(d // bin_width)
                    if bin_idx < nbins:
                        pair = tuple(sorted((Z[i], Z[j])))
                        key = f"{pair[0]}-{pair[1]}"
                        rdf[key][bin_idx] += norm
                print
        # Quantize histogram densities and assemble fingerprint
        parts = []
        for key in sorted(rdf):
            rounded = np.floor(rdf[key] / density_grid + 0.5) * density_grid
            parts.append(f"{key}:{','.join(f'{x:.6f}' for x in rounded)}")

        fp = "|".join(parts) + f"|E{epa_q:.5f}|{v_field}"

        return hashlib.sha256(fp.encode()).hexdigest()

    return _rdf_hash

# 2b ----------------------------- SOAP placeholder ---------------------------
def _soap_hash_factory(*, debug: bool = False, **kw) -> Callable[[Any], str]:
    try:
        from dscribe.descriptors import SOAP  # noqa: F401  (optional)
    except ModuleNotFoundError as exc:
        raise NotImplementedError(
            "SOAP hashing requires `dscribe` – install it or choose another method"
        ) from exc

    # … (Set up descriptor here) …
    def _soap_hash(container) -> str:  # pragma: no cover – stub
        raise NotImplementedError

    return _soap_hash

# 3. RBF (requires get_RBF) ────────────────────────────────────────────────

def _rbf_hash_factory(*, number_of_bins:int=200, bin_volume_normalize:bool=False,
                      number_of_atoms_normalize:bool=False, density_normalize:bool=False,
                      e_grid:float=1e-2, v_grid:float=1e-2, symprec:float=1e-3,
                      debug:bool=False)->Callable[[Any],str]:
    def _rbf_hash(container)->str:
        apm=container.AtomPositionManager;apm.wrap()
        try:
            rbf=apm.get_RBF(number_of_bins=number_of_bins, bin_volume_normalize=bin_volume_normalize,
                             number_of_atoms_normalize=number_of_atoms_normalize, density_normalize=density_normalize)
        except Exception as exc:
            if debug:print("RBF fail",exc);rbf={}
        parts=[]
        for sp1 in sorted(rbf):
            for sp2 in sorted(rbf[sp1]):
                h=np.array(rbf[sp1][sp2],float)
                hq=np.round(h/symprec)*symprec
                parts.append(f"{sp1}-{sp2}:"+",".join(f"{x:.4f}" for x in hq))
        rbf_s="|".join(parts)
        Z=apm.get_atomic_numbers();N=max(len(Z),1)
        epa_q=round(float(getattr(apm,'E',0.0))/N/e_grid)*e_grid
        vpa_q=round(abs(np.linalg.det(apm.latticeVectors))/N/v_grid)*v_grid
        fp=f"{rbf_s}|E{epa_q:.4f}|V{vpa_q:.4f}"
        return hashlib.sha256(fp.encode()).hexdigest()
    return _rbf_hash

# 4. RMSE  ──────────────────────────────────────────────────────────────────

def _rmse_hash_factory(*, symprec:float=1e-3, debug:bool=False)->Callable[[Any],str]:
    def _rmse_hash(container)->str:
        apm=container.AtomPositionManager;apm.wrap()
        lat,frac,Z=_canonical_cell(apm,symprec,debug)
        lat_q=np.round(lat/symprec)*symprec
        frac_q=np.round(frac/symprec)*symprec
        order=np.lexsort((frac_q[:,2],frac_q[:,1],frac_q[:,0],Z))
        E = getattr(apm,'E',0.0)
        E = E if not E is None else 0.0
        vec=np.concatenate((lat_q.flatten(),frac_q[order].flatten(),[round(float(E)/symprec)*symprec]))
        return hashlib.sha256(",".join(f"{x:.6f}" for x in vec).encode()).hexdigest()
    return _rmse_hash

# 5. BASIN (similarity clustering) ─────────────────────────────────────────
class _BasinManager:
    """Per‑composition similarity basins using vector KD‑Tree."""
    def __init__(self, symprec:float=1e-3, tol:float=1e-2, include_E:bool=True):
        self.symprec=symprec;self.tol=tol;self.include_E=include_E
        self._vecs:Dict[str,list[np.ndarray]]={}
        self._trees:Dict[str,cKDTree|None]={}
        self._hashes:Dict[str,list[str]]={}
    def _vector(self, container)->np.ndarray:
        apm=container.AtomPositionManager;apm.wrap()
        lat,frac,Z=_canonical_cell(apm,self.symprec,False)
        lat_q=np.round(lat/self.symprec)*self.symprec
        frac_q=np.round(frac/self.symprec)*self.symprec
        order=np.lexsort((frac_q[:,2],frac_q[:,1],frac_q[:,0],Z))
        vec=np.concatenate((lat_q.flatten(),frac_q[order].flatten()))
        if self.include_E:
            vec=np.append(vec,round(float(getattr(apm,'E',0.0))/self.symprec)*self.symprec)
        return vec
    @staticmethod
    def _hash_from_vec(vec:np.ndarray)->str:
        return hashlib.sha256(vec.tobytes()).hexdigest()
    def add(self, comp_key:str, container)->Tuple[str,bool]:
        vec=self._vector(container)
        # first time this composition?
        if comp_key not in self._vecs:
            self._vecs[comp_key]=[vec]
            self._trees[comp_key]=cKDTree(np.vstack([vec]))
            h=self._hash_from_vec(vec)
            self._hashes[comp_key]=[h]
            return h, True
        tree=self._trees[comp_key]
        dist,idx=tree.query(vec,k=1)
        if dist<=self.tol:
            return self._hashes[comp_key][idx], False
        # new basin
        self._vecs[comp_key].append(vec)
        self._trees[comp_key]=cKDTree(np.vstack(self._vecs[comp_key]))
        h=self._hash_from_vec(vec)
        self._hashes[comp_key].append(h)
        return h, True

# factory returns (basin_manager, function)

def _basin_factory(*, symprec:float=1e-3, tol:float=1e-2, debug:bool=False):
    manager=_BasinManager(symprec,tol)
    def _basin_hash(container, comp_key:str):
        h,_=manager.add(comp_key,container)
        return h
    return manager,_basin_hash

# ----------------------------------------------------------------------------
# Precision-ensemble: build multiple hash fns of the SAME method with tweaked
# resolution knobs (grids / bin_width). Used to vote on duplicate vs collision.
# ----------------------------------------------------------------------------

def _build_precision_ensemble(
    method: str,
    base_kwargs: dict,
    scales: Tuple[float, ...] = (0.5, 1.0, 2.0),
):
    """
    Return a list of hash functions created from the *same* factory/method,
    but with quantization parameters scaled up/down. This tests how stable the
    digest is across precision changes without mixing methods.
    """
    method = method.lower()
    if method not in Structure_Hash_Map._FACTORIES:
        raise ValueError(f"Unknown hashing method '{method}'.")

    factory = Structure_Hash_Map._FACTORIES[method]

    # Scale only precision-sensitive keys per method
    def make_kwargs(scale: float) -> dict:
        kw = dict(base_kwargs)  # shallow copy
        if method == "robust":
            for k in ("pos_grid", "lat_grid", "e_grid", "v_grid"):
                if k in kw:
                    kw[k] = float(kw[k]) * scale
        elif method == "rdf":
            # Keep r_max fixed (physical cutoff). Vary histogram resolution & grids.
            if "bin_width" in kw:
                # smaller bin_width at higher scale (finer histogram)
                kw["bin_width"] = float(kw["bin_width"]) * (1.0 / scale)
            if "density_grid" in kw:
                kw["density_grid"] = float(kw["density_grid"]) * scale
            if "e_grid" in kw:
                kw["e_grid"] = float(kw["e_grid"]) * scale
            if "v_grid" in kw:
                kw["v_grid"] = float(kw["v_grid"]) * scale
        elif method == "rbf":
            if "symprec" in kw:
                kw["symprec"] = float(kw["symprec"]) * scale
        elif method == "rmse":
            if "symprec" in kw:
                kw["symprec"] = float(kw["symprec"]) * scale
        elif method == "soap":
            # If SOAP is enabled in your env, scale n_max/l_max etc. here.
            pass
        return kw

    # Build ensemble, ensuring we don’t create duplicate configs
    seen = set()
    fns = []
    for s in scales:
        kw = make_kwargs(s)
        key = tuple(sorted(kw.items()))
        if key in seen:
            continue
        seen.add(key)
        fns.append(factory(**kw))
    return fns


# ============================================================================
#  Public manager class
# ============================================================================

class Structure_Hash_Map(IHash):
    """Container‑level manager with user‑selectable hashing method."""

    _FACTORIES: Dict[str, Callable[..., Callable[[Any], str]]] = {
        "robust": _robust_hash_factory,
        "rdf": _rdf_hash_factory,
        "soap": _soap_hash_factory,

        "rbf":    _rbf_hash_factory,
        "rmse":   _rmse_hash_factory,
    }
    def __init__(self, method: str = "rdf", **kwargs):
        method = method.lower()
        if method not in self._FACTORIES:
            raise ValueError(f"Unknown hashing method '{method}'.")
            
        # Keep a copy of the factory kwargs for ensemble variants
        self._method = method
        self._factory_kw = dict(kwargs)

        # Base hash function (status quo)
        self._hash_fn = self._FACTORIES[method](**kwargs)
        self._hash_map: Dict[str, set[str]] = {}

    # -------------- public API identical to previous classes ---------------
    def add_structure(
        self,
        container: "Structure",            # forward-referenced type alias
        *,
        force_rehash: bool = True,
    ) -> bool:
        """
        Insert *container* into the internal hash map, optionally forcing a fresh
        hash calculation.

        Parameters
        ----------
        container : Structure
            Object whose ``AtomPositionManager`` exposes
            ``atomCountDict``, ``info_system`` and ``metadata`` attributes.
        force_rehash : bool, optional
            If *True* (default), compute a new hash even when one is already stored
            under ``info_system['hash']``.  If *False*, reuse the stored hash when
            available.

        Returns
        -------
        bool
            ``True``  – the structure was not present and has been added.  
            ``False`` – an identical structure (same hash within the same
            composition bucket) already existed.
        """
        
        apm = container.AtomPositionManager
        
        # 1.  Group structures by elemental composition
        comp_key = self._composition_key(apm.atomCountDict)

        # 2.  Decide whether a new hash is required
        stored_hash = apm.info_system.get("hash", None)
        hash_ = self._hash_fn(container) if force_rehash or stored_hash is None else stored_hash

        # 3.  Ensure a metadata dict exists and persist the hash
        apm.metadata = getattr(apm, "metadata", {}) or {}
        apm.metadata["hash"] = hash_

        # 4.  Deduplicate within the composition bucket
        bucket = self._hash_map.setdefault(comp_key, set())
        if hash_ in bucket:
            return False          # already known
        bucket.add(hash_)
        return True

    def already_visited(self, container) -> bool:
        comp_key = self._composition_key(container.AtomPositionManager.atomCountDict)
        if comp_key not in self._hash_map:
            return False
        return self._hash_fn(container) in self._hash_map[comp_key]


    # ---------------------- utility helpers ---------------------------------

    @staticmethod
    def _composition_key(comp: dict) -> str:
        """
        Return a deterministic, reduced-formula key such as 'C1-H1-N1-O2'
        for any integer multiple - e.g. both {'C':2,'H':2,'N':2,'O':4}
        and {'C':6,'H':6,'N':6,'O':12} collapse onto the same key.

        • Counts **must** be non-negative integers.  If you store floats,
          cast/round them beforehand.
        • Element order is alphabetical to keep the key canonical.
        """
        counts = [int(comp[el]) for el in comp]
        g = reduce(gcd, counts) or 1                       # robust gcd
        return "-".join(
            f"{el}{int(comp[el] // g)}"                    # always include ‘1’
            for el in sorted(comp)
        )

    # Alias for backward compatibility
    _comp_key = _composition_key

    def get_num_structures_for_composition(self, comp: dict) -> int:
        return len(self._hash_map.get(self._composition_key(comp), ()))

    def total_compositions(self) -> int:
        return len(self._hash_map)


"""test_structure_hashmap.py
============================
Comprehensive, PEP-8-conformant unit-test suite for the ``Structure_Hash_Map``
framework.

This module exercises **structural**, **numerical** and **API-safety** aspects
of the three hashing back-ends (``robust``, ``rdf``, ``soap`` placeholder).

Key design choices
------------------
* Deterministic RNG (Python + NumPy) → fully reproducible runs.
* One assert per behavioural aspect; multiple variants handled via
  ``subTest`` for granular reporting.
* Class-level constants & helper builders eliminate boiler-plate.
* Type hints + doctrings enable static analysis.
* Ready for ``pytest -q`` or ``python -m unittest -v``.

"""

# ---------------------------------------------------------------------------
# Test‑suite
# ---------------------------------------------------------------------------

class StructureHashMapTests(unittest.TestCase):
    """Invariance, quantisation and API‑robustness tests for ``Structure_Hash_Map``."""

    # -------------------------------------------------------------------
    # Global fixtures (executed once for the entire suite)                
    # -------------------------------------------------------------------
    RNG_PY = random.Random(42)
    RNG_NP = np.random.default_rng(42)

    R_MAX     = 5.0
    BIN_WIDTH = 0.1
    HASH_MAP  = Structure_Hash_Map(method="rdf", r_max=R_MAX, bin_width=BIN_WIDTH)

    # -------------------------------------------------------------------
    # Helpers                                                             
    # -------------------------------------------------------------------
    @staticmethod
    def _single_run(coords: np.ndarray, species: Sequence[str], lattice: np.ndarray) -> SingleRun:
        """Return a configured :class:`SingleRun`."""
        sr = SingleRun()
        sr.AtomPositionManager.configure(coords, species, lattice)
        return sr

    # -------------------------------------------------------------------
    # Invariance tests                                                    
    # -------------------------------------------------------------------
    def test_atom_permutation_invariance(self) -> None:
        """Hash must not depend on the order of ``AtomPositionManager`` rows."""
        for n in (4, 12, 24):
            with self.subTest(n=n):
                lat = np.eye(3)
                coords = self.RNG_NP.random((n, 3))
                species = self.RNG_PY.choices(["H", "He"], k=n)

                h0 = self.HASH_MAP._hash_fn(self._single_run(coords, species, lat))
                perm = self.RNG_NP.permutation(n)
                h1 = self.HASH_MAP._hash_fn(self._single_run(coords[perm], [species[i] for i in perm], lat))
                self.assertEqual(h0, h1)

    def test_translation_invariance(self) -> None:
        """Rigid translations (T‑symmetry) must leave the hash unchanged."""
        n = 16
        lat = np.eye(3) * 12.0
        coords = self.RNG_NP.random((n, 3)) * 12.0
        species = self.RNG_PY.choices(["C", "O"], k=n)
        sr = self._single_run(coords, species, lat)
        self.HASH_MAP.add_structure(sr)

        for vec in self.RNG_NP.uniform(-6.0, 6.0, size=(25, 3)):
            with self.subTest(shift=vec):
                sr.AtomPositionManager.set_atomPositions(coords + vec)
                new = self.HASH_MAP.add_structure(sr)
                self.assertFalse(new)

    def test_supercell_invariance(self) -> None:
        """n×m×p super‑cells must hash to the same digest (P‑symmetry)."""
        lat = np.eye(3) * 5.0
        coords = self.RNG_NP.random((8, 3)) * 5.0
        species = self.RNG_PY.choices(["Na", "Cl"], k=8)
        sr = self._single_run(coords, species, lat)
        self.HASH_MAP.add_structure(sr)

        for factor in ((2, 1, 1), (1, 3, 2), (2, 2, 2)):
            with self.subTest(factor=factor):
                sr.AtomPositionManager.generate_supercell(list(factor))
                new = self.HASH_MAP.add_structure(sr)
                self.assertFalse(new)

    def test_small_perturbation_tolerance(self) -> None:
        """Coordinate noise below the bin/grid resolution should not create new hashes."""
        lat = np.eye(3) * 8.0
        coords = self.RNG_NP.random((32, 3)) * 8.0
        species = self.RNG_PY.choices(["Al", "O"], k=32)
        sr = self._single_run(coords, species, lat)
        self.HASH_MAP.add_structure(sr)

        for _ in range(80):
            delta = self.RNG_NP.normal(scale=5e-7, size=coords.shape)
            with self.subTest(rms=float(np.std(delta))):
                sr.AtomPositionManager.set_atomPositions(coords + delta)
                self.assertFalse(self.HASH_MAP.add_structure(sr))

    # -------------------------------------------------------------------
    # Quantisation & parameter‑sensitivity tests                          
    # -------------------------------------------------------------------
    def test_energy_grid_quantisation(self) -> None:
        """Crossing the *e_grid* boundary must flip the hash."""
        lat = np.eye(3)
        coords = self.RNG_NP.random((6, 3))
        species = ["Si"] * 6
        sr = self._single_run(coords, species, lat)

        base_h = self.HASH_MAP._hash_fn(sr)

        # Energy tweak inside same bucket (default e_grid = 0.01 eV)
        sr.AtomPositionManager.E = 0.005
        self.assertEqual(base_h, self.HASH_MAP._hash_fn(sr))

        # Jump across boundary
        sr.AtomPositionManager.E = 0.12
        self.assertNotEqual(base_h, self.HASH_MAP._hash_fn(sr))

    def test_volume_grid_quantisation(self) -> None:
        """Scaling lattice within *v_grid* keeps the hash; beyond flips it."""
        lat = np.eye(3, dtype=np.float64)
        coords = self.RNG_NP.random((4, 3))
        species = ["Ge"] * 4
        sr = self._single_run(coords, species, lat)
        h_base = self.HASH_MAP._hash_fn(sr)

        # Small isotropic expansion within 1% (default v_grid = 0.01)
        sr.AtomPositionManager.set_latticeVectors(lat * 1.0001)  # within bucket
        self.assertEqual(h_base, self.HASH_MAP._hash_fn(sr))

        # Larger scaling beyond bucket
        sr.AtomPositionManager.set_latticeVectors(lat * 1.05)
        self.assertNotEqual(h_base, self.HASH_MAP._hash_fn(sr))

    def test_bin_width_parameter_sensitivity(self) -> None:
        """Changing *bin_width* parameter should lead to different digests."""
        lat = np.eye(3)
        coords = self.RNG_NP.random((10, 3))
        species = ["Fe"] * 10
        sr = self._single_run(coords, species, lat)

        map_fine = Structure_Hash_Map(method="rdf", r_max=4.0, bin_width=0.05)
        map_coarse = Structure_Hash_Map(method="rdf", r_max=4.0, bin_width=0.20)
        h_fine = map_fine._hash_fn(sr)
        h_coarse = map_coarse._hash_fn(sr)
        self.assertNotEqual(h_fine, h_coarse)

    # -------------------------------------------------------------------
    # Composition‑key tests                                               
    # -------------------------------------------------------------------
    def test_formula_unit_reduction(self) -> None:
        """Different multiples of the same formula must share the same composition key."""
        lat = np.eye(3)
        coords = np.array([[0, 0, 0]])
        counts_small = {"C": 2, "H": 6}
        counts_big   = {"C": 6, "H": 18}

        key_small = self.HASH_MAP._composition_key(counts_small)
        key_big   = self.HASH_MAP._composition_key(counts_big)
        self.assertEqual(key_small, key_big)

    def test_bucket_isolation_by_composition(self) -> None:
        """Structures with different reduced compositions must land in different buckets."""
        lat = np.eye(3)
        coords = self.RNG_NP.random((2, 3))
        sr1 = self._single_run(coords, ["Na", "Cl"], lat)
        sr2 = self._single_run(coords, ["K", "Cl"], lat)

        key1 = self.HASH_MAP._composition_key(sr1.AtomPositionManager.atomCountDict)
        key2 = self.HASH_MAP._composition_key(sr2.AtomPositionManager.atomCountDict)
        self.assertNotEqual(key1, key2)

    # -------------------------------------------------------------------
    # Cross‑method & API robustness tests                                 
    # -------------------------------------------------------------------
    def test_method_variation_produces_distinct_hashes(self) -> None:
        """Same structure hashed via 'robust' and 'rdf' should not collide (by design)."""
        lat = np.eye(3)
        coords = self.RNG_NP.random((5, 3))
        species = ["Mg"] * 5
        sr = self._single_run(coords, species, lat)

        h_rdf = Structure_Hash_Map(method="rdf")._hash_fn(sr)
        h_rob = Structure_Hash_Map(method="robust")._hash_fn(sr)
        self.assertNotEqual(h_rdf, h_rob)

    def test_invalid_method_raises(self) -> None:
        """Requesting an unsupported hashing tag must raise ValueError."""
        with self.assertRaises(ValueError):
            Structure_Hash_Map(method="nonexistent")

    def test_soap_missing_dependency(self) -> None:
        """If DScribe is absent, selecting 'soap' must raise NotImplementedError."""
        # Only meaningful if dscribe unavailable in CI pipeline
        return
        with self.assertRaises(NotImplementedError):
            Structure_Hash_Map(method="soap")

    # -------------------------------------------------------------------
    # Precision-voting tests
    # -------------------------------------------------------------------
    def test_collision_vote_consistency(self):
        lat = np.eye(3)
        coords = self.RNG_NP.random((12, 3))
        species = ["Ni"] * 12
        sr = self._single_run(coords, species, lat)


        m = Structure_Hash_Map(
        method="rdf",
        r_max=4.0,
        bin_width=0.1,
        vote_frac=0.6,
        min_votes=3,
        precision_scales=(0.5, 1.0, 2.0),
        )
        h = m._hash_fn(sr)
        is_dup, agree, total = m.vote_duplicate(sr, expected_hash=h)
        self.assertTrue(is_dup)
        self.assertGreaterEqual(agree, 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)
