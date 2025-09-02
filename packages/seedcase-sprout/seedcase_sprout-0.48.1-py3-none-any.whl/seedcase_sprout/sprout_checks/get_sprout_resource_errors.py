from typing import Any

import seedcase_sprout.check_datapackage as cdp
from seedcase_sprout.internals import (
    _create_resource_data_path,
)
from seedcase_sprout.sprout_checks.check_fields_not_blank import (
    check_fields_not_blank,
)
from seedcase_sprout.sprout_checks.check_fields_present import (
    check_fields_present,
)
from seedcase_sprout.sprout_checks.check_no_inline_data import check_no_inline_data
from seedcase_sprout.sprout_checks.check_resource_path_string import (
    check_resource_path_string,
)
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)
from seedcase_sprout.sprout_checks.is_resource_name_correct import (
    _is_resource_name_correct,
)
from seedcase_sprout.sprout_checks.required_fields import (
    RESOURCE_SPROUT_REQUIRED_FIELDS,
)


def get_sprout_resource_errors(
    properties: dict[str, Any], index: int | None = None
) -> list[cdp.CheckError]:
    """Checks the resource `properties` against Sprout-specific requirements only.

    Args:
        properties: The resource properties.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    errors = check_resource_path_string(properties, index)
    errors += _check_resource_path_format(properties, index)
    errors += check_no_inline_data(properties, index)
    errors += check_fields_not_blank(properties, RESOURCE_SPROUT_REQUIRED_FIELDS, index)
    errors += check_fields_present(properties, RESOURCE_SPROUT_REQUIRED_FIELDS, index)
    return errors


def _check_resource_path_format(
    properties: dict[str, Any], index: int | None = None
) -> list[cdp.CheckError]:
    """Checks if the data path in the resource properties has the correct format.

    As the path is constructed from the resource name, its format can only be checked
    if the resource name is correct. Type, required, and blank errors are not flagged
    here to avoid flagging them twice.

    Args:
        properties: The resource properties to check.
        index: The index of the resource properties. Defaults to None.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    name = properties.get("name")
    path = properties.get("path")

    if (
        # Do not check path if name is incorrect
        not _is_resource_name_correct(name)
        # Do not flag type and required errors twice
        or not isinstance(path, str)
        # Do not flag blank errors twice
        or path == ""
    ):
        return []

    expected_path = _create_resource_data_path(str(name))
    if path == expected_path:
        return []

    return [
        cdp.CheckError(
            message=f"Expected the path to be '{expected_path}' but found '{path}'.",
            json_path=get_json_path_to_resource_field("path", index),
            validator="pattern",
        )
    ]
