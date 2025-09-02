from pytest import mark

from seedcase_sprout.check_datapackage import RequiredFieldType
from seedcase_sprout.sprout_checks.check_fields_not_blank import (
    check_fields_not_blank,
)
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)

FIELDS = {"name": RequiredFieldType.str, "tags": RequiredFieldType.list}


@mark.parametrize("index", [None, 2])
def test_no_error_found_in_properties_with_populated_fields(index):
    """Should pass properties with fields populated."""
    properties = {"name": "My name", "tags": ["a", "b"]}

    assert check_fields_not_blank(properties, FIELDS, index) == []


@mark.parametrize("index", [None, 2])
def test_no_error_found_in_properties_with_fields_missing(index):
    """Should pass properties without the specified fields."""
    assert check_fields_not_blank({}, FIELDS, index) == []


@mark.parametrize("index", [None, 2])
def test_error_found_if_properties_have_a_blank_field(index):
    """Should find an error if properties contain a blank field."""
    properties = {"name": "My name", "tags": []}

    errors = check_fields_not_blank(properties, FIELDS, index)

    assert len(errors) == 1
    assert "blank" in errors[0].message
    assert errors[0].json_path == get_json_path_to_resource_field("tags", index)
    assert errors[0].validator == "blank"


@mark.parametrize("index", [None, 2])
def test_error_found_if_properties_have_multiple_blank_fields(index):
    """Should find an error if properties contain multiple blank fields."""
    properties = {"name": "", "tags": []}

    errors = check_fields_not_blank(properties, FIELDS, index)

    assert len(errors) == 2
    assert all(error.validator == "blank" for error in errors)
    assert any(
        error.json_path == get_json_path_to_resource_field("name", index)
        for error in errors
    )
    assert any(
        error.json_path == get_json_path_to_resource_field("tags", index)
        for error in errors
    )
