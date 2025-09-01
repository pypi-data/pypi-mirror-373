"""Registry client for accessing component files."""

import re
from pathlib import Path
from typing import Any


class RegistryClient:
    """Client for accessing components in the local registry."""

    def __init__(self, registry_path: Path | None = None) -> None:
        self.registry_path = registry_path or Path(__file__).parent / "components"

    def list_components(self) -> list[str]:
        """List all available components."""
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Registry directory not found: {self.registry_path}"
            )

        return sorted(
            f.stem
            for f in self.registry_path.glob("*.py")
            if f.name not in ("__init__.py", "utils.py")
        )

    def component_exists(self, component_name: str) -> bool:
        """Check if a component exists."""
        return (self.registry_path / f"{component_name}.py").exists()

    def get_component_source(self, component_name: str) -> str:
        """Get component source code."""
        if not self.component_exists(component_name):
            raise FileNotFoundError(f"Component '{component_name}' not found")

        return (self.registry_path / f"{component_name}.py").read_text(encoding="utf-8")

    def get_component_metadata(self, component_name: str) -> dict[str, Any]:
        """Extract metadata from component."""
        source = self.get_component_source(component_name)

        # Extract description from docstring
        description = ""
        if match := re.search(r'"""([^"]+)"""', source, re.DOTALL):
            description = match.group(1).strip()
            if "Dependencies:" in description:
                description = description.split("Dependencies:")[0].strip()

        # Extract dependencies
        dependencies = []
        if match := re.search(r'Dependencies:\s*([^\n"]+)', source, re.IGNORECASE):
            deps_text = match.group(1).strip()
            if deps_text:
                dependencies = [d.strip() for d in deps_text.split(",") if d.strip()]

        return {
            "name": component_name,
            "description": description,
            "dependencies": dependencies,
        }
