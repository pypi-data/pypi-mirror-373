from pathlib import Path
from typing import cast

from seedcase_sprout.check_properties import check_properties
from seedcase_sprout.internals import _to_dedented, _write_json
from seedcase_sprout.internals.get import _get_nested_attr
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import (
    FieldProperties,
    PackageProperties,
)


def write_properties(properties: PackageProperties, path: Path | None = None) -> Path:
    """Write the `properties` to the `datapackage.json` file.

    If the `datapackage.json` file already exists, it will be overwritten. If not,
    a new file will be created.

    Args:
        properties: The properties to write. Use `create_properties_script()` to
            create a file with your properties object.
        path: A `Path` to the `datapackage.json` file.

    Returns:
        The path to the updated `datapackage.json` file.

    Raises:
        ExceptionGroup: If there is an error in the properties. A group of
            `CheckError`s, one error for each failed check.
    """
    path = path or PackagePath().properties()

    # Dedent descriptions
    properties.description = _to_dedented(properties.description)

    # TODO: Code to find all description fields and dedent to avoid nested for-loops?
    for resource in properties.resources or []:
        resource.description = _to_dedented(resource.description)

        for field in cast(
            list[FieldProperties],
            _get_nested_attr(resource, "schema.fields", default=[]),
        ):
            field.description = _to_dedented(field.description)

    check_properties(properties)

    return _write_json(properties.compact_dict, path)
