# Interactive interface to display graphs

## Developer Setup

`This setup requires at least Python 3.10`

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

### Camera calibration

The `calib` command allows the user to calibrate the camera with the help of multiple modes to choose from. The `AUTO`
mode creates a calibration renderer which renders a ChArUco board which gets displayed by the projector. The connected
camera then uses this projection for calibration. Use this mode with **CAUTION** as the projector itself can introduce
distortions which we want to get rid off in the first place.

The `SEMI_AUTO` mode captures a set of images (in an even interval) automatically. The user has to move around a printed
out version of the ChArUco board in the camera's field of view. The captured images get used to calibrate the camara.

The `MANUAL` mode only captures images when the user presses the `C` key on a keyboard. The ChArUco board has again to
be printed out and moved around manually.

The data is stored in `.data/calib.json` regardless of the mode.

```shell
python src/main.py calib
```

### Marker Generation

```shell
python src/main.py gen markers
```

### Board Generation

```shell
python src/main.py gen board
```