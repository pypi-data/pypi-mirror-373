"""Code quality rules for C++ code."""

import re
from typing import Any, List, Set

from ..core.issue import LintIssue
from .base import ASTRule


class QualityMagicNumbersRule(ASTRule):
    """Rule to detect magic numbers in code.

    Magic numbers are numeric literals that appear in code without explanation.
    They should be replaced with named constants that explain their purpose.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all numeric literals in the code
        numeric_nodes = self.find_nodes_by_type(tree, "number_literal")

        for node in numeric_nodes:
            if self.is_inside_comment(node, content):
                continue

            value = self.get_text_from_node(node, content)
            
            # Only process actual numeric values (not character literals, strings, etc.)
            if not self._is_numeric_value(value):
                continue

            # Skip acceptable numbers
            if self._is_acceptable_number(value, node, content):
                continue

            line_num = self.get_line_from_byte(node.start_byte, content)
            column = node.start_byte - content.rfind("\n", 0, node.start_byte)

            # Check if this line should be skipped due to NOLINT directives
            lines = content.split("\n")
            line_content = lines[line_num - 1] if line_num <= len(lines) else ""
            if self.should_skip_line(line_content, str(self.rule_id)):
                continue
            
            # Check if next line skip applies
            should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
            if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                continue
            
            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=column,
                message=f"Magic number '{value}' should be replaced with a named constant",
                suggested_fix=f"const auto kSomeDescriptiveName = {value};",
            )

        return self.issues

    def _is_numeric_value(self, value: str) -> bool:
        """Check if the value is actually a numeric literal."""
        if not value:
            return False
        
        # Skip single character values (likely character literals)
        if len(value) == 1:
            return False
            
        # Skip values that contain non-numeric characters (except for valid float suffixes)
        # Valid numeric patterns: 123, 123.456, 123f, 123.456f, 0x123, etc.
        import re
        
        # Pattern for valid numeric literals
        numeric_pattern = r'^[+-]?(?:0x[0-9a-fA-F]+|0b[01]+|0[0-7]*|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)[flLuU]*$'
        
        return bool(re.match(numeric_pattern, value))

    def _is_power_of_two(self, value: str) -> bool:
        """Check if a number is a power of 2."""
        try:
            # Remove any suffix (f, l, u, etc.)
            cleaned_value = value.rstrip('flLuU')
            
            # Handle hexadecimal numbers
            if cleaned_value.startswith('0x') or cleaned_value.startswith('0X'):
                num = int(cleaned_value, 16)
            elif cleaned_value.startswith('0b') or cleaned_value.startswith('0B'):
                num = int(cleaned_value, 2)
            elif '.' in cleaned_value:
                # Float values can't be powers of 2 in the traditional sense
                return False
            else:
                num = int(cleaned_value)
            
            # Check if it's a positive power of 2
            return num > 0 and (num & (num - 1)) == 0
        except (ValueError, OverflowError):
            return False

    def _is_acceptable_number(
        self, value: str, node: Any, content: str
    ) -> bool:
        """Check if a number is acceptable (not a magic number)."""
        # Common acceptable numbers (only very basic ones)
        if value in ["0", "1", "-1", "2"]:
            return True

        # Powers of 2 are common and acceptable (e.g., 1024, 2048, 4096)
        if self._is_power_of_two(value):
            return True

        # Boolean literals (true/false should be handled separately)
        if value in ["true", "false"]:
            return True

        # Numbers in array/vector sizing contexts (be more restrictive)
        if self._is_in_sizing_context(node, content):
            return True

        # Float literals for common values
        if value in ["0.0", "0.0f", "1.0", "1.0f", "2.0", "2.0f"]:
            return True

        # Numbers in const/constexpr declarations are acceptable
        if self._is_in_const_declaration(node, content):
            return True

        return False

    def _is_in_sizing_context(self, node: Any, content: str) -> bool:
        """Check if number is used in array sizing or similar context."""
        parent_context = self._get_parent_context(node, content, 50)
        sizing_patterns = [
            r"std::array<[^>]*,\s*(?:\d+|0x[0-9A-Fa-f]+|0b[01]+)",
            r"\[\s*(?:\d+|0x[0-9A-Fa-f]+|0b[01]+)\s*\]",
            r"\.resize\s*\(\s*(?:\d+|0x[0-9A-Fa-f]+|0b[01]+)",
            r"\.reserve\s*\(\s*(?:\d+|0x[0-9A-Fa-f]+|0b[01]+)",
        ]

        for pattern in sizing_patterns:
            if re.search(pattern, parent_context):
                return True

        return False

    def _get_parent_context(
        self, node: Any, content: str, context_size: int = 30
    ) -> str:
        """Get surrounding context of a node."""
        start = max(0, node.start_byte - context_size)
        end = min(len(content), node.end_byte + context_size)
        return content[start:end]

    def _is_in_const_declaration(self, node: Any, content: str) -> bool:
        """Check if number is part of a named constant declaration."""
        # Look for const/constexpr keywords in the line
        line_start = content.rfind("\n", 0, node.start_byte) + 1
        line_end = content.find("\n", node.start_byte)
        if line_end == -1:
            line_end = len(content)

        line_content = content[line_start:line_end]

        # Only accept const/constexpr if it's a named constant (has 'k' prefix)
        if any(keyword in line_content for keyword in ["const ", "constexpr "]):
            # Check if variable name starts with 'k' (naming convention for constants)
            import re

            # Look for pattern like "const type kVariableName" or "constexpr type kVariableName"
            pattern = r"\b(?:const|constexpr)\s+[\w:\<\>\s\*&]+?\s+k[A-Z]\w*"
            return bool(re.search(pattern, line_content))

        return False



