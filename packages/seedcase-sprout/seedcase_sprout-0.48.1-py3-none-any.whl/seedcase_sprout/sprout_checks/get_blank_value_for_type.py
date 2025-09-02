from typing import Any

from seedcase_sprout.check_datapackage import RequiredFieldType


def get_blank_value_for_type(type: RequiredFieldType) -> str | list[Any] | None:
    """Returns the blank value for each type of (required) field.

    Args:
        type: The type of the field.

    Returns:
        The corresponding blank value.
    """
    match type:
        case RequiredFieldType.str:
            return ""
        case RequiredFieldType.list:
            return []
        case _:
            return None
