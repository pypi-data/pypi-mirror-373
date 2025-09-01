import click

from .utils import load_alias


@click.command()
@click.argument('name', required=True)
def read(name):
    """Read an alias."""
    alias_data = load_alias(name)
    if not alias_data:
        click.echo(f"Alias '{name}' does not exist.")
        return
    for key, value in alias_data.items():
        click.echo(f'{key}: {value}')
