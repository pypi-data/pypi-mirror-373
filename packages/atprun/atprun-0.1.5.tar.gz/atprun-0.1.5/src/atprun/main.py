import subprocess
from pprint import pprint

import typer
from atptools import DictDefault

default_config_path: str = "./.atprun.yml"
app = typer.Typer()


@app.callback()
def callback():
    """
    Awesome Portal Gun
    """
    typer.echo("Shooting Call back.")


@app.command()
def script(name: str):
    """
    Run script
    """
    typer.echo(f"Run script '{name}'")


if __name__ == "__main__":
    app()
