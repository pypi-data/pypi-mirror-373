from typing import Any

from seedcase_sprout.check_datapackage import CheckError, RequiredFieldType
from seedcase_sprout.sprout_checks.check_fields_not_blank import (
    SPROUT_BLANK_ERROR_MESSAGE,
)
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)


def check_list_item_field_not_blank(
    properties: dict[str, Any],
    list_name: str,
    field_name: str,
    field_type: RequiredFieldType = RequiredFieldType.str,
) -> list[CheckError]:
    """Checks that the specified field of items in a list is not blank.

    Args:
        properties: The properties object containing the list.
        list_name: The name of the list field.
        field_name: The name of the item field.
        field_type: The type of the item field. Defaults to str.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    return [
        CheckError(
            message=SPROUT_BLANK_ERROR_MESSAGE.format(field_name=field_name),
            json_path=f"$.{list_name}[{index}].{field_name}",
            validator="blank",
        )
        for index, item in enumerate(properties.get(list_name, []))
        if item.get(field_name) == get_blank_value_for_type(field_type)
    ]
