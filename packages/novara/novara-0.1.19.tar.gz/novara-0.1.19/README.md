# Novara cli

This is the cli for the novara api

## Commands

### configure

This command configures the cli to use a server and fetches some configs from it

### generate

This command will regenerate the Dockerfile from the novara.toml. Additionally the command can add dependencies to the toml file.

### init

This command initializes a new directory with a template already configured for the given service

### run

This command can either run the exploit locally or upload it to remote to execute it.

### status

This command will retreive the info for a container or optionally all containers including their current health

### stop

This command stops the currently running remote container.

### remove

This command will delete a exploit.

## Installation

You can install the CLI directly from PyPI:

```sh
pip install novara
```

Or build and install from source:

```sh
poetry build -f wheel
pip install dist/*.whl
```

The cli can then be access by running `novara [OPTIONS] command` in your terminal.

# Development

To install the CLI for development, use:

```sh
poetry install
poetry shell
```

Alternatively, you can install in editable mode with pip:

```sh
pip install -e .
```

## Project Structure

- `configs.py` - Manages all CLI configurations and settings
- `main.py` - Entry point that registers all available commands  
- `commands/` - Directory containing individual command implementations
  - Each command is implemented in `command_name.py`
- `utils.py` - Utility functions and helpers (including Logger class)

## Adding New Commands

1. Create a new file in `commands/command_name.py`
2. Implement your command function
3. Register it in `main.py`

## Publishing

To publish a new version of the CLI, simply push a GitHub tag:

```sh
git tag v1.0.0
git push origin v1.0.0
```

This will trigger the automated build