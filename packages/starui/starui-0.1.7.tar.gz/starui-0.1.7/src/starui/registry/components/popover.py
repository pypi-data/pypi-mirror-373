from uuid import uuid4

from starhtml import FT, Div
from starhtml.datastar import ds_position, ds_ref

from .button import Button
from .utils import cn, inject_signals, make_injectable


def Popover(*children, cls="relative inline-block", **attrs):
    signal = f"popover_{uuid4().hex[:8]}"
    return Div(*inject_signals(children, signal), cls=cls, **attrs)


def PopoverTrigger(*children, variant="default", cls="", **attrs):
    def _inject_signal(signal):
        return Button(
            *children,
            ds_ref(f"{signal}Trigger"),
            variant=variant,
            popovertarget=f"{signal}-content",
            popoveraction="toggle",
            id=f"{signal}-trigger",
            cls=cls,
            **attrs,
        )

    return make_injectable(_inject_signal)


def PopoverContent(*children, cls="", side="bottom", align="center", **attrs):
    def _inject_signal(signal):
        placement = f"{side}-{align}" if align != "center" else side

        def process_element(element):
            if callable(element) and getattr(element, "_is_popover_close", False):
                return element(signal)

            if (
                hasattr(element, "tag")
                and hasattr(element, "children")
                and element.children
            ):
                processed_children = tuple(
                    process_element(child) for child in element.children
                )
                return FT(element.tag, processed_children, element.attrs)

            return element

        processed_children = [process_element(child) for child in children]

        return Div(
            *processed_children,
            ds_ref(f"{signal}Content"),
            ds_position(
                anchor=f"{signal}-trigger",
                placement=placement,
                offset=8,
                flip=True,
                shift=True,
                hide=True,
            ),
            popover="auto",
            id=f"{signal}-content",
            role="dialog",
            aria_labelledby=f"{signal}-trigger",
            tabindex="-1",
            cls=cn(
                "z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none dark:border-input",
                cls,
            ),
            **attrs,
        )

    return make_injectable(_inject_signal)


def PopoverClose(*children, cls="", variant="ghost", size="sm", **attrs):
    def close_button(signal):
        return Button(
            *children,
            popovertarget=f"{signal}-content",
            popoveraction="hide",
            variant=variant,
            size=size,
            cls=cn("absolute right-2 top-2", cls),
            aria_label="Close popover",
            **attrs,
        )

    close_button._is_popover_close = True
    return close_button
