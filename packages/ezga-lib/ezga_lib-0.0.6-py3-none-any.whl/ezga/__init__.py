"""Public API of bansga.

Import here ONLY what you want users to see:
    from bansga import GAConfig, load_config, build_default_engine, GeneticAlgorithm
"""
# (Opcional) si también quieres dar estos atajos:
# from .aggregates import Operators, Evaluators, Selectors

# (Opcional) versión
try:
    from importlib.metadata import version
    __version__ = version("ezga")
except Exception:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = [
    "__version__",
]

def __getattr__(name):
    if name == "GeneticAlgorithm":
        from .core.engine import GeneticAlgorithm
        return GeneticAlgorithm
    raise AttributeError(name)