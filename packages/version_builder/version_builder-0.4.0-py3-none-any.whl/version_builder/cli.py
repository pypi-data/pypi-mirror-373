"""Module for the command-line interface of version_builder.

Provides a CLI entry point to interact with Git tags and display help.
"""

import argparse

from semver import Version

from .constants import ENABLED_CHOICES, INITIAL_VERSION
from .exceptions import BadChoiceError, VersionMismatchPyError, VersionMismatchTomlError
from .files import PyFileHelper, TomlFileHelper
from .git import GitHelper
from .logger import logger as log
from .version import VERSION


class CLI:
    """Handles command-line arguments and user interaction.

    Parses CLI inputs and delegates actions to Git and file helpers.
    """

    git: GitHelper
    version_file_helper: PyFileHelper | None = None
    toml_helper: TomlFileHelper | None = None

    def __init__(self) -> None:
        """Initialize the Git helper and argument parser.

        Args:
            None

        Returns:
            None

        """
        self.git = GitHelper()

        self.parser = argparse.ArgumentParser(
            prog="version_builder",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.parser.add_argument(
            "-v",
            "--builder-version",
            action="store_true",
            help="Show builder version",
        )
        self.parser.add_argument(
            "-s",
            "--show",
            action="store_true",
            help="Show last tag",
        )
        self.parser.add_argument(
            "-b",
            "--bump",
            choices=ENABLED_CHOICES,
            help="Bump version (default: patch)",
        )
        self.parser.add_argument(
            "-tf",
            "--toml-file",
            type=str,
            default=None,
            help="Path to the toml file (default: not set)",
        )
        self.parser.add_argument(
            "-vf",
            "--version-file",
            type=str,
            default=None,
            help="Path to the version file (default: not set)",
        )

    def __call__(self) -> None:
        """Parse arguments and execute the appropriate command.

        Args:
            None

        Returns:
            None

        """
        args = self.parser.parse_args()
        if args.version_file:
            self.version_file_helper = PyFileHelper(filepath=args.version_file)
        if args.toml_file:
            self.toml_helper = TomlFileHelper(filepath=args.toml_file)

        if args.show:
            self.show()
        elif args.bump:
            self.bump(choice=args.bump)
        elif args.builder_version:
            self.builder_version()
        else:
            self.help()

    def show(self) -> None:
        """Display the latest Git tag and version from TOML and Python files.

        Args:
            None

        Returns:
            None

        Example:
            ```python
            cli.show()
            #> Last git tag: 1.0.0
            #> Last toml version: 1.0.0
            #> Last package version: 1.0.0
            ```

        """
        try:
            self._last_version()
        except Exception as e:  # noqa: BLE001
            log.error("Cannot show last version: %s", e)

    def bump(self, choice: ENABLED_CHOICES) -> None:
        """Bump the version in Git, TOML and Python files.

        Args:
            choice (str): One of 'major', 'minor', 'patch'

        Returns:
            None

        Raises:
            BadChoiceError: If an invalid bump option is provided.
            VersionMismatchPyError: If Git and Python versions do not match.
            VersionMismatchTomlError: If Git and TOML versions do not match.

        Example:
            ```python
            cli.bump(choice="minor")
            #> Success!
            #> You can now commit and push your changes.
            ```

        """
        try:
            last_version = self._last_version()
            if last_version:
                new_version = self._generate_tag_name(
                    version=last_version,
                    choice=choice,
                )
            else:
                new_version = INITIAL_VERSION

            self.toml_helper.update(new_version=new_version)
            self.version_file_helper.update(new_version=new_version)
            self.git.create_tag(tag=new_version)

            log.info("Success!\nYou can now commit and push your changes.")
        except Exception as e:  # noqa: BLE001
            log.error("Cannot bump version: %s", e)

    def help(self) -> None:
        """Print help message from the argument parser.

        Args:
            None

        Returns:
            None

        """
        self.parser.print_help()

    @staticmethod
    def builder_version() -> None:
        """Display the current version of the version_builder package.

        Args:
            None

        Returns:
            None

        Example:
            ```python
            CLI.builder_version()
            #> Current version of builder: 0.3.0
            ```

        """
        log.info("Current version of builder: %s", VERSION)

    def _last_version(self) -> Version | None:
        """Get the latest version from Git and compare it with TOML and Python files.

        Args:
            None

        Returns:
            Version or None: Latest semantic version from Git.

        Raises:
            VersionMismatchPyError: If Git and Python versions do not match.
            VersionMismatchTomlError: If Git and TOML versions do not match.

        Example:
            ```python
            print(cli._last_version())
            #> Last git tag: 1.0.0
            #> Last toml version: 1.0.0
            #> Last package version: 1.0.0
            #> 1.0.0
            ```

        """
        last_tag: Version | None = self.git.get_version()
        log.info("Last git tag: %s", last_tag)

        if self.toml_helper:
            last_toml_version: Version | None = self.toml_helper.get_version()
            log.info("Last toml version: %s", last_toml_version)
            if last_tag != last_toml_version:
                raise VersionMismatchTomlError

        if self.version_file_helper:
            last_package_version: Version | None = (
                self.version_file_helper.get_version()
            )
            log.info("Last package version: %s", last_package_version)
            if last_tag != last_package_version:
                raise VersionMismatchPyError

        return last_tag

    @staticmethod
    def _generate_tag_name(*, version: Version, choice: ENABLED_CHOICES) -> str:
        """Generate a new semantic version string.

        Args:
            version (Version): Last semantic version.
            choice (str): One of 'major', 'minor', 'patch'.

        Returns:
            str: New semantic version string.

        Raises:
            BadChoiceError: If an invalid bump option is provided.

        Example:
            ```python
            print(CLI._generate_tag_name(
                version=Version.parse("1.2.3"),
                choice="minor")
            )
            #> '1.3.0'
            ```

        """
        match choice:
            case "major":
                version = version.bump_major()
            case "minor":
                version = version.bump_minor()
            case "patch":
                version = version.bump_patch()
            case _:
                raise BadChoiceError

        return str(version)


def main() -> None:
    """Entry point for the CLI application.

    Args:
        None

    Returns:
        None

    """
    cli_helper = CLI()
    cli_helper()
