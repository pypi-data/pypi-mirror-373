from pathlib import Path

from seedcase_sprout.internals.to import _to_snake_case


def _create_resource_data_path(resource_name: str) -> str:
    """Creates a stringified relative path to the resource data file based on the name.

    Args:
        resource_name: The name of the resource.

    Returns:
        The relative path from the package root to the resource data file.
            E.g., "resources/test-resource/data.parquet"
    """
    return str(Path("resources", resource_name, "data.parquet"))


def _create_resource_properties_script_filename(resource_name: str = "") -> str:
    """Creates the filename for the resource properties script from the resource name.

    Args:
        resource_name: The name of the resource. Defaults to "".

    Returns:
        The filename.
    """
    return f"resource_properties{resource_name and '_'}{_to_snake_case(resource_name)}"
