import click

from .utils import CONFIG_DIR, DEFAULT_FILE, ensure_config_dir, get_default_alias


@click.command()
def list():
    """List all aliases."""
    ensure_config_dir()
    aliases = [f.stem for f in CONFIG_DIR.glob('*') if f.is_file() and f.stem != DEFAULT_FILE.stem]
    default_alias = get_default_alias()
    if not aliases:
        click.echo('No aliases found.')
        return
    for alias_name in aliases:
        if alias_name == default_alias:
            click.echo(f'{alias_name} (default)')
        else:
            click.echo(alias_name)
