import click

from .utils import load_alias, save_alias_field


@click.command()
@click.argument('name', required=True)
@click.argument('field', required=True)
@click.argument('value', required=True)
def update(name, field, value):
    """Update a specific field in an alias."""
    alias_data = load_alias(name)
    if not alias_data:
        click.echo(f"Alias '{name}' does not exist.")
        return
    save_alias_field(name, field.upper(), value)
    click.echo(f"Alias '{name}' updated. Field '{field}' is now '{value}'.")
