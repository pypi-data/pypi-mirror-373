import tempfile
from pathlib import Path

from pytest import raises

from seedcase_sprout.check_data import check_data
from seedcase_sprout.check_properties import (
    check_package_properties,
    check_properties,
    check_resource_properties,
)
from seedcase_sprout.examples import (
    ExamplePackage,
    example_data,
    example_data_all_types,
    example_package_properties,
    example_resource_properties,
    example_resource_properties_all_types,
)
from seedcase_sprout.read_properties import read_properties


def test_creates_correct_package_properties_object():
    assert check_package_properties(example_package_properties())


def test_creates_correct_resource_properties_object():
    assert check_resource_properties(example_resource_properties())


def test_creates_correct_resource_properties_object_all_types():
    assert check_resource_properties(example_resource_properties_all_types())


def test_example_data_matches_resource_properties():
    data = example_data()
    assert check_data(data, example_resource_properties()) is data


def test_example_data_matches_resource_properties_all_types():
    data = example_data_all_types()
    assert check_data(data, example_resource_properties_all_types()) is data


def test_creates_package_with_resources():
    """Should create: package folder, datapackage.json, README."""
    with ExamplePackage() as package_path:
        # Test root folder
        assert package_path.root().is_dir()
        assert len(list(package_path.root().iterdir())) == 3
        # Test README
        assert package_path.readme().is_file()
        assert package_path.readme().read_text()
        # Test datapackage.json
        assert package_path.properties().is_file()
        properties = read_properties(package_path.properties())
        assert properties.resources
        assert check_resource_properties(properties.resources[0])
        # Test resources
        assert properties.resources and len(properties.resources) == 1


def test_creates_package_without_resources():
    """Should create: package folder, datapackage.json, README."""
    with ExamplePackage(with_resources=False) as package_path:
        # Test root folder
        assert package_path.root().is_dir()
        assert len(list(package_path.root().iterdir())) == 2
        # Test README
        assert package_path.readme().is_file()
        assert package_path.readme().read_text()
        # Test datapackage.json
        assert package_path.properties().is_file()
        properties = read_properties(package_path.properties())
        assert check_properties(properties)
        assert properties.name == package_path.root().stem
        # Test no resources
        assert not properties.resources


def test_changes_cwd_to_package_root_in_package_context():
    """Within the context, the cwd should be the package root.
    After exiting the context, the cwd should be reset to the original location."""
    original_cwd = Path.cwd()
    with ExamplePackage() as package_path:
        # Resolve paths to ensure symlinks are compared correctly on MacOS as well
        # (i.e., `/var` -> `/private/var` on MacOS)
        assert Path.cwd().resolve() == package_path.root().resolve()

    assert Path.cwd() == original_cwd


def test_restores_cwd_when_error_raised_in_context():
    """The original cwd should be restored after exiting the context, even if an error
    was raised inside the context."""
    original_cwd = Path.cwd()
    with ExamplePackage(), raises(ValueError):
        raise ValueError("An error!")

    assert Path.cwd() == original_cwd


def test_manages_temp_folder_correctly():
    """The package root should be in a temporary folder.
    After exiting the context, the package root should not exist."""
    temp_root = Path(tempfile.gettempdir())
    with ExamplePackage() as package_path:
        assert temp_root in package_path.root().parents

    assert not package_path.root().exists()


def test_can_use_context_without_referencing_package_path_explicitly():
    """It should be possible to omit the package path from function calls within the
    context."""
    with ExamplePackage():
        properties = read_properties()
        assert check_properties(properties)


def test_can_set_name_for_package():
    """It should be possible to specify a custom name for the package."""
    package_name = "basking-shark-study"
    with ExamplePackage(package_name=package_name) as package_path:
        assert read_properties().name == package_name
        assert package_path.root().stem == package_name
