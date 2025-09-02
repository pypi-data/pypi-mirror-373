from pytest import mark

from seedcase_sprout import (
    PackageProperties,
    as_readme_text,
    example_package_properties,
    example_resource_properties_all_types,
)


def test_creates_readme():
    """Should create a README with basic information about the properties."""
    properties = example_package_properties()
    resource = example_resource_properties_all_types()
    assert resource.schema
    assert resource.schema.fields
    properties.resources = [resource]

    readme = as_readme_text(properties)

    assert str(resource.title) in readme
    assert all([str(field.name) in readme for field in resource.schema.fields])


def test_creates_readme_with_empty_values():
    """Should be able to create a README for an empty set of properties."""
    assert as_readme_text(PackageProperties())


@mark.parametrize(
    "description, expected",
    [
        # Empty or whitespace-only.
        ("", ""),
        ("    ", ""),
        # Single line text.
        ("Non-indented one-line text.", "Non-indented one-line text."),
        ("    Indented one-line text.", "Indented one-line text."),
        (
            "    Indented one-line text with trailing whitespace.   ",
            "Indented one-line text with trailing whitespace.   ",
        ),
        # Multiline text.
        ("Non-indented\nmultiline\ntext.", "Non-indented\nmultiline\ntext."),
        ("    Indented\n    multiline text.", "Indented\nmultiline text."),
        (
            """Non-indented first line,
            indented second line.""",
            "Non-indented first line,\nindented second line.",
        ),
        (
            """
            Indented multiline
            text
            """,
            "Indented multiline\ntext",
        ),
        # Tab indentation.
        (
            "\tIndented with tab\n\tAlso indented with tab",
            "Indented with tab\nAlso indented with tab",
        ),
        # Mixed indentation.
        (
            "\tIndented with tab\n    Indented with spaces\n\t  Mixed indented line",
            "Indented with tab\nIndented with spaces\nMixed indented line",
        ),
        (
            "  Indented with 2 spaces\n    Indented with 4 spaces\n  Back to 2 spaces",
            "Indented with 2 spaces\nIndented with 4 spaces\nBack to 2 spaces",
        ),
        # Multi-level list (relative indentation removed, not ideal).
        (
            """
            Description with multilevel list:
            - Item 1
                - Item 2""",
            "Description with multilevel list:\n- Item 1\n- Item 2",
        ),
    ],
)
def test_dedents_multiline_description(description, expected):
    """Should be able to dedent description."""
    properties = PackageProperties(
        name="diabetes-hypertension-study",
        description=description,
    )

    readme_text = as_readme_text(properties)
    assert expected in readme_text
