from pathlib import Path

from seedcase_sprout import (
    example_package_properties,
    write_properties,
)


def create_test_data_package(tmp_path: Path) -> Path:
    """Creates a package file structure (with empty files) for path function tests.

    Args:
        tmp_path: Path to a temporary folder.

    Returns:
        Path of package.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    write_properties(
        properties=example_package_properties(), path=tmp_path / "datapackage.json"
    )

    (tmp_path / "README.md").touch()

    return tmp_path
