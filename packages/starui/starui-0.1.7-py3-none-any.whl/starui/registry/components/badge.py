from typing import Literal

from starhtml import FT, A, Span
from starhtml import Button as HTMLButton

from .utils import cn, cva

BadgeVariant = Literal["default", "secondary", "destructive", "outline"]


badge_variants = cva(
    base="inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
    config={
        "variants": {
            "variant": {
                "default": "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
                "secondary": "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
                "destructive": "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
                "outline": "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
            }
        },
        "defaultVariants": {"variant": "default"},
    },
)


def Badge(
    *children,
    variant: BadgeVariant = "default",
    href: str | None = None,
    clickable: bool = False,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> FT:
    classes = cn(badge_variants(variant=variant), class_name, cls)

    if href:
        return A(*children, href=href, cls=classes, data_slot="badge", **attrs)

    if clickable:
        return HTMLButton(
            *children,
            cls=cn(classes, "cursor-pointer"),
            data_slot="badge",
            type="button",
            **attrs,
        )

    return Span(*children, cls=classes, data_slot="badge", **attrs)
