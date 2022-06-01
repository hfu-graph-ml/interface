from typing import Tuple, TypedDict
import toml
import os

import utils.checks as checks

ARUCO_ALLOWED_UNIQUES = [50, 100, 250, 1000]
ARUCO_ALLOWED_SIZES = [4, 5, 6, 7]

# NOTE (Techassi): Maybe move this generic error class into models


class Error:
    def __init__(self, message: str) -> None:
        self.message = message


class BackendOptions(TypedDict):
    host: str
    port: int


class TrackerOptions(TypedDict):
    max_failed_read: int
    debug: bool


class CalibrationOptions(TypedDict):
    number_images: int
    interval: float
    height: int
    width: int
    cols: int
    rows: int


class ArUcoOtions(TypedDict):
    uniques: int
    size: int


class CaptureOptions(TypedDict):
    calibration: CalibrationOptions
    tracker: TrackerOptions
    aruco: ArUcoOtions
    camera_id: int
    path: str
    fps: int


class RendererOptions(TypedDict):
    height: int
    width: int


class Config(TypedDict):
    renderer: RendererOptions
    backend: BackendOptions
    capture: CaptureOptions


def read(path: str, auto_validate: bool = False) -> Tuple[Config, Error]:
    '''
    Read a TOML file at 'path' and return a new Config class.

    Parameters
    ----------
    path : str
        Path to the TOML config file
    auto_validate : bool
        If this config should be auto validated

    Returns
    -------
    config : Tuple[Config, Error]
        The decoded config or err when error occured
    '''
    if not path:
        return None, Error('Invalid/empty path')

    if not os.path.exists(path):
        return None, Error('File not found')

    try:
        config = toml.load(path, Config)

        if not auto_validate:
            return config, None

        return config, validate(config)
    except toml.TomlDecodeError:
        return None, Error('TOML decode error')


def validate(cfg: Config) -> Error:
    '''
    Validate config values. Returns an error if validation failed.

    Parameters
    ----------
    cfg : Config
        Config to validate

    Returns
    -------
    err : Error
        Non None if validation failed
    '''
    if not cfg['backend']['host']:
        return Error('Invalid host')

    if cfg['backend']['port'] < 0 or cfg['backend']['port'] > 65535:
        return Error('Invalid port')

    if cfg['capture']['camera_id'] < 0:
        return Error('Invalid camera device ID')

    if cfg['capture']['fps'] < 0:
        return Error('Invalid FPS')

    if not checks.is_in(cfg['capture']['aruco']['uniques'], ARUCO_ALLOWED_UNIQUES):
        return Error(f'Invalid ArUco uniques number. Allowed are: {ARUCO_ALLOWED_UNIQUES}')

    if not checks.is_in(cfg['capture']['aruco']['size'], ARUCO_ALLOWED_SIZES):
        return Error(f'Invalid ArUco size. Allowed are: {ARUCO_ALLOWED_SIZES}')

    if cfg['capture']['tracker']['max_failed_read'] < 0:
        return Error('Invalid max failed read amount')

    if cfg['capture']['calibration']['number_images'] <= 0:
        return Error('Invalid number of calibration images. Choose value > 0. More than 5 recommended')

    if cfg['capture']['calibration']['interval'] <= 0:
        return Error('Invalid calibration interval. Choose value > 0')

    if cfg['capture']['calibration']['height'] < 0:
        return Error('Invalid calibration board height')

    if cfg['capture']['calibration']['width'] < 0:
        return Error('Invalid calibration board width')

    if cfg['capture']['calibration']['rows'] < 0:
        return Error('Invalid calibration board row count')

    if cfg['capture']['calibration']['cols'] < 0:
        return Error('Invalid calibration board col count')

    if cfg['renderer']['height'] < 0:
        return Error('Invalid renderer height')

    if cfg['renderer']['width'] < 0:
        return Error('Invalid renderer width')

    return None
