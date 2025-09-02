"""Internal functions for the package."""

from .check import _check_is_dir, _check_is_file
from .create import (
    _create_resource_data_path,
    _create_resource_properties_script_filename,
)
from .functionals import _map, _map2
from .get import _get_iso_timestamp, _get_nested_attr
from .read import _read_json
from .to import _to_camel_case, _to_dedented, _to_snake_case
from .write import _write_json

__all__ = [
    "_check_is_file",
    "_check_is_dir",
    "_create_resource_data_path",
    "_create_resource_properties_script_filename",
    "_to_snake_case",
    "_get_iso_timestamp",
    "_get_nested_attr",
    "_map",
    "_map2",
    "_read_json",
    "_write_json",
    "_to_camel_case",
    "_to_dedented",
]
