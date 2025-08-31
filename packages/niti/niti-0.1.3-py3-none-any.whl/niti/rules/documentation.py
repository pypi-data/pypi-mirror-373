"""Documentation rules for C++ code."""

import re
from typing import Any, Dict, List, Set

from ..core.issue import LintIssue
from .base import ASTRule


class DocFunctionMissingRule(ASTRule):
    """Rule to check for missing function documentation.

    Checks that public functions have Doxygen-style documentation comments.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_documentation(
                    func_node, content, file_path
                )

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_documentation(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function has proper documentation."""
        try:
            # Skip private functions (heuristic: inside private: section)
            if self._is_private_function(func_node, content):
                return

            # Skip constructors and destructors (different documentation rules)
            func_name = self._get_function_name(func_node, content)
            if self._is_constructor_or_destructor(func_name):
                return

            # Check for Doxygen comment before function
            has_doc = self._has_doxygen_comment(func_node, content)

            if not has_doc:
                line_num = self.get_line_from_byte(
                    func_node.start_byte, content
                )
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Public function missing documentation: {func_name}",
                    suggested_fix="Add Doxygen comment block (/** ... */) before function declaration",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Free functions (outside of classes) are never private
            if not self._is_inside_class(func_node, content):
                return False

            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier within the current class
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _is_inside_class(self, func_node: Any, content: str) -> bool:
        """Check if function is inside a class or struct."""
        try:
            # Check if the function node is inside a class_specifier or struct_specifier
            current = func_node.parent
            while current:
                if current.type in ["class_specifier", "struct_specifier"]:
                    return True
                current = current.parent
            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _is_constructor_or_destructor(self, func_name: str) -> bool:
        """Check if function is constructor or destructor."""
        # Skip if function name is unknown (AST parsing issue)
        if func_name == "unknown":
            return True  # Skip unknown functions to avoid false positives

        # Destructors start with ~
        if func_name.startswith("~"):
            return True

        # Constructors typically have the same name as their class
        # This is a heuristic but should cover most cases
        return False

    def _has_doxygen_comment(self, func_node: Any, content: str) -> bool:
        """Check if function has Doxygen comment immediately before it."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            # Look at the few lines before the function
            for i in range(max(0, func_start_line - 5), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    # Check for Doxygen comment patterns
                    if "/**" in line or line.startswith("*") or "*/" in line:
                        return True

            return False
        except Exception:
            return False


class DocMissingDeclarationCommentRule(ASTRule):
    """Rule to check for missing documentation on declarations.

    Checks that public classes, structs, and enums have Doxygen-style
    documentation comments.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all class, struct, and enum declarations
        nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier", "enum_specifier"]
        )

        for node in nodes:
            self._check_declaration_documentation(node, content)

        return self.issues

    def _check_declaration_documentation(self, node: Any, content: str) -> None:
        """Check if a declaration has proper documentation."""
        try:
            # Get declaration name and type
            decl_type = node.type.replace("_specifier", "")
            decl_name = self._get_declaration_name(node, content)

            # Skip template specializations and anonymous declarations
            if not decl_name or decl_name == "anonymous":
                return

            # Check for Doxygen comment before the declaration
            has_doc = self._has_doxygen_comment(node, content)

            if not has_doc:
                line_num = node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                issue = LintIssue(
                    file_path=self.current_file,
                    line_number=line_num,
                    column=node.start_point[1] + 1,
                    severity=self.severity,
                    rule_id=str(self.rule_id),
                    message=f"{decl_type.capitalize()} missing documentation: {decl_name}",
                    suggested_fix=f"Add Doxygen comment block (/** ... */) before {decl_type} declaration",
                )
                self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _get_declaration_name(self, node: Any, content: str) -> str:
        """Extract declaration name from AST node."""
        try:
            # Look for type_identifier child
            for child in node.children:
                if child.type == "type_identifier":
                    return self.get_text_from_node(child, content)
            return "anonymous"
        except Exception:
            return "unknown"

    def _has_doxygen_comment(self, node: Any, content: str) -> bool:
        """Check if node has Doxygen comment immediately before it."""
        try:
            node_start_line = node.start_point[0]
            lines = content.split("\n")

            # Look at the few lines before the node
            for i in range(max(0, node_start_line - 5), node_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    # Check for Doxygen comment patterns
                    if "/**" in line or line.startswith("*") or "*/" in line:
                        return True

            return False
        except Exception:
            return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocParamDirectionMissingRule(ASTRule):
    """Rule to check for missing parameter direction annotations.

    Checks that function parameters have direction annotations like /*[in]*/, /*[out]*/, /*[inout]*/.
    This is critical for the Vajra codebase style.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_parameters(func_node, content, file_path)

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_parameters(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function parameters have direction annotations in Doxygen comments."""
        try:
            # Get the Doxygen comment before this function
            doxygen_comment = self._get_doxygen_comment_before_function(
                func_node, content
            )
            if not doxygen_comment:
                return  # No documentation, skip

            # Extract @param lines from the comment
            param_docs = self._extract_param_docs(doxygen_comment)

            # Check each @param for direction annotations
            for param_name, param_desc, line_offset in param_docs:
                if not self._has_direction_annotation(param_desc):
                    # Calculate line number of the @param line
                    comment_start_line = self._get_comment_start_line(
                        func_node, content
                    )
                    line_num = comment_start_line + line_offset

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Parameter '{param_name}' missing direction annotation (in), (out), or (in/out) in documentation",
                        suggested_fix=f"Add direction annotation like: @param {param_name} Description (in)",
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_doxygen_comment_before_function(
        self, func_node: Any, content: str
    ) -> str:
        """Get the Doxygen comment immediately before a function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for comment block
            comment_lines = []
            i = func_start_line - 1
            in_comment = False

            while i >= 0:
                line = lines[i].strip()
                if line.endswith("*/"):
                    in_comment = True
                    comment_lines.insert(0, line)
                elif in_comment:
                    comment_lines.insert(0, line)
                    if line.startswith("/**") or line.startswith("/*"):
                        break
                elif line == "":
                    pass  # Skip empty lines
                else:
                    break  # Hit non-comment, non-empty line
                i -= 1

            return "\n".join(comment_lines) if comment_lines else ""
        except Exception:
            return ""

    def _extract_param_docs(self, comment: str) -> List[tuple]:
        """Extract @param lines from Doxygen comment. Returns [(param_name, description, line_offset), ...]"""
        try:
            param_docs = []
            lines = comment.split("\n")

            for i, line in enumerate(lines):
                line = line.strip()
                # Remove comment markers
                line = line.lstrip("/*").lstrip("*").strip()

                # Look for @param lines
                if line.startswith("@param "):
                    parts = line[7:].split(
                        None, 1
                    )  # Split into name and description
                    if len(parts) >= 1:
                        param_name = parts[0]
                        description = parts[1] if len(parts) > 1 else ""
                        param_docs.append((param_name, description, i))

            return param_docs
        except Exception:
            return []

    def _has_direction_annotation(self, param_description: str) -> bool:
        """Check if parameter description has direction annotation."""
        # Look for direction annotations in parentheses
        direction_patterns = [
            r"\(in\)",
            r"\(out\)",
            r"\(in/out\)",
            r"\(inout\)",
            r"\[in\]",
            r"\[out\]",
            r"\[in/out\]",
            r"\[inout\]",
            r"\[in,out\]",
        ]

        for pattern in direction_patterns:
            if self.regex_search(pattern, param_description):
                return True
        return False

    def _get_comment_start_line(self, func_node: Any, content: str) -> int:
        """Get the line number where the Doxygen comment starts."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for comment start
            i = func_start_line - 1
            while i >= 0:
                line = lines[i].strip()
                if line.startswith("/**") or line.startswith("/*"):
                    return i + 1  # Convert to 1-based line number
                elif line == "":
                    pass
                else:
                    break
                i -= 1

            return func_start_line + 1  # Fallback
        except Exception:
            return 1

    def _is_simple_type(self, param_text: str) -> bool:
        """Check if parameter type is simple and doesn't need direction annotation."""
        # Simple built-in types that are typically passed by value
        simple_types = {
            "bool",
            "char",
            "int",
            "float",
            "double",
            "std::int32_t",
            "std::int64_t",
            "std::uint32_t",
            "std::uint64_t",
            "std::size_t",
            "size_t",
        }

        # Extract type from parameter (remove const, &, *, etc.)
        type_match = self.regex_search(
            r"\b([a-zA-Z_][a-zA-Z0-9_:]*)", param_text
        )
        if type_match:
            base_type = type_match.group(1)
            if base_type in simple_types:
                return True

        return False


class DocFunctionMissingParamDocsRule(ASTRule):
    """Rule to check that function @param documentation matches actual parameters.

    Functions with parameters should document each parameter with @param tags.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_param_docs(func_node, content, file_path)

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_param_docs(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function parameters are properly documented."""
        try:
            # Skip private functions
            if self._is_private_function(func_node, content):
                return

            # Get function name first
            func_name = self._get_function_name(func_node, content)

            # Skip destructors (no parameters) but DO check constructors.
            if func_name.startswith("~"):
                return

            # Collect the actual parameter names for the function
            param_names = set(self._get_parameter_names(func_node, content))

            # Skip if no parameters
            if not param_names:
                return

            # Get documentation before function
            doc_comment = self._get_doxygen_comment(func_node, content)
            if not doc_comment:
                return  # No documentation at all - handled by other rule

            # Parse @param tags from documentation
            documented_params = self._parse_param_tags(doc_comment)

            # Check for missing @param documentation
            missing_params = [
                param for param in param_names if param not in documented_params
            ]

            if missing_params:
                line_num = func_node.start_point[0] + 1
                if not self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    if len(missing_params) == 1:
                        message = f"Function '{func_name}' missing @param documentation for parameter: {missing_params[0]}"
                        suggested_fix = f"Add @param {missing_params[0]} description to function documentation"
                    else:
                        param_list = ", ".join(missing_params)
                        message = f"Function '{func_name}' missing @param documentation for parameters: {param_list}"
                        suggested_fix = f"Add @param documentation for parameters: {param_list}"

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=func_node.start_point[1] + 1,
                        message=message,
                        suggested_fix=suggested_fix,
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _get_parameter_names(self, func_node: Any, content: str) -> List[str]:
        """Extract parameter names from function node."""
        param_names = []
        try:
            # Find parameter list
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "parameter_list":
                            param_names.extend(
                                self._extract_param_names(subchild, content)
                            )
                            break
                    break
        except Exception:
            pass
        return param_names

    def _extract_param_names(
        self, param_list_node: Any, content: str
    ) -> List[str]:
        """Extract parameter names from parameter list node."""
        param_names = []
        try:
            for child in param_list_node.children:
                if child.type not in [
                    "parameter_declaration",
                    "optional_parameter_declaration",
                ]:
                    continue

                # Perform a depth-first search to find the last identifier inside
                # the parameter declaration – this generally corresponds to the
                # variable name rather than a type component (e.g., template
                # argument).
                last_identifier: str | None = None

                stack = list(child.children)
                while stack:
                    node = stack.pop()
                    if node.type == "identifier":
                        last_identifier = self.get_text_from_node(node, content)
                    # Push children for further traversal
                    stack.extend(node.children)

                if last_identifier is not None:
                    param_names.append(last_identifier)
        except Exception:
            pass
        return param_names

    def _get_doxygen_comment(self, func_node: Any, content: str) -> str:
        """Get Doxygen comment before function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the function
            for i in range(max(0, func_start_line - 10), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _parse_param_tags(self, doc_comment: str) -> Set[str]:
        """Parse @param tags from Doxygen comment."""
        param_names = set()
        try:
            # Look for @param tags
            param_matches = re.findall(
                r"@param\s+(\w+)", doc_comment, re.IGNORECASE
            )
            param_names.update(param_matches)
        except Exception:
            pass
        return param_names

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocFunctionMissingReturnDocsRule(ASTRule):
    """Rule to check that non-void functions have @return documentation.

    Functions that return values should document the return value with @return tag.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_return_docs(func_node, content, file_path)

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_return_docs(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function return value is properly documented."""
        try:
            # Skip private functions
            if self._is_private_function(func_node, content):
                return

            # Get function name and return type
            func_name = self._get_function_name(func_node, content)
            return_type = self._get_return_type(func_node, content)

            # Skip void functions
            if self._is_void_function(return_type):
                return

            # Skip constructors and destructors
            if self._is_constructor_or_destructor(func_name):
                return

            # Get documentation before function
            doc_comment = self._get_doxygen_comment(func_node, content)
            if not doc_comment:
                return  # No documentation at all - handled by other rule

            # Check for @return tag
            has_return_doc = self._has_return_tag(doc_comment)

            if not has_return_doc:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                # Check for return type and if docs are missing
                if return_type and return_type not in [
                    "void",
                    "auto",
                    "unknown",
                ]:
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=func_node.start_point[1] + 1,
                        message=f"Function '{func_name}' with return type '{return_type}' missing @return documentation",
                        suggested_fix="Add @return description to function documentation",
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _get_return_type(self, func_node: Any, content: str) -> str:
        """Extract return type from function node."""
        try:
            # Look for primitive_type, type_identifier, or other type nodes before function_declarator
            for child in func_node.children:
                if child.type in [
                    "primitive_type",
                    "type_identifier",
                    "qualified_identifier",
                    "template_type",
                    "auto",
                ]:
                    return self.get_text_from_node(child, content)
            return "unknown"
        except Exception:
            return "unknown"

    def _is_void_function(self, return_type: str) -> bool:
        """Check if function returns void."""
        return return_type.strip() == "void"

    def _is_constructor_or_destructor(self, func_name: str) -> bool:
        """Check if function is constructor or destructor."""
        # Skip if function name is unknown (AST parsing issue)
        if func_name == "unknown":
            return True  # Skip unknown functions to avoid false positives

        # Destructors start with ~
        if func_name.startswith("~"):
            return True

        # Constructors typically have the same name as their class
        # This is a heuristic but should cover most cases
        return False

    def _get_doxygen_comment(self, func_node: Any, content: str) -> str:
        """Get Doxygen comment before function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the function
            for i in range(max(0, func_start_line - 10), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _has_return_tag(self, doc_comment: str) -> bool:
        """Check if documentation has @return tag."""
        try:
            return bool(re.search(r"@return\b", doc_comment, re.IGNORECASE))
        except Exception:
            return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocFunctionMissingThrowsDocsRule(ASTRule):
    """Rule to check that functions with throw specifications have @throws documentation.

    Functions that can throw exceptions should document them with @throws tags.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        function_nodes = self.find_nodes_by_types(
            tree, ["function_declaration", "function_definition"]
        )

        for func_node in function_nodes:
            self._check_function_throws_docs(func_node, content)

        return self.issues

    def _check_function_throws_docs(self, func_node: Any, content: str) -> None:
        """Check if function throw specifications are properly documented."""
        try:
            # Skip private functions
            if self._is_private_function(func_node, content):
                return

            # Get function name and check for throw specifications
            func_name = self._get_function_name(func_node, content)
            can_throw = self._can_function_throw(func_node, content)

            # Skip if function doesn't throw
            if not can_throw:
                return

            # Get documentation before function
            doc_comment = self._get_doxygen_comment(func_node, content)
            if not doc_comment:
                return  # No documentation at all - handled by other rule

            # Check for @throws or @exception tag
            has_throws_doc = self._has_throws_tag(doc_comment)

            if not has_throws_doc:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                issue = LintIssue(
                    file_path=self.current_file,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    severity=self.severity,
                    rule_id=str(self.rule_id),
                    message=f"Function '{func_name}' can throw exceptions but missing @throws documentation",
                    suggested_fix="Add @throws exception_type description to function documentation",
                )
                self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _can_function_throw(self, func_node: Any, content: str) -> bool:
        """Check if function can throw exceptions."""
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Check for explicit throw specifications
            if "throw(" in func_text and "throw()" not in func_text:
                return True

            # Check for noexcept specification (indicates might throw otherwise)
            if "noexcept" in func_text:
                return False

            # Heuristic: assume functions that call throwing operations can throw
            throwing_patterns = [
                r"throw\s+",  # explicit throw statements
                r"new\s+",  # dynamic allocation can throw
                r"\.at\(",  # vector/map at() can throw
                r"dynamic_cast",  # can throw bad_cast
            ]

            # Check for potentially throwing string operations (but not simple ToString methods)
            if re.search(r"std::string", func_text):
                # Skip simple ToString() methods that just format basic values
                if (
                    re.search(r"ToString\s*\(", func_text)
                    and "std::format" in func_text
                ):
                    # ToString methods using std::format with simple patterns are unlikely to throw
                    return False
                elif not re.search(r"ToString\s*\(", func_text):
                    # Other functions using std::string operations might throw
                    return True

            for pattern in throwing_patterns:
                if re.search(pattern, func_text):
                    return True

            return False
        except Exception:
            return False

    def _get_doxygen_comment(self, func_node: Any, content: str) -> str:
        """Get Doxygen comment before function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the function
            for i in range(max(0, func_start_line - 10), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _has_throws_tag(self, doc_comment: str) -> bool:
        """Check if documentation has @throws or @exception tag."""
        try:
            return bool(
                re.search(r"@(throws|exception)\b", doc_comment, re.IGNORECASE)
            )
        except Exception:
            return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocFunctionExtraParamDocsRule(ASTRule):
    """Rule to detect extra @param documentation for non-existent parameters.

    Functions should not have @param documentation for parameters that don't exist.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_extra_param_docs(
                    func_node, content, file_path
                )

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_extra_param_docs(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check for extra @param documentation."""
        try:
            # Skip private functions
            if self._is_private_function(func_node, content):
                return

            # Determine the function name first
            func_name = self._get_function_name(func_node, content)

            # Skip destructors (no parameters) but DO check constructors.
            if func_name.startswith("~"):
                return

            # Gather the parameter names actually present in the signature
            param_names = set(self._get_parameter_names(func_node, content))

            # Get documentation before function
            doc_comment = self._get_doxygen_comment(func_node, content)
            if not doc_comment:
                return  # No documentation at all

            # Parse @param tags from documentation
            documented_params = self._parse_param_tags(doc_comment)

            # Check for extra @param documentation
            for documented_param in documented_params:
                if documented_param not in param_names:
                    line_num = func_node.start_point[0] + 1
                    if self.should_skip_line(
                        self.get_line(content, line_num), str(self.rule_id)
                    ):
                        continue

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=func_node.start_point[1] + 1,
                        message=f"Function '{func_name}' has @param documentation for non-existent parameter: {documented_param}",
                        suggested_fix=f"Remove @param {documented_param} from function documentation or check parameter name spelling",
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _get_parameter_names(self, func_node: Any, content: str) -> List[str]:
        """Extract parameter names from function node."""
        param_names = []
        try:
            # Find parameter list
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "parameter_list":
                            param_names.extend(
                                self._extract_param_names(subchild, content)
                            )
                            break
                    break
        except Exception:
            pass
        return param_names

    def _extract_param_names(
        self, param_list_node: Any, content: str
    ) -> List[str]:
        """Extract parameter names from parameter list node."""
        param_names = []
        try:
            for child in param_list_node.children:
                if child.type not in [
                    "parameter_declaration",
                    "optional_parameter_declaration",
                ]:
                    continue

                # Perform a depth-first search to find the last identifier inside
                # the parameter declaration – this generally corresponds to the
                # variable name rather than a type component (e.g., template
                # argument).
                last_identifier: str | None = None

                stack = list(child.children)
                while stack:
                    node = stack.pop()
                    if node.type == "identifier":
                        last_identifier = self.get_text_from_node(node, content)
                    # Push children for further traversal
                    stack.extend(node.children)

                if last_identifier is not None:
                    param_names.append(last_identifier)
        except Exception:
            pass
        return param_names

    def _get_doxygen_comment(self, func_node: Any, content: str) -> str:
        """Get Doxygen comment before function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the function
            for i in range(max(0, func_start_line - 10), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _parse_param_tags(self, doc_comment: str) -> Set[str]:
        """Parse @param tags from Doxygen comment."""
        param_names = set()
        try:
            # Look for @param tags
            param_matches = re.findall(
                r"@param\s+(\w+)", doc_comment, re.IGNORECASE
            )
            param_names.update(param_matches)
        except Exception:
            pass
        return param_names

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def _is_constructor_or_destructor(self, func_name: str) -> bool:
        """Determine whether the provided function name is a constructor or destructor."""
        # Unknown names: play it safe and skip.
        if func_name == "unknown":
            return True

        # Destructors begin with a tilde.
        if func_name.startswith("~"):
            return True

        # Heuristic for constructors: the name starts with an uppercase letter
        # (PascalCase), matching typical class names.
        return func_name[0].isupper() if func_name else False


class DocFunctionParamDescQualityRule(ASTRule):
    """Rule to check parameter description quality.

    Parameter descriptions should be meaningful, not just "the parameter".
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations and definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_function_param_desc_quality(
                    func_node, content, file_path
                )

        return self.issues

    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration."""
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                return True

        return False

    def _check_function_param_desc_quality(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check quality of parameter descriptions."""
        try:
            # Skip private functions
            if self._is_private_function(func_node, content):
                return

            # Get function name
            func_name = self._get_function_name(func_node, content)

            # Get documentation before function
            doc_comment = self._get_doxygen_comment(func_node, content)
            if not doc_comment:
                return  # No documentation at all

            # Parse @param tags and their descriptions
            param_descriptions = self._parse_param_descriptions(doc_comment)

            # Check quality of each parameter description
            for param_name, description in param_descriptions.items():
                if self._is_low_quality_description(param_name, description):
                    line_num = func_node.start_point[0] + 1
                    if self.should_skip_line(
                        self.get_line(content, line_num), str(self.rule_id)
                    ):
                        continue

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=func_node.start_point[1] + 1,
                        message=f"Function '{func_name}' parameter '{param_name}' has low-quality description: '{description}'",
                        suggested_fix=f"Improve @param {param_name} description to explain the parameter's purpose and expected values",
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_private_function(self, func_node: Any, content: str) -> bool:
        """Check if function is in private section (heuristic)."""
        try:
            # Free functions (outside of classes) are never private
            if not self._is_inside_class(func_node, content):
                return False

            # Look for 'private:' before this function
            func_start = func_node.start_point[0]
            lines = content.split("\n")

            # Look backwards for access specifier within the current class
            for i in range(max(0, func_start - 1), -1, -1):
                line = lines[i].strip()
                if "private:" in line:
                    return True
                elif "public:" in line or "protected:" in line:
                    return False
                elif line.startswith("class ") or line.startswith("struct "):
                    break

            return False
        except Exception:
            return False

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Look for qualified_identifier (for namespaced functions)
            for child in func_node.children:
                if child.type == "qualified_identifier":
                    # Get the last part of the qualified name
                    parts = self.get_text_from_node(child, content).split("::")
                    if parts:
                        return parts[-1]

            # Strategy 4: Parse the text directly to extract function name
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def _get_doxygen_comment(self, func_node: Any, content: str) -> str:
        """Get Doxygen comment before function."""
        try:
            func_start_line = func_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the function
            for i in range(max(0, func_start_line - 10), func_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _parse_param_descriptions(self, doc_comment: str) -> Dict[str, str]:
        """Parse @param tags and their descriptions from Doxygen comment."""
        param_descriptions = {}
        try:
            # Look for @param tags with descriptions
            param_matches = re.findall(
                r"@param\s+(\w+)\s+(.+?)(?=@\w+|$|\*/)",
                doc_comment,
                re.IGNORECASE | re.DOTALL,
            )
            for param_name, description in param_matches:
                # Clean up description
                cleaned_desc = re.sub(r"\s+", " ", description.strip())
                cleaned_desc = re.sub(r"[*\n]+", " ", cleaned_desc).strip()

                # Remove C++ style comments (// ...)
                cleaned_desc = re.sub(r"//.*$", "", cleaned_desc).strip()

                param_descriptions[param_name] = cleaned_desc
        except Exception:
            pass
        return param_descriptions

    def _is_low_quality_description(
        self, param_name: str, description: str
    ) -> bool:
        """Check if parameter description is low quality."""
        if not description:
            return True

        # Normalize description
        desc_lower = description.lower().strip()

        # Check for exact matches or very generic descriptions
        low_quality_exact_patterns = [
            f"the {param_name.lower()}",
            f"a {param_name.lower()}",
            f"an {param_name.lower()}",
            param_name.lower(),  # Just repeats the parameter name
            "the parameter",
            "a parameter",
            "parameter",
            "input",
            "output",
            "data",
            "value",
            "variable",
            "object",
            "item",
        ]

        for pattern in low_quality_exact_patterns:
            if desc_lower == pattern:
                return True

        # Check for patterns that are only slightly better than just the param name
        lazy_patterns = [
            f"the {param_name.lower()}",
            f"a {param_name.lower()}",
            f"an {param_name.lower()}",
        ]

        for pattern in lazy_patterns:
            # Only flag if it exactly matches or just adds direction info
            if (
                desc_lower == pattern
                or desc_lower == pattern + " (in)"
                or desc_lower == pattern + " (out)"
                or desc_lower == pattern + " (in/out)"
            ):
                return True

        # Check minimum length (should be more descriptive than just a few words)
        if len(description.strip()) < 10:
            return True

        return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocClassDocstringBriefRule(ASTRule):
    """Rule to require @brief tag in class documentation.

    Class documentation should include a @brief tag for clear summaries.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all class and struct declarations
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            self._check_class_brief_tag(class_node, content, file_path)

        return self.issues

    def _check_class_brief_tag(
        self, class_node: Any, content: str, file_path: str
    ) -> None:
        """Check if class has @brief tag in documentation."""
        try:
            # Get class name
            class_name = self._get_class_name(class_node, content)

            # Skip anonymous classes
            if not class_name or class_name == "anonymous":
                return

            # Get documentation before class
            doc_comment = self._get_doxygen_comment(class_node, content)
            if not doc_comment:
                return  # No documentation at all - handled by other rule

            # Check for @brief tag
            has_brief = self._has_brief_tag(doc_comment)

            if not has_brief:
                line_num = class_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=class_node.start_point[1] + 1,
                    message=f"Class '{class_name}' documentation missing @brief tag",
                    suggested_fix="Add @brief description to class documentation",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract class name from AST node."""
        try:
            # Look for type_identifier child
            for child in class_node.children:
                if child.type == "type_identifier":
                    return self.get_text_from_node(child, content)
            return "anonymous"
        except Exception:
            return "unknown"

    def _get_doxygen_comment(self, class_node: Any, content: str) -> str:
        """Get Doxygen comment before class."""
        try:
            class_start_line = class_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the class, searching backwards for the closest comment
            for i in range(
                class_start_line - 1, max(0, class_start_line - 10) - 1, -1
            ):
                if i < len(lines):
                    line = lines[i].strip()
                    if "*/" in line:
                        if not in_comment:
                            in_comment = True
                            comment_lines.insert(0, line)
                        else:
                            comment_lines.insert(0, line)
                            break
                    elif in_comment:
                        comment_lines.insert(0, line)
                        if "/**" in line:
                            break
                    elif line == "":
                        # Empty line - continue looking
                        continue
                    else:
                        # Non-empty, non-comment line - stop looking
                        break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _has_brief_tag(self, doc_comment: str) -> bool:
        """Check if documentation has @brief tag."""
        try:
            # Look for @brief at start of line (with optional whitespace and *)
            return bool(
                re.search(
                    r"^\s*\*?\s*@brief\s+",
                    doc_comment,
                    re.IGNORECASE | re.MULTILINE,
                )
            )
        except Exception:
            return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""


class DocClassDocstringThreadSafetyRule(ASTRule):
    """Rule to require thread safety documentation for manager/engine classes.

    Classes with names containing 'Manager' or 'Engine' should document thread safety.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        self.current_file = file_path

        # Only apply to header files
        if not file_path.endswith((".h", ".hpp", ".hxx", ".hh")):
            return self.issues

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all class and struct declarations
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            self._check_class_thread_safety_docs(class_node, content)

        return self.issues

    def _check_class_thread_safety_docs(
        self, class_node: Any, content: str
    ) -> None:
        """Check if manager/engine class has thread safety documentation."""
        try:
            # Get class name
            class_name = self._get_class_name(class_node, content)

            # Skip anonymous classes
            if not class_name or class_name == "anonymous":
                return

            # Check if class needs thread safety documentation
            if not self._is_manager_or_engine_class(class_name):
                return

            # Get documentation before class
            doc_comment = self._get_doxygen_comment(class_node, content)
            if not doc_comment:
                return  # No documentation at all - handled by other rule

            # Check for thread safety documentation
            has_thread_safety_docs = self._has_thread_safety_docs(doc_comment)

            if not has_thread_safety_docs:
                line_num = class_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                issue = LintIssue(
                    file_path=self.current_file,
                    line_number=line_num,
                    column=class_node.start_point[1] + 1,
                    severity=self.severity,
                    rule_id=str(self.rule_id),
                    message=f"Manager/Engine class '{class_name}' missing thread safety documentation",
                    suggested_fix="Add thread safety documentation (e.g., @note Thread-safe, @warning Not thread-safe, etc.)",
                )
                self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract class name from AST node."""
        try:
            # Look for type_identifier child
            for child in class_node.children:
                if child.type == "type_identifier":
                    return self.get_text_from_node(child, content)
            return "anonymous"
        except Exception:
            return "unknown"

    def _is_manager_or_engine_class(self, class_name: str) -> bool:
        """Check if class is a manager or engine that needs thread safety docs."""
        manager_engine_patterns = [
            "Manager",
            "Engine",
            "Controller",
            "Scheduler",
            "Pool",
            "Store",
            "Cache",
            "Registry",
            "Factory",
            "Service",
        ]

        for pattern in manager_engine_patterns:
            if pattern in class_name:
                return True

        return False

    def _get_doxygen_comment(self, class_node: Any, content: str) -> str:
        """Get Doxygen comment before class."""
        try:
            class_start_line = class_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the class
            for i in range(max(0, class_start_line - 10), class_start_line):
                if i < len(lines):
                    line = lines[i].strip()
                    if "/**" in line:
                        in_comment = True
                        comment_lines.append(line)
                    elif in_comment:
                        comment_lines.append(line)
                        if "*/" in line:
                            break

            return "\n".join(comment_lines)
        except Exception:
            return ""

    def _has_thread_safety_docs(self, doc_comment: str) -> bool:
        """Check if documentation has thread safety information."""
        try:
            thread_safety_patterns = [
                r"thread[- ]safe",
                r"thread[- ]safety",
                r"concurrent",
                r"synchronization",
                r"mutex",
                r"lock",
                r"atomic",
                r"race condition",
                r"not thread[- ]safe",
                r"single[- ]threaded",
                r"multi[- ]threaded",
            ]

            for pattern in thread_safety_patterns:
                if re.search(pattern, doc_comment, re.IGNORECASE):
                    return True

            return False
        except Exception:
            return False

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""
