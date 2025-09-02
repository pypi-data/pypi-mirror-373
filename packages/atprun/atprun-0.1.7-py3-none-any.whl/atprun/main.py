# https://typer.tiangolo.com/tutorial/package/

import subprocess
from pprint import pprint

import typer
from atptools import DictDefault

default_config_path: str = "./atprun.yml"
app = typer.Typer()
config: DictDefault = DictDefault()


@app.callback()
def callback():
    """
    Awesome Portal Gun 2
    """
    # load config file
    config.from_file(path=default_config_path)
    pass


@app.command()
def script(name: str):
    """
    Run script
    """

    # get script config
    scripts: DictDefault | None = config.get("scripts")
    if scripts is None:
        typer.secho(
            "Error: No scripts entity in config found",
            err=True,
            fg=typer.colors.RED,
        )
        return

    if name not in scripts:
        typer.secho(
            f"Error: Script '{name}' not found",
            err=True,
            fg=typer.colors.RED,
        )
        return

    script: DictDefault = scripts[name]

    # execute command
    command: str = script["run"]
    if len(command) <= 0:
        raise ValueError("No command found for script")
    subprocess.run(
        args=command,
        shell=True,
    )


if __name__ == "__main__":
    app()
