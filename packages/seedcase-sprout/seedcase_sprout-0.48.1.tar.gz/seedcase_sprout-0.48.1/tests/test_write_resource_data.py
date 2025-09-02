from typing import cast

import polars as pl
from polars.testing import assert_frame_equal

from seedcase_sprout.examples import (
    ExamplePackage,
    example_data,
    example_data_all_types,
    example_resource_properties,
    example_resource_properties_all_types,
)
from seedcase_sprout.properties import ResourceProperties
from seedcase_sprout.read_properties import read_properties
from seedcase_sprout.write_resource_data import write_resource_data
from tests.assert_raises_errors import (
    assert_raises_check_errors,
    assert_raises_errors,
)


def test_writes_data_to_correct_location():
    """Should write data to correct location with custom path and default path."""
    with ExamplePackage() as package_path:
        resources = cast(list[ResourceProperties], read_properties().resources)
        resource_properties = resources[0]
        data = example_data()
        # Resolve paths to ensure symlinks are compared correctly on MacOS as well
        # (i.e., `/var` -> `/private/var` on MacOS)
        assert resource_properties.name
        expected_path = package_path.resource_data(resource_properties.name).resolve()

        # With custom path
        data_path = write_resource_data(data, resource_properties, package_path.root())

        assert data_path.resolve() == expected_path
        assert_frame_equal(pl.read_parquet(data_path), data)

        # With default path
        data_path = write_resource_data(data, resource_properties)

        assert data_path.resolve() == expected_path
        assert_frame_equal(pl.read_parquet(data_path), data)


def test_rewrites_data_file():
    """New data files should rewrite old data files."""
    with ExamplePackage():
        old_resources = cast(list[ResourceProperties], read_properties().resources)
        old_resource_properties = old_resources[0]
        old_data = example_data()
        new_resource_properties = example_resource_properties_all_types()
        new_resource_properties.name = old_resource_properties.name
        new_resource_properties.path = old_resource_properties.path
        new_data = example_data_all_types()
        write_resource_data(old_data, old_resource_properties)

        data_path = write_resource_data(new_data, new_resource_properties)

        assert_frame_equal(pl.read_parquet(data_path), new_data)


def test_throws_error_if_resource_properties_incorrect():
    """Should throw an error if the resource properties are incorrect."""
    resource_properties = example_resource_properties()
    resource_properties.name = "spaces in name"

    assert_raises_check_errors(
        lambda: write_resource_data(example_data(), resource_properties)
    )


def test_throws_error_if_properties_do_not_match_data():
    """Should throw an error if the resource properties and the data don't match."""
    resource_properties = example_resource_properties()
    assert resource_properties.schema and resource_properties.schema.fields
    resource_properties.schema.fields[0].type = "yearmonth"

    assert_raises_errors(
        lambda: write_resource_data(example_data(), resource_properties), ValueError
    )
