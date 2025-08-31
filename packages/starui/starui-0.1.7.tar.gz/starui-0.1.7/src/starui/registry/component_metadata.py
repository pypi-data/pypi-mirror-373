from typing import Any

from pydantic import BaseModel, Field


class ComponentMetadata(BaseModel):
    name: str
    description: str = ""
    dependencies: list[str] = Field(default_factory=list)
    packages: list[str] = Field(default_factory=list)
    css_files: list[str] = Field(default_factory=list)
    css_imports: list[str] = Field(default_factory=list)
    handlers: list[str] = Field(default_factory=list)
    handler_configs: dict[str, dict] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "ignore"}


def _component(
    name: str,
    desc: str,
    deps: list[str] | None = None,
    handlers: list[str] | None = None,
    **kwargs,
) -> ComponentMetadata:
    return ComponentMetadata(
        name=name,
        description=desc,
        dependencies=deps or [],
        handlers=handlers or [],
        **kwargs,
    )


COMPONENT_REGISTRY = {
    "code_block": _component(
        "code_block",
        "Code block with syntax highlighting",
        ["utils"],
        packages=["starlighter"],
        options={
            "available_themes": [
                "github",
                "monokai",
                "dracula",
                "catppuccin",
                "vscode",
            ],
            "default_theme": "github",
        },
    ),
    "theme_toggle": _component(
        "theme_toggle", "Theme toggle button", ["utils", "button"]
    ),
    "sheet": _component("sheet", "Slide-out panel", ["utils", "button"]),
    "dialog": _component("dialog", "Modal dialog", ["utils", "button"]),
    "button": _component("button", "Button with variants", ["utils"]),
    "alert": _component("alert", "Alert notifications", ["utils"]),
    "badge": _component("badge", "Badge for labels", ["utils"]),
    "breadcrumb": _component("breadcrumb", "Breadcrumb navigation", ["utils"]),
    "card": _component("card", "Card container", ["utils"]),
    "checkbox": _component("checkbox", "Checkbox input", ["utils"]),
    "hover_card": _component(
        "hover_card", "Hover card with content", ["utils"], ["position"]
    ),
    "input": _component("input", "Form input", ["utils"]),
    "label": _component("label", "Form label", ["utils"]),
    "popover": _component("popover", "Popover with trigger", ["utils"], ["position"]),
    "radio_group": _component("radio_group", "Radio button group", ["utils"]),
    "select": _component("select", "Dropdown selection", ["utils"], ["position"]),
    "switch": _component("switch", "Toggle switch", ["utils"]),
    "tabs": _component("tabs", "Tabbed interface", ["utils"]),
    "textarea": _component("textarea", "Multi-line text input", ["utils"]),
    "typography": _component(
        "typography",
        "Typography components with beautiful defaults",
        ["utils"],
        css_imports=['@plugin "@tailwindcss/typography";'],
    ),
    "utils": _component("utils", "Class name utilities"),
}


def get_component_metadata(component_name: str) -> ComponentMetadata | None:
    return COMPONENT_REGISTRY.get(component_name)
