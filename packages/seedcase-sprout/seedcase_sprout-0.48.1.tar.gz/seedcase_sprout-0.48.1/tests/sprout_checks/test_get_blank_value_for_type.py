from pytest import mark

from seedcase_sprout.check_datapackage import RequiredFieldType
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)


@mark.parametrize(
    "type,value",
    [
        (RequiredFieldType.str, ""),
        (RequiredFieldType.list, []),
        ("int", None),
        (None, None),
        ("something else", None),
    ],
)
def test_returns_expected_blank_value_for_each_type(type, value):
    """Should return the expected blank value for each type."""
    assert get_blank_value_for_type(type) == value
