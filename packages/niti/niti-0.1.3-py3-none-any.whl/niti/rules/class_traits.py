"""Class trait rules for enforcing proper class design patterns."""

from enum import Enum
from typing import Any, Dict, List

from ..core.issue import LintIssue
from .base import ASTRule


class ClassTrait(Enum):
    """Enumeration of class trait concepts.

    Every class should implement exactly one of these trait patterns
    to clearly express its copying and moving semantics.
    """

    NON_COPYABLE_NON_MOVABLE = (
        "NonCopyableNonMovable"  # Cannot be copied or moved
    )
    NON_COPYABLE = "NonCopyable"  # Can be moved but not copied
    NON_MOVABLE = "NonMovable"  # Can be copied but not moved
    COPYABLE_MOVABLE = (
        "CopyableMovable"  # Can be both copied and moved (default)
    )

    def __str__(self) -> str:
        return self.value


class ClassTraitMissingRule(ASTRule):
    """Rule to enforce that all classes inherit from appropriate trait base classes.

    This rule ensures architectural consistency by requiring that every class
    explicitly inherits from one of the trait base classes that define its
    copying/moving semantics.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Build inheritance graph by parsing all classes
        inheritance_graph = self._build_inheritance_graph(content, tree)

        # Check each class for trait inheritance
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            class_name = self._get_class_name(class_node, content)
            if not class_name or self._should_skip_class(
                class_name, class_node, content
            ):
                continue

            # Check if class has any trait in its inheritance chain
            if not self._class_has_trait_in_chain(
                class_name, inheritance_graph
            ):
                line_num = self.get_line_from_byte(
                    class_node.start_byte, content
                )
                suggested_trait = self._suggest_appropriate_trait(
                    class_node, content
                )

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
                            message=f"Class {class_name} must inherit from a trait base class to define its copying/moving semantics",
                            suggested_fix=f"class {class_name} : public {suggested_trait} {{",
                        )

        return self.issues

    def _build_inheritance_graph(
        self, content: str, tree: Any
    ) -> Dict[str, List[str]]:
        """Build complete inheritance graph by parsing all classes."""
        inheritance_graph = {}

        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            class_name = self._get_class_name(class_node, content)
            base_classes = []
            has_body = False

            # Extract base classes and check if it's a definition (not forward declaration)
            for child in class_node.children:
                if child.type == "base_class_clause":
                    base_classes = self._extract_base_classes(child, content)
                elif child.type == "field_declaration_list":
                    has_body = True

            # Only add classes with actual definitions
            if class_name and has_body:
                inheritance_graph[class_name] = base_classes

        return inheritance_graph

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract class name from class node."""
        for child in class_node.children:
            if child.type == "type_identifier":
                return self.get_text_from_node(child, content)
        return ""

    def _extract_base_classes(
        self, base_clause_node: Any, content: str
    ) -> List[str]:
        """Extract all base class names from base_class_clause."""
        base_classes = []

        for child in base_clause_node.children:
            if child.type in ["type_identifier", "qualified_identifier"]:
                base_class_name = self.get_text_from_node(child, content)
                # Clean up namespace qualifiers and template parameters
                base_class_name = base_class_name.split("::")[
                    -1
                ]  # Take last part after ::
                base_class_name = base_class_name.split("<")[
                    0
                ]  # Remove template params
                if base_class_name and base_class_name not in [
                    "public",
                    "private",
                    "protected",
                ]:
                    base_classes.append(base_class_name)

        return base_classes

    def _class_has_trait_in_chain(
        self, class_name: str, inheritance_graph: Dict[str, List[str]]
    ) -> bool:
        """Recursively check if class inherits from any trait base class."""
        visited = set()

        def check_inheritance_chain(current_class: str) -> bool:
            if current_class in visited:
                return False  # Avoid infinite loops
            visited.add(current_class)

            # Check if current class is a trait base class
            if current_class in [trait.value for trait in ClassTrait]:
                return True

            # Recursively check base classes
            base_classes = inheritance_graph.get(current_class, [])
            for base_class in base_classes:
                if check_inheritance_chain(base_class):
                    return True

            return False

        return check_inheritance_chain(class_name)

    def _should_skip_class(
        self, class_name: str, class_node: Any, content: str
    ) -> bool:
        """Check if this class should be skipped from trait checking."""
        # Skip forward declarations (classes without body definition)
        if self._is_forward_declaration(class_node):
            return True

        # Skip trait base classes themselves
        if class_name in [trait.value for trait in ClassTrait]:
            return True

        # Skip system types and POSIX types
        system_types = {
            "sockaddr",
            "sockaddr_in",
            "sockaddr_un",
            "in_addr",
            "hostent",
            "servent",
            "protoent",
            "stat",
            "dirent",
            "FILE",
            "DIR",
            "pthread_t",
            "pthread_mutex_t",
            "pthread_cond_t",
            "sigaction",
            "sigset_t",
            "timespec",
            "timeval",
            "fd_set",
            "pollfd",
            "epoll_event",
            "IsBoostQueue",
        }

        if class_name in system_types:
            return True

        # Skip POD structs (simple data containers)
        if self._is_pod_struct(class_node, content):
            return True

        # Skip template specializations and forward declarations
        if self._is_template_specialization(class_node, content):
            return True

        return False

    def _is_pod_struct(self, class_node: Any, content: str) -> bool:
        """Check if this is a simple POD struct that doesn't need traits."""
        # Look for class body
        for child in class_node.children:
            if child.type == "field_declaration_list":
                # Check if it only contains simple field declarations (no methods)
                has_methods = False
                for field_child in child.children:
                    if field_child.type == "field_declaration":
                        # Check if this field declaration is actually a method
                        field_text = self.get_text_from_node(
                            field_child, content
                        )
                        if "(" in field_text and ")" in field_text:
                            has_methods = True
                            break
                return not has_methods
        return False

    def _is_template_specialization(
        self, class_node: Any, content: str
    ) -> bool:
        """Check if this is a template specialization."""
        class_text = self.get_text_from_node(class_node, content)
        return "<" in class_text and ">" in class_text

    def _is_forward_declaration(self, class_node: Any) -> bool:
        """Check if class node is a forward declaration (no body definition)."""
        # Forward declarations don't have a field_declaration_list child
        for child in class_node.children:
            if child.type == "field_declaration_list":
                return False  # Has a body, so it's a definition
        return True  # No body found, so it's a forward declaration

    def _suggest_appropriate_trait(self, class_node: Any, content: str) -> str:
        """Suggest the most appropriate trait based on class analysis."""
        # For now, suggest NonCopyableNonMovable as the safest default
        # TODO: Add more sophisticated analysis based on class members
        return ClassTrait.NON_COPYABLE_NON_MOVABLE.value


class ClassTraitStaticRule(ASTRule):
    """Rule to enforce static class trait requirements for utility classes.

    Utility classes that contain only static methods should inherit from
    StaticClass trait to explicitly indicate their nature and prevent
    instantiation.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// niti-lint-disable {str(self.rule_id)}" in content:
            return self.issues

        # Find all class declarations
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            self._check_static_class_trait(class_node, content, file_path)

        return self.issues

    def _check_static_class_trait(
        self, class_node: Any, content: str, file_path: str
    ) -> None:
        """Check if a utility class should inherit from StaticClass."""
        try:
            class_name = self._get_class_name(class_node, content)
            if not class_name:
                return

            # Skip if already inherits from StaticClass
            if self._inherits_from_static_class(class_node, content):
                return

            # Analyze class members
            class_analysis = self._analyze_class_for_static_trait(
                class_node, content
            )

            if self._should_be_static_class(class_analysis, class_name):
                line_num = self.get_line_from_byte(
                    class_node.start_byte, content
                )

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
                            message=f"Utility class '{class_name}' with only static methods should inherit from StaticClass",
                            suggested_fix=f"class {class_name} : public StaticClass {{",
                        )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract class name from class node."""
        for child in class_node.children:
            if child.type == "type_identifier":
                return self.get_text_from_node(child, content)
        return ""

    def _inherits_from_static_class(
        self, class_node: Any, content: str
    ) -> bool:
        """Check if class already inherits from StaticClass."""
        for child in class_node.children:
            if child.type == "base_class_clause":
                base_classes_text = self.get_text_from_node(child, content)
                return "StaticClass" in base_classes_text
        return False

    def _analyze_class_for_static_trait(
        self, class_node: Any, content: str
    ) -> dict:
        """Analyze class to determine if it should be static."""
        analysis = {
            "static_methods": 0,
            "instance_methods": 0,
            "member_variables": 0,
            "constructors": 0,
            "destructors": 0,
            "has_public_constructor": False,
            "has_private_constructor": False,
        }

        current_access = (
            "public"  # Default for struct, or first section for class
        )

        for child in class_node.children:
            if child.type == "field_declaration_list":
                # Parse class body
                for member in child.children:
                    if member.type == "access_specifier":
                        access_text = (
                            self.get_text_from_node(member, content)
                            .strip()
                            .rstrip(":")
                        )
                        if access_text in ["public", "protected", "private"]:
                            current_access = access_text

                    elif member.type == "field_declaration":
                        # Check if this field_declaration is actually a function
                        if self._is_function_declaration(member, content):
                            self._analyze_method(
                                member, content, current_access, analysis
                            )
                        else:
                            analysis["member_variables"] += 1

                    elif member.type in [
                        "function_declaration",
                        "function_definition",
                    ]:
                        self._analyze_method(
                            member, content, current_access, analysis
                        )

        return analysis

    def _is_function_declaration(self, field_node: Any, content: str) -> bool:
        """Check if a field_declaration node is actually a function declaration."""
        # Check if it has a function_declarator child
        for child in field_node.children:
            if child.type == "function_declarator":
                return True

        # Alternative check: look for parentheses in the text (function signature)
        field_text = self.get_text_from_node(field_node, content)
        return "(" in field_text and ")" in field_text

    def _analyze_method(
        self, method_node: Any, content: str, access_level: str, analysis: dict
    ) -> None:
        """Analyze a method to categorize it."""
        method_text = self.get_text_from_node(method_node, content)
        method_name = self._extract_method_name(method_node, content)

        # Check if method is static
        if "static" in method_text:
            analysis["static_methods"] += 1
        else:
            analysis["instance_methods"] += 1

        # Check for constructors/destructors
        if method_name:
            if method_name.startswith("~"):
                analysis["destructors"] += 1
            elif method_name[
                0
            ].isupper():  # Likely constructor (same name as class)
                analysis["constructors"] += 1
                if access_level == "public":
                    analysis["has_public_constructor"] = True
                elif access_level == "private":
                    analysis["has_private_constructor"] = True

    def _extract_method_name(self, method_node: Any, content: str) -> str:
        """Extract method name from method node."""
        try:
            for child in method_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""

    def _should_be_static_class(self, analysis: dict, class_name: str) -> bool:
        """Determine if class should inherit from StaticClass based on analysis."""
        # Must have only static methods and no instance methods
        if analysis["instance_methods"] > 0:
            return False

        # Must have at least one static method
        if analysis["static_methods"] == 0:
            return False

        # Should not have member variables (except static const)
        if analysis["member_variables"] > 0:
            return False

        # Should not have public constructors (private constructor for prevention is OK)
        if analysis["has_public_constructor"]:
            return False

        # Class name should suggest it's a utility class
        utility_indicators = ["utils", "helper", "utility", "tools", "factory"]
        class_name_lower = class_name.lower()

        # Either the name suggests utility class OR it has the right pattern
        name_suggests_utility = any(
            indicator in class_name_lower for indicator in utility_indicators
        )
        pattern_suggests_utility = (
            analysis["static_methods"] >= 2
            and analysis["instance_methods"] == 0
            and analysis["member_variables"] == 0
        )

        return name_suggests_utility or pattern_suggests_utility
