import click

from .dataclass import ENV_VARS
from .utils import CONFIG_DIR, DEFAULT_FILE, ensure_config_dir, save_alias_field, set_default_alias


@click.command()
def create():
    """Create a new alias."""
    ensure_config_dir()
    name = click.prompt('Enter alias name (eg. prod, test)', type=str)
    alias_file = CONFIG_DIR / f'{name}.env'
    if alias_file.exists():
        click.echo(f"Alias '{name}' already exists.")
        return
    if alias_file.name == DEFAULT_FILE.name:
        click.echo(f"Invalid alias name '{name}'.")
        return

    alias_data = {}

    for key, value in ENV_VARS.items():
        prompt_kwargs = {'text': value.name, 'type': value.type, 'show_default': value.show_default}
        if bool(value.default):
            prompt_kwargs['default'] = alias_data[value.default]

        alias_data[key] = click.prompt(**prompt_kwargs)

    for key, value in alias_data.items():
        save_alias_field(name, key, value)

    # Set the default alias if it is the first alias created
    if not DEFAULT_FILE.exists():
        set_default_alias(name)

    click.echo(f"Alias '{name}' created.")
