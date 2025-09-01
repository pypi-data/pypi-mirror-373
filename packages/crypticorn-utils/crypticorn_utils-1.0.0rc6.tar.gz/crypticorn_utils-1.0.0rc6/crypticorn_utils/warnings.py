"""Crypticorn-specific warnings."""

from __future__ import annotations

from typing import Union


class CrypticornDeprecationWarning(DeprecationWarning):
    """A Crypticorn specific deprecation warning.

    This warning is raised when using deprecated functionality in Crypticorn. It provides information on when the
    deprecation was introduced and the expected version in which the corresponding functionality will be removed.

    Attributes:
        message: Description of the warning.
        since: Crypticorn version in what the deprecation was introduced.
        expected_removal: Crypticorn version in what the corresponding functionality expected to be removed.
    """

    message: str
    since: tuple[int, int]
    expected_removal: tuple[int, int]

    def __init__(
        self,
        message: str,
        *args: object,
        since: tuple[int, int],
        expected_removal: Union[tuple[int, int], None] = None,
    ) -> None:
        super().__init__(message, *args)
        self.message = message.rstrip(".")
        self.since = since
        self.expected_removal = (
            expected_removal if expected_removal is not None else (since[0] + 1, 0)
        )

    def __str__(self) -> str:
        message = (
            f"{self.message}. Deprecated in Crypticorn v{self.since[0]}.{self.since[1]}"
            f" to be removed in v{self.expected_removal[0]}.{self.expected_removal[1]}."
        )
        return message


class CrypticornExperimentalWarning(Warning):
    """A Crypticorn specific experimental functionality warning.

    This warning is raised when using experimental functionality in Crypticorn.
    It is raised to warn users that the functionality may change or be removed in future versions of Crypticorn.
    """
