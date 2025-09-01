import click

from .utils import delete_alias_file, load_alias


@click.command()
@click.argument('name', required=True)
def delete(name):
    """Delete an alias."""
    alias_data = load_alias(name)
    if not alias_data:
        click.echo(f"Alias '{name}' does not exist.")
        return
    delete_alias_file(name)
    click.echo(f"Alias '{name}' deleted.")
