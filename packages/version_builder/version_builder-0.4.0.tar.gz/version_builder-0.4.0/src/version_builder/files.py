"""Module for reading and updating version information in files.

Provides abstract and concrete helpers for TOML and Python files.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path

from semver import Version


class BaseFileHelper(ABC):
    """Abstract base class for file-based version helpers.

    Provides common functionality for reading and writing file content.
    """

    path: Path

    def __init__(self, filepath: str) -> None:
        """Initialize the file path.

        Args:
            filepath (str): Relative path to the target file.

        Returns:
            None

        """
        self.path = Path.joinpath(Path(Path.cwd()), filepath)

    @abstractmethod
    def update(self, new_version: str) -> None:
        """Update the version in the file.

        Args:
            new_version (str): New version string to write.

        Returns:
            None

        Raises:
            NotImplementedError: If not implemented in a subclass.

        """
        raise NotImplementedError

    def get_version(self) -> Version | None:
        """Get the current version from the file.

        Args:
            None

        Returns:
            Version or None: Parsed semantic version if found, else None.

        Example:
            ```python
            print(helper.get_version())
            #> Version.parse("1.0.0")
            ```

        """
        version = self._get_version()
        return Version.parse(version) if version else None

    @abstractmethod
    def _get_version(self) -> str | None:
        """Extract the version string from the file.

        Args:
            None

        Returns:
            str or None: Version string if found, else None.

        Raises:
            NotImplementedError: If not implemented in a subclass.

        """
        raise NotImplementedError

    def _get_lines(self) -> list[str]:
        r"""Read all lines from the file.

        Args:
            None

        Returns:
            list[str]: List of lines in the file.

        Example:
            ```python
            print(helper._get_lines())
            #> ['version = "1.0.0"\n', '...\n']
            ```

        """
        lines: list
        with self.path.open() as file:
            lines = file.readlines()
        return lines

    def _write_lines(self, lines: list) -> None:
        r"""Write a list of strings back to the file.

        Args:
            lines (list): List of strings to write to the file.

        Returns:
            None

        Example:
            ```python
            helper._write_lines(['version = "1.0.0"\n'])
            ```

        """
        with self.path.open(mode="w") as file:
            file.writelines(lines)


class TomlFileHelper(BaseFileHelper):
    """Helper class for TOML-formatted version files.

    Supports extracting and updating version strings using TOML syntax.
    """

    def update(self, new_version: str) -> None:
        """Update the version in a TOML file.

        Args:
            new_version (str): New version string to write.

        Returns:
            None

        Example:
            ```python
            helper.update("1.2.0")
            ```

        """
        version: str | None = self._get_version()
        lines = self._get_lines()

        if version is not None:
            for i, line in enumerate(lines):
                if "version" in line and version in line:
                    lines[i] = line.replace(version, new_version)
                    break
        else:
            lines.append(f'version = "{new_version}"\n')

        self._write_lines(lines=lines)

    def _get_version(self) -> str | None:
        """Extract the version string from a TOML file.

        Args:
            None

        Returns:
            str or None: Version string if found, else None.

        Example:
            ```python
            print(helper._get_version())
            #> '1.0.0'
            ```

        """
        version: str | None = None

        for line in self._get_lines():
            matched = re.search(
                pattern=r"version.*?\=.*?(\"|\')(.*)(\"|\')",
                string=line,
            )
            if matched and (value := matched.group(2)):
                version = value
                break

        return version


class PyFileHelper(BaseFileHelper):
    """Helper class for Python-formatted version files.

    Supports extracting and updating version strings using Python assignment syntax.
    """

    def update(self, new_version: str) -> None:
        """Update the version in a Python file.

        Args:
            new_version (str): New version string to write.

        Returns:
            None

        Example:
            ```python
            helper.update("1.2.0")
            ```

        """
        version: str | None = self._get_version()
        lines = self._get_lines()

        if version is not None:
            for i, line in enumerate(lines):
                if "VERSION" in line and version in line:
                    lines[i] = line.replace(version, new_version)
                    break
        else:
            lines.append(f'VERSION: str = "{new_version}"\n')

        self._write_lines(lines=lines)

    def _get_version(self) -> str | None:
        """Extract the version string from a Python file.

        Args:
            None

        Returns:
            str or None: Version string if found, else None.

        Example:
            ```python
            print(helper._get_version())
            #> '1.0.0'
            ```

        """
        version: str | None = None

        for line in self._get_lines():
            matched = re.search(
                pattern=r"VERSION.*?\=.*?(\"|\')(.*)(\"|\')",
                string=line,
            )
            if matched and (value := matched.group(2)):
                version = value
                break

        return version
