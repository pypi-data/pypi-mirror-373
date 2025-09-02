from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from seedcase_sprout.constants import TEMPLATES_PATH
from seedcase_sprout.paths import PackagePath
from seedcase_sprout.properties import PackageProperties
from seedcase_sprout.write_file import write_file


def create_properties_script(path: Path | None = None) -> Path:
    """Create a properties script with default values.

    If the script already exists, it will not be overwritten.

    Args:
        path: The path to the package folder. Defaults to the current working directory.

    Returns:
        The path to the newly created properties script.

    Examples:
        ```{python}
        import seedcase_sprout as sp

        with sp.ExamplePackage():
            sp.create_properties_script()
        ```
    """
    package_path = PackagePath(path)
    script_path = package_path.properties_script()
    script_path.parent.mkdir(exist_ok=True)
    # We don't want to overwrite an existing script.
    if script_path.exists():
        return script_path

    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=True)
    template = env.get_template("package_properties.py.jinja2")
    text = template.render(
        properties=PackageProperties.from_default(name=package_path.root().name)
    )
    return write_file(text, script_path)
