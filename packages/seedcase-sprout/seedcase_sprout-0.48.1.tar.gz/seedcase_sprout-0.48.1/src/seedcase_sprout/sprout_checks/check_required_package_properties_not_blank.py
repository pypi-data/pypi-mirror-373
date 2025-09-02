from typing import Any

from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.sprout_checks.check_fields_not_blank import (
    check_fields_not_blank,
)
from seedcase_sprout.sprout_checks.check_list_item_field_not_blank import (
    check_list_item_field_not_blank,
)
from seedcase_sprout.sprout_checks.required_fields import (
    PACKAGE_SPROUT_REQUIRED_FIELDS,
)


def check_required_package_properties_not_blank(
    properties: dict[str, Any],
) -> list[CheckError]:
    """Checks that required package properties fields are not blank.

    Both Sprout-specific required fields and fields required by the Data Package
    standard are checked.

    Args:
        properties: The package properties.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    errors = check_fields_not_blank(properties, PACKAGE_SPROUT_REQUIRED_FIELDS)
    errors += check_list_item_field_not_blank(properties, "contributors", "title")
    errors += check_list_item_field_not_blank(properties, "sources", "title")
    errors += check_list_item_field_not_blank(properties, "licenses", "name")
    errors += check_list_item_field_not_blank(properties, "licenses", "path")
    return errors
