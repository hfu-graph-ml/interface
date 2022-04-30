import click

from tracker.generator import Generator, Error


def execute(config_path: str, path: str, size: int, num: int, uniq: int, res: int):
    '''
    Generate a variable amount of ArUco markers and save them to disk.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    path : str
        Path where generated ArUco markers are saved
    size : int
        Size of the ArUco marker, e.g. 5X5
    num : int
        Number of ArUco markers to generate
    uniq : int
        Number of possible unique markers
    res : int
        Width/Height (Resolution) of the ArUco markers in pixels
    '''
    gen = Generator(size, uniq, path)

    err = gen.generate(num, res)
    if err != None:
        click.echo(err)
