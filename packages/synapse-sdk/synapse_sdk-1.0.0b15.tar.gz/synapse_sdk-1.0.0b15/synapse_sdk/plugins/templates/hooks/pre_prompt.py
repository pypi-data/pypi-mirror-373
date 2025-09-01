import json
from pathlib import Path

from synapse_sdk.plugins.utils import get_plugin_categories
from synapse_sdk.utils.file import get_dict_from_file


def update_config(config):
    config['category'] = get_plugin_categories()
    return config


def main():
    cookiecutter_path = Path('cookiecutter.json')
    config = get_dict_from_file(cookiecutter_path)
    config = update_config(config)
    cookiecutter_path.write_text(json.dumps(config, indent=4, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
