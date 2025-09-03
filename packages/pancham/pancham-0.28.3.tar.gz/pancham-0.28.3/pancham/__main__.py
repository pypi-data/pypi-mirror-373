from typing import Annotated, Optional

import typer

from .runner import PanchamRunner, start_pancham

app = typer.Typer()

@app.command()
def run(
        configuration: Annotated[str, typer.Argument(help = "Path to the Pancham configuration file")],
        data_configuration: Annotated[Optional[str], typer.Argument(help = "Path to the data mapping if individual files are being used")] = None,
        test: Annotated[bool, typer.Option(help="Run all the tests")] = False
):
    start_pancham(configuration, data_configuration, test = test)
