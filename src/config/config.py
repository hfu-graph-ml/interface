from typing import Tuple, TypedDict
import toml
import os

# NOTE (Techassi): Maybe move this generic error class into models


class Error:
    def __init__(self, message: str) -> None:
        self.message = message


class BackendOptions(TypedDict):
    host: str
    port: int


class TrackerOptions(TypedDict):
    uniques: int
    path: str
    size: int


class Config(TypedDict):
    backend: BackendOptions
    tracker: TrackerOptions


def read(path: str) -> Tuple[Config, Error]:
    '''
    Read a TOML file at 'path' and return a new Config class.

    Parameters
    ----------
    path : str
        Path to the TOML config file

    Returns
    -------
    config : Config
        The decoded config
    '''
    if not path:
        return None, Error('Invalid/empty path')

    if not os.path.exists(path):
        return None, Error('File not found')

    try:
        config = toml.load(path, Config)
        return config, None
    except toml.TomlDecodeError:
        return None, Error('TOML decode error')
