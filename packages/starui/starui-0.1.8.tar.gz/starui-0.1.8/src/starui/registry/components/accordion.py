from typing import Any, Literal
from uuid import uuid4

from starhtml import FT, Button, Div, Icon
from starhtml.datastar import ds_on_click, ds_show, ds_signals, value

from .utils import cn, inject_signals, make_injectable

AccordionType = Literal["single", "multiple"]


def Accordion(
    *children: Any,
    type: AccordionType = "single",
    collapsible: bool = False,
    default_value: str | list[str] | None = None,
    signal: str = "",
    class_name: str = "",
    cls: str = "",
    **attrs: Any,
) -> FT:
    signal = signal or f"accordion_{uuid4().hex[:8]}"

    match (type, default_value):
        case ("single", _):
            initial_value = value(default_value or "")
        case ("multiple", None):
            initial_value = value([])
        case ("multiple", str() as val):
            initial_value = value([val])
        case ("multiple", val):
            initial_value = value(val)

    processed_children = inject_signals(children, signal, type, collapsible)

    return Div(
        *processed_children,
        ds_signals(**{signal: initial_value}),
        data_type=type,
        data_collapsible=str(collapsible).lower(),
        cls=cn("w-full", class_name, cls),
        **attrs,
    )


def AccordionItem(
    *children: Any,
    value: str,
    class_name: str = "",
    cls: str = "",
    **attrs: Any,
) -> FT:
    def _inject_signal(signal, type="single", collapsible=False):
        processed_children = inject_signals(children, signal, type, collapsible, value)
        return Div(
            *processed_children,
            data_value=value,
            cls=cn("border-b", class_name, cls),
            **attrs,
        )

    return make_injectable(_inject_signal)


def AccordionTrigger(
    *children: Any,
    class_name: str = "",
    cls: str = "",
    **attrs: Any,
) -> FT:
    def _inject_signal(signal, type="single", collapsible=False, item_value=None):
        if not item_value:
            raise ValueError("AccordionTrigger must be used inside AccordionItem")

        is_single = type == "single"

        if is_single:
            click_expr = (
                f"${signal} = ${signal} === '{item_value}' ? '' : '{item_value}'"
                if collapsible
                else f"${signal} = '{item_value}'"
            )
            is_open_expr = f"${signal} === '{item_value}'"
        else:
            click_expr = (
                f"${signal} = ${signal}.includes('{item_value}') "
                f"? ${signal}.filter(v => v !== '{item_value}') "
                f": [...${signal}, '{item_value}']"
            )
            is_open_expr = f"${signal}.includes('{item_value}')"

        return Div(
            Button(
                *children,
                Icon(
                    "lucide:chevron-down",
                    cls="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
                    data_attr_style=f"({is_open_expr}) ? 'transform: rotate(180deg)' : 'transform: rotate(0deg)'",
                ),
                ds_on_click(click_expr),
                type="button",
                cls=cn(
                    "flex w-full flex-1 items-center justify-between py-4 text-sm font-medium transition-all hover:underline text-left",
                    class_name,
                    cls,
                ),
                **attrs,
            ),
            cls="flex",
        )

    return make_injectable(_inject_signal)


def AccordionContent(
    *children: Any,
    class_name: str = "",
    cls: str = "",
    **attrs: Any,
) -> FT:
    def _inject_signal(signal, type="single", collapsible=False, item_value=None):
        if not item_value:
            raise ValueError("AccordionContent must be used inside AccordionItem")

        show_expr = (
            f"${signal} === '{item_value}'"
            if type == "single"
            else f"${signal}.includes('{item_value}')"
        )

        return Div(
            Div(
                *children,
                cls=cn("pb-4 pt-0", class_name),
            ),
            ds_show(show_expr),
            cls=cn("overflow-hidden text-sm", cls),
            **attrs,
        )

    return make_injectable(_inject_signal)
