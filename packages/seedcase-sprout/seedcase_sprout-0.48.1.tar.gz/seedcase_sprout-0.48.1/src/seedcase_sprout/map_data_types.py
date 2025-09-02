from typing import cast

import polars as pl

from seedcase_sprout.properties import FieldType

"""
Mapping between Polars types and Data Package types.

Each Polars type can be described by any of the specified Data Package types.
When extracting Data Package types from a data frame, each Polars type is mapped to
the first Data Package type in the corresponding entry.
"""
_POLARS_TO_DATAPACKAGE: dict[type[pl.DataType], list[FieldType]] = {
    pl.Int8: ["integer", "year", "any"],
    pl.Int16: ["integer", "year", "any"],
    pl.Int32: ["integer", "year", "any"],
    pl.Int64: ["integer", "year", "any"],
    pl.Int128: ["integer", "year", "any"],
    pl.UInt8: ["integer", "year", "any"],
    pl.UInt16: ["integer", "year", "any"],
    pl.UInt32: ["integer", "year", "any"],
    pl.UInt64: ["integer", "year", "any"],
    pl.Float32: ["number", "any"],
    pl.Float64: ["number", "any"],
    pl.Decimal: ["number", "any"],
    pl.Boolean: ["boolean", "any"],
    pl.String: ["string", "array", "object", "geojson", "duration", "any"],
    pl.Binary: ["string", "any"],
    pl.Categorical: ["string", "any"],
    pl.Enum: ["string", "any"],
    pl.Date: ["date", "yearmonth", "any"],
    pl.Datetime: ["datetime", "any"],
    pl.Time: ["time", "any"],
    pl.Duration: ["integer", "any"],
    pl.Array: ["array", "any"],
    pl.List: ["array", "any"],
    pl.Struct: ["object", "geojson", "any"],
    pl.Object: ["object", "geojson", "any"],
    pl.Unknown: ["any"],
    pl.Null: ["any"],
}


def _get_allowed_datapackage_types(polars_type: pl.DataType) -> list[FieldType]:
    """Return the Data Package types that can describe the given Polars type.

    Args:
        polars_type: The Polars type to get the Data Package types for.

    Returns:
        The allowed Data Package types.
    """
    base_type = cast(type[pl.DataType], polars_type.base_type())
    allowed_types = _POLARS_TO_DATAPACKAGE.get(base_type, ["any"])

    if (
        isinstance(polars_type, pl.Array)
        and polars_type.size == 2
        and polars_type.inner.is_numeric()
    ):
        return allowed_types + ["geopoint"]

    return allowed_types


def _polars_and_datapackage_types_match(
    polars_type: pl.DataType, datapackage_type: FieldType | None
) -> bool:
    """Decide if the given Polars and Data Package types match.

    Args:
        polars_type: The Polars type to check.
        datapackage_type: The Data Package type to check.

    Returns:
        Whether the given types match.
    """
    return (datapackage_type or "any") in _get_allowed_datapackage_types(polars_type)


def _get_allowed_polars_types(
    datapackage_type: FieldType | None,
) -> list[type[pl.DataType]]:
    """Return the Polars types that can represent the given Data Package type.

    Args:
        datapackage_type: The Data Package type.

    Returns:
        The allowed Polars types.
    """
    datapackage_type = datapackage_type or "any"
    if datapackage_type == "geopoint":
        # Strictly speaking, this should be an Array of a numeric type with size 2, but
        # it wouldn't be practical to list all combinations here. This information is
        # added directly to the error message instead.
        return [pl.Array]

    # TODO: Revise once `_map_keep()` has been implemented
    return [
        polars_type
        for polars_type, datapackage_types in _POLARS_TO_DATAPACKAGE.items()
        if datapackage_type in datapackage_types
    ]


def _polars_to_datapackage(polars_type: pl.DataType) -> FieldType:
    """Return the Data Package type that is the best match for the given Polars type.

    Args:
        polars_type: The Polars type to match.

    Returns:
        The best-match Data Package type.
    """
    return _get_allowed_datapackage_types(polars_type)[0]
