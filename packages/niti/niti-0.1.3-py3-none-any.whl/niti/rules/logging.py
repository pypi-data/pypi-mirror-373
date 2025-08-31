"""Logging rules for C++ code to enforce proper logging practices."""

import re
from typing import Any, List

from ..core.issue import LintIssue
from .base import RegexRule


class LoggingForbiddenOutputRule(RegexRule):
    """Rule to detect and forbid direct output operations.

    Forbids the use of std::cout, std::cerr, printf, fprintf and similar
    direct output operations, suggesting the use of LOG_* macros instead
    for consistent logging throughout the codebase.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        lines = self.get_lines(content)

        # Patterns for forbidden output operations
        forbidden_patterns = [
            (
                re.compile(r"\bstd::cout\s*<<"),
                "std::cout",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* logging macro",
            ),
            (
                re.compile(r"\bstd::cerr\s*<<"),
                "std::cerr",
                "Use LOG_ERROR(), LOG_WARNING(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"\bstd::clog\s*<<"),
                "std::clog",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"(?<!std::)\bcout\s*<<"),
                "cout",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"(?<!std::)\bcerr\s*<<"),
                "cerr",
                "Use LOG_ERROR(), LOG_WARNING(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"(?<!std::)\bclog\s*<<"),
                "clog",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"\bprintf\s*\("),
                "printf",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro with formatting",
            ),
            (
                re.compile(r"\bfprintf\s*\("),
                "fprintf",
                "Use LOG_ERROR(), LOG_WARNING(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"\bsprintf\s*\("),
                "sprintf",
                "Use string formatting with LOG_* macros or std::format",
            ),
            (
                re.compile(r"\bsnprintf\s*\("),
                "snprintf",
                "Use string formatting with LOG_* macros or std::format",
            ),
            (
                re.compile(r"\bputs\s*\("),
                "puts",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro",
            ),
            (
                re.compile(r"\bputchar\s*\("),
                "putchar",
                "Use LOG_INFO(), LOG_DEBUG(), or appropriate LOG_* macro",
            ),
        ]

        for line_num, line in enumerate(lines, 1):
            # Skip comment lines
            stripped = line.strip()
            if (
                stripped.startswith("//")
                or stripped.startswith("*")
                or stripped.startswith("/*")
            ):
                continue

            # Check for skip directives
            if self.should_skip_line(line, str(self.rule_id)):
                continue

            should_skip_next, skip_rules = self.should_skip_next_line(
                content, line_num
            )
            if should_skip_next and (
                skip_rules == "all" or str(self.rule_id) in skip_rules
            ):
                continue

            for pattern, operation_name, alternative in forbidden_patterns:
                for match in pattern.finditer(line):
                    # Check if inside string literal or comment
                    if self.is_in_string_literal(
                        line, match.start()
                    ) or self.is_in_comment(line, match.start()):
                        continue

                    # Check for test files or debug contexts where this might be acceptable
                    if self._is_acceptable_context(
                        file_path, line, operation_name
                    ):
                        continue

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start() + 1,
                        message=f"Direct output operation '{operation_name}' detected. Use structured logging instead.",
                        suggested_fix=alternative,
                    )

        return self.issues

    def _is_acceptable_context(
        self, file_path: str, line: str, operation_name: str
    ) -> bool:
        """Check if the output operation is in an acceptable context."""
        # Allow in test files (but be more specific to avoid false positives)
        if (
            "/test/" in file_path.lower()
            or "/tests/" in file_path.lower()
            or "_test." in file_path.lower()
            or "test_" in file_path.lower()
            or file_path.lower().endswith("_test.cpp")
            or file_path.lower().endswith("_test.cc")
            or file_path.lower().endswith("_test.cxx")
        ):
            return True

        # Allow in example or demo files
        if (
            "example" in file_path.lower()
            or "demo" in file_path.lower()
            or "sample" in file_path.lower()
        ):
            return True

        # Allow in main functions for simple programs
        if "main(" in line or "int main" in line:
            return True

        # Allow debug builds or debug sections
        if (
            "#ifdef DEBUG" in line
            or "#ifndef NDEBUG" in line
            or "DEBUG_PRINT" in line
            or "VERBOSE_OUTPUT" in line
        ):
            return True

        # Allow specific printf-style operations for performance logging
        if operation_name in ["printf", "fprintf"] and (
            "benchmark" in line.lower()
            or "perf" in line.lower()
            or "timing" in line.lower()
            or "profil" in line.lower()
        ):
            return True

        # Allow in error handling for critical failures
        if operation_name in ["fprintf"] and (
            "stderr" in line or "STDERR" in line
        ):
            # Still suggest logging, but don't flag emergency error output
            return False

        return False
