from pathlib import Path

from seedcase_sprout.check_properties import check_properties
from seedcase_sprout.internals import _check_is_file, _read_json
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import PackageProperties


def read_properties(path: Path | None = None) -> PackageProperties:
    """Read in the properties from the `datapackage.json` file.

    Reads the `datapackage.json` file, checks that it is correct, and then
    outputs a `PackageProperties` object.

    Args:
        path: The path to the `datapackage.json` file. Use `PackagePath().properties()`
            to help get the correct path. If no path is provided, this function looks
            for the `datapackage.json` file in the current working directory.

    Returns:
        A `PackageProperties` object with the properties from the
            `datapackage.json` file.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            sp.read_properties()
        ```

    Raises:
        FileNotFound: If the `datapackage.json` file doesn't exist.
        JSONDecodeError: If the `datapackage.json` file couldn't be read.
    """
    path = path or PackagePath().properties()
    _check_is_file(path)
    properties_dict = _read_json(path)
    properties = PackageProperties.from_dict(properties_dict)
    check_properties(properties)
    return properties
