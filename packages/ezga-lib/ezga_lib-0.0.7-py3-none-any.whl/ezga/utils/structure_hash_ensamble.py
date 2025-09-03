from ..utils.structure_hash_map import Structure_Hash_Map  # type: ignore
from ..core.interfaces import IHash
from typing import Dict, Any

# ======================================================================
#  Higher-level ensemble manager
# ======================================================================
class Structure_Hash_Ensemble(IHash):
    """
    Manage multiple Structure_Hash_Map instances of the SAME method but
    different precision settings; decide duplicate vs. new by voting.

    Parameters
    ----------
    method : str
        Hashing method tag ("rdf", "robust", "rbf", "rmse", "soap"*).
    vote_frac : float, optional
        Fractional agreement threshold (default 0.6).
    min_votes : int, optional
        Minimum number of agreeing precisions (default 5).
    precision_scales : tuple[float, ...], optional
        Scalars applied to precision knobs (grids / bin_width / symprec).
        1.0 is always enforced for the base member.
    **kwargs : Any
        Base factory kwargs (e.g., r_max, bin_width, density_grid, symprec...).
        These are scaled per precision where applicable.

    Notes
    -----
    • Each precision member keeps its own internal hash map; the base (scale=1.0)
      member is used for convenience metrics.
    • We intentionally DO NOT use per-map consensus APIs here to keep the
      separation of concerns clean.
    """

    def __init__(self, method: str = "rdf", /, **kwargs: Any):
        method = method.lower()
        if method not in Structure_Hash_Map._FACTORIES:
            raise ValueError(f"Unknown hashing method '{method}'.")
        # Avoid: got multiple values for keyword argument 'method'
        kwargs.pop("method", None)

        # Voting policy
        self.vote_frac: float = float(kwargs.pop("vote_frac", 0.6))
        self.min_votes: int = int(kwargs.pop("min_votes", 5))

        # Precision scales — ensure 1.0 is included exactly once, keep order
        scales_cfg = tuple(kwargs.pop("precision_scales", (0.5, 1.0, 2.0)))
        if 1.0 not in scales_cfg:
            ordered = (1.0,) + scales_cfg
        else:
            seen, ordered = set(), []
            for s in scales_cfg:
                if s not in seen:
                    seen.add(s)
                    ordered.append(float(s))
            ordered = tuple(ordered)
        self.scales: tuple[float, ...] = tuple(float(s) for s in ordered)

        self.method = method
        self._base_kwargs = dict(kwargs)

        # Helper: scale precision-sensitive keys per method
        def _scale_kwargs(scale: float) -> dict:
            kw = dict(self._base_kwargs)
            # ensure ensemble-only keys never propagate to child maps
            kw.pop("method", None)
            kw.pop("precision_scales", None)
            kw.pop("vote_frac", None)
            kw.pop("min_votes", None)

            if method == "robust":
                for k in ("pos_grid", "lat_grid", "e_grid", "v_grid"):
                    if k in kw:
                        kw[k] = float(kw[k]) * scale
            elif method == "rdf":
                # keep r_max fixed; vary resolution/quantisation
                if "bin_width" in kw:
                    kw["bin_width"] = float(kw["bin_width"]) * (1.0 / scale)
                if "density_grid" in kw:
                    kw["density_grid"] = float(kw["density_grid"]) * scale
                if "e_grid" in kw:
                    kw["e_grid"] = float(kw["e_grid"]) * scale
                if "v_grid" in kw:
                    kw["v_grid"] = float(kw["v_grid"]) * scale
            elif method in ("rbf", "rmse"):
                if "symprec" in kw:
                    kw["symprec"] = float(kw["symprec"]) * scale
            elif method == "soap":
                # if SOAP is available, you could scale n_max/l_max here
                pass
            # Disable any per-map internal ensemble to avoid recursion
            kw.setdefault("precision_scales", ())
            return kw

        # Build child maps (one per scale; index 0 is the base precision)
        self.maps: list[Structure_Hash_Map] = [
            Structure_Hash_Map(method=method, **_scale_kwargs(s)) for s in self.scales
        ]

    # ----------------------------- core ops ---------------------------------

    @staticmethod
    def _composition_key(container) -> str:
        return Structure_Hash_Map._composition_key(
            container.AtomPositionManager.atomCountDict
        )

    def _hashes(self, container) -> list[str]:
        """Compute hashes for every precision member in fixed order."""
        return [m._hash_fn(container) for m in self.maps]

    def _exists_flags(self, comp_key: str, hashes: list[str]) -> list[bool]:
        """Per-precision membership flags for given comp_key and hashes."""
        flags: list[bool] = []
        for m, h in zip(self.maps, hashes):
            bucket = m._hash_map.get(comp_key, set())
            flags.append(h in bucket)
        return flags

    def vote_duplicate(self, container) -> tuple[bool, int, int, list[bool]]:
        """
        Vote duplicate vs. new across precisions.
        Returns (is_duplicate, agree, total, flags_per_precision).
        """
        comp_key = self._composition_key(container)
        hashes = self._hashes(container)
        flags = self._exists_flags(comp_key, hashes)
        agree = int(sum(flags))
        total = len(flags)
        is_dup = (agree >= self.min_votes) and (agree / total >= self.vote_frac)
        return is_dup, agree, total, flags

    def add(self, container, *, force_rehash: bool = True) -> dict:
        """
        Consensus-aware add across all precisions.
        If duplicate by vote → do not add. Otherwise → add to *all* maps.
        Returns a report with per-precision hashes and hit flags.
        """
        apm = container.AtomPositionManager
        comp_key = self._composition_key(container)

        hashes = self._hashes(container)
        flags = self._exists_flags(comp_key, hashes)
        agree = int(sum(flags))
        total = len(flags)
        is_dup = (agree >= self.min_votes) and (agree / total >= self.vote_frac)

        added = False
        base_hash = hashes[0]
        if not is_dup:
            for m, h in zip(self.maps, hashes):
                m._hash_map.setdefault(comp_key, set()).add(h)
            # persist base hash in container metadata for convenience
            apm.metadata = getattr(apm, "metadata", {}) or {}
            apm.info_system = getattr(apm, "info_system", {}) or {}
            apm.metadata["hash"] = base_hash
            apm.info_system["hash"] = base_hash
            added = True

        collision = (agree > 0) and not is_dup

        return {
            "added": added,
            "duplicate": is_dup,
            "collision": collision,
            "hash_base": base_hash,
            "votes_agree": agree,
            "votes_total": total,
            "comp_key": comp_key,
            "scales": list(self.scales),
            "hashes": hashes,
            "exists": flags,
        }

    # ----------------------------- IHash compatibility -----------------------

    def add_structure(self, container, *, force_rehash: bool = True) -> bool:
        """
        IHash-compatible boolean add. Uses ensemble voting internally.
        Returns True if structure is considered NEW and was added; False if duplicate.
        """
        report = self.add(container, force_rehash=force_rehash)
        return bool(report["added"])

    def already_visited(self, container) -> bool:
        """
        True if, by the ensemble vote, this structure is considered a duplicate.
        """
        is_dup, _, _, _ = self.vote_duplicate(container)
        return is_dup

    # ----------------------------- proxies ---------------------------------

    def get_num_structures_for_composition(self, comp: dict) -> int:
        """Use base map for convenience metrics."""
        return self.maps[0].get_num_structures_for_composition(comp)

    def total_compositions(self) -> int:
        return self.maps[0].total_compositions()
