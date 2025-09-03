from __future__ import annotations
import json
from typing import Dict, Tuple, Optional
import numpy as np
from ase.calculators.calculator import Calculator, all_changes

# -----------------------------
# Built‑in convenience table (Å, eV)
# -----------------------------
# Materials-oriented defaults: σ derived from target like–like r_min via σ = r_min / 2^(1/6)
# r_min choices reflect typical materials intuition (anions > cations; noble gases from LJ fluid fits).
# Units: σ in Å, ε in eV.
_DEFAULT_LJ_TABLE: Dict[str, Tuple[float, float]] = {
    # Noble gases (kept from standard LJ fits; widely used in MD benchmarks)
    "He": (2.64, 0.00088),     # ε/kB≈10.22 K
    "Ne": (2.80, 0.00307),     # ε/kB≈35.6 K
    "Ar": (3.405, 0.01032),    # ε/kB≈119.8 K
    "Kr": (3.65, 0.01410),     # ε/kB≈164 K
    "Xe": (4.10, 0.01900),     # ε/kB≈221 K

    # Light elements / nonmetals (σ from r_min targets; ε ~ UFF/DREIDING-scale placeholders)
    # r_min targets (Å): H~2.5, C~3.40 (graphitic contact), N~3.1, O~2.0, F~2.9
    "H":  (2.228, 0.00280),    # σ=2.5/1.12246
    "C":  (3.029, 0.00280),    # σ=3.40/1.12246
    "N":  (2.762, 0.00320),    # σ=3.10/1.12246
    "O":  (1.782, 0.00630),    # σ=2.00/1.12246 (oxide O; ε≈UFF)
    "F":  (2.584, 0.01040),    # σ=2.90/1.12246

    # Main-group nonmetals/metalloids
    # r_min targets (Å): Si~3.90, P~3.70, S~3.60, Cl~3.50
    "Si": (3.475, 0.00450),    # σ=3.90/1.12246
    "P":  (3.296, 0.00530),    # σ=3.70/1.12246
    "S":  (3.207, 0.01000),    # σ=3.60/1.12246
    "Cl": (3.118, 0.01200),    # σ=3.50/1.12246

    # Alkali / alkaline-earth metals (coarse; solids usually need EAM/MEAM/ionic models)
    # r_min targets (Å): Li~2.70, Na~3.80, K~4.60, Mg~3.50, Ca~4.20
    "Li": (2.405, 0.00120),    # σ=2.70/1.12246
    "Na": (3.385, 0.00450),    # σ=3.80/1.12246
    "K":  (4.098, 0.00380),    # σ=4.60/1.12246
    "Mg": (3.118, 0.00500),    # σ=3.50/1.12246
    "Ca": (3.742, 0.00400),    # σ=4.20/1.12246

    # Early metals / p-block
    # r_min targets (Å): Be~2.60, B~3.20, Al~4.00
    "Be": (2.316, 0.00300),    # σ=2.60/1.12246
    "B":  (2.851, 0.00500),    # σ=3.20/1.12246
    "Al": (3.564, 0.00400),    # σ=4.00/1.12246

    # 3d transition metals (smaller σ than O; ε kept small—LJ is only for scouting here)
    # r_min targets (Å): Fe~2.80, Ni~3.00, Cu~2.80, Zn~2.70
    "Fe": (2.495, 0.00150),    # σ=2.80/1.12246
    "Ni": (2.673, 0.00090),    # σ=3.00/1.12246 (matches your Ni≈3 Å aim)
    "Cu": (2.495, 0.00180),    # σ=2.80/1.12246
    "Zn": (2.405, 0.00180),    # σ=2.70/1.12246
}


# -----------------------------
# Optional VdW‑based inference as fallback
# -----------------------------
try:
    from ase.data import atomic_numbers, vdw_radii
    _ASE_DATA_OK = True
except Exception:
    _ASE_DATA_OK = False
    atomic_numbers = {"X": 0}
    vdw_radii = {0: 1.7}

_SIXTH_ROOT_OF_2 = 2.0 ** (1.0 / 6.0)

def _infer_sigma_from_vdw(r_vdw: float) -> float:
    return (2.0 * r_vdw) / _SIXTH_ROOT_OF_2

def _infer_eps_from_size(r_vdw: float, eps0: float) -> float:
    scale = (r_vdw / 1.5) ** 2
    return max(1e-6, eps0 * scale)


def _get_vdw_radius(symbol: str) -> float:
    if not _ASE_DATA_OK:
        return 1.7
    z = atomic_numbers.get(symbol, 6)
    return float(vdw_radii.get(z, 1.7))


def _pair_params_LB(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    sigma = 0.5 * (p1[0] + p2[0])
    eps = np.sqrt(p1[1] * p2[1])
    return sigma, float(eps)

# -----------------------------
# Numba‑accelerated core (with graceful fallback)
# -----------------------------
try:
    from numba import njit
    _NUMBA_OK = True
except Exception:
    _NUMBA_OK = False
    def njit(*args, **kwargs):
        def deco(f):
            return f
        return deco

@njit(fastmath=True)
def _lj_energy_forces_virial_pbc(positions, types, sigma_mat, eps_mat,
                                 rc2, shift_e_mat, cell, inv_cell):
    """
    Lennard-Jones energy/forces/virial with minimum image convention.
    """
    n = positions.shape[0]
    forces = np.zeros((n, 3), dtype=np.float64)
    virial = np.zeros((3, 3), dtype=np.float64)
    energy = 0.0

    for i in range(n - 1):
        ri0, ri1, ri2 = positions[i, 0], positions[i, 1], positions[i, 2]
        ti = types[i]
        for j in range(i + 1, n):
            # bare displacement
            dx0 = ri0 - positions[j, 0]
            dx1 = ri1 - positions[j, 1]
            dx2 = ri2 - positions[j, 2]
            rij = np.array([dx0, dx1, dx2])

            # fractional coords
            s = inv_cell @ rij
            # wrap into [-0.5,0.5)
            s -= np.rint(s)
            rij = cell @ s

            r2 = rij[0]*rij[0] + rij[1]*rij[1] + rij[2]*rij[2]
            if r2 == 0.0 or (rc2 > 0.0 and r2 > rc2):
                continue

            tj = types[j]
            sigma = sigma_mat[ti, tj]
            eps = eps_mat[ti, tj]

            sr2  = (sigma * sigma) / r2
            sr6  = sr2 * sr2 * sr2
            sr12 = sr6 * sr6

            e_ij = 4.0 * eps * (sr12 - sr6) - shift_e_mat[ti, tj]
            energy += e_ij

            coef = 24.0 * eps * (2.0 * sr12 - sr6) / r2
            fij = coef * rij

            forces[i, 0] += fij[0]; forces[i, 1] += fij[1]; forces[i, 2] += fij[2]
            forces[j, 0] -= fij[0]; forces[j, 1] -= fij[1]; forces[j, 2] -= fij[2]

            virial[0,0] += rij[0]*fij[0]; virial[0,1] += rij[0]*fij[1]; virial[0,2] += rij[0]*fij[2]
            virial[1,0] += rij[1]*fij[0]; virial[1,1] += rij[1]*fij[1]; virial[1,2] += rij[1]*fij[2]
            virial[2,0] += rij[2]*fij[0]; virial[2,1] += rij[2]*fij[1]; virial[2,2] += rij[2]*fij[2]

    return energy, forces, virial


# -----------------------------
# Calculator
# -----------------------------
class LJMixer(Calculator):
    """
    Multi‑species Lennard–Jones calculator with optional Numba acceleration.
    Non‑PBC (no MIC), O(N^2). Implements energy, forces, and stress.

    Parameters
    ----------
    species_params : dict[str, dict], optional
    pair_params : dict[str, dict], optional
    rc : float, optional
    shift : bool
    eps0 : float
    inference_mode : {"auto", "table", "vdw"}
    dump_params_to : str | None
    """

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self,
                 species_params: Optional[Dict[str, Dict[str, float]]] = None,
                 pair_params: Optional[Dict[str, Dict[str, float]]] = None,
                 rc: Optional[float] = None,
                 shift: bool = True,
                 eps0: float = 0.010,
                 inference_mode: str = "auto",
                 dump_params_to: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.species_params = species_params or {}
        self.pair_params = pair_params or {}
        self.rc = rc
        self.shift = shift
        self.eps0 = eps0
        self.inference_mode = inference_mode
        self.dump_params_to = dump_params_to

    # -----------------------------
    # Parameter resolution
    # -----------------------------
    def _resolve_per_element(self, symbols: list[str]) -> Dict[str, Tuple[float, float]]:
        uniq = sorted(set(symbols))
        resolved: Dict[str, Tuple[float, float]] = {}
        for s in uniq:
            if s in self.species_params:
                sp = self.species_params[s]
                resolved[s] = (float(sp["sigma"]), float(sp["epsilon"]))
            elif self.inference_mode == "table":
                resolved[s] = _DEFAULT_LJ_TABLE[s]
            elif self.inference_mode == "vdw":
                r = _get_vdw_radius(s)
                resolved[s] = (_infer_sigma_from_vdw(r), _infer_eps_from_size(r, self.eps0))
            else:  # auto
                if s in _DEFAULT_LJ_TABLE:
                    resolved[s] = _DEFAULT_LJ_TABLE[s]
                else:
                    r = _get_vdw_radius(s)
                    resolved[s] = (_infer_sigma_from_vdw(r), _infer_eps_from_size(r, self.eps0))
        return resolved

    # -----------------------------
    # Core calculation (Numba or NumPy)
    # -----------------------------
    def calculate(self, atoms=None, properties=('energy',), system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)
        positions = self.atoms.get_positions().astype(np.float64, copy=False)
        symbols   = self.atoms.get_chemical_symbols()
        cell      = self.atoms.get_cell().array.astype(np.float64)
        inv_cell  = np.linalg.inv(cell)
        volume    = float(abs(np.linalg.det(cell)))

        per_elem = self._resolve_per_element(symbols)

        if self.dump_params_to:
            try:
                with open(self.dump_params_to, 'w', encoding='utf-8') as f:
                    json.dump({k: {"sigma": v[0], "epsilon": v[1]} for k, v in per_elem.items()}, f, indent=2)
            except Exception:
                pass

        uniq = sorted(set(symbols))
        idx = {s: i for i, s in enumerate(uniq)}
        types = np.array([idx[s] for s in symbols], dtype=np.int64)
        m = len(uniq)

        sigma_mat = np.zeros((m, m), dtype=np.float64)
        eps_mat   = np.zeros((m, m), dtype=np.float64)
        for i, si in enumerate(uniq):
            for j, sj in enumerate(uniq):
                if f"{si}-{sj}" in self.pair_params:
                    p = self.pair_params[f"{si}-{sj}"]
                    sij, eij = float(p["sigma"]), float(p["epsilon"])
                elif f"{sj}-{si}" in self.pair_params:
                    p = self.pair_params[f"{sj}-{si}"]
                    sij, eij = float(p["sigma"]), float(p["epsilon"])
                else:
                    sij, eij = _pair_params_LB(per_elem[si], per_elem[sj])
                sigma_mat[i, j] = sij
                eps_mat[i, j] = eij

        if self.rc is None:
            rc2 = -1.0
            shift_e_mat = np.zeros_like(eps_mat)
        else:
            rc2 = float(self.rc) * float(self.rc)
            if self.shift:
                sr2c  = (sigma_mat * sigma_mat) / rc2
                sr6c  = sr2c * sr2c * sr2c
                sr12c = sr6c * sr6c
                shift_e_mat = 4.0 * eps_mat * (sr12c - sr6c)
            else:
                shift_e_mat = np.zeros_like(eps_mat)

        if _NUMBA_OK:
            energy, forces, virial = _lj_energy_forces_virial_pbc(
                positions, types, sigma_mat, eps_mat, rc2, shift_e_mat, cell, inv_cell)
        else:
            raise RuntimeError("Numba required for PBC version")

        self.results["energy"] = float(energy)
        self.results["forces"] = forces

        if volume > 1e-12:
            sigma_tensor = -virial / volume
            sxx, syy, szz = sigma_tensor[0,0], sigma_tensor[1,1], sigma_tensor[2,2]
            syz = 0.5*(sigma_tensor[1,2] + sigma_tensor[2,1])
            sxz = 0.5*(sigma_tensor[0,2] + sigma_tensor[2,0])
            sxy = 0.5*(sigma_tensor[0,1] + sigma_tensor[1,0])
            self.results["stress"] = np.array([sxx, syy, szz, syz, sxz, sxy], dtype=float)
        else:
            self.results["stress"] = np.zeros(6, dtype=float)

# Factory for simple use in configs
def lj_mixer(**kwargs) -> LJMixer:
    return LJMixer(**kwargs)


