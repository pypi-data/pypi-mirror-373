import json
from pathlib import Path
from typing import Any

from seedcase_sprout.write_file import write_file


def _write_json(json_object: dict[str, Any], path: Path) -> Path:
    """Writes an object as an indented JSON string to the specified location.

    Args:
        json_object: The object to write to the file. Must be JSON serialisable.
        path: The path to the file with name and extension.

    Returns:
        The path to the newly created JSON file.

    Raises:
        FileNotFoundError: If the parent folder of the file doesn't exist.
        TypeError: If the object is not JSON serialisable.
    """
    return write_file(json.dumps(json_object, indent=2, ensure_ascii=False), path)
