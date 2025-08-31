"""Namespace organization rules for C++ code."""

import re
from collections import defaultdict
from typing import Any, Dict, List

from ..core.issue import LintIssue
from .base import ASTRule, RegexRule


class NamespaceOldStyleRule(ASTRule):
    """Rule to detect old-style nested namespace declarations.

    Detects old-style nested namespace declarations like:
    namespace vajra {
    namespace native {
    namespace core {
    // content
    }}}

    And suggests C++17 style:
    namespace vajra::native::core {
    // content
    }
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all namespace declarations
        namespace_nodes = self._find_nested_namespaces(tree)

        for nested_group in namespace_nodes:
            self._check_nested_namespace_group(nested_group, file_path, content)

        return self.issues

    def _find_nested_namespaces(self, tree: Any) -> List[List[Any]]:
        """Find groups of nested namespace declarations."""
        namespace_nodes = self.find_nodes_by_type(tree, "namespace_definition")
        nested_groups = []

        for node in namespace_nodes:
            # Check if this namespace contains another namespace as its first child
            nested_chain = self._get_nested_chain(node)
            if len(nested_chain) >= 2:  # At least 2 levels of nesting
                nested_groups.append(nested_chain)

        return nested_groups

    def _get_nested_chain(self, namespace_node: Any) -> List[Any]:
        """Get the chain of nested namespaces starting from this node."""
        chain = [namespace_node]
        current = namespace_node

        while True:
            # Look for a namespace_definition as the first significant child
            body = None
            for child in current.children:
                if child.type == "declaration_list":
                    body = child
                    break

            if not body:
                break

            # Find the first namespace_definition child
            next_namespace = None
            for child in body.children:
                if child.type == "namespace_definition":
                    next_namespace = child
                    break
                elif child.type not in ["{", "}"] and child.type != "comment":
                    # If we find non-namespace content, stop the chain
                    break

            if next_namespace:
                chain.append(next_namespace)
                current = next_namespace
            else:
                break

        return chain

    def _check_nested_namespace_group(
        self, nested_chain: List[Any], file_path: str, content: str
    ):
        """Check a group of nested namespaces and suggest C++17 style."""
        if len(nested_chain) < 2:
            return

        # Extract namespace names
        namespace_names = []
        for node in nested_chain:
            name = self._get_namespace_name(node, content)
            if name:
                namespace_names.append(name)

        if len(namespace_names) < 2:
            return

        # Check if this is already C++17 style (contains ::)
        first_name = namespace_names[0]
        if "::" in first_name:
            return  # Already C++17 style

        # Build the suggested C++17 declaration
        cpp17_style = "::".join(namespace_names)

        # Get the line number of the first namespace
        first_node = nested_chain[0]
        line_num = self.get_line_from_byte(first_node.start_byte, content)

        # Create the suggestion
        suggestion = f"namespace {cpp17_style} {{"

        self.add_issue(
            file_path=file_path,
            line_number=line_num,
            column=1,
            message=f"Use C++17 nested namespace declaration: namespace {cpp17_style}",
            suggested_fix=suggestion,
        )

    def _get_namespace_name(self, namespace_node: Any, content: str) -> str:
        """Extract the name of a namespace from its node."""
        for child in namespace_node.children:
            if child.type == "identifier":
                return self.get_text_from_node(child, content)
        return ""


class NamespaceUsingForbiddenRule(RegexRule):
    """Rule to forbid 'using namespace' directives in header files.

    Using namespace directives in header files can cause namespace pollution
    and naming conflicts when the header is included in other files.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Only check header files
        if not self._is_header_file(file_path):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        lines = self.get_lines(content)

        # Pattern to match 'using namespace' directives
        using_namespace_pattern = re.compile(
            r"^\s*using\s+namespace\s+([^;]+);"
        )

        for line_num, line in enumerate(lines, 1):
            # Skip lines with disable directive
            if self.should_skip_line(line, str(self.rule_id)):
                continue

            # Skip comments
            if line.strip().startswith("//") or line.strip().startswith("/*"):
                continue

            match = using_namespace_pattern.match(line)
            if match:
                namespace_name = match.group(1).strip()

                # Check if this is inside a comment
                if self.is_in_comment(line, match.start()):
                    continue

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() + 1,
                    message=f"'using namespace {namespace_name};' is forbidden in header files",
                    suggested_fix=f"Use fully qualified names instead: {namespace_name}::",
                )

        return self.issues

    def _is_header_file(self, file_path: str) -> bool:
        """Check if this is a header file."""
        header_extensions = {".h", ".hpp", ".hxx", ".hh", ".h++"}
        return any(file_path.endswith(ext) for ext in header_extensions)


class NamespaceLongUsageRule(RegexRule):
    """Rule to detect repeated long namespace usage patterns.

    Detects when the same long namespace (3+ levels) is used repeatedly
    and suggests using a 'using' directive to simplify the code.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Skip headers to avoid conflicting with NamespaceUsingForbiddenRule    
        if self._is_header_file(file_path):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all namespace usage patterns
        namespace_usage = self._find_namespace_usage(content)

        # Analyze usage patterns
        for namespace, usage_info in namespace_usage.items():
            if self._should_suggest_using_directive(namespace, usage_info):
                self._suggest_using_directive(namespace, usage_info, file_path)

        return self.issues

    def _find_namespace_usage(self, content: str) -> Dict[str, Dict]:
        """Find all namespace usage patterns in the content."""
        lines = self.get_lines(content)
        namespace_usage = defaultdict(
            lambda: {"count": 0, "lines": [], "contexts": []}
        )

        # Pattern to match namespace::qualified::names
        namespace_pattern = re.compile(
            r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*){2,})::[a-zA-Z_][a-zA-Z0-9_]*"
        )

        for line_num, line in enumerate(lines, 1):
            # Skip lines with disable directive
            if self.should_skip_line(line, str(self.rule_id)):
                continue

            # Skip comments and string literals
            if line.strip().startswith("//") or line.strip().startswith("/*"):
                continue

            matches = namespace_pattern.findall(line)
            for namespace in matches:
                # Skip if this is inside a comment or string
                match_pos = line.find(namespace)
                if self.is_in_comment(
                    line, match_pos
                ) or self.is_in_string_literal(line, match_pos):
                    continue

                namespace_usage[namespace]["count"] += 1
                namespace_usage[namespace]["lines"].append(line_num)
                namespace_usage[namespace]["contexts"].append(line.strip())

        return dict(namespace_usage)

    def _should_suggest_using_directive(
        self, namespace: str, usage_info: Dict
    ) -> bool:
        """Determine if we should suggest a using directive for this namespace."""
        # Must have at least 3 levels (e.g., vajra::native::core)
        if namespace.count("::") < 2:
            return False

        # Must be used at least 3 times
        if usage_info["count"] < 3:
            return False

        # Must span multiple lines (not all on the same line)
        unique_lines = set(usage_info["lines"])
        if len(unique_lines) < 2:
            return False

        return True

    def _suggest_using_directive(
        self, namespace: str, usage_info: Dict, file_path: str
    ):
        """Suggest using a using directive for this namespace."""
        first_line = min(usage_info["lines"])

        # Create a meaningful suggestion
        suggestion = f"using {namespace};"

        # Count how many times it's used
        usage_count = usage_info["count"]
        line_count = len(set(usage_info["lines"]))

        message = (
            f"Namespace '{namespace}' is used {usage_count} times across {line_count} lines. "
            f"Consider adding 'using {namespace};' to simplify the code."
        )

        self.add_issue(
            file_path=file_path,
            line_number=first_line,
            column=1,
            message=message,
            suggested_fix=suggestion,
        )

    def _is_header_file(self, file_path: str) -> bool:
        """Check if this is a header file."""
        header_extensions = {".h", ".hpp", ".hxx", ".hh", ".h++"}
        return any(file_path.endswith(ext) for ext in header_extensions)

