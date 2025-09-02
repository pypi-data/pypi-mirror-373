import subprocess
from pprint import pprint

import typer
from atptools import DictDefault

default_config_path: str = "./.atprun.yml"


def main(
    script: str = "",
) -> None:
    print("atprun:", "Start")
    print("script:", script)
    # load config file
    config: DictDefault = DictDefault()
    config.from_file(path=default_config_path)
    # print("config")
    # pprint(object=config)

    # get scripts
    scripts: DictDefault = config.get("scripts", {})
    # print("scripts:", scripts)

    # get script config
    script_config: DictDefault = scripts.get(script, {})
    pprint(script_config)

    # get command
    script_name: str = script_config.get("name", script)
    print("Execute:", script_name)

    # execute command
    command: str = script_config.get("run")
    if command is None:
        raise ValueError("No command found for script")
    subprocess.run(
        command,
        shell=True,
    )

    print("atprun:", "End")
    return None


if __name__ == "__main__":
    typer.run(main)
