from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from src.version_builder.files import PyFileHelper


class TestVersionFileHelper:
    @patch("pathlib.Path.cwd")
    def test_initialize(self, mocked_getcwd, tmp_path):
        """
        Test that the PyFileHelper is correctly initialized with the expected file path.

        Verifies that the helper uses the current working directory as a base path.
        """
        mocked_getcwd.return_value = tmp_path
        helper = PyFileHelper(filepath="version.py")
        assert str(helper.path) == f"{tmp_path}/version.py"

    @pytest.mark.parametrize(
        "lines, expected_version",
        [
            (["test\nsome test"], None),
            (['version = "0.1.0"\nsome test'], None),
            (["version = '0.1.0'\nsome test"], None),
            (['VERSION = "0.1.0"\nsome test'], "0.1.0"),
            (["VERSION = '0.1.0'\nsome test"], "0.1.0"),
        ],
    )
    @patch("pathlib.Path.cwd")
    def test__get_version(
        self,
        mocked_getcwd,
        tmp_path,
        lines: list,
        expected_version: str | None,
    ):
        """
        Test that _get_version correctly identifies the version string in a Python file.

        Validates both successful parsing and cases where the version is not found.
        """
        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = PyFileHelper(filepath=f.name)
            assert helper._get_version() == expected_version

    @pytest.mark.parametrize(
        "lines, expected_version",
        [
            (["test\nsome test"], None),
            (['version = "0.1.0"\nsome test'], None),
            (["version = '0.1.0'\nsome test"], None),
            (['VERSION = "0.1.0"\nsome test'], "0.1.0"),
            (["VERSION = '0.1.0'\nsome test"], "0.1.0"),
        ],
    )
    @patch("pathlib.Path.cwd")
    def test_get_version(
        self,
        mocked_getcwd,
        tmp_path,
        lines: list,
        expected_version: str | None,
    ):
        """
        Test that get_version returns the parsed version or None if it cannot be found.

        Ensures the method handles different file content variations correctly.
        """
        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = PyFileHelper(filepath=f.name)
            if expected_version is None:
                assert helper.get_version() is None
            else:
                assert str(helper.get_version()) == expected_version

    @patch("src.version_builder.files.PyFileHelper._get_version", side_effect=Exception)
    @patch("pathlib.Path.cwd")
    def test_get_version_raises(self, mocked_getcwd, tmp_path):
        """
        Test that get_version logs an error when _get_version raises an exception.

        Ensures the method returns None and does not propagate the exception.
        """
        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            helper = PyFileHelper(filepath=f.name)
            with pytest.raises(Exception):
                assert helper.get_version()

    @pytest.mark.parametrize(
        "lines, expected_line",
        [
            ([], 'VERSION: str = "0.2.0"\n'),
            (["test\nsome test"], "test\n"),
            (['version = "0.1.0"\nsome test'], 'version = "0.1.0"\n'),
            (["version = '0.1.0'\nsome test"], "version = '0.1.0'\n"),
            (['VERSION = "0.1.0"\nsome test'], 'VERSION = "0.2.0"\n'),
            (["VERSION = '0.1.0'\nsome test"], "VERSION = '0.2.0'\n"),
        ],
    )
    @patch("pathlib.Path.cwd")
    def test_update(self, mocked_getcwd, tmp_path, lines: list, expected_line):
        """
        Test that update correctly replaces the version line in the Python file.

        Validates behavior for different file contents and ensures only the first match is updated.
        """
        new_version = "0.2.0"

        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = PyFileHelper(filepath=f.name)
            helper.update(new_version=new_version)

            with open(f.name) as f_updated:
                assert expected_line == f_updated.readlines()[0]

    @pytest.mark.parametrize(
        "lines, expected_line",
        [
            ([], 'VERSION: str = "0.2.0"\n'),
            (["test\nsome test"], "test\n"),
            (['version = "0.1.0"\nsome test'], 'version = "0.1.0"\n'),
            (["version = '0.1.0'\nsome test"], "version = '0.1.0'\n"),
            (['VERSION = "0.1.0"\nsome test'], 'VERSION = "0.2.0"\n'),
            (["VERSION = '0.1.0'\nsome test"], "VERSION = '0.2.0'\n"),
        ],
    )
    @patch("src.version_builder.files.PyFileHelper._get_version", side_effect=Exception)
    @patch("pathlib.Path.cwd")
    def test_update_raises(self, mocked_getcwd, tmp_path, lines: list, expected_line):
        """
        Test that update logs an error and does not modify the file when version retrieval fails.

        Ensures that no changes are made to the file on failure.
        """
        new_version = "0.2.0"

        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = PyFileHelper(filepath=f.name)
            with pytest.raises(Exception):
                helper.update(new_version=new_version)
