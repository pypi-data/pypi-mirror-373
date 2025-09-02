from datetime import datetime
from pathlib import Path
from uuid import uuid4

import polars as pl

from seedcase_sprout.check_data import check_data
from seedcase_sprout.check_properties import (
    check_resource_properties,
)
from seedcase_sprout.constants import BATCH_TIMESTAMP_FORMAT
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import ResourceProperties


def write_resource_batch(
    data: pl.DataFrame,
    resource_properties: ResourceProperties,
    package_path: Path | None = None,
) -> Path:
    """Write the tidied data into the resource's batch data folder.

    Use this function to write the original data that is in a tidy Polars
    DataFrame to the resource folder provided by the `path` property in the
    `resource_properties`. The function saves the DataFrame as file with a
    timestamped, unique name, as a backup. If the data is exactly the same as
    the data in one of the existing batch files, it won't be duplicated. See the
    [design](https://sprout.seedcase-project.org/docs/design/) docs for an
    explanation of this batch file. Data is always checked against the
    `resource_properties` before it is written to the batch folder.

    Args:
        data: A Polars DataFrame object with the data to write to the batch folder.
        resource_properties: The properties object for the specific resource.
            Use `read_properties()` to read the properties for the resource.
        package_path: The path to the data package root folder (where `datapackage.json`
            is located). Defaults to the current working directory.

    Returns:
        The path to the written Parquet resource file.

    Raises:
        ExceptionGroup[CheckError]: If the resource properties are incorrect.
        ValueError: If column names in the data are incorrect.
        ExceptionGroup[ValueError]: If data types in the data are incorrect.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            resource_properties = sp.read_properties().resources[0]
            sp.write_resource_batch(
                data=sp.example_data(),
                resource_properties=resource_properties,
            )
        ```
    """
    check_resource_properties(resource_properties)
    check_data(data, resource_properties)

    package = PackagePath(package_path)
    resource_name = str(resource_properties.name)

    for batch_path in package.resource_batch_files(resource_name):
        batch = pl.read_parquet(batch_path)
        if data.equals(batch):
            return batch_path

    batch_path = package.resource_batch(resource_name)
    batch_path.mkdir(exist_ok=True, parents=True)
    # TODO: Move out some of this into the create_batch_file_name during refactoring
    batch_file_path = batch_path / _create_batch_file_name()

    data.write_parquet(batch_file_path)

    return batch_file_path


def _create_batch_file_name() -> Path:
    return Path(f"{_get_compact_iso_timestamp()}-{uuid4()}.parquet")


def _get_compact_iso_timestamp() -> str:
    """Gets the current timestamp in a compact ISO format.

    Returns:
        The current compact ISO timestamp as a string in the format defined by
        BATCH_TIMESTAMP_FORMAT.
    """
    return datetime.now().strftime(BATCH_TIMESTAMP_FORMAT)
