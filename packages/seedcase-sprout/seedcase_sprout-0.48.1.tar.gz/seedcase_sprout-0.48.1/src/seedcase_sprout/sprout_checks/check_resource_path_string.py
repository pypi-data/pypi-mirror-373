from typing import Any

from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)

CHECKS_TYPE_ERROR_MESSAGE = "{field_value} is not of type '{field_type}'"


def check_resource_path_string(
    properties: dict[str, Any], index: int | None = None
) -> list[CheckError]:
    """Checks that the `path` field of a set of resource properties is of type string.

    Args:
        properties: The resource properties.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. An empty list if no error was found.
    """
    path = properties.get("path", "")
    if isinstance(path, str):
        return []

    return [
        CheckError(
            message=CHECKS_TYPE_ERROR_MESSAGE.format(
                field_value=path, field_type="string"
            ),
            json_path=get_json_path_to_resource_field("path", index),
            validator="type",
        )
    ]
