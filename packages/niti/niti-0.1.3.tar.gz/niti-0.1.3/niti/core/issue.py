"""Data structures for representing linting issues."""

from dataclasses import dataclass
from typing import Optional

from .severity import Severity


@dataclass
class LintIssue:
    """Represents a single linting issue found during code analysis.

    This data class encapsulates all information about a specific linting
    violation, including its location, severity, and potential fixes.

    Attributes:
        file_path: Path to the file containing the issue
        line_number: Line number where the issue occurs (1-indexed)
        column: Column number where the issue occurs (1-indexed)
        severity: Severity level of the issue
        rule_id: Unique identifier for the violated rule
        message: Human-readable description of the issue
        suggested_fix: Optional suggested correction for auto-fix functionality
    """

    file_path: str
    line_number: int
    column: int
    severity: Severity
    rule_id: str
    message: str
    suggested_fix: Optional[str] = None

    def __str__(self) -> str:
        """Format issue for display."""
        location = f"{self.file_path}:{self.line_number}:{self.column}"
        return (
            f"{self.severity.icon} {location} [{self.rule_id}] {self.message}"
        )
