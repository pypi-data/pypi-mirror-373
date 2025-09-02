from pytest import mark

from seedcase_sprout.sprout_checks.check_no_inline_data import check_no_inline_data
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)


@mark.parametrize("index", [None, 2])
def test_passes_if_data_not_set(index):
    """Should pass if inline data is not set."""
    assert check_no_inline_data({}, index) == []


@mark.parametrize("index", [None, 2])
def test_error_found_if_data_is_set(index):
    """Should find an error if inline data is set."""
    properties = {"data": "some data"}

    errors = check_no_inline_data(properties, index)

    assert len(errors) == 1
    assert errors[0].message
    assert errors[0].json_path == get_json_path_to_resource_field("data", index)
    assert errors[0].validator == "inline-data"
