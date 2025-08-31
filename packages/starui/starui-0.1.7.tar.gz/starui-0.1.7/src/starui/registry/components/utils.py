from collections.abc import Callable
from typing import Any


def cn(*classes: Any) -> str:
    result_classes: list[str] = []

    for cls in classes:
        if not cls:
            continue

        if isinstance(cls, str):
            result_classes.append(cls)
        elif isinstance(cls, dict):
            for class_name, condition in cls.items():
                if condition:
                    result_classes.append(str(class_name))
        elif isinstance(cls, list | tuple):
            result_classes.append(cn(*cls))
        else:
            result_classes.append(str(cls))

    return " ".join(result_classes)


def cva(base: str = "", config: dict[str, Any] | None = None) -> Callable[..., str]:
    if config is None:
        config = {}

    variants = config.get("variants", {})
    compound_variants = config.get("compoundVariants", [])
    default_variants = config.get("defaultVariants", {})

    def variant_function(**props: Any) -> str:
        classes = [base] if base else []

        # Merge defaults with props
        final_props = {**default_variants, **props}

        # Apply variants
        for variant_key, variant_values in variants.items():
            prop_value = final_props.get(variant_key)
            if prop_value and prop_value in variant_values:
                classes.append(variant_values[prop_value])

        # Apply compound variants
        for compound in compound_variants:
            compound_class = compound.get("class", "")
            if not compound_class:
                continue

            matches = True
            for key, value in compound.items():
                if key == "class":
                    continue
                if final_props.get(key) != value:
                    matches = False
                    break

            if matches:
                classes.append(compound_class)

        return cn(*classes)

    return variant_function


def make_injectable(func: Callable) -> Callable:
    """Mark a function as injectable for signal propagation."""
    func._inject_signal = func
    return func


def inject_signals(children: list[Any], *args: Any) -> list[Any]:
    """Process children and inject signals where possible."""
    result = []
    for child in children:
        if hasattr(child, "_inject_signal") and callable(child._inject_signal):
            result.append(child._inject_signal(*args))
        else:
            result.append(child)
    return result
