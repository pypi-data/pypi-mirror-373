import os
import re

import polars as pl
from polars.testing import assert_frame_equal
from pytest import raises

from seedcase_sprout.constants import BATCH_TIMESTAMP_PATTERN
from seedcase_sprout.examples import (
    example_data,
    example_resource_properties,
)
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.write_resource_batch import write_resource_batch


def test_writes_correct_resource_batch_file(tmp_path):
    """Writes tidy resource batch file correctly."""
    # Given
    (tmp_path / "resources" / example_resource_properties().name).mkdir(parents=True)

    # When
    batch_path = write_resource_batch(
        example_data(), example_resource_properties(), tmp_path
    )
    batch_data = pl.read_parquet(batch_path)

    # Then
    assert batch_path.exists()
    assert f"resources/{example_resource_properties().name}/batch" in str(batch_path)
    assert len(re.findall(BATCH_TIMESTAMP_PATTERN, batch_path.stem)) == 1
    assert_frame_equal(batch_data, example_data(), check_exact=True)


def test_does_not_duplicate_batch_file(tmp_cwd):
    """Should not create a new batch file when the data has already been saved in an
    existing batch file."""
    # Given
    data = example_data()
    resource_properties = example_resource_properties()
    existing_batch_path = write_resource_batch(data, resource_properties)

    # When
    new_batch_path = write_resource_batch(data, resource_properties)

    # Then
    assert new_batch_path == existing_batch_path
    assert len(PackagePath().resource_batch_files(str(resource_properties.name))) == 1
    assert_frame_equal(pl.read_parquet(new_batch_path), data)


def test_creates_new_batch_file_when_data_not_duplicate(tmp_cwd):
    """Should create a new batch file when the data is different from data in
    existing batch files."""
    # Given
    existing_data = example_data()
    new_data = example_data()
    new_data[2, "name"] = "Bob"
    resource_properties = example_resource_properties()
    existing_batch_path = write_resource_batch(existing_data, resource_properties)

    # When
    new_batch_path = write_resource_batch(new_data, resource_properties)

    # Then
    assert_frame_equal(pl.read_parquet(existing_batch_path), existing_data)
    assert_frame_equal(pl.read_parquet(new_batch_path), new_data)


def test_writes_correct_resource_batch_file_with_unordered_columns(tmp_path):
    """Writes batch file correctly even if columns aren't in the order expected by the
    resource properties."""
    # Given
    (tmp_path / "resources" / example_resource_properties().name).mkdir(parents=True)
    data = example_data().select(["value", "name", "id"])

    # When
    batch_path = write_resource_batch(data, example_resource_properties(), tmp_path)
    batch_data = pl.read_parquet(batch_path)

    # Then
    assert batch_path.exists()
    assert_frame_equal(batch_data, data, check_exact=True)


def test_throws_error_if_data_do_not_match_example_resource_properties(tmp_path):
    """Throws ExceptionGroup if data don't match resource properties."""
    with raises(ValueError):
        write_resource_batch(pl.DataFrame(), example_resource_properties(), tmp_path)


def test_throws_error_if_data_do_not_match_resource_properties(tmp_path):
    """Throws ExceptionGroup if data don't match resource properties (extra column)."""
    # Given
    os.chdir(tmp_path)
    (tmp_path / "resources" / example_resource_properties().name).mkdir(parents=True)

    data = example_data().insert_column(2, pl.Series("extra_column", [1, 2, 3]))

    # When
    with raises(ValueError):
        write_resource_batch(data, example_resource_properties(), tmp_path)


def test_uses_cwd_if_no_path_provided(tmp_cwd):
    """If no path is provided, should use the cwd as the package root."""
    # Given
    package_path = PackagePath(tmp_cwd)
    resource_properties = example_resource_properties()
    assert resource_properties.name
    package_path.resource(resource_properties.name).mkdir(parents=True)

    # When
    batch_file = write_resource_batch(example_data(), resource_properties)

    # Then
    assert batch_file.exists()
    assert package_path.resource_batch(resource_properties.name) in batch_file.parents
