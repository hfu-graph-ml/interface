import os

from capture.calibration import Calibration, read_calibration_result
from config.config import Config

from typings.capture.calibration import CalibrationMode, CharucoCalibrationData
from typings.error import Err, Result, Error


def confirmation_prompt(text: str, default: bool | None = False) -> bool:
    '''
    This displays a confirmation prompt in which the user has to select 'y' or 'n'.

    Args:.
        text: The text message to display
        default: The default value returned. If None the user HAS to select either 'y' or 'n'.

    Returns:
        True if input is 'y' or False if input is 'n'.
    '''
    valid = False
    text = '{} [{}]: '.format(text, "y/n" if default is None else ("Y/n" if default else "y/N"))

    while not valid:
        inp = input(text).lower()

        if inp == '' and default != None:
            return default

        valid = inp in ['y', 'n']

    return inp == 'y'


def handle_calibration(cfg: Config, mode: str) -> Result[CharucoCalibrationData, Error]:
    '''
    Handle calibration flow. This first detects if a calibration jSON file exists. If this is not the case the user is
    asked to run the calibration. Denying this prompt exists the program. If a JSON file already exists the user is
    prompted if the file should be overwritten. If not, the existing JSON file gets used.

    Args:
        cfg: Config data

    Returns:
        Calibration data or error
    '''
    # First we try to convert the provided mode (string) into an enum
    result = CalibrationMode.from_str(mode)
    if result.is_err():
        return Err(result.error())

    # Construct calib JSON file path
    calib_file_path = os.path.join(cfg['capture']['path'], 'calib.pckl')

    # Check if we already have a calib JSON file
    if not os.path.exists(calib_file_path):
        if confirmation_prompt('No calibration file (.data/pckl.json) detected. Run calibration?'):
            c = Calibration(cfg)
            return c.calibrate_save(result.unwrap())

    if confirmation_prompt('Calibration file exists. Re-run calibration?'):
        c = Calibration(cfg)
        return c.calibrate_save(result.unwrap())
    else:
        return read_calibration_result(calib_file_path)
