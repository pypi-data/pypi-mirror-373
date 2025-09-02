from pathlib import Path
from typing import cast

from pytest import ExceptionInfo, fixture, mark, raises

from seedcase_sprout.check_datapackage import CheckError
from seedcase_sprout.check_properties import (
    check_package_properties,
    check_properties,
    check_resource_properties,
)
from seedcase_sprout.examples import example_resource_properties
from seedcase_sprout.properties import (
    ContributorProperties,
    LicenseProperties,
    PackageProperties,
    ResourceProperties,
    SourceProperties,
)
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)
from seedcase_sprout.sprout_checks.required_fields import (
    PACKAGE_SPROUT_REQUIRED_FIELDS,
    RESOURCE_SPROUT_REQUIRED_FIELDS,
)


@fixture
def properties():
    return PackageProperties(
        name="package-1",
        id="abc1",
        title="Package 1",
        description="A package.",
        version="1.0.0",
        created="2024-05-14T05:00:01+00:00",
        licenses=[LicenseProperties(name="a-license")],
        contributors=[ContributorProperties(title="a contributor")],
        sources=[SourceProperties(title="a source")],
        resources=[
            ResourceProperties(
                name="resource-1",
                title="Resource 1",
                description="A resource.",
            ),
            ResourceProperties(
                name="resource-2",
                title="Resource 2",
                description="A second resource.",
            ),
        ],
    )


def test_passes_correct_properties(properties):
    """Should pass if all required properties are present and correct."""
    assert check_properties(properties) == properties
    assert check_package_properties(properties) == properties
    assert check_resource_properties(properties.resources[0]) == properties.resources[0]
    assert check_resource_properties(properties.resources[1]) == properties.resources[1]

    # Even when resources isn't there.
    delattr(properties, "resources")
    assert check_properties(properties) == properties


def test_error_incorrect_argument():
    """Should be an error if it isn't a `*Properties` object."""
    with raises(TypeError):
        check_properties(ResourceProperties())

    with raises(TypeError):
        check_resource_properties(PackageProperties())

    with raises(TypeError):
        check_properties("")

    with raises(TypeError):
        check_properties([1, 2, 3])

    with raises(TypeError):
        check_package_properties([1, 2, 3])

    with raises(TypeError):
        check_package_properties("")

    with raises(TypeError):
        check_resource_properties([1, 2, 3])

    with raises(TypeError):
        check_resource_properties("")


@mark.parametrize("field", PACKAGE_SPROUT_REQUIRED_FIELDS.keys())
def test_error_missing_required_package_properties(properties, field):
    """Should be an error if a required package properties is missing."""
    delattr(properties, field)

    # All properties checks
    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.{field}"
    assert errors[0].validator == "required"

    # Package only checks
    with raises(ExceptionGroup) as error_info:
        check_package_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.{field}"
    assert errors[0].validator == "required"


@mark.parametrize(
    "item,value,validator",
    [
        ("name", "a name with spaces", "pattern"),
        ("title", 123, "type"),
        ("homepage", "not a URL", "format"),
        ("resources", 123, "type"),
    ],
)
def test_error_incorrect_property_values(properties, item, value, validator):
    """Should be an error when the property value is incorrect."""
    setattr(properties, item, value)

    with raises(ExceptionGroup) as error_info:
        check_package_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.{item}"
    assert errors[0].validator == f"{validator}"

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.{item}"
    assert errors[0].validator == f"{validator}"


@mark.parametrize("name,type", PACKAGE_SPROUT_REQUIRED_FIELDS.items())
def test_error_blank_package_properties(properties, name, type):
    """Should be an error when a required package field is blank."""
    setattr(properties, name, get_blank_value_for_type(type))

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    blank_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "blank"
    ]

    assert len(blank_errors) == 1
    assert blank_errors[0].json_path == f"$.{name}"

    with raises(ExceptionGroup) as error_info:
        check_package_properties(properties)

    blank_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "blank"
    ]

    assert len(blank_errors) == 1
    assert blank_errors[0].json_path == f"$.{name}"


def test_error_missing_required_nested_properties(properties):
    """Should have errors when the nested required properties are missing."""
    setattr(properties, "licenses", [{}])
    setattr(properties, "contributors", [{}])
    setattr(properties, "sources", [{}])

    with raises(ExceptionGroup) as error_info:
        check_package_properties(properties)

    required_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "required"
    ]
    assert [error.json_path for error in required_errors] == [
        "$.contributors[0].title",
        "$.licenses[0].name",
        "$.licenses[0].path",
        "$.sources[0].title",
    ]

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    required_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "required"
    ]
    assert [error.json_path for error in required_errors] == [
        "$.contributors[0].title",
        "$.licenses[0].name",
        "$.licenses[0].path",
        "$.sources[0].title",
    ]


# Resource properties specific --------------------------------------------


@mark.parametrize(
    "field",
    RESOURCE_SPROUT_REQUIRED_FIELDS.keys(),
)
def test_error_missing_required_resource_properties(properties, field):
    """Should be an error if a required resource properties is missing."""
    delattr(properties.resources[0], field)

    with raises(ExceptionGroup) as error_info:
        check_resource_properties(properties.resources[0])

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.{field}"
    assert errors[0].validator == "required"

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == f"$.resources[0].{field}"
    assert errors[0].validator == "required"


@mark.parametrize("name,type", RESOURCE_SPROUT_REQUIRED_FIELDS.items())
def test_error_blank_resource_properties(properties, name, type):
    """Should be an error when one required resource field is blank."""
    setattr(properties.resources[0], name, get_blank_value_for_type(type))

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    blank_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "blank"
    ]

    assert len(blank_errors) == 1
    assert blank_errors[0].json_path == f"$.resources[0].{name}"

    with raises(ExceptionGroup) as error_info:
        check_resource_properties(properties.resources[0])

    blank_errors = [
        error for error in _as_check_errors(error_info) if error.validator == "blank"
    ]

    assert len(blank_errors) == 1
    assert blank_errors[0].json_path == f"$.{name}"


def test_errors_flagged_for_fields_with_multipart_name():
    """Errors should be flagged when the name of the field has more than one word."""
    properties = example_resource_properties()
    assert properties.schema
    properties.schema.primary_key = []

    with raises(ExceptionGroup) as error_info:
        check_resource_properties(properties)

    assert all(
        error.json_path == "$.schema.primaryKey"
        for error in _as_check_errors(error_info)
    )


def test_error_incorrect_resource_property_values(properties):
    """Should be an error when the property value is incorrect."""
    properties.resources[0].title = 123

    with raises(ExceptionGroup) as error_info:
        check_resource_properties(properties.resources[0])

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == "$.title"
    assert errors[0].validator == "type"

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) == 1
    assert errors[0].json_path == "$.resources[0].title"
    assert errors[0].validator == "type"


@mark.parametrize(
    "path", ["", [], 123, str(Path("resources", "1")), "/bad/path/data.csv"]
)
def test_error_no_resource_name_in_path(properties, path):
    """Should be an error when the resource name isn't in the `path` or is empty."""
    properties.resources[0].path = path

    with raises(ExceptionGroup) as error_info:
        check_resource_properties(properties.resources[0])

    errors = _as_check_errors(error_info)
    assert len(errors) >= 1
    assert all(error.json_path.endswith("path") for error in errors)

    with raises(ExceptionGroup) as error_info:
        check_properties(properties)

    errors = _as_check_errors(error_info)
    assert len(errors) >= 1
    assert all(error.json_path.endswith("path") for error in errors)


def _as_check_errors(
    error_info: ExceptionInfo[ExceptionGroup[Exception]],
) -> list[CheckError]:
    errors = error_info.value.exceptions
    assert all(isinstance(error, CheckError) for error in errors)
    return cast(list[CheckError], errors)
