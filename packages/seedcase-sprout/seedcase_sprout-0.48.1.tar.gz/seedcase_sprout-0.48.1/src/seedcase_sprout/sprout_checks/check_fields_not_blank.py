from typing import Any

from seedcase_sprout.check_datapackage import CheckError, RequiredFieldType
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)

SPROUT_BLANK_ERROR_MESSAGE = "The '{field_name}' field is blank, please fill it in."


def check_fields_not_blank(
    properties: dict[str, Any],
    fields: dict[str, RequiredFieldType],
    index: int | None = None,
) -> list[CheckError]:
    """Checks that fields in `fields` are not blank if they are present.

    Fields not present in `properties` are not checked.

    For resource properties, an index may be supplied, if the resource properties are
    part of a set of package properties.

    Args:
        properties: The properties where the fields are.
        fields: A set of fields and their types.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    return [
        CheckError(
            message=SPROUT_BLANK_ERROR_MESSAGE.format(field_name=field),
            json_path=get_json_path_to_resource_field(field, index),
            validator="blank",
        )
        for field, type in fields.items()
        if properties.get(field) == get_blank_value_for_type(type)
    ]
