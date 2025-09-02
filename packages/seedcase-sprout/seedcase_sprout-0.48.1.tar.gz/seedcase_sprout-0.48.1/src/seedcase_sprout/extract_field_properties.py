import polars as pl

from seedcase_sprout.internals import _map, _map2
from seedcase_sprout.map_data_types import (
    _polars_to_datapackage,
)
from seedcase_sprout.properties import FieldProperties


def extract_field_properties(data: pl.DataFrame) -> list[FieldProperties]:
    """Extract field properties from a Polars DataFrame.

    Data types are extracted from the DataFrame's schema and mapped from Polars to
    Data Package data types. For the best results, ensure that the DataFrame's schema is
    correct---this may require some manually fixing. Since there are differences
    between Polars and Data Package data types, the mapping may not always be
    perfect, and some data types may be extracted to simpler types. For
    example, a year column may be extracted as an integer instead of Data
    Package's `year` type. Be sure to review and modify the extracted
    properties to suit your needs.

    Args:
        data: A Polars DataFrame containing the data to extract properties from.

    Returns:
        A list of `FieldProperties` objects, each representing a field/column in the
        DataFrame.

    Raises:
        ValueError: If the data is empty.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        sp.extract_field_properties(
            data=sp.example_data(),
        )
        ```
    """
    if data.is_empty():
        raise ValueError("Data is empty. Cannot extract field properties.")

    # TODO: add format="binary" to Binary field type?
    field_names = data.columns
    field_types = _map(data.dtypes, _polars_to_datapackage)

    field_properties = _map2(
        field_names,
        field_types,
        lambda name, type: FieldProperties(name=name, type=type),
    )

    return field_properties
