from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.sprout_checks.exclude_non_sprout_resource_errors import (
    exclude_non_sprout_resource_errors,
)


def test_returns_unaltered_empty_list():
    """Should not alter an empty list."""
    assert exclude_non_sprout_resource_errors([]) == []


def test_returns_only_sprout_related_errors():
    """Should only remove errors not relevant for Sprout."""
    errors = [
        CheckError(
            message="'data' is a required property",
            json_path="$.data",
            validator="required",
        ),
        CheckError(
            message="'name' is a required property",
            json_path="$.name",
            validator="required",
        ),
        CheckError(
            message="123 is not of type 'array'", json_path="$.path", validator="type"
        ),
        CheckError(
            message="123 is not of type 'string'", json_path="$.path", validator="type"
        ),
        CheckError(
            message="123 is not of type 'array'",
            json_path="$.sources",
            validator="type",
        ),
    ]

    assert exclude_non_sprout_resource_errors(errors) == [
        CheckError(
            message="'name' is a required property",
            json_path="$.name",
            validator="required",
        ),
        CheckError(
            message="123 is not of type 'string'", json_path="$.path", validator="type"
        ),
        CheckError(
            message="123 is not of type 'array'",
            json_path="$.sources",
            validator="type",
        ),
    ]
