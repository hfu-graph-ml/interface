# Interactive interface to display graphs

## Developer Setup

It is highly recommended to develop this project inside a python virtual environment (VENV). To get started run the
following commands in your favourite shell (on Linux). For further infos how the setup a VENV on Windows see
[here](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This

1. Creates a new VENV
2. Activates the VENV. Enter `deactivate` in your shell to exit the VENV
3. Install all required dependencies

After copying the `default.toml` config file to `config.toml` and making any neccesarry adjustments, run the application
like:

```shell
python src/main.py <SUBCOMMAND>
```

## Usage

### Debug Tracking

The `track` command allows to debug the ArUco tracking process. It uses the debug renderer which runs in the same thread
as the tracker.

```shell
python src/main.py track
```

### Marker Generation

```shell
python src/main.py gen markers
```

### Board Generation

```shell
python src/main.py gen board
```