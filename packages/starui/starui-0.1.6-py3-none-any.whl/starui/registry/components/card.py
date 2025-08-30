from typing import Literal

from starhtml import FT, H1, H2, H3, H4, H5, H6, Div, P

from .utils import cn

HeadingLevel = Literal["h1", "h2", "h3", "h4", "h5", "h6"]


def Card(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn(
        "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
        class_name,
        cls,
    )
    return Div(*children, cls=classes, data_slot="card", **attrs)


def CardHeader(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        class_name,
        cls,
    )
    return Div(*children, cls=classes, data_slot="card-header", **attrs)


def CardTitle(
    *children,
    level: HeadingLevel = "h3",
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn("leading-none font-semibold", class_name, cls)

    heading_components = {
        "h1": H1,
        "h2": H2,
        "h3": H3,
        "h4": H4,
        "h5": H5,
        "h6": H6,
    }

    Heading = heading_components[level]
    return Heading(*children, cls=classes, data_slot="card-title", **attrs)


def CardDescription(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn("text-muted-foreground text-sm", class_name, cls)
    return P(*children, cls=classes, data_slot="card-description", **attrs)


def CardAction(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        class_name,
        cls,
    )
    return Div(*children, cls=classes, data_slot="card-action", **attrs)


def CardContent(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn("px-6", class_name, cls)
    return Div(*children, cls=classes, data_slot="card-content", **attrs)


def CardFooter(
    *children,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn("flex items-center px-6 [.border-t]:pt-6", class_name, cls)
    return Div(*children, cls=classes, data_slot="card-footer", **attrs)
