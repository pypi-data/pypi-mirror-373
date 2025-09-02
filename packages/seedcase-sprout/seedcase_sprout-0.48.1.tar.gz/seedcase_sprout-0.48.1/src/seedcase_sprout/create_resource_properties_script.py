from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from seedcase_sprout.constants import TEMPLATES_PATH
from seedcase_sprout.internals import _create_resource_properties_script_filename
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import FieldProperties
from seedcase_sprout.sprout_checks.is_resource_name_correct import (
    _is_resource_name_correct,
)
from seedcase_sprout.write_file import write_file


def create_resource_properties_script(
    resource_name: str | None = None,
    fields: list[FieldProperties] | None = None,
    path: Path | None = None,
) -> Path:
    """Create a script using the resource properties template.

    You can include the resource name and the fields' name and type information.
    If the script already exists, it will not be overwritten.

    Args:
        resource_name: The name of the new resource. Defaults to None.
        fields: The fields (columns) of the new resource. Defaults to None.
        path: The path to the package folder. Defaults to the current working directory.

    Returns:
        The path to the newly created script file.

    Raises:
        ValueError: If the resource name is not correct (e.g., contains spaces).

    Examples:
        ```{python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            sp.create_resource_properties_script("my-resource")
        ```
    """
    if resource_name and not _is_resource_name_correct(resource_name):
        raise ValueError(
            f"The resource name '{resource_name}' is not correct. Resource names"
            " should only include lowercase alphanumeric characters and `.-_`."
        )
    resource_name = resource_name or ""
    script_path = PackagePath(path).resource_properties_script(resource_name)
    script_path.parent.mkdir(exist_ok=True)
    if script_path.exists():
        return script_path

    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=True)
    env.filters["to_variable_name"] = _create_resource_properties_script_filename
    template = env.get_template("resource_properties.py.jinja2")
    text = template.render(resource_name=resource_name, fields=fields)

    return write_file(text, script_path)
