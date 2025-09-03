# SPDX-License-Identifier: GPL-3.0-only
from typer import Typer

app = Typer(help="EZGA – YAML-driven multi-objective GA")

# Importá las sub-APIs
from .run import app as run_app
from .resume import app as resume_app
from .wizard import app as wizard_app 

# Montá las sub-APIs como grupos
app.add_typer(run_app, name="run")         # => ezga run ...
app.add_typer(resume_app, name="resume")   # => ezga resume ...
app.add_typer(wizard_app, name="wizard")  # <-- and this one
