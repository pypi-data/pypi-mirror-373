"""Modern C++ feature rules."""

from typing import Any, List

from ..core.issue import LintIssue
from .base import ASTRule
from .rule_id import RuleId


class ModernMissingNoexceptRule(ASTRule):
    """Rule to suggest adding noexcept to functions.

    Checks for destructors and move operations that should be noexcept.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations/definitions
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
                self._check_noexcept_candidacy(func_node, content, file_path)

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

    def _check_noexcept_candidacy(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function should be noexcept."""
        try:
            func_name = self._get_function_name(func_node, content)

            if not func_name:
                return

            # Check if it's already noexcept
            if self._is_already_noexcept(func_node, content):
                return

            should_be_noexcept = False
            reason = ""

            # Check for destructor
            if func_name.startswith("~"):
                should_be_noexcept = True
                reason = "Destructors should be noexcept"

            # Check for move constructor/assignment
            elif self._is_move_operation(func_node, content):
                should_be_noexcept = True
                reason = "Move operations should be noexcept for performance"

            # Check for swap functions
            elif "swap" in func_name.lower():
                should_be_noexcept = True
                reason = "Swap functions should be noexcept"

            # Check for simple getter/setter/query methods that could be noexcept
            elif self._is_simple_method_candidate(
                func_node, func_name, content
            ):
                should_be_noexcept = True
                reason = "Simple getter/setter methods should be noexcept when possible"

            if should_be_noexcept:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Function '{func_name}' should be noexcept - {reason}",
                    suggested_fix="Add 'noexcept' specifier to function declaration",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type in ["identifier", "field_identifier"]:
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""

    def _is_already_noexcept(self, func_node: Any, content: str) -> bool:
        """Check if function is already marked noexcept."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "noexcept" in func_text
        except Exception:
            return False

    def _is_move_operation(self, func_node: Any, content: str) -> bool:
        """Check if function is a move constructor or move assignment."""
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Look for move constructor/assignment patterns
            if "&&" in func_text:  # Rvalue reference
                # Move constructor or move assignment
                if (
                    "operator=" in func_text
                    or self._looks_like_move_constructor(func_text)
                ):
                    return True

            return False
        except Exception:
            return False

    def _looks_like_move_constructor(self, func_text: str) -> bool:
        """Check if function looks like a move constructor."""
        # Heuristic: constructor with rvalue reference parameter
        return (
            "&&" in func_text
            and "(" in func_text
            and ")" in func_text
            and "operator=" not in func_text
        )

    def _is_simple_method_candidate(
        self, func_node: Any, func_name: str, content: str
    ) -> bool:
        """Check if a method is a simple candidate for noexcept."""
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Skip if function contains throwing keywords
            throwing_keywords = ["throw", "new", "delete", "dynamic_cast"]
            for keyword in throwing_keywords:
                if keyword in func_text:
                    return False

            # Skip if function calls other functions that might throw
            # This is a simple heuristic - look for function calls with ()
            if (
                func_text.count("(") > 1
            ):  # More than just the function declaration
                # Check for common safe operations
                safe_operations = [
                    "return",
                    "=",
                    "==",
                    "!=",
                    "<",
                    ">",
                    "<=",
                    ">=",
                    "&&",
                    "||",
                ]
                # If it has function calls but doesn't look like simple operations, skip
                func_body = (
                    func_text.split("{", 1)[-1].split("}", 1)[0]
                    if "{" in func_text
                    else ""
                )
                if func_body and not any(
                    op in func_body for op in safe_operations
                ):
                    # Has complex function calls, might throw
                    return False

            # Simple getters (const methods that return something)
            if (
                "const" in func_text
                and "return" in func_text
                and "void" not in func_text
            ):
                return True

            # Simple setters/mutators with basic assignments
            if "void" in func_text and "=" in func_text and "{" in func_text:
                # Check that it's just doing simple assignment
                func_body = (
                    func_text.split("{", 1)[-1].split("}", 1)[0]
                    if "{" in func_text
                    else ""
                )
                if func_body and func_body.count(";") <= 2:  # Very simple body
                    return True

            return False
        except Exception:
            return False


class ModernMissingConstRule(ASTRule):
    """Rule to suggest making methods const.

    Detects getter methods that should be const but aren't marked as const.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # We only care about definitions, as declarations might not have the 'const' keyword
        function_nodes = self.find_nodes_by_types(tree, ["function_definition"])

        for func_node in function_nodes:
            # Ensure we are inside a class
            parent = func_node.parent
            while parent and parent.type != "class_specifier":
                parent = parent.parent
            if not parent:
                continue  # Skip free functions

            self._check_const_candidacy(func_node, content, file_path, parent)

        return self.issues

    def _check_const_candidacy(
        self, func_node: Any, content: str, file_path: str, class_node: Any
    ) -> None:
        """Check if a specific function should be const."""
        try:
            func_name = self._get_function_name(func_node, content)
            class_name = self._get_class_name(class_node, content)

            if not func_name or self._should_skip_function(
                func_name, class_name
            ):
                return

            if self._is_already_const(func_node, content):
                return

            if self._is_getter_method(func_name, func_node, content):
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Getter method '{func_name}' should be const",
                    suggested_fix="Add 'const' qualifier to method declaration",
                )
        except Exception:
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from a function_definition node."""
        declarator = func_node.child_by_field_name("declarator")
        if declarator:
            # This can be a simple identifier or a qualified_identifier
            name_node = declarator.child_by_field_name("declarator")
            if name_node:
                return self.get_text_from_node(name_node, content)
        return ""

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract the class name from a class_specifier node."""
        name_node = class_node.child_by_field_name("name")
        if name_node:
            return self.get_text_from_node(name_node, content)
        return ""

    def _should_skip_function(self, func_name: str, class_name: str) -> bool:
        """Check if function should be skipped from const checking."""
        if (
            func_name == class_name  # Constructor
            or func_name.startswith("~")  # Destructor
            or func_name.startswith("operator")  # Operator
        ):
            return True

        mutating_prefixes = {
            "set",
            "add",
            "insert",
            "remove",
            "delete",
            "clear",
            "update",
            "modify",
        }
        for prefix in mutating_prefixes:
            if func_name.lower().startswith(prefix):
                return True
        return False

    def _is_already_const(self, func_node: Any, content: str) -> bool:
        """Check if function is already marked const."""
        declarator = func_node.child_by_field_name("declarator")
        if not declarator:
            return False

        # The 'const' qualifier can be:
        # 1. A child of the function_declarator node
        # 2. A sibling of the declarator (less common)

        # First check within the declarator
        for child in declarator.children:
            if (
                child.type == "type_qualifier"
                and self.get_text_from_node(child, content) == "const"
            ):
                return True

        # Also check siblings of the declarator
        for child in func_node.children:
            if (
                child.type == "type_qualifier"
                and self.get_text_from_node(child, content) == "const"
            ):
                if child.start_byte > declarator.end_byte:
                    return True
        return False

    def _is_getter_method(
        self, func_name: str, func_node: Any, content: str
    ) -> bool:
        """Check if function is a getter method."""
        if self._returns_void(func_node, content):
            return False

        getter_prefixes = {
            "get",
            "is",
            "has",
            "can",
            "should",
            "will",
            "size",
            "empty",
        }
        for prefix in getter_prefixes:
            if func_name.lower().startswith(prefix):
                return True

        if self._has_no_parameters(func_node, content):
            return True

        return False

    def _returns_void(self, func_node: Any, content: str) -> bool:
        """Check if function returns void."""
        return_type = func_node.child_by_field_name("type")
        return (
            return_type is not None
            and self.get_text_from_node(return_type, content) == "void"
        )

    def _has_no_parameters(self, func_node: Any, content: str) -> bool:
        """Check if function has no parameters."""
        declarator = func_node.child_by_field_name("declarator")
        if declarator:
            param_list = declarator.child_by_field_name("parameters")
            if param_list:
                return param_list.named_child_count == 0
        return True


class ModernNodiscardMissingRule(ASTRule):
    """Enhanced rule to suggest adding [[nodiscard]] to functions.

    This is a more comprehensive version of the existing nodiscard rule,
    with enhanced detection for factory functions, getters, and validation functions.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations/definitions
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
                self._check_enhanced_nodiscard(func_node, content, file_path)

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

    def _check_enhanced_nodiscard(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Enhanced check for nodiscard candidacy."""
        try:
            func_name = self._get_function_name(func_node, content)

            if not func_name or self._should_skip_function(func_name):
                return

            # Check if it's already marked with nodiscard
            if self._has_nodiscard(func_node, content):
                return

            # Check if it returns void
            if self._returns_void(func_node, content):
                return

            should_have_nodiscard = False
            reason = ""

            # Enhanced factory function detection
            if self._is_enhanced_factory_function(func_name):
                should_have_nodiscard = True
                reason = "Factory functions should not have their return value ignored"

            # Enhanced query/getter functions
            elif self._is_enhanced_query_function(func_name):
                should_have_nodiscard = True
                reason = "Query/getter functions should not have their return value ignored"

            # Validation and checking functions
            elif self._is_validation_function(func_name):
                should_have_nodiscard = True
                reason = "Validation functions should not have their return value ignored"

            # Functions returning important resources or handles
            elif self._returns_important_resource(func_node, content):
                should_have_nodiscard = True
                reason = "Functions returning important resources should not be ignored"

            # Mathematical or computational functions
            elif self._is_computational_function(func_name):
                should_have_nodiscard = True
                reason = "Computational functions should not have their return value ignored"

            if should_have_nodiscard:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Function '{func_name}' should be [[nodiscard]] - {reason}",
                    suggested_fix="Add [[nodiscard]] attribute before function declaration",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type in ["identifier", "field_identifier"]:
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""

    def _should_skip_function(self, func_name: str) -> bool:
        """Check if function should be skipped."""
        if func_name.startswith("~") or func_name.startswith("operator"):
            return True
        return False

    def _has_nodiscard(self, func_node: Any, content: str) -> bool:
        """Check if function already has [[nodiscard]]."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "[[nodiscard]]" in func_text or "nodiscard" in func_text
        except Exception:
            return False

    def _returns_void(self, func_node: Any, content: str) -> bool:
        """Check if function returns void."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return func_text.strip().startswith("void ")
        except Exception:
            return False

    def _is_enhanced_factory_function(self, func_name: str) -> bool:
        """Enhanced factory function detection."""
        factory_patterns = {
            "Create",
            "Make",
            "Build",
            "Construct",
            "New",
            "Generate",
            "Produce",
            "Allocate",
            "GetInstance",
            "GetSingleton",
            "Clone",
            "Copy",
            "Duplicate",
            "Spawn",
            "FromString",
            "FromJson",
            "FromConfig",
            "Parse",
            "Deserialize",
        }

        for pattern in factory_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _is_enhanced_query_function(self, func_name: str) -> bool:
        """Enhanced query/getter function detection."""
        query_patterns = {
            "Get",
            "Find",
            "Search",
            "Query",
            "Lookup",
            "Fetch",
            "Retrieve",
            "Extract",
            "Compute",
            "Calculate",
            "Count",
            "Size",
            "Length",
            "Is",
            "Has",
            "Can",
            "Should",
            "Check",
            "Contains",
            "Exists",
            "Empty",
            "Full",
            "Available",
            "Ready",
            "Active",
            "Enabled",
            "Valid",
            "Equal",
            "Compare",
        }

        for pattern in query_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _is_validation_function(self, func_name: str) -> bool:
        """Check if function is for validation."""
        validation_patterns = {
            "Validate",
            "Verify",
            "Test",
            "Ensure",
            "Assert",
            "Confirm",
            "Audit",
            "TryParse",
            "TryGet",
            "TrySet",
            "TryConnect",
            "TryLock",
            "TryAcquire",
        }

        for pattern in validation_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _returns_important_resource(self, func_node: Any, content: str) -> bool:
        """Check if function returns important resources."""
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Look for important resource types
            resource_indicators = {
                "std::unique_ptr",
                "std::shared_ptr",
                "std::weak_ptr",
                "Handle",
                "Socket",
                "Connection",
                "Stream",
                "Buffer",
                "Token",
                "Key",
                "Credential",
                "Result",
                "Status",
                "Optional",
                "Expected",
                "Future",
                "Promise",
            }

            for indicator in resource_indicators:
                if indicator in func_text:
                    return True
            return False
        except Exception:
            return False

    def _is_computational_function(self, func_name: str) -> bool:
        """Check if function performs computation."""
        computational_patterns = {
            "Calculate",
            "Compute",
            "Evaluate",
            "Process",
            "Transform",
            "Convert",
            "Encode",
            "Decode",
            "Compress",
            "Decompress",
            "Hash",
            "Checksum",
            "Sum",
            "Average",
            "Min",
            "Max",
            "Sort",
            "Filter",
            "Map",
            "Reduce",
            "Aggregate",
        }

        for pattern in computational_patterns:
            if func_name.startswith(pattern):
                return True

        # Also check for mathematical operations
        math_patterns = {"Add", "Subtract", "Multiply", "Divide", "Mod"}
        for pattern in math_patterns:
            if func_name.startswith(pattern):
                return True

        return False


class ModernSmartPtrByRefRule(ASTRule):
    """Rule to enforce passing smart pointers by value for ownership transfer.

    Detects function parameters that are smart pointers passed by reference
    and suggests passing them by value instead for clear ownership semantics.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all function declarations/definitions
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
                self._check_smart_ptr_parameters(func_node, content, file_path)

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

    def _check_smart_ptr_parameters(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check function parameters for smart pointers passed by reference."""
        try:
            # Find the parameter list
            param_list = self._find_parameter_list(func_node)
            if not param_list:
                return

            # Check each parameter
            for param in param_list.children:
                if param.type == "parameter_declaration":
                    self._check_parameter_for_smart_ptr(
                        param, content, file_path
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _find_parameter_list(self, func_node: Any) -> Any:
        """Find the parameter list node within a function."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "parameter_list":
                            return subchild
            return None
        except Exception:
            return None

    def _check_parameter_for_smart_ptr(
        self, param_node: Any, content: str, file_path: str
    ) -> None:
        """Check a single parameter for smart pointer by reference."""
        try:
            param_text = self.get_text_from_node(param_node, content)

            # Check if parameter is a smart pointer type
            if not self._is_smart_pointer_type(param_text):
                return

            # Check if it's passed by reference (which we want to flag)
            if not self._is_passed_by_reference(param_text):
                return  # Already by value, which is what we want

            # Check if it's a move parameter (T&&) - allow this
            if self._is_move_parameter(param_text):
                return

            # Get parameter name for better error message
            param_name = self._extract_parameter_name(param_node, content)

            line_num = param_node.start_point[0] + 1
            if self.should_skip_line(
                self.get_line(content, line_num), str(self.rule_id)
            ):
                return

            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=param_node.start_point[1] + 1,
                message=f"Smart pointer parameter '{param_name}' should be passed by value for clear ownership transfer semantics",
                suggested_fix="Remove 'const' and '&' to pass by value: 'std::unique_ptr<T> param' or 'std::shared_ptr<T> param'",
            )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_smart_pointer_type(self, param_text: str) -> bool:
        """Check if parameter text contains smart pointer types."""
        smart_ptr_types = {
            "std::unique_ptr",
            "std::shared_ptr",
            "std::weak_ptr",
            "unique_ptr",
            "shared_ptr",
            "weak_ptr",
        }

        for smart_ptr in smart_ptr_types:
            if smart_ptr in param_text:
                return True
        return False

    def _is_passed_by_reference(self, param_text: str) -> bool:
        """Check if parameter is already passed by reference."""
        # Look for & (reference) but not && (move)
        if "&" in param_text:
            # Check if it's a single & (reference) not && (move)
            if "&&" not in param_text:
                return True
        return False

    def _is_const_reference(self, param_text: str) -> bool:
        """Check if parameter is a const reference."""
        return (
            "const" in param_text
            and "&" in param_text
            and "&&" not in param_text
        )

    def _is_passed_by_value(self, param_text: str) -> bool:
        """Check if parameter is passed by value (no & or &&)."""
        return "&" not in param_text

    def _is_unique_ptr_type(self, param_text: str) -> bool:
        """Check if parameter is a unique_ptr type."""
        return "unique_ptr" in param_text

    def _is_shared_ptr_type(self, param_text: str) -> bool:
        """Check if parameter is a shared_ptr type."""
        return "shared_ptr" in param_text

    def _is_move_parameter(self, param_text: str) -> bool:
        """Check if parameter is a move parameter (T&&)."""
        return "&&" in param_text

    def _extract_parameter_name(self, param_node: Any, content: str) -> str:
        """Extract parameter name from parameter declaration."""
        try:
            # Find the last identifier in the parameter declaration
            identifiers = []

            def collect_identifiers(node):
                if node.type == "identifier":
                    identifiers.append(self.get_text_from_node(node, content))
                for child in node.children:
                    collect_identifiers(child)

            collect_identifiers(param_node)

            # Return the last identifier (parameter name)
            if identifiers:
                return identifiers[-1]
            return "unknown"
        except Exception:
            return "unknown"

