"""StarUI component registry system."""

from .client import RegistryClient
from .dependencies import ensure_component_dependencies, require_scroll_handler
from .loader import ComponentLoader, DependencyResolver
from .local import discover_components

__all__ = [
    "RegistryClient",
    "ComponentLoader",
    "DependencyResolver",
    "require_scroll_handler",
    "ensure_component_dependencies",
    "discover_components",
]
