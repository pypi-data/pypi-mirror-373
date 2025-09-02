from datetime import datetime
from typing import cast
from unittest.mock import patch
from uuid import UUID
from zoneinfo import ZoneInfo

import time_machine

from seedcase_sprout.create_properties_script import create_properties_script
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import LicenseProperties, PackageProperties
from tests.load_properties import load_properties


@patch("seedcase_sprout.properties.uuid4", return_value=UUID(int=1))
@time_machine.travel(datetime(2024, 5, 14, 5, 0, 1, tzinfo=ZoneInfo("UTC")), tick=False)
def test_creates_script_with_default_values(mock_uuid, tmp_cwd):
    """Should create a script with default values."""
    script_path = create_properties_script()

    assert script_path == PackagePath().properties_script()
    properties = load_properties(script_path, "package_properties")
    assert properties == PackageProperties(
        name=tmp_cwd.name,
        title="",
        description="",
        licenses=[LicenseProperties(name="")],
        id=str(mock_uuid()),
        version="0.1.0",
        created="2024-05-14T05:00:01+00:00",
    )


def test_works_with_custom_path(tmp_path):
    """Should work with a custom path."""
    script_path = create_properties_script(tmp_path)

    assert script_path == PackagePath(tmp_path).properties_script()
    properties = cast(
        PackageProperties, load_properties(script_path, "package_properties")
    )
    assert properties.name == tmp_path.name


def test_does_not_overwrite_existing_script(tmp_path):
    """Should not overwrite an existing script."""
    script_path = create_properties_script(tmp_path)

    # Create a file at the script path>
    script_path.write_text("This is a test file.")

    # Call the function again.
    new_script_path = create_properties_script(tmp_path)

    # The path should be the same, and the content should not change.
    assert new_script_path == script_path
    assert script_path.read_text() == "This is a test file."
