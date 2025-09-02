import re


def _to_snake_case(name: str) -> str:
    """Creates a snake-case version of a package or resource name.

    Args:
        name: The package or resource name.

    Returns:
        The package or resource name in snake case.

    """
    return name.replace(".", "_").replace("-", "_").lower()


def _to_camel_case(text: str) -> str:
    """Converts snake case to camel case.

    Args:
        text: The snake-case string to convert.

    Returns:
        The converted string in camel case.
    """
    first_part, *remaining_parts = text.split("_")
    return first_part + "".join(part.title() for part in remaining_parts)


def _to_dedented(text: str | None) -> str | None:
    """Dedents text by removing leading whitespace and tabs from each line.

    If it is not indented, it will be returned as is.
    If the first line starts with newlines, those will be removed.

    Args:
        text: The text to dedent.

    Returns:
        The dedented text or `None` if the input is `None`.
    """
    if text is None:
        return None

    # Remove leading whitespace or tabs from each line
    dedented = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)
    # Remove leading newlines from the very start
    return dedented.lstrip("\n")
