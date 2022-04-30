import click

import cmd.gen as gen
import cmd.run as run


@click.group()
def cli():
    pass


@click.command('gen')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('-p', '--path', default='.markers', help='Path where generated ArUco markers are saved', type=str, show_default=True)
@click.option('-s', '--size', default=5, help='Width/Height of the ArUco markers in pixels', type=int, show_default=True)
@click.option('-n', '--number', default=10, help='Number of ArUco markers to generate', type=int, show_default=True)
@click.option('-u', '--uniques', default=50, help='Number of possible unique markers', type=int, show_default=True)
@click.option('-r', '--res', default=300, help='Size of the ArUco marker, e.g. 5X5', type=int, show_default=True)
def gen_cmd(config_path: str, path: str, size: int, number: int, uniques: int, res: int):
    gen.execute(config_path, path, size, number, uniques, res)


@click.command('run')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def run_cmd(config_path: str):
    run.execute(config_path)


cli.add_command(gen_cmd)
cli.add_command(run_cmd)


def execute():
    cli()
