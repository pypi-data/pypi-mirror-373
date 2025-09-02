"""External-facing functions of Seedcase Sprout."""
# This exposes only the functions we want exposed when
# the package is imported via `from seedcase_sprout import *`.

from pprint import pprint
from textwrap import dedent

from .as_readme_text import as_readme_text
from .check_data import check_data
from .check_properties import (
    check_package_properties,
    check_properties,
    check_resource_properties,
)
from .create_properties_script import create_properties_script
from .create_resource_properties_script import create_resource_properties_script
from .examples import (
    ExamplePackage,
    example_data,
    example_data_all_types,
    example_package_properties,
    example_resource_properties,
    example_resource_properties_all_types,
)
from .extract_field_properties import extract_field_properties
from .join_resource_batches import join_resource_batches
from .paths import PackagePath
from .properties import (
    ConstraintsProperties,
    ContributorProperties,
    FieldProperties,
    LicenseProperties,
    PackageProperties,
    ReferenceProperties,
    ResourceProperties,
    SourceProperties,
    TableSchemaForeignKeyProperties,
    TableSchemaProperties,
)
from .read_properties import read_properties
from .read_resource_batches import read_resource_batches
from .read_resource_data import read_resource_data
from .write_file import write_file
from .write_properties import write_properties
from .write_resource_batch import write_resource_batch
from .write_resource_data import write_resource_data

__all__ = [
    # Properties -----
    "ConstraintsProperties",
    "ContributorProperties",
    "FieldProperties",
    "LicenseProperties",
    "PackageProperties",
    "ReferenceProperties",
    "ResourceProperties",
    "SourceProperties",
    "TableSchemaForeignKeyProperties",
    "TableSchemaProperties",
    "read_properties",
    "create_properties_script",
    # Example data and properties -----
    "example_package_properties",
    "example_package_properties_diabetes_study",
    "example_resource_properties",
    "example_data",
    "example_data_patients",
    "example_data_all_types",
    "example_resource_properties_all_types",
    "ExamplePackage",
    # Packages -----
    "write_properties",
    "as_readme_text",
    # Resources -----
    "extract_field_properties",
    "join_resource_batches",
    "read_resource_batches",
    "read_resource_data",
    "write_resource_batch",
    "create_resource_properties_script",
    "write_resource_data",
    # Path -----
    "PackagePath",
    # Helpers -----
    # "pretty_json",
    "write_file",
    "pprint",
    "dedent",
    # Checks -----
    "check_package_properties",
    "check_properties",
    "check_resource_properties",
    "check_data",
]
