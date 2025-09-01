import click

from .utils import load_alias, set_default_alias


@click.command()
@click.argument('name', required=True)
def default(name):
    """Set an alias as the default."""
    alias_data = load_alias(name)
    if not alias_data:
        click.echo(f"Alias '{name}' does not exist.")
        return

    set_default_alias(name)
    click.echo(f"Alias '{name}' is now the default.")
