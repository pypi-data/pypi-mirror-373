from pytest import mark

from seedcase_sprout import PackagePath


def test_package_path_outputs_an_absolute_path(tmp_path):
    """Test that the path functions output an absolute path."""
    # This is a simple test to just check that a path is output.
    # Need to give the `tmp_path` to the class otherwise it uses the working directory
    # of the test script.
    path = PackagePath(tmp_path)
    assert path.root().is_absolute()
    assert path.properties().is_absolute()
    assert path.readme().is_absolute()
    assert path.resources().is_absolute()
    assert path.resource("test").is_absolute()
    assert path.resource_data("test").is_absolute()
    assert path.resource_batch("test").is_absolute()


def test_methods_return_correct_path(tmp_path):
    """Methods should return the expected path."""
    package_path = PackagePath(tmp_path)
    assert package_path.root() == tmp_path
    assert package_path.properties() == tmp_path / "datapackage.json"
    assert package_path.readme() == tmp_path / "README.md"
    assert package_path.resources() == tmp_path / "resources"
    assert package_path.resource("test") == tmp_path / "resources" / "test"
    assert (
        package_path.resource_data("test")
        == tmp_path / "resources" / "test" / "data.parquet"
    )

    assert (
        package_path.resource_batch("test") == tmp_path / "resources" / "test" / "batch"
    )


def test_resource_batch_files_returns_empty_list_when_no_batches(tmp_path):
    """resource_batch_files() should return an empty list when no batches are found
    for the resource."""
    assert PackagePath(tmp_path).resource_batch_files("test") == []


def test_resource_batch_files_returns_file_paths_when_batches(tmp_path):
    """resource_batch_files() should return the file paths to the batch files of the
    resource. Only Parquet files should be returned."""
    package_path = PackagePath(tmp_path)
    # Add batches for 2 resources
    for resource in ["test1", "test2"]:
        batch_folder = package_path.resource_batch(resource)
        batch_folder.mkdir(parents=True)
        (batch_folder / "sub-folder").mkdir()
        for file in ["file", "file.txt", "file.parquet"]:
            (batch_folder / file).touch()

    # Only the batch file for the given resource should be returned
    assert package_path.resource_batch_files("test2") == [batch_folder / "file.parquet"]


def test_path_defaults_to_cwd_at_call_time(tmp_cwd):
    """When no root path is provided, the root path should default to the cwd of the
    calling script."""
    package_path = PackagePath()
    assert package_path.root() == tmp_cwd


@mark.parametrize("resource_name", ["my_resource", "my.resource", "my-resource"])
def test_resource_properties_script_returns_correct_path_with_resource_name(
    tmp_path, resource_name
):
    """Should return the path to the resource properties script with the resource
    name in snake case."""
    package_path = PackagePath(tmp_path)
    assert (
        package_path.resource_properties_script(resource_name)
        == tmp_path / "scripts" / "resource_properties_my_resource.py"
    )


def test_resource_properties_script_returns_correct_path_without_resource_name(
    tmp_path,
):
    """Should return the path to the resource properties script without a
    resource name."""
    package_path = PackagePath(tmp_path)
    assert (
        package_path.resource_properties_script()
        == tmp_path / "scripts" / "resource_properties.py"
    )
