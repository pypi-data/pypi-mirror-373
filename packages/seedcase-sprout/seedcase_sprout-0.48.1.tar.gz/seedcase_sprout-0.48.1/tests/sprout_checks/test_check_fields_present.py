from pytest import mark

from seedcase_sprout.check_datapackage import RequiredFieldType
from seedcase_sprout.sprout_checks.check_fields_present import (
    check_fields_present,
)
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)

REQUIRED_FIELDS = {"name": RequiredFieldType.str, "tags": RequiredFieldType.list}


@mark.parametrize("index", [None, 2])
def test_no_error_found_in_properties_with_required_fields(index):
    """Should pass properties with required fields present and populated."""
    properties = {"name": "My name", "tags": ["a", "b"]}

    assert check_fields_present(properties, REQUIRED_FIELDS, index) == []


@mark.parametrize("index", [None, 2])
def test_no_error_found_in_properties_with_required_fields_blank(index):
    """Should pass properties with required fields present but blank."""
    properties = {"name": "", "tags": []}

    assert check_fields_present(properties, REQUIRED_FIELDS, index) == []


@mark.parametrize("index", [None, 2])
def test_error_found_if_there_is_a_missing_required_field(index):
    """Should find an error if there is a missing required field."""
    properties = {"name": "My name"}

    errors = check_fields_present(properties, REQUIRED_FIELDS, index)

    assert len(errors) == 1
    assert "required" in errors[0].message
    assert errors[0].json_path == get_json_path_to_resource_field("tags", index)
    assert errors[0].validator == "required"


@mark.parametrize("index", [None, 2])
def test_error_found_if_there_are_multiple_missing_required_fields(index):
    """Should find an error if there are multiple missing required fields."""
    errors = check_fields_present({}, REQUIRED_FIELDS, index)

    assert len(errors) == 2
    assert all(error.validator == "required" for error in errors)
    assert any(
        error.json_path == get_json_path_to_resource_field("name", index)
        for error in errors
    )
    assert any(
        error.json_path == get_json_path_to_resource_field("tags", index)
        for error in errors
    )
