"""Type system rules for enforcing proper C++ types."""

import re
from typing import Any, List

from ..core.issue import LintIssue
from .base import ASTRule, RegexRule
from .rule_id import RuleId


class TypeForbiddenIntRule(RegexRule):
    """Rule to enforce use of fixed-width integer types instead of 'int'.

    This rule enforces the use of std::int32_t instead of 'int' to ensure
    consistent behavior across different platforms and architectures.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        lines = self.get_lines(content)

        # Patterns to match primitive integer types
        # More robust patterns to match unsigned types to avoid false positives
        # Order matters: longer patterns first to avoid shorter patterns matching first
        primitive_int_patterns = [
            (
                re.compile(r"\bunsigned\s+long\s+long\b"),
                "unsigned long long",
                "std::uint64_t",
            ),
            (
                re.compile(r"\blong\s+long\b"),
                "long long",
                "std::int64_t",
            ),
            (
                re.compile(r"\bunsigned\s+long\b"),
                "unsigned long",
                "std::uint64_t",
            ),
            (
                re.compile(r"\bunsigned\s+int\b"),
                "unsigned int",
                "std::uint32_t",
            ),
            (
                re.compile(r"\bunsigned\s+short\b"),
                "unsigned short",
                "std::uint16_t",
            ),
            (re.compile(r"\blong\b"), "long", "std::int64_t"),
            (re.compile(r"\bshort\b"), "short", "std::int16_t"),
            (re.compile(r"\bint\b"), "int", "std::int32_t"),
        ]

        for line_num, line in enumerate(lines, 1):
            # Skip comment lines and most preprocessor directives (but not #define)
            stripped = line.strip()
            if stripped.startswith("//") or (
                stripped.startswith("#") and not stripped.startswith("#define")
            ):
                continue

            # Skip lines with common exceptions
            if any(
                exception in line
                for exception in [
                    "main(",
                    "printf",
                    "sprintf",
                    "fprintf",  # C functions
                    "sizeof(int)",
                    "alignof(int)",  # Size queries
                    "::int",  # Namespaced ints
                    "template<int",  # Template parameters
                ]
            ):
                continue

            # Find all primitive integer type occurrences
            # Track matched regions to avoid overlapping matches
            matched_regions = []

            for (
                pattern,
                type_name,
                suggested_replacement,
            ) in primitive_int_patterns:
                for match in pattern.finditer(line):
                    pos = match.start()
                    end_pos = match.end()

                    # Skip if this region was already matched by a longer pattern
                    if any(
                        start <= pos < end or start < end_pos <= end
                        for start, end in matched_regions
                    ):
                        continue

                    # Skip if inside string literal or comment
                    if self.is_in_string_literal(
                        line, pos
                    ) or self.is_in_comment(line, pos):
                        continue

                    # Check if this is a type declaration context
                    if self._is_type_context(line, pos, len(match.group())):
                        # Check if this line should be skipped due to NOLINT directives
                        if self.should_skip_line(line, str(self.rule_id)):
                            continue
                        
                        # Check if next line skip applies
                        should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                        if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                            continue
                        
                        matched_regions.append((pos, end_pos))
                        self.add_issue(
                            file_path=file_path,
                            line_number=line_num,
                            column=pos + 1,
                            message=f"Use fixed-width integer types ({suggested_replacement}) instead of '{type_name}'",
                            suggested_fix=suggested_replacement,
                        )

        return self.issues

    def _is_type_context(
        self, line: str, position: int, type_length: int
    ) -> bool:
        """Check if type at position is used as a type declaration."""
        # Look at the character before the type
        char_before = line[position - 1] if position > 0 else " "

        # Look at characters after the type
        end_pos = position + type_length
        char_after = line[end_pos] if end_pos < len(line) else " "

        # Must be preceded by whitespace, comma, or type modifiers
        valid_before = char_before in " \t,<>()[]{}*&" or line[
            :position
        ].endswith(("const ", "static ", "unsigned "))

        # Must be followed by whitespace, identifier, or punctuation
        valid_after = (
            char_after in " \t,;()[]{}*&:"
            or char_after.isalpha()
            or char_after == "_"
        )

        return valid_before and valid_after


class TypePairTupleRule(ASTRule):
    """Rule to detect std::pair/tuple usage and suggest alternatives.

    std::pair and std::tuple can make code harder to read and maintain.
    This rule suggests using structs or classes with named members instead.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find all template types and instantiations
        template_nodes = self.find_nodes_by_types(
            tree, ["template_type", "template_instantiation"]
        )

        for node in template_nodes:
            type_text = self.get_text_from_node(node, content)
            line_num = self.get_line_from_byte(node.start_byte, content)

            # Skip if this line should be skipped due to directive
            lines = content.split("\n")
            if line_num <= len(lines):
                line_content = lines[line_num - 1]
                if self.should_skip_line(line_content, str(self.rule_id)):
                    continue

            # Check for std::pair usage
            if type_text.startswith("pair<"):
                # Check if this is std::pair by looking at parent or surrounding context
                parent_text = (
                    self.get_text_from_node(node.parent, content)
                    if node.parent
                    else ""
                )
                if "std::" in parent_text or "std::" in type_text:
                    self._check_pair_usage(
                        node, type_text, file_path, line_num, content
                    )

            # Check for std::tuple usage
            elif type_text.startswith("tuple<"):
                # Check if this is std::tuple by looking at parent or surrounding context
                parent_text = (
                    self.get_text_from_node(node.parent, content)
                    if node.parent
                    else ""
                )
                if "std::" in parent_text or "std::" in type_text:
                    self._check_tuple_usage(
                        node, type_text, file_path, line_num, content
                    )

        # Also check for pair/tuple in type aliases
        type_alias_nodes = self.find_nodes_by_type(
            tree, "type_alias_declaration"
        )
        for node in type_alias_nodes:
            type_text = self.get_text_from_node(node, content)
            line_num = self.get_line_from_byte(node.start_byte, content)

            # Skip if this line should be skipped
            lines = content.split("\n")
            if line_num <= len(lines):
                line_content = lines[line_num - 1]
                if self.should_skip_line(line_content, str(self.rule_id)):
                    continue

            if "pair<" in type_text and "std::" in type_text:
                self._check_pair_usage(
                    node, type_text, file_path, line_num, content
                )
            elif "tuple<" in type_text and "std::" in type_text:
                self._check_tuple_usage(
                    node, type_text, file_path, line_num, content
                )

        return self.issues

    def _check_pair_usage(
        self,
        node: Any,
        type_text: str,
        file_path: str,
        line_num: int,
        content: str,
    ) -> None:
        """Check std::pair usage and suggest alternatives."""
        # Extract the types inside the pair
        pair_types = self._extract_template_args(type_text, "pair")

        if len(pair_types) == 2:
            first_type, second_type = pair_types

            # Generate suggestions based on context
            suggestion = self._generate_pair_suggestion(
                first_type, second_type, node, content
            )

            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=1,
                message=f"Consider using a struct with named members instead of std::pair<{first_type}, {second_type}>",
                suggested_fix=suggestion,
            )

    def _check_tuple_usage(
        self,
        node: Any,
        type_text: str,
        file_path: str,
        line_num: int,
        content: str,
    ) -> None:
        """Check std::tuple usage and suggest alternatives."""
        # Extract the types inside the tuple
        tuple_types = self._extract_template_args(type_text, "tuple")

        if len(tuple_types) >= 2:
            types_str = ", ".join(tuple_types)
            suggestion = self._generate_tuple_suggestion(
                tuple_types, node, content
            )

            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=1,
                message=f"Consider using a struct with named members instead of std::tuple<{types_str}>",
                suggested_fix=suggestion,
            )

    def _extract_template_args(
        self, type_text: str, template_name: str
    ) -> List[str]:
        """Extract template arguments from a template instantiation."""
        # Find the start of template arguments
        start_idx = type_text.find(template_name + "<")
        if start_idx == -1:
            return []

        start_idx += len(template_name) + 1  # Move past 'template_name<'

        # Find matching closing bracket
        bracket_count = 1
        current_idx = start_idx
        args_start = start_idx

        while current_idx < len(type_text) and bracket_count > 0:
            if type_text[current_idx] == "<":
                bracket_count += 1
            elif type_text[current_idx] == ">":
                bracket_count -= 1
            current_idx += 1

        if bracket_count == 0:
            args_text = type_text[args_start : current_idx - 1]
            # Simple comma split (doesn't handle nested templates perfectly, but good enough)
            args = [arg.strip() for arg in args_text.split(",")]
            return args

        return []

    def _generate_pair_suggestion(
        self, first_type: str, second_type: str, node: Any, content: str
    ) -> str:
        """Generate a suggestion for replacing std::pair."""
        # Try to infer meaningful names from context
        context = self._get_context_around_node(node, content)

        # Default names
        first_name = "first"
        second_name = "second"

        # Try to infer better names from variable names or function context
        if "key" in context.lower() or "id" in context.lower():
            first_name = "key"
            second_name = "value"
        elif "index" in context.lower():
            first_name = "index"
            second_name = "value"
        elif "name" in context.lower():
            first_name = "name"
            second_name = "value"

        return f"struct {{ {first_type} {first_name}; {second_type} {second_name}; }}"

    def _generate_tuple_suggestion(
        self, tuple_types: List[str], node: Any, content: str
    ) -> str:
        """Generate a suggestion for replacing std::tuple."""
        # Generate generic field names
        fields = []
        for i, type_name in enumerate(tuple_types):
            field_name = f"field_{i}"
            fields.append(f"{type_name} {field_name}")

        return f"struct {{ {'; '.join(fields)}; }}"

    def _get_context_around_node(self, node: Any, content: str) -> str:
        """Get some context around a node to help with naming suggestions."""
        # Get the line containing the node and some surrounding lines
        line_num = self.get_line_from_byte(node.start_byte, content)
        lines = content.split("\n")

        start_line = max(0, line_num - 3)
        end_line = min(len(lines), line_num + 2)

        context_lines = lines[start_line:end_line]
        return "\n".join(context_lines)


# Rule registration has been moved to registry.py
