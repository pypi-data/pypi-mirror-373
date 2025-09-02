from typing import Any

from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)


def check_no_inline_data(
    properties: dict[str, Any], index: int | None = None
) -> list[CheckError]:
    """Checks that the `data` field of a set of resource properties is not set.

    Args:
        properties: The resource properties.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. The empty list if no error was found.
    """
    if properties.get("data") is None:
        return []

    return [
        CheckError(
            message=(
                "Sprout doesn't use the 'data' field, instead it expects data "
                "in separate files that are given in the 'path' field."
            ),
            json_path=get_json_path_to_resource_field("data", index),
            validator="inline-data",
        )
    ]
