from pathlib import Path

from dotenv import dotenv_values, load_dotenv, set_key, unset_key

CONFIG_DIR = Path.home() / '.config' / 'synapse'
DEFAULT_FILE = CONFIG_DIR / '__default__'


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_alias(alias_name):
    ensure_config_dir()
    alias_file = CONFIG_DIR / alias_name
    if not alias_file.exists():
        return None
    return dotenv_values(alias_file)


# Save or update a field in an alias .env file
def save_alias_field(alias_name, key, value):
    ensure_config_dir()
    alias_file = CONFIG_DIR / alias_name
    set_key(alias_file, key, value)


# Delete a field from an alias .env file
def delete_alias_field(alias_name, key):
    ensure_config_dir()
    alias_file = CONFIG_DIR / alias_name
    unset_key(alias_file, key)


# Delete an alias .env file
def delete_alias_file(alias_name):
    ensure_config_dir()
    alias_file = CONFIG_DIR / alias_name
    if alias_file.exists():
        alias_file.unlink()


def get_default_alias():
    ensure_config_dir()
    if DEFAULT_FILE.exists():
        default_data = dotenv_values(DEFAULT_FILE)
        return default_data.get('DEFAULT_ALIAS')
    return None


# Set the default alias
def set_default_alias(alias_name):
    ensure_config_dir()
    with open(DEFAULT_FILE, 'w') as f:
        f.write(f'DEFAULT_ALIAS={alias_name}\n')


def load_dotenv_default_alias():
    default_alias = get_default_alias()
    if default_alias is not None:
        load_dotenv(CONFIG_DIR / default_alias)
