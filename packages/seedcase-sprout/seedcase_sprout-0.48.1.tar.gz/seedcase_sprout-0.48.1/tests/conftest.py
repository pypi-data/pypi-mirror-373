import os

from pytest import fixture


@fixture
def tmp_cwd(tmp_path):
    """Temporarily changes the working directory to a temporary path.

    This fixture changes the current working directory to a temporary one
    (provided by pytest's `tmp_path`) for the duration of the test. After the
    test finishes, the original working directory is restored.

    Yields:
        The temporary path that becomes the current working directory.

    Examples:
        ```{python}
        def test_something(tmp_cwd):
            # cwd is now a temporary directory
            ...
        ```
    """
    original = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original)
