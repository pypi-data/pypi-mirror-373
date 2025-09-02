from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from seedcase_sprout.constants import TEMPLATES_PATH
from seedcase_sprout.internals import _to_dedented
from seedcase_sprout.properties import (
    LicenseProperties,
    PackageProperties,
)


def as_readme_text(properties: PackageProperties) -> str:
    """Create a human-readable version of the properties as a README string.

    Convert the properties object into human-readable version as Markdown-formatted
    text. Use this to generate the text for a `README.md` file and save it using
    `write_file()`.

    Args:
        properties: A `PackageProperties` object containing the package and resource
            properties.

    Returns:
        A Markdown-styled string to eventually save as a `README.md` file.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=True)
    env.filters["join_names"] = _join_names
    env.filters["format_date"] = _format_date
    env.filters["inline_code"] = _inline_code
    env.filters["format_link"] = _format_link
    template = env.get_template("README.jinja2")

    # Dedent description text.
    if properties.description:
        properties.description = _to_dedented(properties.description)

    return template.render(properties=properties)


def _join_names(licenses: list[LicenseProperties] | None) -> str:
    """Joins license names into a comma-separated list.

    Args:
        licenses: The licenses.

    Returns:
        A comma-separated list of names.
    """
    return ", ".join(str(license.name) for license in licenses) if licenses else "N/A"


def _format_date(created: str | None) -> str:
    """Transforms ISO date stamp to human-readable format.

    Args:
        created: The ISO date stamp.

    Returns:
        The date in a human-readable format.
    """
    return (
        datetime.fromisoformat(created).strftime("%d %B %Y, %H:%M")
        if created
        else "N/A"
    )


def _inline_code(value: str | None) -> str:
    """Adds inline code formatting to the input.

    Args:
        value: The value to format as inline code.

    Returns:
        The value formatted as inline code.
    """
    return f"`{value}`" if value else "N/A"


def _format_link(url: str | None, title: str = "See more") -> str:
    """Formats a URL as a markdown link.

    Args:
        url: The URL to format.
        title: The title to show for the link. Defaults to "See more".

    Returns:
        A markdown link using the URL and the title.
    """
    return f"[{title}]({url})" if url else "N/A"
