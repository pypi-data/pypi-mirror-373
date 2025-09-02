from seedcase_sprout.check_datapackage import CheckError


def exclude_non_sprout_resource_errors(
    errors: list[CheckError],
) -> list[CheckError]:
    """Filters out resource errors that are not relevant for Sprout.

    Errors filtered out:
      - inline `data` required but missing
      - `path` is not of type array

    Args:
        errors: The full error list.

    Returns:
        The filtered error list.
    """
    return [
        error
        for error in errors
        if not (error.validator == "required" and error.json_path.endswith(".data"))
        and not (
            error.validator == "type"
            and error.json_path.endswith(".path")
            and error.message.endswith("not of type 'array'")
        )
    ]
