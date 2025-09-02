from typing import Any

from pytest import fixture, mark

from seedcase_sprout.examples import example_package_properties
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)
from seedcase_sprout.sprout_checks.get_sprout_package_errors import (
    get_sprout_package_errors,
)
from seedcase_sprout.sprout_checks.required_fields import (
    PACKAGE_SPROUT_REQUIRED_FIELDS,
)


@fixture
def properties() -> dict[str, Any]:
    return example_package_properties().compact_dict


def test_passes_full_package_properties(properties):
    """Should pass with a full set of package properties."""
    assert get_sprout_package_errors(properties) == []


@mark.parametrize("name,type", PACKAGE_SPROUT_REQUIRED_FIELDS.items())
def test_error_found_if_fields_are_blank(properties, name, type):
    """Should find an error if there is one required field that is present but blank."""
    properties[name] = get_blank_value_for_type(type)

    errors = get_sprout_package_errors(properties)

    assert len(errors) == 1
    assert errors[0].json_path == f"$.{name}"
    assert errors[0].validator == "blank"


@mark.parametrize("name", PACKAGE_SPROUT_REQUIRED_FIELDS.keys())
def test_error_found_if_required_fields_are_missing(properties, name):
    """Should find an error if there is a missing required field."""
    del properties[name]

    errors = get_sprout_package_errors(properties)

    assert len(errors) == 1
    assert errors[0].json_path == f"$.{name}"
    assert errors[0].validator == "required"
