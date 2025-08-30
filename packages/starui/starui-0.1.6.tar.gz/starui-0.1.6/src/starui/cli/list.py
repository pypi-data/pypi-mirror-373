from pathlib import Path
from typing import Any

import typer
from rich.table import Table
from rich.text import Text

from starui.registry.client import RegistryClient

from .utils import console, error, info

CATEGORY_KEYWORDS = {
    "ui": ["button", "card", "badge", "avatar", "separator"],
    "form": ["input", "label", "select", "checkbox", "radio", "form", "field"],
    "layout": ["card", "container", "grid", "flex", "stack", "column"],
    "navigation": ["nav", "menu", "breadcrumb", "tab", "link"],
    "feedback": ["alert", "toast", "notification", "progress", "spinner"],
    "overlay": ["dialog", "modal", "popover", "tooltip", "dropdown"],
    "data": ["table", "list", "tree", "calendar", "chart"],
}


def is_installed(name: str) -> bool:
    cwd = Path.cwd()
    paths = [
        cwd / "components" / "ui" / f"{name}.py",
        cwd / "components" / f"{name}.py",
        cwd / "ui" / f"{name}.py",
    ]
    return any(p.exists() for p in paths)


def get_category(component: dict[str, Any]) -> str | None:
    name = component["name"].lower()
    desc = component.get("description", "").lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name or kw in desc for kw in keywords):
            return category
    return None


def list_command(
    category: str | None = typer.Option(None, "--category", help="Filter by category"),
    search: str | None = typer.Option(None, "--search", help="Search components"),
    installed: bool = typer.Option(False, "--installed", help="Show installed only"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
) -> None:
    """List available components."""

    try:
        client = RegistryClient()
        names = client.list_components()

        if not names:
            info("No components found")
            return

        # Get metadata
        components: list[dict[str, Any]] = []
        for name in names:
            try:
                meta = client.get_component_metadata(name)
                meta["installed"] = is_installed(name)
                components.append(meta)
            except Exception as e:
                error(f"Failed to load {name}: {e}")

        # Filter
        if installed:
            components = [c for c in components if c["installed"]]

        if search:
            search = search.lower()
            components = [
                c
                for c in components
                if search in c["name"].lower()
                or search in c.get("description", "").lower()
            ]

        if category:
            components = [c for c in components if get_category(c) == category.lower()]

        if not components:
            info("No components match filters")
            return

        # Display
        if verbose:
            console.print("[bold magenta]Components (Detailed)[/bold magenta]\n")
            for i, comp in enumerate(sorted(components, key=lambda x: x["name"])):
                if i > 0:
                    console.print()

                name = comp["name"]
                installed = comp.get("installed", False)
                desc = comp.get("description", "No description")
                deps = comp.get("dependencies", [])

                icon = "[bold green]◉" if installed else "[bold cyan]○"
                status = "(installed)" if installed else "(available)"
                console.print(f"{icon} {name}[/] [dim]{status}[/dim]")
                console.print(f"  {desc}")

                if deps:
                    console.print(f"  [dim]Dependencies: {', '.join(deps)}[/dim]")

                if cat := get_category(comp):
                    console.print(f"  [dim]Category: {cat}[/dim]")
        else:
            table = Table(
                title="Components", show_header=True, header_style="bold blue"
            )
            table.add_column("Name", style="cyan")
            table.add_column("Status", justify="center", min_width=8)
            table.add_column("Description")
            table.add_column("Dependencies", style="dim")

            for comp in sorted(components, key=lambda x: x["name"]):
                status = (
                    Text("✓ Installed", style="green")
                    if comp.get("installed")
                    else Text("Available", style="yellow")
                )
                desc = comp.get("description", "")
                if len(desc) > 60:
                    desc = desc[:57] + "..."

                deps = comp.get("dependencies", [])
                deps_text = ", ".join(deps[:3])
                if len(deps) > 3:
                    deps_text += f" +{len(deps) - 3}"
                elif not deps:
                    deps_text = "None"

                table.add_row(comp["name"], status, desc, deps_text)

            console.print(table)

        # Summary
        total = len(names)
        shown = len(components)
        installed_count = sum(1 for c in components if c.get("installed"))

        summary = f"\n[dim]Showing {shown} of {total} components"
        if installed_count:
            summary += f" ({installed_count} installed)"
        console.print(summary + "[/dim]")

    except Exception as e:
        error(f"Failed to list components: {e}")
        raise typer.Exit(1) from e
