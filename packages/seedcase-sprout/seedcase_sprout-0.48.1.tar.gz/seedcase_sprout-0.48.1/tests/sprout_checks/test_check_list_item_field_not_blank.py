from pytest import mark

from seedcase_sprout.check_datapackage import RequiredFieldType
from seedcase_sprout.sprout_checks.check_list_item_field_not_blank import (
    check_list_item_field_not_blank,
)
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)


def test_no_error_found_in_properties_without_list():
    """Should pass if the properties do not contain the specified list."""
    assert check_list_item_field_not_blank({}, "items", "field") == []


@mark.parametrize("items", [[], [{}, {}], [{"a": 1}, {"a": 2}]])
def test_no_error_found_when_list_does_not_contain_field(items):
    """Should pass if list items do not contain the field."""
    properties = {"items": items}

    assert check_list_item_field_not_blank(properties, "items", "field") == []


def test_no_error_found_when_fields_populated():
    """Should pass if all fields are populated."""
    properties = {"items": [{"field": "value"}, {"field": "value"}]}

    assert check_list_item_field_not_blank(properties, "items", "field") == []


def test_no_error_found_when_fields_are_of_wrong_type():
    """Should pass if the fields are present but of the wrong type."""
    properties = {"items": [{"field": "value"}, {"field": ""}]}

    assert (
        check_list_item_field_not_blank(
            properties, "items", "field", RequiredFieldType.list
        )
        == []
    )


@mark.parametrize(
    "field_type,value",
    [(RequiredFieldType.str, "value"), (RequiredFieldType.list, [1])],
)
def test_error_found_if_an_item_has_a_blank_field(field_type, value):
    """Should find an error if there is an item with a blank field."""
    properties = {
        "items": [{"field": value}, {"field": get_blank_value_for_type(field_type)}]
    }

    errors = check_list_item_field_not_blank(properties, "items", "field", field_type)

    assert len(errors) == 1
    assert "blank" in errors[0].message
    assert errors[0].json_path == "$.items[1].field"
    assert errors[0].validator == "blank"


@mark.parametrize("field_type", RequiredFieldType)
def test_error_found_if_multiple_items_have_a_blank_field(field_type):
    """Should find an error if there are multiple items with a blank field."""
    properties = {"items": [{"field": get_blank_value_for_type(field_type)}] * 2}

    errors = check_list_item_field_not_blank(properties, "items", "field", field_type)

    assert len(errors) == 2
    assert all(
        "blank" in error.message and error.validator == "blank" for error in errors
    )
    assert any(error.json_path == "$.items[0].field" for error in errors)
    assert any(error.json_path == "$.items[1].field" for error in errors)
