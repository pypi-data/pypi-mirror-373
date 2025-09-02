from json import loads
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    """Reads the contents of a JSON file into an object.

    Args:
        path: The path to the file to load.

    Returns:
        The contents of the file as an object.

    Raises:
        JSONDecodeError: If the contents of the file cannot be de-serialised as JSON.
        TypeError: If the object in the file is not a dictionary.
    """
    loaded_object = loads(path.read_text())
    if not isinstance(loaded_object, dict):
        raise TypeError(
            f"Expected {path} to contain a JSON dictionary object "
            f"but found {type(loaded_object)}."
        )
    return loaded_object
