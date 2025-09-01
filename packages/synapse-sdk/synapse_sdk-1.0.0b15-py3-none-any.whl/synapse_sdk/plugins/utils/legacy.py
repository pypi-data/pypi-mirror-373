"""Legacy utility functions for backward compatibility."""

from pathlib import Path

from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.exceptions import ActionError

from .actions import get_action


def read_requirements(file_path):
    """Read and parse a requirements.txt file.

    Args:
        file_path: Path to the requirements.txt file

    Returns:
        List of requirement strings, or None if file doesn't exist
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return None

    requirements = []
    for line in file_path.read_text().splitlines():
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):
            requirements.append(stripped_line)
    return requirements


def run_plugin(
    action,
    params,
    plugin_config=None,
    plugin_path=None,
    modules=None,
    requirements=None,
    envs=None,
    debug=False,
    **kwargs,
):
    """Execute a plugin action with the specified parameters.

    Args:
        action: The action name to execute
        params: Parameters for the action
        plugin_config: Plugin configuration dictionary
        plugin_path: Path to the plugin directory
        modules: List of modules for debugging
        requirements: List of requirements
        envs: Environment variables dictionary
        debug: Whether to run in debug mode
        **kwargs: Additional keyword arguments

    Returns:
        Result of the action execution
    """
    from synapse_sdk.plugins.models import PluginRelease

    if not envs:
        envs = {}

    if debug:
        if plugin_path and plugin_path.startswith('http'):
            if not plugin_config:
                raise ActionError({'config': _('"plugin_path"가 url인 경우에는 "config"가 필수입니다.')})
            plugin_release = PluginRelease(config=plugin_config)
        else:
            plugin_release = PluginRelease(plugin_path=plugin_path)
            plugin_config = plugin_release.config

        if action not in plugin_release.actions:
            raise ActionError({'action': _('해당 액션은 존재하지 않습니다.')})

        if plugin_path:
            envs['SYNAPSE_DEBUG_PLUGIN_PATH'] = plugin_path

        if modules:
            envs['SYNAPSE_DEBUG_MODULES'] = ','.join(modules)

    else:
        if plugin_config is None:
            raise ActionError({'config': _('플러그인 설정은 필수입니다.')})

    action = get_action(
        action,
        params,
        config=plugin_config,
        requirements=requirements,
        envs=envs,
        debug=debug,
        **kwargs,
    )
    return action.run_action()
