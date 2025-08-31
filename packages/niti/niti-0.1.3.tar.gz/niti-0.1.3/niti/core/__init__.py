"""Core components for the C++ linter."""

from .config import LinterConfig
from .engine import LintingEngine
from .issue import LintIssue
from .severity import Severity

__all__ = [
    "Severity",
    "LintIssue",
    "LinterConfig",
    "LintingEngine",
]
