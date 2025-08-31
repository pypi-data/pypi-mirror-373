"""Modern C++ Linter Package.

A comprehensive, configurable linting tool for enforcing modern C++ style guide
rules that are not covered by standard tools like clang-format and cpplint.

This package provides:
- AST-based analysis using tree-sitter
- Configurable project-specific rules
- Auto-fix capabilities for many violations
- Extensible rule system with clear severity levels
- Class trait enforcement (NonCopyable, NonMovable, etc.)

The package is designed to be standalone and can be easily extracted into
a separate repository for broader use.
"""

__version__ = "1.0.0"
__author__ = "Vajra Team"

from .core.config import LinterConfig
from .core.engine import LintingEngine
from .core.issue import LintIssue
from .core.severity import Severity

__all__ = [
    "Severity",
    "LintIssue",
    "LinterConfig",
    "LintingEngine",
]
