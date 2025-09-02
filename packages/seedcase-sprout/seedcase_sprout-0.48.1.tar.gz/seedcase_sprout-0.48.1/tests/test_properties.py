from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from uuid import UUID
from zoneinfo import ZoneInfo

import time_machine
from pytest import mark

from seedcase_sprout.properties import (
    ConstraintsProperties,
    ContributorProperties,
    FieldProperties,
    LicenseProperties,
    PackageProperties,
    ReferenceProperties,
    ResourceProperties,
    SourceProperties,
    TableSchemaForeignKeyProperties,
    TableSchemaProperties,
)


@mark.parametrize(
    "cls",
    [
        ContributorProperties,
        LicenseProperties,
        SourceProperties,
        ReferenceProperties,
        TableSchemaForeignKeyProperties,
        ConstraintsProperties,
        FieldProperties,
        TableSchemaProperties,
        ResourceProperties,
        PackageProperties,
    ],
)
def test_initiated_class_only_contains_none_values(cls):
    """When a Properties class is instantiated, all values should be None."""
    assert all(value is None for value in asdict(cls()).values())


def test_compact_dict_generates_empty_dictionary_when_no_args_given():
    """Should return an empty dictionary, when no arguments are given to Properties
    class."""
    # Since this is a test of the base class, it's enough to test only one subclass
    assert ResourceProperties().compact_dict == {}


def test_compact_dict_preserves_only_non_none_values():
    """Should return a dictionary with only non-None values when args given."""
    # Since this is a test of the base class, it's enough to test only one subclass

    # Given
    properties = PackageProperties(name="package-1", version="3.2.1")

    # When, then
    assert properties.compact_dict == {"name": "package-1", "version": "3.2.1"}


def test_compact_dict_removes_none_values_in_nested_objects():
    """Given properties with a nested structure, should return a dictionary with only
    non-None values"""
    properties = PackageProperties(
        resources=[
            ResourceProperties(
                schema=TableSchemaProperties(
                    fields=[
                        FieldProperties(
                            constraints=ConstraintsProperties(
                                json_schema={"test": "test"}
                            )
                        )
                    ]
                ),
            ),
        ],
    )

    assert properties.compact_dict == {
        "resources": [
            {"schema": {"fields": [{"constraints": {"jsonSchema": {"test": "test"}}}]}}
        ]
    }


@patch("seedcase_sprout.properties.uuid4", return_value=UUID(int=1))
@time_machine.travel(datetime(2024, 5, 14, 5, 0, 1, tzinfo=ZoneInfo("UTC")), tick=False)
def test_creates_package_properties_with_correct_defaults(mock_uuid):
    """`from_default` should create `PackageProperties` with correct defaults for id,
    version, and created."""
    properties = PackageProperties.from_default()

    assert properties.id == str(mock_uuid())
    assert properties.version == "0.1.0"
    assert properties.created == "2024-05-14T05:00:01+00:00"


@time_machine.travel(datetime(2024, 5, 14, 5, 0, 1, tzinfo=ZoneInfo("UTC")), tick=False)
def test_allows_overriding_defaults():
    """It should be possible to override defaults with non-None values when creating
    `PackageProperties` using `from_default`."""
    properties = PackageProperties.from_default(id="abc", name="my-name", created=None)

    assert properties.name == "my-name"
    assert properties.id == "abc"
    assert properties.version == "0.1.0"
    assert properties.created == "2024-05-14T05:00:01+00:00"


@mark.parametrize(
    "dict, expected_properties",
    [
        ({"familyName": "Doe"}, ContributorProperties(family_name="Doe")),
        ({"name": "a licence"}, LicenseProperties(name="a licence")),
        ({"title": "a source"}, SourceProperties(title="a source")),
        ({"resource": "a resource"}, ReferenceProperties(resource="a resource")),
        ({"fields": ["a field"]}, TableSchemaForeignKeyProperties(fields=["a field"])),
        ({"required": False}, ConstraintsProperties(required=False)),
        ({"name": "a field name"}, FieldProperties(name="a field name")),
        ({"fieldsMatch": ["exact"]}, TableSchemaProperties(fields_match=["exact"])),
        (
            {
                "name": "resource-name",
                "licenses": [{"name": "MIT"}],
            },
            ResourceProperties(
                name="resource-name",
                licenses=[LicenseProperties(name="MIT")],
            ),
        ),
        (
            {"version": "1.0.0", "contributors": [{"familyName": "Doe"}]},
            PackageProperties(
                version="1.0.0", contributors=[ContributorProperties(family_name="Doe")]
            ),
        ),
    ],
)
def test_transforms_dict_to_properties(dict, expected_properties):
    """Should transform a (nested) dictionary to a properties object."""
    properties_cls = type(expected_properties)
    properties = properties_cls.from_dict(dict)

    assert properties == expected_properties


@mark.parametrize(
    "resource_properties, path",
    [
        (ResourceProperties(name="space in name"), None),
        (
            ResourceProperties(name="test-resource"),
            str(Path("resources", "test-resource", "data.parquet")),
        ),
        (
            ResourceProperties(name="test-resource", path="some/path"),
            str(Path("resources", "test-resource", "data.parquet")),
        ),
    ],
)
def test_autogenerates_resource_data_path(resource_properties, path):
    """Should autogenerate the resource path from the resource name after object
    creation (if the name is correct)."""
    assert resource_properties.path == path


def test_resource_path_included_in_compact_dict():
    """`compact_dict` should include the autogenerated resource path."""
    resource_properties = ResourceProperties(name="test-resource")

    assert resource_properties.compact_dict == {
        "name": "test-resource",
        "path": str(Path("resources", "test-resource", "data.parquet")),
    }
