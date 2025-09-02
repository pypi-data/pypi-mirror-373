from pathlib import Path


def _check_is_dir(path: Path) -> Path:
    """Checks whether the path exists and is a directory.

    Args:
        path: The path to check.

    Returns:
        The path if it is a directory.

    Raises:
        NotADirectoryError: If path either doesn't exist or isn't a directory.
    """
    if not path.is_dir():
        raise NotADirectoryError(f"{path} either doesn't exist or isn't a directory.")

    return path


def _check_is_file(path: Path) -> Path:
    """Checks whether the file given by the path exists and is a file.

    Args:
        path: The path to check.

    Returns:
        A path to the file if the path refers to a file.

    Raises:
        FileNotFound: If the file in the path doesn't exist or isn't a file.
    """
    if not path.is_file():
        raise FileNotFoundError(f"{path} is not a file.")

    return path
