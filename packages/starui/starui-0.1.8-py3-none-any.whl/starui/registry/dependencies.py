import json

from fastcore.xml import FT
from starhtml import Script
from starhtml.starapp import DATASTAR_VERSION


class DependencyManager:
    def __init__(self):
        self._injected = set[str]()

    def require_handler(self, name: str, config: dict | None = None) -> FT | None:
        if name in self._injected:
            return None

        self._injected.add(name)
        config_json = json.dumps(config) if config else "{}"

        return Script(
            f"""
            import handlerPlugin from '/static/js/handlers/{name}.js';
            import {{ load, apply }} from 'https://cdn.jsdelivr.net/gh/starfederation/datastar@{DATASTAR_VERSION}/bundles/datastar.js';

            if (handlerPlugin.setConfig) handlerPlugin.setConfig({config_json});
            load(handlerPlugin);
            apply();
            """,
            type="module",
            id=f"starui-{name}-handler",
        )


_manager = DependencyManager()


def require_scroll_handler() -> FT | None:
    return _manager.require_handler("scroll")


def require_handler(name: str, config: dict | None = None) -> FT | None:
    return _manager.require_handler(name, config)


def ensure_component_dependencies(component_name: str) -> list[FT]:
    try:
        from .component_metadata import get_component_metadata

        if not (metadata := get_component_metadata(component_name)):
            return []

        scripts = []
        for handler_name in metadata.handlers:
            config = metadata.handler_configs.get(handler_name)
            if script := _manager.require_handler(handler_name, config):
                scripts.append(script)

        return scripts

    except ImportError:
        return []
