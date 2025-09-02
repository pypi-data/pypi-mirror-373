from json import JSONDecodeError
from pathlib import Path

from pytest import raises

from seedcase_sprout import (
    example_package_properties,
    read_properties,
    write_properties,
)
from seedcase_sprout.internals import _write_json
from seedcase_sprout.paths import PackagePath


def test_reads_in_as_package_properties(tmp_path):
    """Should read in the properties from the `datapackage.json` file."""

    expected_properties = example_package_properties()
    properties_path = tmp_path / "datapackage.json"
    properties_path = write_properties(expected_properties, properties_path)
    actual_properties = read_properties(properties_path)

    assert expected_properties == actual_properties


def test_reads_when_resource_not_exists(tmp_path):
    """Should not give an error if there are no resources on the package."""

    expected_properties = example_package_properties()
    expected_properties.resources = None
    properties_path = tmp_path / "datapackage.json"
    properties_path = write_properties(expected_properties, properties_path)
    actual_properties = read_properties(properties_path)

    assert expected_properties == actual_properties


def test_throws_error_if_path_points_to_dir(tmp_path):
    """Should throw FileNotFoundError if the path points to a folder."""
    with raises(FileNotFoundError):
        read_properties(tmp_path)


def test_throws_error_if_path_points_to_nonexistent_file(tmp_path):
    """Should throw FileNotFoundError if the path points to a nonexistent file."""
    with raises(FileNotFoundError):
        read_properties(tmp_path / "datapackage.json")


def test_throws_error_if_properties_file_cannot_be_read(tmp_path):
    """Should throw JSONDecodeError if the properties file cannot be read as JSON."""
    file_path = Path(tmp_path / "datapackage.json")
    file_path.write_text(",,, this is not, JSON")

    with raises(JSONDecodeError):
        read_properties(file_path)


def test_error_incorrect_properties_in_file(tmp_path):
    """Can't read in properties if the properties file is incorrect."""
    properties = example_package_properties()
    properties.name = "incorrect name"
    _write_json(properties.compact_dict, tmp_path / "datapackage.json")

    with raises(ExceptionGroup):
        read_properties(tmp_path / "datapackage.json")


def test_reads_properties_from_cwd_if_no_path_provided(tmp_cwd):
    """If no path is provided, should read datapackage.json from the cwd."""
    properties = example_package_properties()
    write_properties(properties, PackagePath(tmp_cwd).properties())

    assert read_properties() == properties


def test_fails_correctly_if_no_path_provided_and_no_properties_in_cwd(tmp_cwd):
    """Should throw the expected error if no path is provided and there is no
    datapackage.json in the cwd."""
    with raises(FileNotFoundError):
        read_properties()
