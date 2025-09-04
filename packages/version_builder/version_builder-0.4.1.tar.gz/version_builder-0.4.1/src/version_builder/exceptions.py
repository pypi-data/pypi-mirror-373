"""Custom exception raised when an invalid version bump choice is provided.

Used to signal errors in CLI or GitHelper when an unsupported option is selected.
"""


class BadChoiceError(Exception):
    """Exception raised for invalid choices passed to the bump command."""

    def __init__(self) -> None:
        """Initialize the exception with a default message.

        Message: "Invalid choice for bump version"
        """
        super().__init__("Invalid choice for bump version")


class VersionMismatchTomlError(Exception):
    """Exception raised when the version in Git does not match the version in TOML file.

    Args:
        None

    Returns:
        None

    Example:
        ```python
        raise VersionMismatchTomlError()
        #> Traceback (most recent call last):
        #> ...
        #> VersionMismatchTomlError: There is a mismatch between the git and toml-file.
        #> Fix it manually.
        ```

    """

    def __init__(self) -> None:
        """Initialize the exception with a message about version mismatch(TOML file)."""
        super().__init__(
            "There is a mismatch between the git and toml-file. Fix it manually.",
        )


class VersionMismatchPyError(Exception):
    """Exception raised when the version in Git does not match the Python file.

    Args:
        None

    Returns:
        None

    Example:
        ```python
        raise VersionMismatchPyError()
        #> Traceback (most recent call last):
        #> ...
        #> VersionMismatchPyError: There is a mismatch between the git and python-file.
        #> Fix it manually.
        ```

    """

    def __init__(self) -> None:
        """Initialize the exception about version mismatch(Python file)."""
        super().__init__(
            "There is a mismatch between the git and python-file. Fix it manually.",
        )
