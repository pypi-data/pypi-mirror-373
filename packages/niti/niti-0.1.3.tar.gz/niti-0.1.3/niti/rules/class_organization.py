"""Class organization rules for C++ code."""

from typing import Any, List

from ..core.issue import LintIssue
from .base import ASTRule


class ClassAccessSpecifierOrderRule(ASTRule):
    """Rule to enforce access specifier order in classes.

    Classes should organize members in order: public, protected, private.
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
            self._check_access_specifier_order(class_node, content)

        return self.issues

    def _check_access_specifier_order(
        self, class_node: Any, content: str
    ) -> None:
        """Check access specifier order in a class."""
        try:
            access_specifiers = self._find_access_specifiers(
                class_node, content
            )

            if len(access_specifiers) < 2:
                return  # Not enough specifiers to check order

            # Expected order: public, protected, private
            expected_order = ["public", "protected", "private"]

            violations = self._find_order_violations(
                access_specifiers, expected_order
            )

            for violation in violations:
                line_num, message = violation
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    continue

                issue = LintIssue(
                    rule_id=self.rule_id,
                    file_path=self.current_file,
                    line_number=line_num,
                    column=1,
                    message=message,
                    suggestion="Reorganize class members: public, then protected, then private",
                )
                self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _find_access_specifiers(
        self, class_node: Any, content: str
    ) -> List[tuple]:
        """Find all access specifiers in a class."""
        specifiers = []

        # Look for access_specifier nodes
        def find_specifiers(node):
            if node.type == "access_specifier":
                spec_text = (
                    self.get_text_from_node(node, content).strip().rstrip(":")
                )
                line_num = node.start_point[0] + 1
                specifiers.append((line_num, spec_text))

            for child in node.children:
                find_specifiers(child)

        find_specifiers(class_node)
        return specifiers

    def _find_order_violations(
        self, specifiers: List[tuple], expected_order: List[str]
    ) -> List[tuple]:
        """Find violations in access specifier order."""
        violations = []

        # Track the last seen position for each specifier type
        last_position = {}

        for line_num, spec_type in specifiers:
            if spec_type not in expected_order:
                continue

            current_pos = expected_order.index(spec_type)

            # Check if any later specifier appeared before
            for later_spec in expected_order[current_pos + 1 :]:
                if later_spec in last_position:
                    violations.append(
                        (
                            line_num,
                            f"'{spec_type}:' section should come before '{later_spec}:' section",
                        )
                    )
                    break

            last_position[spec_type] = current_pos

        return violations


class ClassMemberOrganizationRule(ASTRule):
    """Rule to enforce member organization in classes.

    Within each access level (public/protected/private):
    1. Type aliases and nested types first
    2. Constructors and destructors
    3. Public methods
    4. Member variables (with trailing underscore)

    Member variables should follow naming conventions.
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
            self._check_member_organization(class_node, content)

        return self.issues

    def _check_member_organization(self, class_node: Any, content: str) -> None:
        """Check member organization in a class."""
        try:
            # Get members grouped by access level
            members_by_access = self._get_members_by_access_level(
                class_node, content
            )

            # Check each access level separately
            for access_level, members in members_by_access.items():
                if len(members) < 2:
                    continue  # Not enough members to check order

                # Check member ordering within this access level
                ordering_violations = (
                    self._check_member_order_within_access_level(members)
                )
                for violation in ordering_violations:
                    line_num, message, suggestion = violation
                    if self.should_skip_line(
                        self.get_line(content, line_num), str(self.rule_id)
                    ):
                        continue

                    issue = LintIssue(
                        rule_id=self.rule_id,
                        file_path=self.current_file,
                        line_number=line_num,
                        column=1,
                        message=message,
                        suggestion=suggestion,
                    )
                    self.issues.append(issue)

                # Check member variable naming (should end with _)
                for member in members:
                    line_num, member_name, member_type, _ = member

                    if member_type == "variable" and not member_name.endswith(
                        "_"
                    ):
                        if self.should_skip_line(
                            self.get_line(content, line_num), str(self.rule_id)
                        ):
                            continue

                        issue = LintIssue(
                            rule_id=self.rule_id,
                            file_path=self.current_file,
                            line_number=line_num,
                            column=1,
                            message=f"Member variable '{member_name}' should end with underscore",
                            suggestion=f"Rename to '{member_name}_'",
                        )
                        self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _find_class_members(self, class_node: Any, content: str) -> List[tuple]:
        """Find all class members (variables and functions)."""
        members = []

        def find_members(node):
            if node.type == "field_declaration":
                # Member variable
                for child in node.children:
                    if child.type == "field_declarator":
                        for subchild in child.children:
                            if subchild.type == "identifier":
                                name = self.get_text_from_node(
                                    subchild, content
                                )
                                line_num = subchild.start_point[0] + 1
                                members.append((line_num, name, "variable"))

            elif node.type in ["function_declaration", "function_definition"]:
                # Member function
                func_name = self._get_function_name(node, content)
                if func_name:
                    line_num = node.start_point[0] + 1
                    members.append((line_num, func_name, "function"))

            for child in node.children:
                find_members(child)

        find_members(class_node)
        return members

    def _get_members_by_access_level(
        self, class_node: Any, content: str
    ) -> dict:
        """Get class members grouped by access level."""
        members_by_access = {"public": [], "protected": [], "private": []}

        current_access = (
            "public"  # Default for structs, or explicit for classes
        )

        # Walk through class body in order
        for child in class_node.children:
            if child.type == "access_specifier":
                access_text = (
                    self.get_text_from_node(child, content).strip().rstrip(":")
                )
                if access_text in ["public", "protected", "private"]:
                    current_access = access_text

            elif child.type == "field_declaration":
                # Member variable
                var_info = self._extract_variable_info(child, content)
                if var_info:
                    line_num, name, member_type = var_info
                    members_by_access[current_access].append(
                        (line_num, name, member_type, "variable")
                    )

            elif child.type in ["function_declaration", "function_definition"]:
                # Member function
                func_info = self._extract_function_info(child, content)
                if func_info:
                    line_num, name, func_type = func_info
                    members_by_access[current_access].append(
                        (line_num, name, func_type, "function")
                    )

            elif child.type in ["type_definition", "alias_declaration"]:
                # Type aliases and nested types
                line_num = child.start_point[0] + 1
                name = "type_alias"
                members_by_access[current_access].append(
                    (line_num, name, "type", "type")
                )

        return members_by_access

    def _extract_variable_info(self, field_node: Any, content: str) -> tuple:
        """Extract variable info from field declaration."""
        try:
            for child in field_node.children:
                if child.type == "field_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            name = self.get_text_from_node(subchild, content)
                            line_num = subchild.start_point[0] + 1
                            return (line_num, name, "variable")
            return None
        except Exception:
            return None

    def _extract_function_info(self, func_node: Any, content: str) -> tuple:
        """Extract function info from function declaration/definition."""
        try:
            func_name = self._get_function_name(func_node, content)
            if func_name:
                line_num = func_node.start_point[0] + 1

                # Classify function type
                if func_name.startswith("~"):
                    func_type = "destructor"
                elif func_name[0].isupper():  # Constructor (same name as class)
                    func_type = "constructor"
                else:
                    func_type = "method"

                return (line_num, func_name, func_type)
            return None
        except Exception:
            return None

    def _check_member_order_within_access_level(
        self, members: List[tuple]
    ) -> List[tuple]:
        """Check ordering of members within an access level."""
        violations = []

        # Expected order: types, constructors, destructors, methods, variables
        order_priority = {
            "type": 0,
            "constructor": 1,
            "destructor": 2,
            "method": 3,
            "variable": 4,
        }

        last_priority = -1

        for line_num, name, member_type, category in members:
            current_priority = order_priority.get(member_type, 999)

            if current_priority < last_priority:
                # Found something out of order
                expected_before = [
                    k for k, v in order_priority.items() if v == last_priority
                ][0]
                violations.append(
                    (
                        line_num,
                        f"{member_type.title()} '{name}' should come before {expected_before}s in class organization",
                        f"Move {member_type}s before {expected_before}s within this access level",
                    )
                )

            last_priority = max(last_priority, current_priority)

        return violations

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""


class ClassMemberOrderRule(ASTRule):
    """Enhanced member order checking within classes.

    This rule provides more detailed member ordering analysis with better
    type categorization than the basic member organization rule.
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
            self._check_enhanced_member_order(class_node, content)

        return self.issues

    def _check_enhanced_member_order(
        self, class_node: Any, content: str
    ) -> None:
        """Enhanced member order checking with detailed categorization."""
        try:
            sections = self._get_detailed_class_sections(class_node, content)

            for section in sections:
                if len(section["members"]) < 2:
                    continue

                violations = self._check_detailed_member_order(
                    section["members"]
                )
                for violation in violations:
                    line_num, message, suggestion = violation

                    issue = LintIssue(
                        rule_id=self.rule_id,
                        file_path=self.current_file,
                        line_number=line_num,
                        column=1,
                        message=message,
                        suggestion=suggestion,
                    )
                    self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _get_detailed_class_sections(
        self, class_node: Any, content: str
    ) -> List[dict]:
        """Get class sections with detailed member categorization."""
        sections = []
        current_section = {"access": "public", "members": []}

        for child in class_node.children:
            if child.type == "access_specifier":
                if current_section["members"]:
                    sections.append(current_section)

                access_text = (
                    self.get_text_from_node(child, content).strip().rstrip(":")
                )
                current_section = {"access": access_text, "members": []}

            else:
                member_info = self._categorize_member_detailed(child, content)
                if member_info:
                    current_section["members"].append(member_info)

        if current_section["members"]:
            sections.append(current_section)

        return sections

    def _categorize_member_detailed(self, node: Any, content: str) -> dict:
        """Categorize member with detailed type information."""
        if node.type in ["type_definition", "alias_declaration"]:
            return {
                "line": node.start_point[0] + 1,
                "name": "type_alias",
                "category": "type",
                "subcategory": "alias",
                "priority": 0,
            }
        elif node.type == "field_declaration":
            var_info = self._extract_detailed_variable_info(node, content)
            if var_info:
                return {
                    "line": var_info[0],
                    "name": var_info[1],
                    "category": "variable",
                    "subcategory": self._classify_variable_type(var_info[1]),
                    "priority": 4,
                }
        elif node.type in ["function_declaration", "function_definition"]:
            func_info = self._extract_detailed_function_info(node, content)
            if func_info:
                return {
                    "line": func_info[0],
                    "name": func_info[1],
                    "category": "function",
                    "subcategory": func_info[2],
                    "priority": self._get_function_priority(func_info[2]),
                }
        return None

    def _classify_variable_type(self, var_name: str) -> str:
        """Classify variable by type."""
        if var_name.startswith("k") and var_name[1].isupper():
            return "constant"
        elif var_name.endswith("_"):
            return "private_member"
        else:
            return "public_member"

    def _get_function_priority(self, func_type: str) -> int:
        """Get priority order for function types."""
        priority_map = {"constructor": 1, "destructor": 2, "method": 3}
        return priority_map.get(func_type, 3)

    def _check_detailed_member_order(self, members: List[dict]) -> List[tuple]:
        """Check detailed member ordering within a section."""
        violations = []
        last_priority = -1

        for member in members:
            current_priority = member["priority"]

            if current_priority < last_priority:
                expected_before = self._get_category_name(last_priority)
                current_category = self._get_category_name(current_priority)

                violations.append(
                    (
                        member["line"],
                        f"{current_category} '{member['name']}' should come before {expected_before}s",
                        f"Move {current_category}s before {expected_before}s within this access level",
                    )
                )

            last_priority = max(last_priority, current_priority)

        return violations

    def _get_category_name(self, priority: int) -> str:
        """Get category name from priority."""
        category_map = {
            0: "type",
            1: "constructor",
            2: "destructor",
            3: "method",
            4: "variable",
        }
        return category_map.get(priority, "member")

    def _extract_detailed_variable_info(
        self, field_node: Any, content: str
    ) -> tuple:
        """Extract detailed variable information."""
        try:
            for child in field_node.children:
                if child.type == "field_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            name = self.get_text_from_node(subchild, content)
                            line_num = subchild.start_point[0] + 1
                            return (line_num, name, "variable")
            return None
        except Exception:
            return None

    def _extract_detailed_function_info(
        self, func_node: Any, content: str
    ) -> tuple:
        """Extract detailed function information."""
        try:
            func_name = self._get_function_name(func_node, content)
            if func_name:
                line_num = func_node.start_point[0] + 1

                if func_name.startswith("~"):
                    func_type = "destructor"
                elif func_name[0].isupper():
                    func_type = "constructor"
                else:
                    func_type = "method"

                return (line_num, func_name, func_type)
            return None
        except Exception:
            return None

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""
