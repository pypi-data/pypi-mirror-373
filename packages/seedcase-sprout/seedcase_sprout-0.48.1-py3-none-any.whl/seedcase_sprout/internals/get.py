from datetime import datetime
from typing import Any, TypeVar

T = TypeVar("T")


def _get_iso_timestamp() -> str:
    """Gets the current ISO timestamp compliant with the Data Package spec.

    Returns:
        The current ISO timestamp as a string. E.g. `2024-05-14T05:00:01+00:00`.
    """
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _get_nested_attr(
    base_object: Any, attributes: str, default: T | None = None
) -> T | None:
    """Returns the attribute specified by `attributes`.

    Tries to resolve the chain of attributes against `base_object`. Returns None
    or the specified default value if the attribute chain cannot be resolved.

    Args:
        base_object: The object to start resolving the attributes from.
        attributes: The chain of attributes as a dot-separated string.
        default: The default value to return if the attributes cannot be resolved.
            Defaults to None.

    Returns:
        The value at the end of the attribute chain.

    Raises:
        ValueError: If the attribute chain contains an element that is not a valid
            identifier.

    Examples:
        ```{python}
        class Inner:
            pass
        class Middle:
            inner: Inner = Inner()
        class Outer:
            middle: Middle = Middle()

        _get_nested_attr(Outer(), "middle.inner")
        ```
    """
    attributes_list = attributes.split(".")
    if any(not attribute.isidentifier() for attribute in attributes_list):
        raise ValueError(
            "`attributes` should contain valid identifiers separated by `.`."
        )

    try:
        for attribute in attributes_list:
            base_object = getattr(base_object, attribute)
    except AttributeError:
        return default

    return default if base_object is None else base_object
