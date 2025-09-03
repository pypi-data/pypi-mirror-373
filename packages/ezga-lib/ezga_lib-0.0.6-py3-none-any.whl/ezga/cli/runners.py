# ezga/cli/runners.py
from ezga.factory import build_default_engine
from ezga.hise.manager import run_hise
from rich.console import Console

console = Console()

def run_standard_cli(cfg):
    """
    Run a standard single GA job using the provided configuration.

    Parameters
    ----------
    cfg : GAConfig
        Fully validated GA configuration object.

    Returns
    -------
    int
        Exit code: 0 on success.
    """
    # Build the engine using the default factory
    engine = build_default_engine(cfg)

    # Execute the GA run
    engine.run()

    console.print("[bold green]Run completed successfully.[/]")
    return 0


def run_hise_cli(cfg):
    """
    Run a Hierarchical Supercell Exploration (HiSE) job from the CLI.

    This function calls the HiSE manager to execute multiple supercell
    explorations, replacing the dataset input at each stage.

    Parameters
    ----------
    cfg : GAConfig
        Fully validated GA configuration object with an `hise` block.

    Returns
    -------
    int
        Exit code: 0 on success.
    """
    # Execute the HiSE pipeline
    stage_dirs = run_hise(cfg)

    # Optional: print a summary of stage directories
    console.print(f"[bold cyan]HiSE completed. Stage outputs:[/]\n{stage_dirs}")
    console.print("[bold green]HiSE (replace-input) completed successfully.[/]")
    return 0


def run_validation_cli(cfg):
    """
    Run a standard single GA job using the provided configuration.

    Parameters
    ----------
    cfg : GAConfig
        Fully validated GA configuration object.

    Returns
    -------
    int
        Exit code: 0 on success.
    """
    # Build the engine using the default factory
    engine = build_default_engine(cfg)

    console.print("[bold green]Run completed successfully.[/]")
    return 0