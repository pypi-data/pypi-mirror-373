from typing import Any

from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.sprout_checks.check_fields_present import (
    check_fields_present,
)
from seedcase_sprout.sprout_checks.check_required_package_properties_not_blank import (  # noqa: E501
    check_required_package_properties_not_blank,
)
from seedcase_sprout.sprout_checks.required_fields import (
    PACKAGE_SPROUT_REQUIRED_FIELDS,
)


def get_sprout_package_errors(properties: dict[str, Any]) -> list[CheckError]:
    """Checks the package `properties` against Sprout-specific requirements only.

    Args:
        properties: The package properties.

    Returns:
        A list of errors. An empty list if no errors were found.
    """
    errors = check_required_package_properties_not_blank(properties)
    errors += check_fields_present(properties, PACKAGE_SPROUT_REQUIRED_FIELDS)
    return errors
