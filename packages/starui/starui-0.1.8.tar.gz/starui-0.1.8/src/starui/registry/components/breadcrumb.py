from starhtml import FT, Icon
from starhtml import A as HTMLA
from starhtml import Li as HTMLLi
from starhtml import Nav as HTMLNav
from starhtml import Ol as HTMLOl
from starhtml import Span as HTMLSpan

from .utils import cn


def Breadcrumb(*children, class_name: str = "", cls: str = "", **attrs) -> FT:
    return HTMLNav(
        *children,
        aria_label="breadcrumb",
        data_slot="breadcrumb",
        cls=cn("", class_name, cls),
        **attrs,
    )


def BreadcrumbList(*children, class_name: str = "", cls: str = "", **attrs) -> FT:
    return HTMLOl(
        *children,
        data_slot="breadcrumb-list",
        cls=cn(
            "text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm break-words sm:gap-2.5",
            class_name,
            cls,
        ),
        **attrs,
    )


def BreadcrumbItem(*children, class_name: str = "", cls: str = "", **attrs) -> FT:
    return HTMLLi(
        *children,
        data_slot="breadcrumb-item",
        cls=cn("inline-flex items-center gap-1.5", class_name, cls),
        **attrs,
    )


def BreadcrumbLink(
    *children, href: str = "#", class_name: str = "", cls: str = "", **attrs
) -> FT:
    return HTMLA(
        *children,
        href=href,
        data_slot="breadcrumb-link",
        cls=cn("hover:text-foreground transition-colors", class_name, cls),
        **attrs,
    )


def BreadcrumbPage(*children, class_name: str = "", cls: str = "", **attrs) -> FT:
    return HTMLSpan(
        *children,
        role="link",
        aria_disabled="true",
        aria_current="page",
        data_slot="breadcrumb-page",
        cls=cn("text-foreground font-normal", class_name, cls),
        **attrs,
    )


def BreadcrumbSeparator(*children, class_name: str = "", cls: str = "", **attrs) -> FT:
    separator_content = children if children else (Icon("lucide:chevron-right"),)

    return HTMLLi(
        *separator_content,
        role="presentation",
        aria_hidden="true",
        data_slot="breadcrumb-separator",
        cls=cn("[&>svg]:size-3.5", class_name, cls),
        **attrs,
    )


def BreadcrumbEllipsis(class_name: str = "", cls: str = "", **attrs) -> FT:
    return HTMLSpan(
        Icon("lucide:more-horizontal", cls="size-4"),
        HTMLSpan("More", cls="sr-only"),
        role="presentation",
        aria_hidden="true",
        data_slot="breadcrumb-ellipsis",
        cls=cn("flex size-9 items-center justify-center", class_name, cls),
        **attrs,
    )
