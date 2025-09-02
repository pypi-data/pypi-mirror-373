def get_json_path_to_resource_field(field: str, index: int | None = None) -> str:
    """Creates the JSON path to the specified field of a set of resource properties.

    Optionally adds the index of the resource properties, if they are part of a set of
    package properties.

    Args:
        field: The name of the field.
        index: The index of the resource properties. Defaults to None.

    Returns:
        The JSON path.
    """
    return "$." + ("" if index is None else f"resources[{index}].") + field
