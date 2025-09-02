import seedcase_sprout.check_datapackage as cdp

# Sprout-specific required fields and their types

PACKAGE_SPROUT_REQUIRED_FIELDS = (
    cdp.PACKAGE_REQUIRED_FIELDS
    | cdp.PACKAGE_RECOMMENDED_FIELDS
    | {
        "title": cdp.RequiredFieldType.str,
        "description": cdp.RequiredFieldType.str,
        "version": cdp.RequiredFieldType.str,
        "created": cdp.RequiredFieldType.str,
    }
)
PACKAGE_SPROUT_REQUIRED_FIELDS.pop("resources", None)

RESOURCE_SPROUT_REQUIRED_FIELDS = cdp.RESOURCE_REQUIRED_FIELDS | {
    "title": cdp.RequiredFieldType.str,
    "description": cdp.RequiredFieldType.str,
}
RESOURCE_SPROUT_REQUIRED_FIELDS.pop("data", None)
