from pathlib import Path

import polars as pl

from seedcase_sprout.check_data import check_data
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import ResourceProperties


def write_resource_data(
    data: pl.DataFrame,
    resource_properties: ResourceProperties,
    package_path: Path | None = None,
) -> Path:
    """Check and write the resource data into a file.

    This function takes the `data` obtained after using
    `join_resource_batches()`, checks it against the `resource_properties`, and
    then writes the data to the resources `data.parquet` file .  The Parquet
    file is saved based on the path found in `ResourceProperties.path` and is
    always overwritten.  Before writing, this function does a check against the
    `resource_properties` to ensure that the data is correctly structured and
    tidy.

    Args:
        data: A DataFrame object with the resources data from the files in its
            `batch/` folder.
        resource_properties: The `ResourceProperties` object that contains the
            properties of the resource you want to create the Parquet file for.
        package_path: The path to the data package root folder (where `datapackage.json`
            is located). Defaults to the current working directory.

    Returns:
        The path of the created Parquet file.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            resource_properties = sp.example_resource_properties()
            # Add and join batch files
            sp.write_resource_batch(sp.example_data(), resource_properties)
            batches = sp.read_resource_batches(resource_properties)
            data = sp.join_resource_batches(batches, resource_properties)
            # Write resource data file
            sp.write_resource_data(data, resource_properties)
    """
    check_data(data, resource_properties)
    data_path = PackagePath(package_path).resource_data(str(resource_properties.name))

    data.write_parquet(data_path)
    return data_path
