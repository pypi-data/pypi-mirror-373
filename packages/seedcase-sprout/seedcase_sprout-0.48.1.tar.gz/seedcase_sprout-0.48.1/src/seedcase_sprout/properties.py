"""This module includes the dataclasses for the properties of a data package.

The properties are based on the Frictionless Data Package specification. They are used
as input for creating and editing the properties of data packages and data resources and
are intended to help users with the correct structure and content of the properties.
"""
# NOTE: This content is modified from the auto-generated
# `generate_properties/generated_properties.py` file. Update the auto-generated
# properties file to add more dataclasses and move them into this file.

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, Literal, Self
from uuid import uuid4

from dacite import Config, from_dict

from seedcase_sprout.internals import (
    _create_resource_data_path,
    _get_iso_timestamp,
    _to_camel_case,
)
from seedcase_sprout.sprout_checks.is_resource_name_correct import (
    _is_resource_name_correct,
)


@dataclass
class Properties(ABC):
    """An abstract base class for all `*Properties` classes holding common logic."""

    @property
    def compact_dict(self) -> dict[str, Any]:
        """Converts the dataclass `*Properties` object to a `camelCase` dictionary.

        Applies recursively to nested `*Properties` objects. Also removes any keys with
        None values.

        Returns:
            A dictionary representation of the `*Properties` object with only non-None
                values.
        """
        return asdict(
            obj=self,
            dict_factory=lambda tuples: {
                _to_camel_case(key): value for key, value in tuples if value is not None
            },
        )

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        """Creates a dataclass `*Properties` object filled with data from a dictionary.

        Args:
            cls: The class to create the `*Properties` object from.
            data: The data to fill the `*Properties` object with.

        Returns:
            A `*Properties` object with the properties from the dictionary.
        """
        return from_dict(
            data_class=cls,
            data=data,
            config=Config(
                # Expect keys in the input to be in camel case
                convert_key=_to_camel_case,
            ),
        )


@dataclass
class ContributorProperties(Properties):
    """The people or organizations who contributed to this data package.

    Creates a dataclass object with all the necessary properties for a
    contributor. This would be given in the `contributors` field of a
    `PackageProperties` object.

    Attributes:
        title (str | None): The name of the contributor.
        path (str | None): A fully qualified URL pointing to a relevant
            location online for the contributor.
        email (str | None): An email address.
        given_name (str | None): The name a person has been
            given, if the contributor is a person.
        family_name (str | None): The familial name that a person
            inherits, if the contributor is a person.
        organization (str | None): An organizational affiliation for this
            contributor.
        roles (list[str] | None): An array of strings describing the roles of the
            contributor.

    Examples:
        ```{python}
        import seedcase_sprout as sp
        print(sp.ContributorProperties())
        print(sp.ContributorProperties(title="Amir Smith"))
        ```
    """

    title: str | None = None
    path: str | None = None
    email: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    organization: str | None = None
    roles: list[str] | None = None


@dataclass
class LicenseProperties(Properties):
    """The license(s) under which the package or resource is provided.

    Creates a dataclass object with all the necessary properties for a
    license, so that it can be added to the `licenses` field of a
    `PackageProperties` object.

    Attributes:
        name (str | None): Must be an Open Definition license identifier,
            see http://licenses.opendefinition.org/
        path (str | None): A fully qualified URL, or a POSIX file path.
        title (str | None): A human-readable title.

    Examples:
        ```{python}
        import seedcase_sprout as sp
        print(sp.LicenseProperties())
        ```
    """

    name: str | None = None
    path: str | None = None
    title: str | None = None


@dataclass
class SourceProperties(Properties):
    """The raw sources for this data package.

    Attributes:
        title (str | None): The title of the source (e.g. document or organization).
        path (str | None): A fully qualified URL, or a POSIX file path.
        email (str | None): An email address.
        version (str | None): The version of the source.
    """

    title: str | None = None
    path: str | None = None
    email: str | None = None
    version: str | None = None


@dataclass
class ReferenceProperties(Properties):
    """The destination part of a foreign key.

    Attributes:
        resource (str | None): The name of the resource within the current data
            package where the `fields` are located.
        fields (list[str] | None): An array of strings of the same length as
            `TableSchemaForeignKeyProperties.fields`, specifying the field (or fields)
            that form the destination part of the foreign key.
    """

    resource: str | None = None
    fields: list[str] | None = None


@dataclass
class TableSchemaForeignKeyProperties(Properties):
    """A foreign key in a table schema.

    A foreign key is a reference where values in a field (or fields) on the table
    ("resource" in data package terminology) described by the table schema connect to
    values in a field (or fields) on this or a separate table (resource).

    Attributes:
        fields (list[str] | None): An array of strings specifying the field (or
            fields) on this resource that form the source part of the foreign key.
        reference (ReferenceProperties | None): An object specifying the
            destination part of the foreign key.
    """

    fields: list[str] | None = None
    reference: ReferenceProperties | None = None


# Allowed types for a field in a table schema.
FieldType = Literal[
    "string",
    "number",
    "integer",
    "boolean",
    "object",
    "array",
    "datetime",
    "date",
    "time",
    "year",
    "yearmonth",
    "duration",
    "geopoint",
    "geojson",
    "any",
]


@dataclass
class ConstraintsProperties(Properties):
    """A dataclass that expresses constraints for validating field values.

    A constraint is a rule that dictates the given values, or range of values,
    that a variable or column can have in a dataset. For instance, a constraint
    for an "age" column could be that it must be greater than 0 but less than 120.

    Attributes:
        required (bool | None): Indicates whether a property must have a
            value for each instance.
        unique (bool | None): When `true`, each value for the property
            must be unique.
        pattern (str | None): A regular expression pattern to test each
            value of the property against, where a truthy response indicates
            validity.
        enum (list[Any] | None): The value of the field must exactly match one of
            the values in the `enum` array.
        min_length (int | None): An integer that specifies the minimum
            length of a value.
        max_length (int | None): An integer that specifies the maximum
            length of a value.
        minimum (str | float | int | None): Specifies a minimum value for a field.
        maximum (str | float | int | None): Specifies a maximum value for a field.
        exclusive_minimum (str | float | int | None): Specifies an exclusive minimum
            value for a field.
        exclusive_maximum (str | float | int | None): Specifies an exclusive maximum
            value for a field.
        json_schema (dict[str, Any] | None): A valid JSON schema object to
            validate field values. If a field value conforms to the provided
            JSON schema then this field value is valid.
    """

    required: bool | None = None
    unique: bool | None = None
    pattern: str | None = None
    enum: list[Any] | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: str | float | int | None = None
    maximum: str | float | int | None = None
    exclusive_minimum: str | float | int | None = None
    exclusive_maximum: str | float | int | None = None
    json_schema: dict[str, Any] | None = None


@dataclass
class FieldProperties(Properties):
    """A field in a table schema.

    Provides human-readable documentation as well as additional information that can
    be used to validate the field or create a user interface for data entry.

    Attributes:
        name (str | None): A name for this field. Must be unique amongst other field
            names in this table schema.
        title (str | None): A human readable label or title for this field.
        type (FieldType | None): The data type of this field.
        format (str | None): The format for this field.
        description (str | None): A text description for this field.
        example (str | None): An example value for this field.
        constraints (ConstraintsProperties | None): The constraints applicable to
            this field.
        categories (list[str] | list[int] | None): A finite set of possible values
            for this field.
        categories_ordered (bool | None): Specifies whether the order of appearance
            of the values in the `categories` property should be regarded as their
            natural order.
    """

    name: str | None = None
    title: str | None = None
    type: FieldType | None = None
    format: str | None = None
    description: str | None = None
    example: str | None = None
    constraints: ConstraintsProperties | None = None
    categories: list[str] | list[int] | None = None
    categories_ordered: bool | None = None


# Allowed strategies for matching fields in the table schema to fields the data source.
FieldsMatchType = Literal["exact", "equal", "subset", "superset", "partial"]


@dataclass
class TableSchemaProperties(Properties):
    """A table schema for a data resource.

    Table schema is a simple language- and implementation-agnostic way to declare a
    schema for tabular data. Table schema is well suited for use cases around handling
    and validating tabular data in text formats such as CSV, but its utility extends
    well beyond this core usage, towards a range of applications where data benefits
    from a portable schema format.

    Attributes:
        fields (list[FieldProperties] | None): Specifies the fields in this table
            schema.
        fields_match (list[FieldsMatchType] | None): Specifies how fields in the table
            schema match the fields in the data source.
        primary_key (list[str] | str | None): A primary key is a field name or an array
            of field names, whose values must uniquely identify each row in the table.
        unique_keys (list[list[str]] | None): A field or a set of fields that are
            required to have unique logical values in each row in the table.
        foreign_keys (list[TableSchemaForeignKeyProperties] | None): A reference where
            values in a field (or fields) on the table (resource) described by this
            table schema connect to values in a field (or fields) on this or a separate
            table (resource).

    Examples:
        ```{python}
        import seedcase_sprout as sp
        print(sp.TableSchemaProperties(primary_key="id"))
        ```
    """

    fields: list[FieldProperties] | None = None
    fields_match: list[FieldsMatchType] | None = None
    primary_key: list[str] | str | None = None
    unique_keys: list[list[str]] | None = None
    foreign_keys: list[TableSchemaForeignKeyProperties] | None = None


@dataclass
class ResourceProperties(Properties):
    """A data resource.

    A simple format to describe and package a single data resource such as an
    individual table or file. The essence of a data resource is a locator for
    the data it describes. A range of other properties can be declared to provide a
    richer set of metadata.

    Creates a dataclass object with all the necessary properties for a resource,
    which would be given in the `resources` field of a `PackageProperties`
    dataclass.

    Attributes:
        name (str | None): A simple name or identifier to be used for this resource.
            Should consist only of lowercase English alphanumeric characters plus
            characters in `.-_`.
        path (str | None): A path pointing to the data for this resource.
        type (Literal['table'] | None): Specifies the type of the resource.
        title (str | None): A human-readable title.
        description (str | None): A text description. Markdown is encouraged.
        sources (list[SourceProperties] | None): The raw sources for this resource.
        licenses (list[LicenseProperties] | None): The license(s) under which the
            resource is published.
        format (str | None): The file format of this resource. Expected to be the
            standard file extension.
        mediatype (str | None): The media type of this resource. Can be any
            valid media type listed with
            [IANA](https://www.iana.org/assignments/media-types/media-types.xhtml).
        encoding (str | None): The file encoding of this resource.
        bytes (int | None): The size of this resource in bytes.
        hash (str | None): The MD5 hash of this resource. Indicate other
            hashing algorithms with the {algorithm}:{hash} format.
        schema (TableSchemaProperties | None): A table schema for the resource data,
            compliant with the table schema specification.

    Examples:
        ```{python}
        import seedcase_sprout as sp
        print(sp.ResourceProperties())
        print(sp.ResourceProperties(name="blood-samples", title="Blood samples"))
        ```
    """

    name: str | None = None
    path: str | None = None
    type: Literal["table"] | None = None
    title: str | None = None
    description: str | None = None
    sources: list[SourceProperties] | None = None
    licenses: list[LicenseProperties] | None = None
    format: str | None = None
    mediatype: str | None = None
    encoding: str | None = None
    bytes: int | None = None
    hash: str | None = None
    schema: TableSchemaProperties | None = None

    def __post_init__(self) -> None:
        """Generates the path from the resource name after object creation."""
        self.path = (
            _create_resource_data_path(str(self.name))
            if _is_resource_name_correct(self.name)
            else None
        )


@dataclass
class PackageProperties(Properties):
    """Properties for a data package.

    A simple container format for describing a coherent collection of data in a single
    "package". It provides the basis for convenient delivery, installation and
    management of datasets.

    Creates a dataclass object with all the necessary properties for the package.

    Attributes:
        name (str | None): A simple name or identifier to be used for this package.
            Should consist only of lowercase English alphanumeric characters plus
            characters in `.-_`.
        id (str | None): The unique identifier of this package.
        title (str | None): A human-readable title.
        description (str | None): A text description. Markdown is encouraged.
        homepage (str | None): The home on the web that is related to this package.
        version (str | None): A version string identifying the version of this package.
        created (str | None): The datetime on which this package was created.
        contributors (list[ContributorProperties] | None): The people or organizations
            who contributed to this package.
        keywords (list[str] | None): A list of keywords that describe this package.
        image (str | None): An image to represent this package.
        licenses (list[LicenseProperties] | None): The license(s) under which this
            package is published.
        resources (list[ResourceProperties] | None): Specifies the data resources
            in this data package, each compliant with the data resource specification.
        sources (list[SourceProperties] | None): The raw sources for this data
            package.

    Examples:
        ```{python}
        import seedcase_sprout as sp
        print(sp.PackageProperties())
        print(sp.PackageProperties(name="diabetes-cohort", title="Diabetes Cohort"))
        print(sp.PackageProperties(licenses=[sp.LicenseProperties(name="ODC-BY-1.0")]))

        # To allow multiline strings, use dedent.
        from textwrap import dedent
        print(sp.PackageProperties(
            title="Birds of North America",
            description=dedent('''
                # Markdown header

                A dataset of bird sightings. With some **bolding**.
                '''
            )
        ))
        ```
    """

    name: str | None = None
    id: str | None = None
    title: str | None = None
    description: str | None = None
    homepage: str | None = None
    version: str | None = None
    created: str | None = None
    contributors: list[ContributorProperties] | None = None
    keywords: list[str] | None = None
    image: str | None = None
    licenses: list[LicenseProperties] | None = None
    resources: list[ResourceProperties] | None = None
    sources: list[SourceProperties] | None = None

    @classmethod
    def from_default(
        cls,
        *,
        name: str | None = None,
        id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        homepage: str | None = None,
        version: str | None = None,
        created: str | None = None,
        contributors: list[ContributorProperties] | None = None,
        keywords: list[str] | None = None,
        image: str | None = None,
        licenses: list[LicenseProperties] | None = None,
        resources: list[ResourceProperties] | None = None,
        sources: list[SourceProperties] | None = None,
    ) -> Self:
        """Creates a `PackageProperties` dataclass with default values.

        Default values (`id`, `version`, and `created`) can be overridden and unset
        values can be set using keyword arguments.

        Args:
            name (str | None): A simple name or identifier to be used for this package.
                Should consist only of lowercase English alphanumeric characters plus
                characters in `.-_`.
            id (str | None): The unique identifier of this package.
            title (str | None): A human-readable title.
            description (str | None): A text description. Markdown is encouraged.
            homepage (str | None): The home on the web that is related to this package.
            version (str | None): A version string identifying the version of this
                package.
            created (str | None): The datetime on which this package was created.
            contributors (list[ContributorProperties] | None): The people or
                organizations
                who contributed to this package.
            keywords (list[str] | None): A list of keywords that describe this package.
            image (str | None): An image to represent this package.
            licenses (list[LicenseProperties] | None): The license(s) under which this
                package is published.
            resources (list[ResourceProperties] | None): Specifies the data resources
                in this data package, each compliant with the data resource
                specification.
            sources (list[SourceProperties] | None): The raw sources for this data
                package.

        Returns:
            A `PackageProperties` dataclass with default values.

        Examples:
            ```{python}
            import seedcase_sprout as sp

            sp.PackageProperties.from_default(name="my-package", title="My Package...")
            ```
        """
        return cls(
            name=name,
            id=id or str(uuid4()),
            title=title,
            description=description,
            homepage=homepage,
            version=version or "0.1.0",
            created=created or _get_iso_timestamp(),
            contributors=contributors,
            keywords=keywords,
            image=image,
            licenses=licenses,
            resources=resources,
            sources=sources,
        )
