"""Severity levels for linting issues."""

from enum import Enum


class Severity(Enum):
    """Enumeration of linting issue severity levels.

    Used to categorize the importance and impact of linting violations.
    The severity level affects how issues are displayed and whether they
    cause the linter to exit with an error.

    ERROR: Critical issues that must be fixed (build will fail or serious bugs)
    WARNING: Important issues that should be fixed (style violations, potential bugs)
    INFO: Minor suggestions or informational messages (optional improvements)
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    def __str__(self) -> str:
        return self.value

    @property
    def icon(self) -> str:
        """Get emoji icon for the severity level."""
        return {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[self.value]
