from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from src.version_builder.files import TomlFileHelper


class TestTomlFileHelper:
    @patch("pathlib.Path.cwd")
    def test_initialize(self, mocked_getcwd, tmp_path):
        """
        Test that the TomlFileHelper is correctly initialized with the expected file path.

        Verifies that the helper uses the current working directory as a base path.
        """
        mocked_getcwd.return_value = tmp_path
        helper = TomlFileHelper(filepath="test.toml")
        assert str(helper.path) == f"{tmp_path}/test.toml"

    @pytest.mark.parametrize(
        "lines, expected_version",
        [
            (["test\nsome test"], None),
            (['version = "0.1.0"\nsome test'], "0.1.0"),
            (["version = '0.1.0'\nsome test"], "0.1.0"),
            (['VERSION = "0.1.0"\nsome test'], None),
            (["VERSION = '0.1.0'\nsome test"], None),
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
        Test that _get_version correctly identifies the version string in a TOML file.

        Validates both successful parsing and cases where the version is not found.
        """
        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = TomlFileHelper(filepath=f.name)
            assert helper._get_version() == expected_version

    @patch(
        "src.version_builder.files.TomlFileHelper._get_version",
        side_effect=Exception,
    )
    @patch("pathlib.Path.cwd")
    def test_get_version_raises(self, mocked_getcwd, tmp_path):
        """
        Test that get_version handles exceptions gracefully and logs errors.

        Ensures that an error message is logged when version retrieval fails.
        """
        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            helper = TomlFileHelper(filepath=f.name)
            with pytest.raises(Exception):
                assert helper.get_version() is None

    @pytest.mark.parametrize(
        "lines, expected_line",
        [
            ([], 'version = "0.2.0"\n'),
            (["test\nsome test"], "test\n"),
            (['version = "0.1.0"\nsome test'], 'version = "0.2.0"\n'),
            (["version = '0.1.0'\nsome test"], "version = '0.2.0'\n"),
            (['VERSION = "0.1.0"\nsome test'], 'VERSION = "0.1.0"\n'),
            (["VERSION = '0.1.0'\nsome test"], "VERSION = '0.1.0'\n"),
        ],
    )
    @patch("pathlib.Path.cwd")
    def test_update(self, mocked_getcwd, tmp_path, lines: list, expected_line):
        """
        Test that update correctly replaces the version line in the TOML file.

        Validates behavior for different file contents and ensures only the first match is updated.
        """
        new_version = "0.2.0"

        mocked_getcwd.return_value = tmp_path
        with NamedTemporaryFile(mode="w") as f:
            f.writelines(lines)
            f.seek(0)

            helper = TomlFileHelper(filepath=f.name)
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
    @patch(
        "src.version_builder.files.TomlFileHelper._get_version",
        side_effect=Exception,
    )
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

            helper = TomlFileHelper(filepath=f.name)
            with pytest.raises(Exception):
                helper.update(new_version=new_version)
