from typing import cast

import polars as pl

from seedcase_sprout.check_properties import (
    check_resource_properties,
)
from seedcase_sprout.internals import _get_nested_attr, _map
from seedcase_sprout.map_data_types import (
    _get_allowed_polars_types,
    _polars_and_datapackage_types_match,
)
from seedcase_sprout.properties import (
    FieldProperties,
    ResourceProperties,
)


def check_data(
    data: pl.DataFrame, resource_properties: ResourceProperties
) -> pl.DataFrame:
    """Check that the DataFrame matches the requirements in the resource properties.

    Run a few checks to compare between the data and the properties on the items:

    | Data | Properties |
    |:------|:------------|
    | Column names | `field.name` |
    | Column types | `field.types` |
    | Column values' types | `field.types` |
    | Column values' constraints | `field.constraints` |

    The error messages are generally in the format of:

    ```
    # {data item}:

    There is a mismatch found:

    - In the properties: {mismatch}
    - In the data: {mismatch}
    ```

    Args:
        data: A Polars DataFrame.
        resource_properties: The specific `ResourceProperties` for the `data`.

    Returns:
        The `data` if checks all pass.

    Raises:
        ExceptionGroup[CheckError]: If the resource properties are incorrect.
        ValueError: If column names in the data are incorrect.
        ExceptionGroup[ValueError]: If data types in the data are incorrect.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        sp.check_data(
            data=sp.example_data(),
            resource_properties=sp.example_resource_properties()
        )
        ```
    """
    check_resource_properties(resource_properties)
    _check_column_names(data, resource_properties)
    _check_column_types(data, resource_properties)
    # _check_column_values_constraints(data, resource_properties)

    return data


def _check_column_names(
    data: pl.DataFrame, resource_properties: ResourceProperties
) -> pl.DataFrame:
    """Checks that column names in `data` match those in `resource_properties`.

    Columns may appear in any order.

    Args:
        data: The data to check.
        resource_properties: The resource properties to check against.

    Returns:
        The data if the column names match.

    Raises:
        ValueError: If the column names don't match the names in
            `resource_properties`.
    """
    columns_in_data = data.schema.names()
    columns_in_resource = [
        str(field.name)
        for field in cast(
            list[FieldProperties],
            _get_nested_attr(resource_properties, "schema.fields", default=[]),
        )
    ]
    extra_columns_in_data = [
        name for name in columns_in_data if name not in columns_in_resource
    ]
    missing_columns_in_data = [
        name for name in columns_in_resource if name not in columns_in_data
    ]

    if extra_columns_in_data or missing_columns_in_data:
        raise ValueError(
            _format_column_name_error_message(
                extra_columns_in_data, missing_columns_in_data
            )
        )

    return data


def _format_column_name_error_message(
    extra_columns_in_data: list[str], missing_columns_in_data: list[str]
) -> str:
    message = (
        "Column names in the data do not match column names in the resource properties:"
    )
    if extra_columns_in_data:
        message += f"\n- Unexpected column(s) in data: {extra_columns_in_data}"
    if missing_columns_in_data:
        message += f"\n- Missing column(s) in data: {missing_columns_in_data}"
    return message


def _check_column_types(
    data: pl.DataFrame, resource_properties: ResourceProperties
) -> pl.DataFrame:
    """Checks that column data types match the data types specified in the properties.

    The resource properties specify a Frictionless data type for each column.
    This function checks if the Polars data type of each column in the data matches
    the expected Frictionless data type.

    Column names are expected to match the names specified in the resource properties.

    Args:
        data: The data frame to check.
        resource_properties: The resource properties to check against.

    Returns:
        The data frame, if all column types are correct.

    Raises:
        ExceptionGroup: A group of `ValueError`s, one per incorrectly typed column.
    """
    fields = cast(
        list[FieldProperties],
        _get_nested_attr(resource_properties, "schema.fields", default=[]),
    )
    polars_schema = data.schema
    errors = [
        _get_column_type_error(polars_schema[str(field.name)], field)
        for field in fields
        if not _polars_and_datapackage_types_match(
            polars_schema[str(field.name)], field.type
        )
    ]

    if errors:
        raise ExceptionGroup(
            (
                "The following columns in the data have data types that do not match "
                "the data types in the resource properties:"
            ),
            errors,
        )
    return data


def _get_column_type_error(
    polars_type: pl.DataType, field: FieldProperties
) -> ValueError:
    """Creates an error for a column where Polars and Frictionless types don't match.

    Args:
        polars_type: The Polars type.
        field: The field properties.

    Returns:
        A `ValueError`.
    """
    allowed_types = _map(_get_allowed_polars_types(field.type), str)
    allowed_types_str = (
        allowed_types[0]
        if len(allowed_types) == 1
        else f"one of {', '.join(allowed_types)}"
    )

    if field.type == "geopoint":
        allowed_types_str = "an Array of a numeric type with size 2"

    return ValueError(
        f"Expected type of column '{field.name}' "
        f"to be {allowed_types_str} but found {polars_type}."
    )
