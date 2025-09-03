# ezga/simulator/calculators/constant_zero.py
import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from . import register_calculator

class ConstantZero(Calculator):
    """ASE-style calculator that always returns 0 energy and 0 forces."""
    implemented_properties = ["energy", "forces"]

    def calculate(self, atoms=None, properties=('energy',), system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)
        n = len(self.atoms)
        self.results["energy"] = 0.0
        self.results["forces"] = np.zeros((n, 3), dtype=float)

@register_calculator("constant_zero")
def constant_zero(**kwargs):
    """Factory so registry returns an ASE-compatible calculator instance."""
    return ConstantZero()
