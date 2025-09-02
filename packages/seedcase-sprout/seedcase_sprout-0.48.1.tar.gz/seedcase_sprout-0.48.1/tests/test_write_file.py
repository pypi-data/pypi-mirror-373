from pytest import fixture, raises

from seedcase_sprout.write_file import write_file


@fixture
def file_content():
    return "This is test content."


def test_returns_path(tmp_path, file_content):
    """Tests that the path is returned."""
    file_path = tmp_path / "test.txt"

    assert write_file(file_content, file_path) == file_path


def test_creates_a_file_with_the_given_content(tmp_path, file_content):
    """Tests that a file with the given content is created."""
    file_path = tmp_path / "test.md"

    assert write_file(file_content, file_path) == file_path
    assert file_path.is_file()
    assert file_path.read_text() == file_content


def test_raises_error_when_parent_folder_does_not_exist(tmp_path, file_content):
    """Tests that FileNotFoundError is raised when the parent folder doesn't exist."""
    file_path = tmp_path / "non_existent_folder" / "test.md"

    with raises(FileNotFoundError):
        write_file(file_content, file_path)


def test_overwrites_file_content_if_file_already_exists(tmp_path, file_content):
    """Tests that if file already exists, it will be overwritten."""
    file_path = tmp_path / "test.txt"
    write_file(file_content, file_path)
    new_file_content = "This is new content."

    assert write_file(new_file_content, file_path) == file_path
    assert file_path.read_text() == new_file_content
