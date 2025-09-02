import polars as pl
from polars.testing import assert_frame_equal
from pytest import fixture, raises

from seedcase_sprout.constants import BATCH_TIMESTAMP_COLUMN_NAME
from seedcase_sprout.examples import example_resource_properties
from seedcase_sprout.join_resource_batches import join_resource_batches
from seedcase_sprout.properties import (
    ResourceProperties,
)


@fixture
def data_list() -> list[pl.DataFrame]:
    return [
        pl.DataFrame(
            {
                "id": [0, 1],
                "name": ["anne", "belinda"],
                "value": [0.0, 1.1],
                # timestamp col from `read_resource_batches`
                BATCH_TIMESTAMP_COLUMN_NAME: ["2025-03-26T100000Z"] * 2,
            }
        ),
        pl.DataFrame(
            {
                "id": [2, 3, 0, 0, 0],
                "name": ["catherine", "dorothy", "anne", "anne", "alberta"],
                "value": [2.2, 3.3, 0.0, 9.9, 0.0],
                # timestamp col from `read_resource_batches` (different year than above)
                BATCH_TIMESTAMP_COLUMN_NAME: ["2024-03-26T100000Z"] * 5,
            }
        ),
    ]


@fixture
def resource_properties() -> ResourceProperties:
    """Fixture for resource_properties."""
    return example_resource_properties()


def test_batches_are_joined_correctly(data_list, resource_properties):
    """Test that the batches are joined correctly."""
    # Given
    resource_properties.schema.primary_key = "id"

    # When
    joined_batches = join_resource_batches(
        data_list=data_list,
        resource_properties=resource_properties,
    )

    # Then
    expected_joined_batches = pl.DataFrame(
        {
            # only one row with id 0 is kept, the latest one (it is unique in terms of
            # id, ignoring timestamp)
            "id": [1, 2, 3, 0],
            "name": ["belinda", "catherine", "dorothy", "anne"],
            "value": [1.1, 2.2, 3.3, 0.0],
        }
    )

    assert_frame_equal(
        joined_batches,
        expected_joined_batches,
        check_row_order=False,
    )


def test_batches_are_joined_correct_with_no_primary_key(data_list, resource_properties):
    """Duplicate rows (all cells are identical except timestamp) are removed when there
    isn't a primary key."""
    # Given
    resource_properties.schema.primary_key = None

    # When
    joined_batches = join_resource_batches(
        data_list=data_list,
        resource_properties=resource_properties,
    )
    # Then
    expected_joined_batches = pl.DataFrame(
        {
            # three rows with id 0 are kept (they are unique, ignoring timestamp)
            "id": [1, 2, 3, 0, 0, 0],
            "name": [
                "belinda",
                "catherine",
                "dorothy",
                "anne",
                "anne",
                "alberta",
            ],
            "value": [1.1, 2.2, 3.3, 0.0, 9.9, 0.0],
        }
    )

    assert_frame_equal(
        joined_batches,
        expected_joined_batches,
        check_row_order=False,
    )


def test_batches_joined_correctly_when_primary_key_is_multiple_fields(
    data_list, resource_properties
):
    """Batches are joined correctly when the primary key is multiple fields."""
    # Given
    resource_properties.schema.primary_key = ["id", "value"]

    # When
    joined_batches = join_resource_batches(
        data_list=data_list,
        resource_properties=resource_properties,
    )
    # Then
    expected_joined_batches = pl.DataFrame(
        {
            # two rows with id 0 are kept (they are unique in terms of id and value,
            # ignoring timestamp)
            "id": [1, 2, 3, 0, 0],
            "name": [
                "belinda",
                "catherine",
                "dorothy",
                "anne",
                "anne",
            ],
            "value": [1.1, 2.2, 3.3, 0.0, 9.9],
        }
    )

    assert_frame_equal(joined_batches, expected_joined_batches, check_row_order=False)


def test_throws_error_with_data_of_different_shapes(data_list, resource_properties):
    """Test that an error is raised when the data have different shapes."""
    # Given, when
    data_list.append(
        pl.DataFrame(
            {
                "id": [2],
                "name": ["bertha"],
                # value column is missing
                BATCH_TIMESTAMP_COLUMN_NAME: ["2024-03-26T100000Z"],
            }
        )
    )

    # Then
    with raises(pl.exceptions.ShapeError):
        join_resource_batches(
            data_list=data_list,
            resource_properties=resource_properties,
        )


def test_throws_error_with_non_matching_data_types(data_list, resource_properties):
    """Test that an error is raised when the data types don't match."""
    # Given, when
    data_list.append(
        pl.DataFrame(
            {
                "id": [2],
                "name": ["bertha"],
                "value": [1.1],
                BATCH_TIMESTAMP_COLUMN_NAME: ["2024-03-26T100000Z"],
            },
            schema={
                "id": pl.Int64,
                "name": pl.String,
                "value": pl.Object,  # different type than the other dataframes
                BATCH_TIMESTAMP_COLUMN_NAME: pl.String,
            },
        ),
    )

    # Then
    with raises(pl.exceptions.SchemaError):
        join_resource_batches(
            data_list=data_list,
            resource_properties=resource_properties,
        )


def test_throws_error_with_non_matching_column_names(data_list, resource_properties):
    """Test that an error is raised when the column names don't match."""
    # Given, when
    data_list.append(
        pl.DataFrame(
            {
                "id": [2],
                "unexpected_column_name": ["bertha"],
                "value": [1.1],
                BATCH_TIMESTAMP_COLUMN_NAME: ["2024-03-26T100000Z"],
            },
        )
    )

    # Then
    with raises(pl.exceptions.ShapeError):
        join_resource_batches(
            data_list=data_list,
            resource_properties=resource_properties,
        )


def test_single_dataframe_in_data_list(data_list, resource_properties):
    """Test that a single DataFrame is returned as is (except row order)."""
    # Given
    data_list = [data_list[0]]

    # When
    joined_batches = join_resource_batches(
        data_list=data_list,
        resource_properties=resource_properties,
    )

    # Then
    expected_joined_batches = data_list[0].drop(BATCH_TIMESTAMP_COLUMN_NAME)
    assert_frame_equal(joined_batches, expected_joined_batches, check_row_order=False)


def test_throws_error_with_empty_data_list(resource_properties):
    """Should throw an informative error if an empty data list is provided."""
    with raises(ValueError) as error:
        join_resource_batches([], resource_properties)

    assert resource_properties.name in str(error)
