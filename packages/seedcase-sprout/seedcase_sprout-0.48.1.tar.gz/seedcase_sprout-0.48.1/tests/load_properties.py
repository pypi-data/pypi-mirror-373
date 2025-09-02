from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from seedcase_sprout.properties import Properties


def load_properties(path: Path, object_name: str) -> Properties:
    """Loads `Properties` object from file."""
    spec = spec_from_file_location("test_module", path)
    assert spec
    assert spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    properties: Properties = getattr(module, object_name)
    return properties
