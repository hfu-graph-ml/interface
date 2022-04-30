from typing import TypedDict
import toml
import os


class BackendOptions(TypedDict):
    host: str
    port: int


class Config(TypedDict):
    backend: BackendOptions


def read(path: str) -> Config:
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
        raise ValueError

    if not os.path.exists(path):
        raise FileNotFoundError

    try:
        config = toml.load(path, Config)
        return config
    except toml.TomlDecodeError:
        raise
