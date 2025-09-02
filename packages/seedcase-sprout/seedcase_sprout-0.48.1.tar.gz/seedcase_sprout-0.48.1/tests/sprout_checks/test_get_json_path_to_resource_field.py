from seedcase_sprout.sprout_checks.get_json_path_to_resource_field import (
    get_json_path_to_resource_field,
)


def test_returns_expected_json_path_without_index():
    """Should form the correct JSON path with no index supplied."""
    assert get_json_path_to_resource_field("myField") == "$.myField"


def test_returns_correct_path_with_index():
    """Should form the correct JSON path with a resource index supplied."""
    assert get_json_path_to_resource_field("myField", 2) == "$.resources[2].myField"
