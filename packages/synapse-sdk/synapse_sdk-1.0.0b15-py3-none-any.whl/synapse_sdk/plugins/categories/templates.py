import shutil
from pathlib import Path

import yaml


def copy_project_category_template(category):
    copy_plugin(category)
    merge_config(category)


def copy_plugin(category):
    template_path = Path(__file__).parent / category / 'templates' / 'plugin'
    if not template_path.exists():
        return

    output_path = Path('plugin')
    shutil.copytree(template_path, output_path, dirs_exist_ok=True)


def merge_config(category):
    config_path = Path(__file__).parent / category / 'templates' / 'config.yaml'
    if not config_path.exists():
        return

    config_base_path = Path('config.yaml')

    config_base = yaml.safe_load(config_base_path.read_text(encoding='utf-8'))
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))

    config_base.update(config)
    config_base_path.write_text(yaml.dump(config_base, sort_keys=False), encoding='utf-8')
