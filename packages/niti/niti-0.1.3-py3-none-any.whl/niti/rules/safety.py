"""Safety rules for C++ code to prevent memory/type safety issues."""

import re
from typing import Any, List

from ..core.issue import LintIssue
from .base import ASTRule, RegexRule
from .rule_id import RuleId


class SafetyUnsafeCastRule(RegexRule):
    """Rule to detect unsafe casting operations.

    Flags dangerous casting operations that can lead to undefined behavior:
    - reinterpret_cast<T>() - Unsafe type punning
    - C-style casts (Type)value - No type safety checks
    - const_cast<T>() in most contexts - Violates const correctness
    - dynamic_cast<T>() - Unsafe type conversions
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        lines = self.get_lines(content)

        # Patterns for unsafe casts
        patterns = [
            (
                re.compile(r"\breinterpret_cast\s*<[^>]+>\s*\("),
                "reinterpret_cast",
                "Use static_cast to avoid type punning",
            ),
            (
                re.compile(r"\bconst_cast\s*<[^>]+>\s*\("),
                "const_cast",
                "Redesign to avoid casting away const, or use mutable keyword",
            ),
            # C-style casts - more complex pattern to avoid false positives
            (
                re.compile(
                    r"\([A-Za-z_][A-Za-z0-9_]*(?:\s*\*+)?\s*\)\s*[&a-zA-Z_]"
                ),
                "C-style cast",
                "Use static_cast<T>() for explicit type conversion",
            ),
            (
                re.compile(r"\bdynamic_cast\s*<[^>]+>\s*\("),
                "dynamic_cast",
                "Use static_cast<T>() to avoid type punning",
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

            for pattern, cast_type, alternative in patterns:
                for match in pattern.finditer(line):
                    # Additional checks for C-style casts to reduce false positives
                    if cast_type == "C-style cast":
                        if self._is_likely_false_positive(line, match):
                            continue

                    # Check if inside string literal or comment
                    if self.is_in_string_literal(
                        line, match.start()
                    ) or self.is_in_comment(line, match.start()):
                        continue

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start() + 1,
                        message=f"Unsafe {cast_type} detected. This can lead to undefined behavior or runtime errors.",
                        suggested_fix=alternative,
                    )

        return self.issues

    def _is_likely_false_positive(self, line: str, match) -> bool:
        """Check if C-style cast pattern is likely a false positive."""
        cast_text = match.group(0)

        # Common false positives
        false_positives = [
            # Function calls that look like casts
            r"\(void\)",  # void casts for unused parameters
            r"\(int\)\s*main",  # main function return
            r"\(.*\)\s*\{",  # Function definitions
            r"\(.*\)\s*;",  # Function declarations
        ]

        for fp_pattern in false_positives:
            if re.search(fp_pattern, cast_text):
                return True

        return False


class SafetyRangeLoopMissingRule(ASTRule):
    """Rule to encourage range-based for loops over traditional loops.

    Detects traditional for loops that iterate over containers and suggests
    using range-based for loops for improved safety and readability.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find all for statements
        for_nodes = self.find_nodes_by_type(tree, "for_statement")

        for for_node in for_nodes:
            if self.is_inside_comment(for_node, content):
                continue

            for_text = self.get_text_from_node(for_node, content)
            line_num = self.get_line_from_byte(for_node.start_byte, content)

            # Check if this looks like a container iteration loop
            if self._is_container_iteration(for_text):
                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=1,
                    message="Consider using range-based for loop for container iteration",
                    suggested_fix="for (const auto& item : container) { ... } or for (auto& item : container) { ... }",
                )

        return self.issues

    def _is_container_iteration(self, for_text: str) -> bool:
        """Check if for loop looks like container iteration."""
        # Patterns that suggest container iteration
        container_patterns = [
            r"\.size\(\)",  # for (i = 0; i < container.size(); ++i)
            r"\.length\(\)",  # for (i = 0; i < str.length(); ++i)
            r"\.end\(\)",  # for (it = container.begin(); it != container.end(); ++it)
            r"\.begin\(\)",  # Iterator-based loops
        ]

        # Must also have typical loop structure
        loop_structure_patterns = [
            r"for\s*\([^;]*;\s*[^;]*\s*<\s*[^;]*\.size\(\)",  # i < size()
            r"for\s*\([^;]*;\s*[^;]*\s*!=\s*[^;]*\.end\(\)",  # it != end()
        ]

        for pattern in container_patterns:
            if re.search(pattern, for_text):
                for struct_pattern in loop_structure_patterns:
                    if re.search(struct_pattern, for_text):
                        return True

        return False


class SafetyRawPointerReturnRule(ASTRule):
    """Rule to detect and forbid raw pointer return types.

    Encourages the use of smart pointers or references for memory safety.
    Allows exceptions for special cases like char*, void*, and low-level APIs.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        function_nodes = self.find_nodes_by_types(
            tree, ["function_declaration", "function_definition"]
        )

        for func_node in function_nodes:
            if self.is_inside_comment(func_node, content):
                continue

            func_text = self.get_text_from_node(func_node, content)
            line_num = self.get_line_from_byte(func_node.start_byte, content)

            # Check if this line should be skipped
            if self.should_skip_line(
                self.get_line(content, line_num), str(self.rule_id)
            ):
                continue

            should_skip_next, skip_rules = self.should_skip_next_line(
                content, line_num
            )
            if should_skip_next and (
                skip_rules == "all" or str(self.rule_id) in skip_rules
            ):
                continue

            # Skip if this looks like a typedef/using statement
            if (
                "typedef" in func_text
                or "using" in func_text
                or "(*" in func_text
            ):
                continue

            if self._has_raw_pointer_return(
                func_text
            ) and not self._is_exception_case(func_text):
                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=1,
                    message="Function returns raw pointer. Consider using std::unique_ptr, std::shared_ptr, or references for memory safety.",
                    suggested_fix="Replace raw pointer return with std::unique_ptr<T>, std::shared_ptr<T>, or T& reference",
                )

        return self.issues

    def _has_raw_pointer_return(self, func_text: str) -> bool:
        """Check if function returns a raw pointer."""
        # Skip typedefs and using declarations
        if "typedef" in func_text or "using" in func_text:
            return False

        # Look for pointer return types
        patterns = [
            r"\w+\s*\*\s+\w+\s*\(",  # Type* functionName(
            r"\w+\s*\*\s*\w+\s*\(",  # Type*functionName(
            r"auto\s*\*\s+\w+\s*\(",  # auto* functionName(
        ]

        for pattern in patterns:
            if re.search(pattern, func_text):
                return True
        return False

    def _is_exception_case(self, func_text: str) -> bool:
        """Check if this is an allowed exception case."""
        exception_patterns = [
            r"void\s*\*",  # void* for generic pointers
            r"const\s+void\s*\*",  # const void* for generic pointers
            r"FILE\s*\*",  # FILE* for C file handles
        ]

        for pattern in exception_patterns:
            if re.search(pattern, func_text):
                return True

        # Check for low-level API patterns
        if (
            "malloc" in func_text
            or "calloc" in func_text
            or "realloc" in func_text
            or "GetProcAddress" in func_text
            or "dlsym" in func_text
        ):
            return True

        return False


class SafetyRawPointerParamRule(ASTRule):
    """Rule to detect and discourage raw pointer parameters.

    Suggests using smart pointers or references instead of raw pointers
    for parameters to improve memory safety and ownership clarity.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        function_nodes = self.find_nodes_by_types(
            tree, ["function_declaration", "function_definition"]
        )

        for func_node in function_nodes:
            if self.is_inside_comment(func_node, content):
                continue

            # Use AST parsing to get parameter list
            raw_pointer_params = self._find_raw_pointer_params_ast(
                func_node, content
            )

            if raw_pointer_params:
                line_num = self.get_line_from_byte(
                    func_node.start_byte, content
                )

                # Check if this line should be skipped
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    continue

                should_skip_next, skip_rules = self.should_skip_next_line(
                    content, line_num
                )
                if should_skip_next and (
                    skip_rules == "all" or str(self.rule_id) in skip_rules
                ):
                    continue

                for param_name, param_text in raw_pointer_params:
                    if not self._is_param_exception_case(param_text):
                        self.add_issue(
                            file_path=file_path,
                            line_number=line_num,
                            column=1,
                            message=f"Parameter '{param_name}' is a raw pointer. Consider using smart pointers or references for better ownership semantics.",
                            suggested_fix="Use std::unique_ptr<T>, std::shared_ptr<T>, or T& reference instead of raw pointer",
                        )

        return self.issues

    def _find_raw_pointer_params_ast(
        self, func_node: Any, content: str
    ) -> List[tuple]:
        """Find raw pointer parameters using AST parsing."""
        raw_pointer_params = []

        # Find parameter list node within the function node
        param_list_nodes = self._find_child_nodes_by_type(
            func_node, "parameter_list"
        )
        if not param_list_nodes:
            return raw_pointer_params

        param_list = param_list_nodes[0]

        # Find parameter declarations within the parameter list
        param_nodes = self._find_child_nodes_by_type(
            param_list, "parameter_declaration"
        )

        for param_node in param_nodes:
            param_text = self.get_text_from_node(param_node, content)

            # Check if this is a raw pointer parameter
            if self._is_raw_pointer_param(param_text):
                param_name = self._extract_param_name(param_text)
                if param_name:
                    raw_pointer_params.append((param_name, param_text))

        return raw_pointer_params

    def _find_child_nodes_by_type(
        self, parent_node: Any, node_type: str
    ) -> List[Any]:
        """Find child nodes of a specific type within a parent node."""
        nodes = []

        def visit(node):
            if node.type == node_type:
                nodes.append(node)
            for child in node.children:
                visit(child)

        visit(parent_node)
        return nodes

    def _find_raw_pointer_params(self, func_text: str) -> List[str]:
        """Find raw pointer parameters in function signature."""
        # Skip if this is a comment or documentation
        if "/**" in func_text or "//" in func_text or "/*" in func_text:
            return []

        # Extract parameter list - be more careful about parentheses
        # Skip function pointer types and focus on actual parameter lists
        param_match = re.search(
            r"(?:^|\s)\w+\s*\([^)]*\)\s*\(([^)]*)\)", func_text
        )
        if not param_match:
            # Try simpler pattern for regular functions
            param_match = re.search(r"\w+\s*\(([^)]*)\)", func_text)
            if not param_match:
                return []

        params_str = param_match.group(1)
        if not params_str.strip():
            return []

        # More careful parameter parsing
        raw_pointer_params = []

        # Split parameters, handling nested templates and function pointers
        params = self._split_parameters(params_str)

        for param in params:
            param = param.strip()
            if not param:
                continue

            # Skip if this looks like documentation
            if "/[" in param and "]/" in param:
                continue

            # Look for actual pointer parameters (not in comments)
            if self._is_raw_pointer_param(
                param
            ) and not self._is_param_exception_case(param):
                param_name = self._extract_param_name(param)
                if param_name:
                    raw_pointer_params.append(param_name)

        return raw_pointer_params

    def _split_parameters(self, params_str: str) -> List[str]:
        """Split parameter string into individual parameters, handling nested structures."""
        params = []
        current_param = ""
        paren_depth = 0
        angle_depth = 0

        for char in params_str:
            if char == "," and paren_depth == 0 and angle_depth == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1
                elif char == "<":
                    angle_depth += 1
                elif char == ">":
                    angle_depth -= 1

        if current_param.strip():
            params.append(current_param.strip())

        return params

    def _is_raw_pointer_param(self, param: str) -> bool:
        """Check if parameter is a raw pointer (not a reference or smart pointer)."""
        # Skip if this contains documentation comments
        if "/*[" in param and "]*/" in param:
            return False
        if "/[" in param and "]/" in param:
            return False

        # Must contain * but not be a reference (&) or smart pointer
        if "*" not in param:
            return False

        # Skip if it's actually a reference
        if "&" in param:
            return False

        # Skip smart pointers
        if any(
            smart_ptr in param
            for smart_ptr in ["unique_ptr", "shared_ptr", "weak_ptr"]
        ):
            return False

        # Skip function pointers (contain both * and parentheses in specific pattern)
        if "(*" in param and ")(" in param:
            return False

        return True

    def _extract_param_name(self, param: str) -> str:
        """Extract parameter name from parameter declaration."""
        # Remove comments first
        param = re.sub(r"/\*[^*]*\*/", "", param)  # Remove /* ... */
        param = re.sub(r"//.*$", "", param)  # Remove // comments

        # Remove const, static, etc.
        param = re.sub(r"\b(const|static|volatile|mutable)\b", "", param)

        # Split by spaces and get the last non-pointer part
        parts = param.replace("*", " * ").split()

        # Find the parameter name (last identifier that's not a type modifier)
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i].strip()
            if part and part != "*" and not part.startswith("//"):
                # Remove any trailing characters like []
                part = re.sub(r"[\[\]()].*$", "", part)
                if part.isidentifier():
                    return part

        return ""

    def _is_param_exception_case(self, param: str) -> bool:
        """Check if parameter is an allowed exception case."""
        exception_patterns = [
            r"char\s*\*",  # char* for C strings
            r"const\s+char\s*\*",  # const char* for C strings
            r"void\s*\*",  # void* for generic pointers
            r"const\s+void\s*\*",  # const void* for generic pointers
            r"FILE\s*\*",  # FILE* for C file handles
            r"va_list",  # Variable argument lists
        ]

        for pattern in exception_patterns:
            if re.search(pattern, param):
                return True

        # Check for C-style callback function pointers
        if "(*" in param and ")(" in param:
            return True

        return False


# Rule registration has been moved to registry.py
