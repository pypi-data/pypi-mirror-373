from functools import lru_cache

from threedi_cmd.commands.app_definitions import registry
from threedi_cmd.plugins.tools import discover


@lru_cache()
def get_app():
    plugin_registry = discover()
    registry.apps.update(plugin_registry.apps)
    for app_name, app_meta in registry.apps.items():
        if not app_meta.add_to:
            continue
        add_to_meta = registry.apps[app_meta.add_to]
        add_to_meta.app.add_typer(app_meta.app, name=app_meta.name, help=app_meta.help)
    return registry.apps["core"].app


app = get_app()

if __name__ == "__main__":
    app = get_app()
    app()
