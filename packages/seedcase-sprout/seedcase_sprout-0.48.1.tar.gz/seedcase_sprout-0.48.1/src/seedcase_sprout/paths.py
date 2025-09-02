"""This module contains functions to get the paths to various data package files.

They are intended to be used in conjunction with other functions to read, write, and
edit the contents and properties of various files within a data package. Specifically,
they are used in the context of a data package stored in the working directory ("local"
first approach).
"""

from pathlib import Path

from seedcase_sprout.internals import _create_resource_properties_script_filename


class PackagePath:
    """Get the absolute path to a specific file or folder in a data package.

    Use the functions in this class to get the absolute path to a specific file
    or folder in your data package. They are intended as convenience functions
    to provide you with easy and quick access to required files and folders
    within your data package.  These functions have these characteristics in
    common:

    -   All of these functions output a `Path` object.
    -   The base class has an optional `path` argument that defaults to
        the current working directory available from the base class.
    -   If the wrong `resource_name` is given, an error message will include a
        list of all the actual `resource_name`'s for a specific package.

    Outputs a `PackagePath` object representing the structure of a data package.

    Args:
        path: Provide a path to the package directory. Defaults to the current working
            directory.

    Examples:
        ```{python}
        from pathlib import Path

        import seedcase_sprout as sp

        # With default path
        sp.PackagePath().properties()
        sp.PackagePath().readme()

        # With custom path
        my_path = Path("my/path")
        sp.PackagePath(my_path).properties()
        sp.PackagePath(my_path).readme()
        ```
    """

    def __init__(self, path: Path | None = None):
        """Set the base path."""
        self.path = path or Path.cwd()

    def root(self) -> Path:
        """Path to the root folder of the package."""
        return self.path

    def properties(self) -> Path:
        """Path to the `datapackage.json` file."""
        return self.root() / "datapackage.json"

    def readme(self) -> Path:
        """Path to the `README.md` file."""
        return self.root() / "README.md"

    def resources(self) -> Path:
        """Path to the `resources/` folder."""
        return self.root() / "resources"

    def resource(self, resource_name: str) -> Path:
        """Path to the specified `resources/<name>/` folder.

        Args:
            resource_name: The name of the resource. Use `ResourceProperties.name` to
                get the correct resource name.
        """
        return self.resources() / str(resource_name)

    def resource_data(self, resource_name: str) -> Path:
        """Path to the specific resource's data file.

        Args:
            resource_name: The name of the resource. Use `ResourceProperties.name` to
                get the correct resource name.
        """
        return self.resource(resource_name) / "data.parquet"

    def resource_batch(self, resource_name: str) -> Path:
        """Path to the specific resource's `batch/` folder.

        Args:
            resource_name: The name of the resource. Use `ResourceProperties.name` to
                get the correct resource name.
        """
        return self.resource(resource_name) / "batch"

    def resource_batch_files(self, resource_name: str) -> list[Path]:
        """Paths to all the files in the specific resource's `batch/` folder.

        Args:
            resource_name: The name of the resource. Use `ResourceProperties.name` to
                get the correct resource name.
        """
        return list(self.resource_batch(resource_name).glob("*.parquet"))

    def properties_script(self) -> Path:
        """Path to the properties script."""
        return self.root() / "scripts" / "package_properties.py"

    def resource_properties_script(self, resource_name: str = "") -> Path:
        """Path to a specific resource's resource properties script.

        Args:
            resource_name: The name of the resource.
        """
        return (
            self.root()
            / "scripts"
            / f"{_create_resource_properties_script_filename(resource_name)}.py"
        )
