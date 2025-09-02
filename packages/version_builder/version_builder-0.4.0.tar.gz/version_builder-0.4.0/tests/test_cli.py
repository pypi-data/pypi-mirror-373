from argparse import Namespace
from unittest.mock import patch

import pytest
from semver import Version

from src.version_builder.cli import CLI
from src.version_builder.constants import INITIAL_VERSION
from src.version_builder.exceptions import BadChoiceError
from src.version_builder.version import VERSION


class TestCLIArgs:
    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_without_arguments(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
    ):
        mock_parse_args.return_value = Namespace(
            version_file=None,
            toml_file=None,
            show=False,
            bump=False,
            builder_version=False,
        )

        cli = CLI()
        cli()

        mock_help.assert_called_once()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_not_called()
        mock_builder_version.assert_not_called()

    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_builder_version_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
    ):
        mock_parse_args.return_value = Namespace(
            version_file=None,
            toml_file=None,
            show=False,
            bump=False,
            builder_version=True,
        )

        cli = CLI()
        cli()

        mock_help.assert_not_called()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_not_called()
        mock_builder_version.assert_called_once()

    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_show_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
    ):
        mock_parse_args.return_value = Namespace(
            version_file=None,
            toml_file=None,
            show=True,
            bump=False,
            builder_version=False,
        )

        cli = CLI()
        cli()

        mock_help.assert_not_called()
        mock_show_last_tag.assert_called_once()
        mock_bump.assert_not_called()
        mock_builder_version.assert_not_called()

    @pytest.mark.parametrize("choice", ["major", "minor", "patch"])
    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_bump_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
        choice,
    ):
        mock_parse_args.return_value = Namespace(
            version_file=None,
            toml_file=None,
            show=False,
            bump=choice,
            builder_version=False,
        )

        cli = CLI()
        cli()

        mock_help.assert_not_called()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_called_once_with(choice=choice)
        mock_builder_version.assert_not_called()

    @pytest.mark.parametrize("choice", ["major", "minor", "patch"])
    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_version_file_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
        choice,
    ):
        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file=None,
            show=False,
            bump=choice,
            builder_version=False,
        )

        cli = CLI()
        cli()

        mock_help.assert_not_called()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_called_once_with(choice=choice)
        mock_builder_version.assert_not_called()
        assert cli.version_file_helper is not None
        assert cli.toml_helper is None

    @pytest.mark.parametrize("choice", ["major", "minor", "patch"])
    @patch("src.version_builder.cli.CLI.builder_version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_toml_file_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_builder_version,
        choice,
    ):
        mock_parse_args.return_value = Namespace(
            version_file=None,
            toml_file="pyproject.toml",
            show=False,
            bump=choice,
            builder_version=False,
        )

        cli = CLI()
        cli()

        mock_help.assert_not_called()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_called_once_with(choice=choice)
        mock_builder_version.assert_not_called()
        assert cli.version_file_helper is None
        assert cli.toml_helper is not None


class TestCLI:
    @patch("src.version_builder.logger.logger.info")
    @patch("src.version_builder.files.PyFileHelper.get_version")
    @patch("src.version_builder.files.TomlFileHelper.get_version")
    @patch("src.version_builder.git.GitHelper.get_version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_show(
        self,
        mock_parse_args,
        mocked_get_version,
        mocked_toml,
        mocked_py,
        mocked_logger,
    ):
        mocked_version = Version.parse("0.1.0")

        mocked_get_version.return_value = mocked_version
        mocked_toml.return_value = mocked_version
        mocked_py.return_value = mocked_version

        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file="pyproject.toml",
            show=False,
            bump=False,
            builder_version=False,
        )

        cli = CLI()
        cli()
        cli.show()

        assert mocked_logger.call_count == 3
        assert mocked_logger.mock_calls[0].args == ("Last git tag: %s", mocked_version)
        assert mocked_logger.mock_calls[1].args == (
            "Last toml version: %s",
            mocked_version,
        )
        assert mocked_logger.mock_calls[2].args == (
            "Last package version: %s",
            mocked_version,
        )

    @patch("src.version_builder.logger.logger.error")
    @patch("src.version_builder.logger.logger.info")
    @patch("src.version_builder.files.PyFileHelper.get_version")
    @patch("src.version_builder.files.TomlFileHelper.get_version")
    @patch("src.version_builder.git.GitHelper.get_version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_show_version_mismatch_toml(
        self,
        mock_parse_args,
        mocked_get_version,
        mocked_toml,
        mocked_py,
        mocked_logger,
        mocked_logger_error,
    ):
        mocked_version = Version.parse("0.1.0")
        mocked_mismatched_version = Version.parse("0.2.0")

        mocked_get_version.return_value = mocked_version
        mocked_toml.return_value = mocked_mismatched_version
        mocked_py.return_value = mocked_version

        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file="pyproject.toml",
            show=False,
            bump=False,
            builder_version=False,
        )

        cli = CLI()
        cli()
        cli.show()

        assert mocked_logger.call_count == 2
        assert mocked_logger.mock_calls[0].args == ("Last git tag: %s", mocked_version)
        assert mocked_logger.mock_calls[1].args == (
            "Last toml version: %s",
            mocked_mismatched_version,
        )

        assert mocked_logger_error.call_count == 1
        assert (
            mocked_logger_error.mock_calls[0].args[0] == "Cannot show last version: %s"
        )

    @patch("src.version_builder.logger.logger.error")
    @patch("src.version_builder.logger.logger.info")
    @patch("src.version_builder.files.PyFileHelper.get_version")
    @patch("src.version_builder.files.TomlFileHelper.get_version")
    @patch("src.version_builder.git.GitHelper.get_version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_show_version_mismatch_py(
        self,
        mock_parse_args,
        mocked_get_version,
        mocked_toml,
        mocked_py,
        mocked_logger,
        mocked_logger_error,
    ):
        mocked_version = Version.parse("0.1.0")
        mocked_mismatched_version = Version.parse("0.2.0")

        mocked_get_version.return_value = mocked_version
        mocked_toml.return_value = mocked_version
        mocked_py.return_value = mocked_mismatched_version

        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file="pyproject.toml",
            show=False,
            bump=False,
            builder_version=False,
        )

        cli = CLI()
        cli()
        cli.show()

        assert mocked_logger.call_count == 3
        assert mocked_logger.mock_calls[0].args == ("Last git tag: %s", mocked_version)
        assert mocked_logger.mock_calls[1].args == (
            "Last toml version: %s",
            mocked_version,
        )
        assert mocked_logger.mock_calls[2].args == (
            "Last package version: %s",
            mocked_mismatched_version,
        )

        assert mocked_logger_error.call_count == 1
        assert (
            mocked_logger_error.mock_calls[0].args[0] == "Cannot show last version: %s"
        )

    @patch("src.version_builder.logger.logger.info")
    def test_builder_version(self, mocked_logger):
        cli = CLI()
        cli.builder_version()

        assert mocked_logger.call_count == 1
        assert mocked_logger.mock_calls[0].args == (
            "Current version of builder: %s",
            VERSION,
        )

    @patch("src.version_builder.logger.logger.error")
    @pytest.mark.parametrize(
        "choice, expected_tag",
        [("major", "1.0.0"), ("minor", "0.2.0"), ("patch", "0.1.1"), ("bla", None)],
    )
    @patch("src.version_builder.files.PyFileHelper._write_lines")
    @patch("src.version_builder.files.TomlFileHelper._write_lines")
    @patch("src.version_builder.git.GitHelper.create_tag")
    @patch("src.version_builder.files.PyFileHelper._get_lines")
    @patch("src.version_builder.files.TomlFileHelper._get_lines")
    @patch("src.version_builder.git.GitHelper.get_version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_bump(
        self,
        mock_parse_args,
        mocked_get_version,
        mocked_toml_lines,
        mocked_py_lines,
        mock_tag,
        mocked_write_toml,
        mocked_write_py,
        mocked_logger,
        choice,
        expected_tag,
    ):
        mocked_version = Version.parse("0.1.0")
        mock_tag.return_value = None

        mocked_get_version.return_value = mocked_version
        mocked_toml_lines.return_value = ['version = "0.1.0"']
        mocked_py_lines.return_value = ['VERSION = "0.1.0"']

        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file="pyproject.toml",
            show=False,
            bump=choice,
            builder_version=False,
        )

        cli = CLI()
        cli()
        if expected_tag:
            mock_tag.assert_called_once_with(tag=expected_tag)
            mocked_logger.assert_not_called()
        else:
            mock_tag.assert_not_called()
            assert mocked_logger.mock_calls[0].args[0] == "Cannot bump version: %s"
            assert type(mocked_logger.mock_calls[0].args[1]) == type(BadChoiceError())

    @pytest.mark.parametrize(
        "choice",
        [
            "major",
            "minor",
            "patch",
        ],
    )
    @patch("src.version_builder.files.PyFileHelper._write_lines")
    @patch("src.version_builder.files.TomlFileHelper._write_lines")
    @patch("src.version_builder.git.GitHelper.create_tag")
    @patch("src.version_builder.files.PyFileHelper._get_lines")
    @patch("src.version_builder.files.TomlFileHelper._get_lines")
    @patch("src.version_builder.git.GitHelper.get_version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_bump_initial(
        self,
        mock_parse_args,
        mocked_get_version,
        mocked_toml_lines,
        mocked_py_lines,
        mock_tag,
        mocked_write_toml,
        mocked_write_py,
        choice,
    ):
        mock_tag.return_value = None

        mocked_get_version.return_value = None
        mocked_toml_lines.return_value = ["bla"]
        mocked_py_lines.return_value = ["bla"]

        mock_parse_args.return_value = Namespace(
            version_file="version.py",
            toml_file="pyproject.toml",
            show=False,
            bump=choice,
            builder_version=False,
        )

        cli = CLI()
        cli()
        cli.bump(choice=choice)

        mock_tag.assert_called_once_with(tag=INITIAL_VERSION)
