# ATP-Run

## Installation

### Pipx

You can install ATP-Run using Pipx, which is a tool to install and run Python applications in isolated environments.

```bash
pipx install atprun
```

### uv tool

You can also install ATP-Run using the `uv tool`, which is a tool to install and run Python applications in isolated environments.

```bash
uv tool install atprun
```

### pip

You can also install ATP-Run using pip:

```bash
pip install atprun
```

### Pipenv

You can also install ATP-Run using Pipenv:

```bash
pipenv install atprun
```

## Usage

Define your scripts in a YAML configuration file (e.g., `atprun.yml`) and use the `atprun` command to run them.

```yaml
scripts:
  my_script:
    name: "My Script"
    run: "echo Hello, World!"
```

You can then run your script using the following command:

```bash
atprun script my_script
```
