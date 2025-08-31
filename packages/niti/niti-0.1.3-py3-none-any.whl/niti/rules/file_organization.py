"""File organization rules for C++ code."""

from typing import Any, List

from ..core.issue import LintIssue
from .base import RegexRule


class FileHeaderCopyrightRule(RegexRule):
    """Rule to check for copyright headers in files.

    All source files should have proper copyright headers.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Skip test files and third-party code
        if self._should_skip_file(file_path):
            return self.issues

        if not self._has_copyright_header(content):
            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[0] if len(lines) > 0 else ""
            if not self.should_skip_line(line_content, str(self.rule_id)):
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                    self.add_issue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        message="File missing copyright header",
                        suggested_fix="Add copyright header at the beginning of the file",
                    )

        return self.issues

    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped from copyright checking."""
        skip_patterns = [
            "/test/",
            "/tests/",
            "/third_party/",
            "/extern/",
            ".pb.h",  # Protobuf generated files
            ".pb.cc",
            "_test.h",
            "_test.cpp",
            "_test.cc",
        ]

        for pattern in skip_patterns:
            if pattern in file_path:
                return True

        return False

    def _has_copyright_header(self, content: str) -> bool:
        """Check if content has a copyright header."""
        lines = content.split("\n")[:20]  # Check first 20 lines

        copyright_indicators = [
            "copyright",
            "license",
            "apache",
            "mit license",
            "bsd license",
        ]

        content_lower = "\n".join(lines).lower()

        for indicator in copyright_indicators:
            if indicator in content_lower:
                return True

        return False


class FileReadErrorRule(RegexRule):
    """Rule to handle file read errors gracefully.

    This rule provides graceful error handling for various file I/O issues
    that might occur during linting, ensuring the linter doesn't crash
    on problematic files.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Skip test files - they may legitimately contain Unicode test data
        if self._should_skip_file(file_path):
            return self.issues

        # This rule is more about error handling during the linting process
        # We check for various file-related issues that could cause problems

        try:
            # Check if file is readable and valid
            if not content:
                # Empty file - this might be intentional, so just warn
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n") if content else [""]
                line_content = lines[0] if len(lines) > 0 else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path=file_path,
                            line_number=1,
                            column=1,
                            message="File appears to be empty",
                            suggested_fix="Verify file is not corrupted and contains expected content",
                        )
                return self.issues

            # Check for binary file content (non-text files)
            if self._appears_to_be_binary(content):
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[0] if len(lines) > 0 else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path=file_path,
                            line_number=1,
                            column=1,
                            message="File appears to contain binary data",
                            suggested_fix="Verify this is a text source file",
                        )
                return self.issues

            # Check for encoding issues
            encoding_issues = self._check_encoding_issues(content)
            if encoding_issues:
                for issue in encoding_issues:
                    line_num, message, fix = issue
                    # Check if this line should be skipped due to NOLINT directives
                    lines = content.split("\n")
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    if not self.should_skip_line(line_content, str(self.rule_id)):
                        # Check if next line skip applies
                        should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                        if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                            self.add_issue(
                                file_path=file_path,
                                line_number=line_num,
                                column=1,
                                message=message,
                                suggested_fix=fix,
                            )

            # Check for extremely long lines that might cause issues
            long_line_issues = self._check_for_extremely_long_lines(content)
            if long_line_issues:
                for issue in long_line_issues:
                    line_num, length = issue
                    # Check if this line should be skipped due to NOLINT directives
                    lines = content.split("\n")
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    if not self.should_skip_line(line_content, str(self.rule_id)):
                        # Check if next line skip applies
                        should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                        if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                            self.add_issue(
                                file_path=file_path,
                                line_number=line_num,
                                column=1,
                                message=f"Extremely long line ({length} characters) may cause performance issues",
                                suggested_fix="Consider breaking long lines or verify file is not corrupted",
                            )

            # Check for files that are suspiciously large
            if self._is_suspiciously_large(content):
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[0] if len(lines) > 0 else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path=file_path,
                            line_number=1,
                            column=1,
                            message="File is unusually large and may cause performance issues",
                            suggested_fix="Consider if this file should be processed by the linter",
                        )

        except Exception as e:
            # Catch any other file processing errors
            self.add_issue(
                file_path=file_path,
                line_number=1,
                column=1,
                message=f"Error processing file: {str(e)}",
                suggested_fix="Check file permissions and integrity",
            )

        return self.issues

    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped from encoding checks."""
        skip_patterns = [
            "/test/",
            "/tests/",
            "Test.cpp",
            "Test.h",
            "_test.cpp",
            "_test.h",
        ]

        for pattern in skip_patterns:
            if pattern in file_path:
                return True
        return False

    def _appears_to_be_binary(self, content: str) -> bool:
        """Check if content appears to be binary data."""
        # Check for null bytes or high ratio of non-printable characters
        if "\x00" in content:
            return True

        # Count non-printable characters (excluding common whitespace)
        printable_chars = 0
        total_chars = len(content)

        if total_chars == 0:
            return False

        for char in content:
            if char.isprintable() or char in "\n\r\t":
                printable_chars += 1

        # If less than 90% of characters are printable, likely binary
        printable_ratio = printable_chars / total_chars
        return printable_ratio < 0.9

    def _check_encoding_issues(self, content: str) -> List[tuple]:
        """Check for encoding-related issues."""
        issues = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for common encoding issues
            if "\ufffd" in line:  # Unicode replacement character
                issues.append(
                    (
                        line_num,
                        "Line contains Unicode replacement character (encoding issue)",
                        "Fix file encoding or remove invalid characters",
                    )
                )

            # Check for mixed line endings within the same file
            if "\r\n" in line and "\n" in line:
                issues.append(
                    (
                        line_num,
                        "Mixed line endings detected",
                        "Standardize line endings (prefer Unix LF)",
                    )
                )

        return issues

    def _check_for_extremely_long_lines(self, content: str) -> List[tuple]:
        """Check for lines that are extremely long."""
        issues = []
        lines = content.split("\n")

        # Lines longer than 10,000 characters are suspicious
        max_reasonable_length = 10000

        for line_num, line in enumerate(lines, 1):
            line_length = len(line)
            if line_length > max_reasonable_length:
                issues.append((line_num, line_length))

        return issues

    def _is_suspiciously_large(self, content: str) -> bool:
        """Check if file is suspiciously large."""
        # Files larger than 1MB might be problematic
        max_reasonable_size = 1024 * 1024  # 1MB
        return len(content) > max_reasonable_size


class FileNamingConventionRule(RegexRule):
    """Rule to enforce file naming conventions.

    Header and source files should use PascalCase naming convention
    to maintain consistency across the codebase.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Only check C++ header and source files
        if not self._is_cpp_file(file_path):
            return self.issues

        filename = self._extract_filename(file_path)
        if not filename:
            return self.issues

        # Check if filename follows PascalCase convention
        if not self._is_pascal_case_filename(filename):
            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[0] if len(lines) > 0 else ""
            if not self.should_skip_line(line_content, str(self.rule_id)):
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                    self.add_issue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        message=f"File '{filename}' should use PascalCase naming convention",
                        suggested_fix=f"Rename to {self._suggest_pascal_case_name(filename)}",
                    )

        return self.issues

    def _is_cpp_file(self, file_path: str) -> bool:
        """Check if file is a C++ header or source file."""
        cpp_extensions = [".h", ".hpp", ".hxx", ".cpp", ".cc", ".cxx"]
        return any(file_path.endswith(ext) for ext in cpp_extensions)

    def _extract_filename(self, file_path: str) -> str:
        """Extract filename from full path."""
        if "/" in file_path:
            return file_path.split("/")[-1]
        return file_path

    def _is_pascal_case_filename(self, filename: str) -> bool:
        """Check if filename follows PascalCase convention."""
        # Remove extension
        name_without_ext = (
            filename.split(".")[0] if "." in filename else filename
        )

        # Skip special files
        special_files = ["main", "pybind", "test"]
        if name_without_ext.lower() in special_files:
            return True

        # PascalCase should start with uppercase and not contain underscores
        if "_" in name_without_ext:
            return False

        # Should start with uppercase letter
        if not name_without_ext[0].isupper():
            return False

        return True

    def _suggest_pascal_case_name(self, filename: str) -> str:
        """Suggest PascalCase equivalent of filename."""
        # Split by extension
        parts = filename.split(".")
        name_part = parts[0]
        extension = "." + ".".join(parts[1:]) if len(parts) > 1 else ""

        # Convert snake_case to PascalCase
        if "_" in name_part:
            words = name_part.split("_")
            pascal_case = "".join(word.capitalize() for word in words)
        else:
            pascal_case = name_part.capitalize()

        return pascal_case + extension


class FileOrganizationHeaderRule(RegexRule):
    """Rule to enforce header file organization.

    Header files should be organized in the csrc/include/ directory structure
    following the established project organization patterns.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Only check header files
        if not self._is_header_file(file_path):
            return self.issues

        # Check if header is in proper location
        if not self._is_properly_organized_header(file_path):
            expected_path = self._suggest_proper_header_path(file_path)

            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[0] if len(lines) > 0 else ""
            if not self.should_skip_line(line_content, str(self.rule_id)):
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                    self.add_issue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        message=f"Header file not in proper csrc/include/ structure",
                        suggested_fix=f"Move to {expected_path}",
                    )

        return self.issues

    def _is_header_file(self, file_path: str) -> bool:
        """Check if file is a header file."""
        header_extensions = [".h", ".hpp", ".hxx"]
        return any(file_path.endswith(ext) for ext in header_extensions)

    def _is_properly_organized_header(self, file_path: str) -> bool:
        """Check if header file is properly organized."""
        # Skip temporary files used in tests
        if "/pip_tmp_dir/" in file_path or "/tmp/" in file_path:
            return True

        # Skip third-party and generated files
        skip_patterns = [
            "/third_party/",
            "/extern/",
            ".pb.h",  # Protobuf generated
            "/build/",
            "/cmake-build-",
        ]

        for pattern in skip_patterns:
            if pattern in file_path:
                return True  # Skip checking these files

        # Check if in csrc/include/ structure
        if "csrc/include/" in file_path:
            return True

        # Allow headers in csrc/test/ for test utilities
        if "csrc/test/" in file_path and file_path.endswith(".h"):
            return True

        return False

    def _suggest_proper_header_path(self, file_path: str) -> str:
        """Suggest proper path for header file."""
        filename = file_path.split("/")[-1]

        # Try to determine the appropriate subdirectory based on current path
        if "/native/" in file_path:
            # Extract the path after /native/
            native_part = file_path.split("/native/")[-1]
            return f"csrc/include/vajra/native/{native_part}"
        elif "/commons/" in file_path:
            # Commons headers
            commons_part = file_path.split("/commons/")[-1]
            return f"csrc/include/vajra/commons/{commons_part}"
        elif "/kernels/" in file_path:
            # Kernel headers
            kernels_part = file_path.split("/kernels/")[-1]
            return f"csrc/include/vajra/kernels/{kernels_part}"
        else:
            # Default to vajra include directory
            return f"csrc/include/vajra/{filename}"


class FileOrganizationTestRule(RegexRule):
    """Rule to enforce test file organization.

    Test files should be organized in the csrc/test/ directory structure
    following established patterns for maintainability.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Only check test files
        if not self._is_test_file(file_path):
            return self.issues

        # Check if test file is in proper location
        if not self._is_properly_organized_test(file_path):
            expected_path = self._suggest_proper_test_path(file_path)

            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[0] if len(lines) > 0 else ""
            if not self.should_skip_line(line_content, str(self.rule_id)):
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                    self.add_issue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        message=f"Test file not in proper csrc/test/ structure",
                        suggested_fix=f"Move to {expected_path}",
                    )

        return self.issues

    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        test_indicators = [
            "_test.cpp",
            "_test.cc",
            "_test.h",
            "Test.cpp",
            "Test.cc",
            "Test.h",
            "/test/",
            "/tests/",
        ]

        return any(indicator in file_path for indicator in test_indicators)

    def _is_properly_organized_test(self, file_path: str) -> bool:
        """Check if test file is properly organized."""
        # Should be in csrc/test/ structure
        if "csrc/test/" in file_path:
            return True

        # Allow some flexibility for legacy test organization
        legacy_patterns = ["/tests/", "/test/", "/gtest/", "/unittest/"]

        for pattern in legacy_patterns:
            if pattern in file_path and "csrc/" in file_path:
                return True  # Allow legacy patterns within csrc/

        return False

    def _suggest_proper_test_path(self, file_path: str) -> str:
        """Suggest proper path for test file."""
        filename = file_path.split("/")[-1]

        # Try to determine the appropriate test subdirectory
        if "/native/" in file_path:
            # Mirror the source structure
            native_part = file_path.split("/native/")[-1]
            # Remove /test/ or /tests/ from the path if present
            native_part = native_part.replace("/test/", "/").replace(
                "/tests/", "/"
            )
            return f"csrc/test/native/{native_part}"
        elif "/commons/" in file_path:
            commons_part = file_path.split("/commons/")[-1]
            commons_part = commons_part.replace("/test/", "/").replace(
                "/tests/", "/"
            )
            return f"csrc/test/commons/{commons_part}"
        elif "/kernels/" in file_path:
            kernels_part = file_path.split("/kernels/")[-1]
            kernels_part = kernels_part.replace("/test/", "/").replace(
                "/tests/", "/"
            )
            return f"csrc/test/kernels/{kernels_part}"
        else:
            # Default test location
            return f"csrc/test/{filename}"
