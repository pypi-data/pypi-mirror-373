"""Module for interacting with Git repositories.

Provides a helper class to work with Git tags and logging.
"""

from git import Repo
from semver import Version


class GitHelper:
    """A helper class to interact with a local Git repository.

    Provides methods to retrieve the latest version from Git tags and create new tags.
    """

    repo: Repo

    def __init__(self) -> None:
        """Initialize the Git repository and remote connection.

        Args:
            None

        Returns:
            None

        """
        self.repo = Repo.init()
        self.remote = self.repo.remote()

    def get_version(self) -> Version | None:
        """Retrieve the latest version from the last Git tag.

        Args:
            None

        Returns:
            Version or None: Parsed semantic version if a tag exists, else None.

        Raises:
            ValueError: If the tag name is not a valid semantic version.

        Example:
            ```python
            print(GitHelper().get_version())
            #> Version.parse("1.0.0")
            ```

        """
        tag: str | None = None

        if self.repo.tags:
            tag: str = self.repo.tags[-1].name

        return Version.parse(tag) if tag else None

    def create_tag(self, *, tag: str) -> None:
        """Create a new Git tag with the specified name.

        Args:
            tag (str): Name of the new Git tag.

        Returns:
            None

        Raises:
            ValueError: If the tag already exists in the repository.

        Example:
            ```python
            GitHelper().create_tag(tag="1.2.0")
            ```

        """
        self.repo.create_tag(tag)
