import importlib
import pkgutil

from threedi_cmd.plugins.models import AppRegistry

PLUGIN_NAME_PREFIX = "threedi_cmd_"


def discover() -> AppRegistry:
    """find installed plugins"""

    discovered_plugins = {
        name: importlib.import_module(name)
        for finder, name, is_pkg in pkgutil.iter_modules()
        if name.startswith(PLUGIN_NAME_PREFIX)
    }
    registry = AppRegistry({})
    for plugin in discovered_plugins.values():
        registry.apps.update(plugin.registry.apps)
    return registry
