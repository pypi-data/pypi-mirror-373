import re

import polars as pl
from polars.testing import assert_frame_equal
from pytest import fixture, mark, raises

from seedcase_sprout.check_data import check_data
from seedcase_sprout.examples import (
    example_data,
    example_resource_properties,
)
from seedcase_sprout.map_data_types import _get_allowed_polars_types
from seedcase_sprout.properties import (
    FieldProperties,
    ResourceProperties,
    TableSchemaProperties,
)
from tests.assert_raises_errors import (
    assert_raises_check_errors,
    assert_raises_errors,
)

string_field = FieldProperties(name="my_string", type="string")
bool_field = FieldProperties(name="my_bool", type="boolean")
number_field = FieldProperties(name="my_number", type="number")


@fixture
def resource_properties() -> ResourceProperties:
    return ResourceProperties(
        name="data",
        title="data",
        description="My data...",
        schema=TableSchemaProperties(),
    )


@mark.parametrize(
    "fr_type, pl_types",
    [
        ("number", [pl.Float32, pl.Float64, pl.Decimal]),
        ("integer", [pl.Int16, pl.UInt8, pl.Duration]),
        ("string", [pl.String, pl.Categorical, pl.Enum(["A"]), pl.Binary]),
        ("date", [pl.Date]),
        ("datetime", [pl.Datetime]),
        ("time", [pl.Time]),
        ("boolean", [pl.Boolean]),
        ("array", [pl.String, pl.Array, pl.List]),
        ("object", [pl.String, pl.Struct, pl.Object]),
        (
            "geopoint",
            [pl.Array(pl.Int128, 2), pl.Array(pl.Float32, 2), pl.Array(pl.Decimal, 2)],
        ),
        ("geojson", [pl.String, pl.Struct, pl.Object]),
        ("year", [pl.Int32, pl.UInt8, pl.Int64]),
        ("yearmonth", [pl.Date]),
        ("duration", [pl.String]),
        ("any", [pl.Unknown, pl.Null, pl.Object, pl.Int128, pl.Boolean]),
    ],
)
def test_accepts_correct_columns(fr_type, pl_types):
    """Should not raise an error when columns in the data match columns in the
    resource properties."""
    resource_properties = example_resource_properties()
    assert resource_properties.schema
    resource_properties.schema.fields = [
        FieldProperties(name=str(pl_type), type=fr_type) for pl_type in pl_types
    ]
    data = pl.DataFrame(
        {str(pl_type): pl.Series([], dtype=pl_type) for pl_type in pl_types}
    )

    assert check_data(data, resource_properties) is data


def test_accepts_columns_in_any_order():
    """Should not raise an error when the data types match but the columns are in a
    different order."""
    resource_properties = example_resource_properties()
    assert resource_properties.schema and resource_properties.schema.fields
    resource_properties.schema.fields.reverse()
    data = example_data()

    assert_frame_equal(check_data(data, resource_properties), data)


def test_throws_error_when_data_has_extra_columns(resource_properties):
    """Should throw an error if the data has extra columns."""
    df = pl.DataFrame({"extra_col1": [""], bool_field.name: [True], "extra_col2": [""]})
    resource_properties.schema.fields = [bool_field]

    with raises(ValueError, match=r"Unexpected.*extra_col1.*extra_col2") as error:
        check_data(df, resource_properties)

    assert bool_field.name and bool_field.name not in str(error)


def test_throws_error_when_data_has_missing_columns(resource_properties):
    """Should throw an error if the data has missing columns."""
    df = pl.DataFrame({bool_field.name: [True]})
    resource_properties.schema.fields = [string_field, bool_field, number_field]

    with raises(
        ValueError, match=rf"Missing.*{string_field.name}.*{number_field.name}"
    ) as error:
        check_data(df, resource_properties)

    assert bool_field.name and bool_field.name not in str(error)


def test_throws_error_when_data_has_extra_and_missing_columns(resource_properties):
    """Should throw an error if the data has extra columns and missing columns."""
    df = pl.DataFrame({"extra_col": [""], bool_field.name: [True]})
    resource_properties.schema.fields = [string_field, bool_field, number_field]

    with raises(ValueError) as error:
        check_data(df, resource_properties)

    assert re.search(r"Unexpected.*extra_col", str(error))
    assert re.search(rf"Missing.*{string_field.name}.*{number_field.name}", str(error))
    assert bool_field.name and bool_field.name not in str(error)


@mark.parametrize(
    "frictionless_type",
    [
        "string",
        "boolean",
        "integer",
        "number",
        "year",
        "datetime",
        "date",
        "time",
        "yearmonth",
        "geopoint",
        "duration",
        "object",
        "array",
        "geojson",
    ],
)
def test_rejects_incorrect_column_type(frictionless_type, resource_properties):
    """Should raise an error if the Polars type does not match the Frictionless type."""
    data = pl.DataFrame({"my_col": pl.Series([], dtype=pl.Null)})
    resource_properties.schema.fields = [
        FieldProperties(name="my_col", type=frictionless_type)
    ]

    with raises(ExceptionGroup) as error_info:
        check_data(data, resource_properties)

    errors = error_info.value.exceptions
    assert len(errors) == 1
    polars_type = re.escape(str(data.schema.dtypes()[0]))
    allowed_types = _get_allowed_polars_types(frictionless_type)
    assert re.search(rf"'my_col'.*{allowed_types}.*found {polars_type}", str(errors[0]))


def test_rejects_multiple_incorrect_column_types():
    """Should raise an error if multiple column types don't match."""
    resource_properties = example_resource_properties()
    data = example_data()
    data = data.select([pl.lit(None).alias(col) for col in data.columns])

    with raises(ExceptionGroup) as error_info:
        check_data(data, resource_properties)

    errors = error_info.value.exceptions
    assert len(errors) == data.width
    assert resource_properties.schema and resource_properties.schema.fields
    for error, field in zip(errors, resource_properties.schema.fields):
        polars_type = re.escape(str(data.schema[str(field.name)]))
        allowed_types = _get_allowed_polars_types(field.type)
        assert re.search(
            rf"'{field.name}'.*{allowed_types}.*found {polars_type}", str(error)
        )


def test_rejects_geopoint_with_incorrect_size():
    """Should raise an error if the size of the array representing a geopoint is not
    correct."""
    data = pl.DataFrame(
        {"my_geopoint": pl.Series([[1, 1, 1]] * 3, dtype=pl.Array(pl.Int8, 3))}
    )
    resource_properties = example_resource_properties()
    assert resource_properties.schema
    resource_properties.schema.fields = [
        FieldProperties(name="my_geopoint", type="geopoint")
    ]

    assert_raises_errors(lambda: check_data(data, resource_properties), ValueError, 1)


def test_rejects_geopoint_with_incorrect_inner_type():
    """Should raise an error if the type of the nested elements in a geopoint array is
    not correct."""
    data = pl.DataFrame(
        {"my_geopoint": pl.Series([["a", "b"]] * 3, dtype=pl.Array(pl.String, 2))}
    )
    resource_properties = example_resource_properties()
    assert resource_properties.schema
    resource_properties.schema.fields = [
        FieldProperties(name="my_geopoint", type="geopoint")
    ]

    assert_raises_errors(lambda: check_data(data, resource_properties), ValueError, 1)


def test_rejects_incorrect_resource_properties():
    """Should throw an error if the resource properties are incorrect."""
    assert_raises_check_errors(lambda: check_data(example_data(), ResourceProperties()))
