import click

import cmd.track as track
import cmd.calib as calib
import cmd.gen as gen
import cmd.run as run


@click.group()
def cli():
    pass


@cli.group('gen')
def gen_group():
    '''
    Generate tracking related markers or boards.
    '''
    pass


@gen_group.command('markers')
@click.option('-c', '--config', 'config_path', default='config.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('-n', '--number', default=10, help='Number of ArUco markers to generate', type=int, show_default=True)
@click.option('-r', '--res', default=300, help='Size of the ArUco marker in pixels', type=int, show_default=True)
def gen_markers(config_path: str, number: int, res: int):
    '''
    Generate ArUco tracking markers.
    '''
    gen.markers(config_path, number, res)


@gen_group.command('board')
@click.option('-c', '--config', 'config_path', default='config.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('--cols', default=7, help='Number of board columns', type=int, show_default=True)
@click.option('--rows', default=5, help='Number of board rows', type=int, show_default=True)
@click.option('-w', '--width', default=1920, help='Width of board in pixels', type=int, show_default=True)
@click.option('-h', '--height', default=1080, help='Height of board in pixels', type=int, show_default=True)
def gen_board(config_path: str, cols: int, rows: int, width, height):
    '''
    Generate ChArUco calibration board.
    '''
    gen.board(config_path, cols, rows, width, height)


@cli.command('run')
@click.option('-c', '--config', 'config_path', default='config.toml', help='Path to the TOML config file', type=str, show_default=True)
def run_cmd(config_path: str):
    '''
    Run the main application.
    '''
    run.execute(config_path)


@cli.command('track')
@click.option('-c', '--config', 'config_path', default='config.toml', help='Path to the TOML config file', type=str, show_default=True)
def track_cmd(config_path: str):
    '''
    Run tracking in debug mode.
    '''
    track.execute(config_path)


@cli.command('calib')
@click.option('-c', '--config', 'config_path', default='config.toml', help='Path to the TOML config file', type=str, show_default=True)
def calibrate_cmd(config_path: str):
    '''
    Calibrate the camera in manual mode.
    '''
    calib.execute(config_path)


def execute():
    cli()
