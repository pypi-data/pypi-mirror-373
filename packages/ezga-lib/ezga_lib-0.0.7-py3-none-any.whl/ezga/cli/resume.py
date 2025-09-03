# SPDX-License-Identifier: GPL-3.0-only
from typer import Typer, Option
from pathlib import Path
from rich.console import Console

app = Typer(help="Resume/inspect past runs")
console = Console()

@app.command("from-archive")
def from_archive(path: Path = Option(..., "--archive", "-a", exists=True, readable=True)):
    console.print(f"Resuming from archive: {path}")
    # TODO: rehidratar estado y continuar
