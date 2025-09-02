import re
from datetime import datetime
from pathlib import Path

import polars as pl

from seedcase_sprout.check_data import check_data
from seedcase_sprout.check_properties import (
    check_resource_properties,
)
from seedcase_sprout.constants import (
    BATCH_TIMESTAMP_COLUMN_NAME,
    BATCH_TIMESTAMP_FORMAT,
    BATCH_TIMESTAMP_PATTERN,
)
from seedcase_sprout.internals import _check_is_file, _map, _map2
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import ResourceProperties


def read_resource_batches(
    resource_properties: ResourceProperties, paths: list[Path] | None = None
) -> list[pl.DataFrame]:
    """Read all the batch resource file(s) into a list of (Polars) DataFrames.

    Use this function to read the Parquet file(s) specified in `paths` into
    a list of Polars DataFrames, and perform checks on each of the DataFrames
    against the `resource_properties`. The `resource_properties` object is used
    to check the data and ensure it is correct. While Sprout generally assumes
    that the files stored in the `resources/<name>/batch/` folder are already
    correctly structured and tidy, this function still runs checks to ensure the
    data are correct by comparing to the properties.

    Args:
        resource_properties: The `ResourceProperties` object that contains the
            properties of the resource you want to check the data against.
        paths: A list of paths for all the Parquet files in the resource's `batch/`
            folder. Use `PackagePath().resource_batch_files()` to help provide the
            correct paths to the batch files. Defaults to the batch files of the given
            resource.

    Returns:
        A list of DataFrame objects from all the batch files.

    Raises:
        ValueError: If the batch file name is not in the expected pattern.
        ValueError: If the timestamp column name matches an existing column in the
            DataFrame.

    Examples:
        ``` {python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            resource_properties = sp.example_resource_properties()
            sp.write_resource_batch(sp.example_data(), resource_properties)

            sp.read_resource_batches(resource_properties)
        ```
    """
    check_resource_properties(resource_properties)
    if paths is None:
        paths = PackagePath().resource_batch_files(str(resource_properties.name))

    _map(paths, _check_is_file)
    return _map2(paths, [resource_properties], _read_parquet_batch_file)


def _read_parquet_batch_file(
    path: Path, resource_properties: ResourceProperties
) -> pl.DataFrame:
    """Reads a Parquet batch file and adds the timestamp as a column.

    This function reads a Parquet batch file into a Polars DataFrame and adds
    a timestamp column to the DataFrame, extracted from the file name.

    Args:
        path: Path to the Parquet batch file.
        resource_properties: The resource properties to check the data against.

    Returns:
        The Parquet file as a DataFrame with a timestamp column added.
    """
    if path.suffix != ".parquet":
        raise ValueError(
            "Failed to read batch file. Expected a file with a "
            f"`.parquet` extension but found {path}."
        )
    data = pl.read_parquet(path)
    check_data(data, resource_properties)

    timestamp = _extract_timestamp_from_batch_file_path(path)
    _check_batch_file_timestamp(timestamp)
    data = _add_timestamp_as_column(data, timestamp)
    return data


def _extract_timestamp_from_batch_file_path(path: Path) -> str:
    """Extracts the timestamp from the file name.

    Since the batch file name has been created by `_create_batch_file_name()`,
    it should contain a timestamp in the format defined by BATCH_TIMESTAMP_PATTERN.

    If multiple timestamps are found in the file name, the first one is used.
    """
    timestamp_list: list[str] = re.findall(BATCH_TIMESTAMP_PATTERN, path.stem)

    if not timestamp_list:
        raise ValueError(
            f"Batch file name '{path.stem}' does not contain a timestamp in the "
            f"expected format '{BATCH_TIMESTAMP_PATTERN}'."
        )

    return timestamp_list[0]


def _check_batch_file_timestamp(timestamp: str) -> str:
    """Checks the timestamp format and that it is a correct calendar date."""
    try:
        datetime.strptime(timestamp, BATCH_TIMESTAMP_FORMAT)
        return timestamp
    except ValueError as error:
        raise ValueError(
            f"Timestamp '{timestamp}' in the batch file name is not in the "
            f"expected format '{BATCH_TIMESTAMP_FORMAT}' or is not a correct calendar "
            "date (e.g., 30 February)."
        ) from error


def _add_timestamp_as_column(data: pl.DataFrame, timestamp: str) -> pl.DataFrame:
    """Adds the timestamp as a column to the data.

    Args:
        data: Data to add timestamp column to.
        timestamp: Timestamp to add as values in the timestamp column.

    Returns:
        Data with added timestamp column.

    Raises:
        ValueError: If a column with the name BATCH_TIMESTAMP_COLUMN_NAME already exists
        in the data.
    """
    # TODO: We could move this to be a check of the resource properties in
    # `sprout_checks/`
    if BATCH_TIMESTAMP_COLUMN_NAME in data.columns:
        raise ValueError(
            "One or multiple of the provided resource batch files contain a "
            f"column named '{BATCH_TIMESTAMP_COLUMN_NAME}'. This column is used "
            "internally in Sprout to remove duplicate rows across batches. Please "
            "rename it in the batch files and resource properties to read the resource "
            "batches."
        )
    return data.with_columns(pl.lit(timestamp).alias(BATCH_TIMESTAMP_COLUMN_NAME))
