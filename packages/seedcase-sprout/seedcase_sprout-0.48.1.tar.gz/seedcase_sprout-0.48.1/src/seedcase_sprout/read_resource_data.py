from pathlib import Path

import polars as pl

from seedcase_sprout.paths import PackagePath


def read_resource_data(
    resource_name: str,
    path: Path | None = None,
) -> pl.DataFrame:
    """Read the resource's `data.parquet` file.

    Use this function to read in the data file for a specific resource in a data
    package as a Polars DataFrame.

    Args:
        resource_name: The name of the resource. This should match the name
            found in the `datapackage.json` file under the `resource.name`
            key for the resource.
        path: The path to the data package folder, where the `datapackage.json`
            file is located. If not provided, it defaults to the current
            working directory. Use `PackagePath().properties()` to help get the
            correct path.

    Returns:
        A Polars DataFrame containing the data from the resource's data file.

    Raises:
        FileNotFoundError: If the resource's data file does not exist in the
            specified path.

    Examples:
        ```{python}
        import seedcase_sprout as sp
        with sp.ExamplePackage() as package_path:
            data = sp.read_resource_data("example-resource")
            print(data)
        ```
    """
    data_path = PackagePath(path).resource_data(resource_name)
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Resource '{resource_name}' not found in the package, so we couldn't",
            "read the data.",
        )

    return pl.read_parquet(data_path)
