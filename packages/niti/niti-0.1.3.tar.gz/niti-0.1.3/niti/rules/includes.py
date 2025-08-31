"""Include order and style rules for C++ code."""

import re
from typing import Any, List

from ..core.issue import LintIssue
from ..core.severity import Severity
from .base import AutofixResult, RegexRule
from .rule_id import RuleId


class IncludeOrderWrongRule(RegexRule):
    """Rule to check include order.

    Enforces the include order:
    1. Main header (for .cpp files)
    2. C standard library headers
    3. C++ standard library headers
    4. Third-party library headers
    5. Project headers

    Also checks for alphabetical sorting within groups and newline separators
    between groups.
    """

    def __init__(self, rule_id: RuleId, severity: Severity):
        super().__init__(rule_id, severity)
        self.supports_autofix = True

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        includes = self._extract_includes(content)
        if len(includes) < 2:
            return self.issues

        lines = content.split("\n")

        # Check for alphabetical order within groups
        self._check_within_group_sorting(includes, file_path, content)

        # Check for newline separators between groups
        self._check_group_separation(includes, lines, file_path, content)

        # Check overall group order
        categorized = self._categorize_includes(includes)
        expected_order = self._get_expected_order(file_path)
        group_order_violations = self._check_group_order(
            categorized, expected_order
        )

        for violation in group_order_violations:
            line_num, message, suggestion = violation
            
            # Check if this line should be skipped due to NOLINT directives
            line_content = self.get_line(content, line_num)
            if self.should_skip_line(line_content, str(self.rule_id)):
                continue
            
            # Check if next line skip applies
            should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
            if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                continue
            
            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=1,
                message=message,
                suggested_fix=suggestion,
            )

        return self.issues

    def _check_within_group_sorting(
        self, includes: List[tuple], file_path: str, content: str
    ):
        """Check for alphabetical sorting within each include group."""
        last_category = None
        group_start_index = 0
        for i, include in enumerate(includes):
            line_num, path, is_system, full_line = include
            category = self._get_include_category(path, is_system)

            if category != last_category and last_category is not None:
                # Process the previous group
                group = includes[group_start_index:i]
                self._verify_and_report_sorting(group, last_category, file_path, content)
                group_start_index = i

            last_category = category

        # Process the last group
        group = includes[group_start_index:]
        self._verify_and_report_sorting(group, last_category, file_path, content)

    def _verify_and_report_sorting(
        self, group: List[tuple], category: str, file_path: str, content: str
    ):
        """Verify sorting for a single group and report the first violation."""
        if len(group) < 2:
            return

        paths = [item[1] for item in group]
        sorted_paths = sorted(paths)

        if paths != sorted_paths:
            for i, path in enumerate(paths):
                if path != sorted_paths[i]:
                    line_num = group[i][0]
                    
                    # Check if this line should be skipped due to NOLINT directives
                    line_content = self.get_line(content, line_num)
                    if self.should_skip_line(line_content, str(self.rule_id)):
                        continue
                    
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                    if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                        continue
                    
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Include '{path}' is not in alphabetical order within the '{category}' group.",
                        suggested_fix="Sort includes alphabetically within each group.",
                    )
                    # Report only the first violation in the group to avoid noise
                    return

    def _check_group_separation(
        self, includes: List[tuple], lines: List[str], file_path: str, content: str
    ):
        """Check for newline separators between different include groups."""
        if len(includes) < 2:
            return

        for i in range(1, len(includes)):
            prev_include = includes[i - 1]
            curr_include = includes[i]

            prev_category = self._get_include_category(
                prev_include[1], prev_include[2]
            )
            curr_category = self._get_include_category(
                curr_include[1], curr_include[2]
            )

            if prev_category != curr_category:
                # Check for a blank line or separator between the two includes
                start_line = prev_include[
                    0
                ]  # 1-based, so it's the line after the include
                end_line = (
                    curr_include[0] - 1
                )  # 1-based, so it's the line before the include

                is_separated = False
                if start_line <= end_line:
                    for line_idx in range(start_line, end_line + 1):
                        line_content = lines[line_idx - 1].strip()
                        if not line_content or line_content.startswith(
                            "//===="
                        ):
                            is_separated = True
                            break

                if not is_separated:
                    # Check if this line should be skipped due to NOLINT directives
                    line_content = lines[curr_include[0] - 1] if curr_include[0] <= len(lines) else ""
                    if self.should_skip_line(line_content, str(self.rule_id)):
                        continue
                    
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, curr_include[0])
                    if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                        continue
                    
                    self.add_issue(
                        file_path=file_path,
                        line_number=curr_include[0],
                        column=1,
                        message=f"Missing newline separator between include groups ('{prev_category}' and '{curr_category}').",
                        suggested_fix="Add a blank line or separator comment between include groups.",
                    )

    def _extract_includes(self, content: str) -> List[tuple]:
        """Extract all #include statements with their line numbers."""
        includes = []
        lines = content.split("\n")

        include_pattern = re.compile(r"^\s*#include\s+[<\"](.*?)[>\"]")

        for line_num, line in enumerate(lines, 1):
            match = include_pattern.match(line)
            if match:
                include_path = match.group(1)
                is_system = "<" in line
                includes.append(
                    (line_num, include_path, is_system, line.strip())
                )

        return includes

    def _categorize_includes(self, includes: List[tuple]) -> dict:
        """Categorize includes by type."""
        categories = {
            "precompiled": [],
            "main_header": [],
            "c_standard": [],
            "cpp_standard": [],
            "third_party": [],
            "project": [],
        }
        for line_num, include_path, is_system, full_line in includes:
            category = self._get_include_category(include_path, is_system)
            categories[category].append((line_num, include_path, full_line))
        return categories

    def _is_precompiled_header(self, include_path: str) -> bool:
        """Check if an include path is a precompiled header."""
        # Common precompiled header patterns
        pch_patterns = [
            "PrecompiledHeaders.h",
            "precompiled.h",
            "stdafx.h",
            "pch.h",
        ]

        # Check if the file name (not path) matches any precompiled header pattern
        file_name = include_path.split("/")[-1]
        return any(file_name == pattern for pattern in pch_patterns)

    def _get_include_category(self, include_path: str, is_system: bool) -> str:
        """Determine the category of an include."""
        # Check for precompiled headers first
        if self._is_precompiled_header(include_path):
            return "precompiled"

        if not is_system or any(
            include_path.startswith(p)
            for p in ["vajra/", "native/", "commons/", "kernels/"]
        ):
            return "project"
        if (
            include_path.startswith("c")
            and len(include_path) > 1
            and include_path[1].islower()
            and "/" not in include_path
        ):
            return "c_standard"
        cpp_standard = {
            "algorithm",
            "array",
            "atomic",
            "bitset",
            "chrono",
            "complex",
            "condition_variable",
            "deque",
            "exception",
            "forward_list",
            "fstream",
            "functional",
            "future",
            "initializer_list",
            "iomanip",
            "ios",
            "iosfwd",
            "iostream",
            "istream",
            "iterator",
            "limits",
            "list",
            "locale",
            "map",
            "memory",
            "mutex",
            "new",
            "numeric",
            "ostream",
            "queue",
            "random",
            "ratio",
            "regex",
            "scoped_allocator",
            "set",
            "sstream",
            "stack",
            "stdexcept",
            "streambuf",
            "string",
            "system_error",
            "thread",
            "tuple",
            "type_traits",
            "typeindex",
            "typeinfo",
            "unordered_map",
            "unordered_set",
            "utility",
            "valarray",
            "vector",
        }
        if include_path in cpp_standard:
            return "cpp_standard"
        third_party_prefixes = {
            "boost/",
            "gtest/",
            "torch/",
            "ATen/",
            "nlohmann/",
            "google/",
            "cuda",
            "cublas",
            "flash",
            "zmq",
            "mpi",
            "omp",
        }
        if any(include_path.startswith(p) for p in third_party_prefixes):
            return "third_party"
        return "third_party"

    def _get_expected_order(self, file_path: str) -> List[str]:
        """Get expected include order for this file type."""
        if file_path.endswith((".cpp", ".cc")):
            return [
                "precompiled",
                "main_header",
                "c_standard",
                "cpp_standard",
                "third_party",
                "project",
            ]
        return [
            "precompiled",
            "c_standard",
            "cpp_standard",
            "third_party",
            "project",
        ]

    def _check_group_order(
        self, categorized: dict, expected_order: List[str]
    ) -> List[tuple]:
        """Check if include groups are in the expected order."""
        violations = []
        first_occurrence = {
            cat: categorized[cat][0][0]
            for cat in expected_order
            if categorized[cat]
        }

        for i, category in enumerate(expected_order):
            if category not in first_occurrence:
                continue
            current_line = first_occurrence[category]
            for j in range(i + 1, len(expected_order)):
                later_category = expected_order[j]
                if (
                    later_category in first_occurrence
                    and first_occurrence[later_category] < current_line
                ):
                    violations.append(
                        (
                            current_line,
                            f"{category.replace('_', ' ').title()} includes should come before {later_category.replace('_', ' ')} includes",
                            f"Move {category.replace('_', ' ').title()} includes above {later_category.replace('_', ' ')} includes",
                        )
                    )
        return violations

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Automatically fix include order issues."""
        if not issues:
            return AutofixResult(success=False, message="No issues to fix")

        includes = self._extract_includes(content)
        if len(includes) < 2:
            return AutofixResult(
                success=False, message="Not enough includes to reorder"
            )

        categorized = self._categorize_includes(includes)
        expected_order = self._get_expected_order(file_path)
        separator = "//=============================================================================="

        reordered_lines = []
        has_content = False
        for category in expected_order:
            if categorized[category]:
                if has_content:
                    reordered_lines.append(separator)

                sorted_category = sorted(
                    categorized[category], key=lambda x: x[1]
                )
                reordered_lines.extend([inc[2] for inc in sorted_category])
                has_content = True

        lines = content.split("\n")

        # Find the start and end lines of the entire include block to replace
        all_include_line_nums = [inc[0] for inc in includes]
        min(all_include_line_nums) - 1
        max(all_include_line_nums) - 1

        # A more robust way to find the block is to find the first and last include lines
        # and remove everything in between that is also an include line.

        # Collect all include line indices (0-based)
        include_indices = {inc[0] - 1 for inc in includes}

        # Create a new list of lines, excluding the old include block
        new_lines = []
        first_include_pos = min(include_indices)

        for i, line in enumerate(lines):
            if i == first_include_pos:
                # Insert the new, sorted and separated block here
                new_lines.extend(reordered_lines)

            if i in include_indices:
                # This line is part of the old include block, so skip it
                continue

            new_lines.append(line)

        new_content = "\n".join(new_lines)
        return AutofixResult(
            success=True,
            new_content=new_content,
            message=f"Reordered {len(includes)} includes and added separators.",
            issues_fixed=len(issues),
        )


class IncludeAngleBracketForbiddenRule(RegexRule):
    """Rule to forbid angle bracket includes for local files.

    Local project files should use quotes (#include "header.h") while
    system/external libraries should use angle brackets (#include <header>).
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        lines = self.get_lines(content)

        angle_include_pattern = re.compile(r"^\s*#include\s+<([^>]+)>")

        for line_num, line in enumerate(lines, 1):
            match = angle_include_pattern.match(line)
            if not match:
                continue

            included_file = match.group(1)

            if self._is_local_project_file(included_file):
                # Check if this line should be skipped due to NOLINT directives
                if self.should_skip_line(line, str(self.rule_id)):
                    continue
                
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                    continue
                
                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() + 1,
                    message=f"Local project file '{included_file}' should use quotes, not angle brackets",
                    suggested_fix=f'#include "{included_file}"',
                )

        return self.issues

    def _is_local_project_file(self, include_path: str) -> bool:
        """Check if an include path refers to a local project file."""
        local_indicators = ["vajra/", "../", "./", "test/"]
        system_prefixes = [
            "std",
            "boost/",
            "gtest/",
            "cuda",
            "cublas",
            "google/",
            "torch/",
            "ATen/",
            "nlohmann/",
            "tokenizers_cpp",
            "arpa/",
            "netinet/",
            "sys/",
        ]

        if any(include_path.startswith(p) for p in system_prefixes):
            return False

        if any(include_path.startswith(i) for i in local_indicators):
            return True

        if "/" not in include_path:
            standard_headers = {
                "algorithm",
                "array",
                "atomic",
                "bitset",
                "cassert",
                "cctype",
                "cerrno",
                "cfenv",
                "cfloat",
                "chrono",
                "cinttypes",
                "climits",
                "clocale",
                "cmath",
                "codecvt",
                "complex",
                "condition_variable",
                "csetjmp",
                "csignal",
                "cstdarg",
                "cstddef",
                "cstdint",
                "cstdio",
                "cstdlib",
                "cstring",
                "ctime",
                "cuchar",
                "cwchar",
                "cwctype",
                "deque",
                "exception",
                "forward_list",
                "fstream",
                "functional",
                "future",
                "initializer_list",
                "iomanip",
                "ios",
                "iosfwd",
                "iostream",
                "istream",
                "iterator",
                "limits",
                "list",
                "locale",
                "map",
                "memory",
                "mutex",
                "new",
                "numeric",
                "ostream",
                "queue",
                "random",
                "ratio",
                "regex",
                "scoped_allocator",
                "set",
                "sstream",
                "stack",
                "stdexcept",
                "streambuf",
                "string",
                "strstream",
                "system_error",
                "thread",
                "tuple",
                "type_traits",
                "typeindex",
                "typeinfo",
                "unordered_map",
                "unordered_set",
                "utility",
                "valarray",
                "vector",
            }
            if include_path in standard_headers:
                return False
            # If it's not a standard header and contains no path separator,
            # it's likely a local project header file
            return True

        return "/" in include_path


class HeaderPragmaOnceRule(RegexRule):
    """Rule to detect missing #pragma once in header files."""

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        if not self._is_header_file(file_path):
            return self.issues

        pragma_info = self._check_pragma_once_position(content)

        if pragma_info["has_pragma_once"]:
            if not pragma_info["is_first"]:
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[pragma_info["pragma_line"] - 1] if pragma_info["pragma_line"] <= len(lines) else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, pragma_info["pragma_line"])
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path=file_path,
                            line_number=pragma_info["pragma_line"],
                            column=1,
                            message="#pragma once must be the first non-comment line",
                            suggested_fix="Move #pragma once to the top of the file",
                        )
        else:
            guard_info = self._has_include_guards(content)
            if guard_info["has_guards"]:
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[guard_info["ifndef_line"] - 1] if guard_info["ifndef_line"] <= len(lines) else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, guard_info["ifndef_line"])
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path=file_path,
                            line_number=guard_info["ifndef_line"],
                            column=1,
                            message="Replace include guards with #pragma once for better performance and reliability",
                            suggested_fix="#pragma once",
                        )
            else:
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
                            message="Header file missing #pragma once directive",
                            suggested_fix="Add '#pragma once' at the top of the file",
                        )

        return self.issues

    def _is_header_file(self, file_path: str) -> bool:
        return any(
            file_path.endswith(ext)
            for ext in [".h", ".hpp", ".hxx", ".hh", ".h++"]
        )

    def _has_pragma_once(self, content: str) -> bool:
        return "#pragma once" in content

    def _check_pragma_once_position(self, content: str) -> dict:
        """Check if #pragma once exists and if it's in the correct position."""
        lines = content.split("\n")
        pragma_line = None
        first_non_comment_line = None

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Check for #pragma once
            if stripped == "#pragma once":
                pragma_line = line_num

            # Skip comments
            if stripped.startswith(("//", "/*")) or stripped.startswith("*"):
                continue

            # This is the first non-comment, non-empty line
            if first_non_comment_line is None:
                first_non_comment_line = line_num
                break

        has_pragma_once = pragma_line is not None
        is_first = False

        if has_pragma_once:
            # #pragma once is considered "first" if it appears before any non-comment code
            if first_non_comment_line is None:
                # Only comments and #pragma once in the file
                is_first = True
            elif pragma_line <= first_non_comment_line:
                is_first = True

        return {
            "has_pragma_once": has_pragma_once,
            "is_first": is_first,
            "pragma_line": pragma_line,
            "first_non_comment_line": first_non_comment_line,
        }

    def _has_include_guards(self, content: str) -> dict:
        lines = content.split("\n")
        ifndef_pattern = re.compile(r"^\s*#ifndef\s+([A-Z_][A-Z0-9_]*)\s*$")
        define_pattern = re.compile(r"^\s*#define\s+([A-Z_][A-Z0-9_]*)\s*$")

        ifndef_line, ifndef_macro = None, None
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith(("//", "/*")):
                continue

            match = ifndef_pattern.match(line)
            if match and ifndef_line is None:
                ifndef_line, ifndef_macro = line_num, match.group(1)

                # Check for matching #define on the next non-empty/comment line
                for next_line in lines[line_num:]:
                    if (
                        next_line.strip().startswith(("//", "/*"))
                        or not next_line.strip()
                    ):
                        continue
                    define_match = define_pattern.match(next_line)
                    if define_match and define_match.group(1) == ifndef_macro:
                        # Check for #endif at the end of the file
                        for end_line in reversed(lines):
                            if end_line.strip() == "#endif":
                                return {
                                    "has_guards": True,
                                    "ifndef_line": ifndef_line,
                                }
                    break  # Mismatch or other content found
                break  # Found the first #ifndef

        return {"has_guards": False, "ifndef_line": 1}


class HeaderCopyrightRule(RegexRule):
    """Enhanced copyright header checking for source files."""

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        if self._should_skip_file(file_path):
            return self.issues

        header_text = "\n".join(content.split("\n")[:20])
        copyright_info = self._analyze_copyright_header(header_text)

        if not copyright_info["has_copyright"]:
            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[0] if len(lines) > 0 else ""
            if not self.should_skip_line(line_content, str(self.rule_id)):
                # Check if next line skip applies
                should_skip_next, skip_rules = self.should_skip_next_line(content, 1)
                if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                    self.add_issue(
                        file_path,
                        1,
                        1,
                        "Missing copyright header",
                        "Add copyright header with: // Copyright (C) YYYY Organization",
                    )
        else:
            if not copyright_info["has_year"]:
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[copyright_info["copyright_line"] - 1] if copyright_info["copyright_line"] <= len(lines) else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, copyright_info["copyright_line"])
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path,
                            copyright_info["copyright_line"],
                            1,
                            "Copyright header missing year",
                            "Add copyright year: // Copyright (C) 2024 Organization",
                        )
            if not copyright_info["has_owner"]:
                # Check if this line should be skipped due to NOLINT directives
                lines = content.split("\n")
                line_content = lines[copyright_info["copyright_line"] - 1] if copyright_info["copyright_line"] <= len(lines) else ""
                if not self.should_skip_line(line_content, str(self.rule_id)):
                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, copyright_info["copyright_line"])
                    if not (should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules)):
                        self.add_issue(
                            file_path,
                            copyright_info["copyright_line"],
                            1,
                            "Copyright header missing owner/organization",
                            "Add copyright owner: // Copyright (C) 2024 Your Organization",
                        )

        return self.issues

    def _should_skip_file(self, file_path: str) -> bool:
        return any(
            p in file_path
            for p in ["/test/", "/third_party/", ".pb.h", "_test."]
        )

    def _analyze_copyright_header(self, header_text: str) -> dict:
        has_copyright = any(
            k in header_text.lower() for k in ["copyright", "(c)", "©"]
        )
        has_year = bool(re.search(r"\d{4}", header_text))
        # A simple heuristic for owner
        has_owner = (
            has_copyright
            and has_year
            and len(re.findall(r"copyright.*\d{4}.*\w+", header_text, re.I)) > 0
        )

        copyright_line = 1
        if has_copyright:
            for i, line in enumerate(header_text.split("\n")):
                if any(k in line.lower() for k in ["copyright", "(c)", "©"]):
                    copyright_line = i + 1
                    break

        return {
            "has_copyright": has_copyright,
            "has_year": has_year,
            "has_owner": has_owner,
            "copyright_line": copyright_line,
        }

