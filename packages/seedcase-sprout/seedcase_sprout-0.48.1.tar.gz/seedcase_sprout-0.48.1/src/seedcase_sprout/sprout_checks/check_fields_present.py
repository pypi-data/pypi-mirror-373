from typing import Any

from seedcase_sprout.check_datapackage import CheckError, RequiredFieldType
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)

CHECKS_REQUIRED_ERROR_MESSAGE = "'{field_name}' is a required property"


def check_fields_present(
    properties: dict[str, Any],
    required_fields: dict[str, RequiredFieldType],
    index: int | None = None,
) -> list[CheckError]:
    """Checks that all fields in `required_fields` are present.

    For resource properties, an index may be supplied, if the resource properties are
    part of a set of package properties.

    Args:
        properties: The properties to check.
        required_fields: The set of required fields and their types.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    return [
        CheckError(
            message=CHECKS_REQUIRED_ERROR_MESSAGE.format(field_name=field),
            json_path=get_json_path_to_resource_field(field, index),
            validator="required",
        )
        for field in required_fields.keys()
        if properties.get(field) is None
    ]
