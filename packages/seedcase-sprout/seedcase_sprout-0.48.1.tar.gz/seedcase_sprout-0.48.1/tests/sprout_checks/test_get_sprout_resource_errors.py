from pathlib import Path

from pytest import fixture, mark

from seedcase_sprout.properties import ResourceProperties
from seedcase_sprout.sprout_checks.get_blank_value_for_type import (
    get_blank_value_for_type,
)
from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)
from seedcase_sprout.sprout_checks.get_sprout_resource_errors import (
    get_sprout_resource_errors,
)
from seedcase_sprout.sprout_checks.required_fields import (
    RESOURCE_SPROUT_REQUIRED_FIELDS,
)


@fixture
def properties():
    return ResourceProperties(
        name="resource-1",
        title="Resource 1",
        description="A resource.",
    ).compact_dict


def test_passes_full_resource_properties(properties):
    """Should pass with a full set of resource properties."""
    assert get_sprout_resource_errors(properties) == []


@mark.parametrize("index", [None, 2])
def test_error_found_if_inline_data_is_set(properties, index):
    """Should find an error if inline data is set."""
    properties["data"] = "some data"

    errors = get_sprout_resource_errors(properties, index=index)

    assert len(errors) == 1
    assert errors[0].json_path == get_json_path_to_resource_field("data", index)
    assert errors[0].validator == "inline-data"


@mark.parametrize("index", [None, 2])
@mark.parametrize("name,type", RESOURCE_SPROUT_REQUIRED_FIELDS.items())
def test_error_found_if_fields_are_blank(properties, name, type, index):
    """Should find an error if there is one required field that is present but blank."""
    properties[name] = get_blank_value_for_type(type)

    errors = get_sprout_resource_errors(properties, index=index)

    assert len(errors) == 1
    assert errors[0].json_path == get_json_path_to_resource_field(name, index)
    assert errors[0].validator == "blank"


@mark.parametrize("index", [None, 2])
@mark.parametrize("name", RESOURCE_SPROUT_REQUIRED_FIELDS.keys())
def test_error_found_if_required_fields_are_missing(properties, name, index):
    """Should find an error if there is a missing required field."""
    del properties[name]

    errors = get_sprout_resource_errors(properties, index=index)

    assert len(errors) == 1
    assert errors[0].json_path == get_json_path_to_resource_field(name, index)
    assert errors[0].validator == "required"


@mark.parametrize("path", ["", [], str(Path("resources", "1"))])
def test_error_found_if_data_path_is_incorrect_(properties, path):
    """Should find one error if `path` is not a string or has the wrong format."""
    properties["path"] = path

    errors = get_sprout_resource_errors(properties)

    assert len(errors) == 1
    assert errors[0].json_path == get_json_path_to_resource_field("path")


def test_ignores_path_if_name_incorrect(properties):
    """Should not check the path if the name is incorrect."""
    properties["name"] = "name with spaces"
    properties["path"] = "bad/path"

    assert get_sprout_resource_errors(properties) == []
