from pathlib import Path


def write_file(string: str, path: Path) -> Path:
    """Write the `string` to a file at the specified `path`.

    The parent folder of the file in `path` must exist.
    If the file already exists, it will be overwritten.

    Args:
        string: The content you want written to the file.
        path: The full path to the file you want to create, including the file name and
            extension.

    Returns:
        The path to the file that was created.

    Raises:
        FileNotFoundError: If the parent folder of the file doesn't exist.
    """
    path.write_text(string)

    return path
