"""Rule ID enumeration for the C++ linter."""

from enum import Enum, auto


class RuleId(Enum):
    """Enumeration of all available linting rules.

    Each rule has a unique identifier and is associated with a specific
    rule implementation class. Rules are categorized by their primary focus.
    """

    # === Type System Rules (CRITICAL - must be fixed) ===
    TYPE_FORBIDDEN_INT = auto()  # Use std::int32_t instead of int
    TYPE_PAIR_TUPLE = (
        auto()
    )  # Detect std::pair/tuple usage and suggest alternatives

    # === Class Trait Rules (CRITICAL - architectural requirements) ===
    CLASS_TRAIT_MISSING = auto()  # Class must inherit trait (NonCopyable, etc.)

    # === Naming Convention Rules (WARNING - style requirements) ===
    NAMING_FUNCTION_CASE = auto()  # Functions should be CamelCase
    NAMING_FUNCTION_VERB = auto()  # Functions should start with verb
    NAMING_VARIABLE_CASE = auto()  # Variables should be snake_case
    NAMING_CLASS_CASE = auto()  # Classes should be CamelCase
    NAMING_CONSTANT_CASE = auto()  # Constants should be kCamelCase

    # === Enhanced Naming Convention Rules ===
    NAMING_ENUM_CASE = (
        auto()
    )  # Enum naming conventions (CamelCase for enum class, snake_case for C-style)
    NAMING_ENUM_VALUE_CASE = (
        auto()
    )  # Enum value naming conventions (CamelCase for enum class, UPPER_CASE for C-style)
    NAMING_STRUCT_CASE = auto()  # Struct naming conventions (CamelCase)
    NAMING_MEMBER_CASE = (
        auto()
    )  # Member variable naming (snake_case_ with trailing underscore)
    NAMING_HUNGARIAN_NOTATION = (
        auto()
    )  # Detect and forbid Hungarian notation (strName, intCount, etc.)

    # === Documentation Rules (WARNING - required for public APIs) ===
    DOC_FUNCTION_MISSING = auto()  # Public functions need documentation
    DOC_CLASS_MISSING = auto()  # Public classes need documentation
    DOC_PARAM_DIRECTION_MISSING = (
        auto()
    )  # Parameters need direction annotations

    # === Enhanced Documentation Rules (WARNING - comprehensive API docs) ===
    DOC_FUNCTION_MISSING_PARAM_DOCS = (
        auto()
    )  # Check @param documentation matches parameters
    DOC_FUNCTION_MISSING_RETURN_DOCS = (
        auto()
    )  # Check @return documentation for non-void functions
    DOC_FUNCTION_MISSING_THROWS_DOCS = (
        auto()
    )  # Check @throws documentation for functions that can throw
    DOC_FUNCTION_EXTRA_PARAM_DOCS = auto()  # Detect extra @param documentation
    DOC_FUNCTION_PARAM_DESC_QUALITY = (
        auto()
    )  # Check parameter description quality
    DOC_CLASS_DOCSTRING_BRIEF = (
        auto()
    )  # Require @brief tag in class documentation
    DOC_CLASS_DOCSTRING_THREAD_SAFETY = (
        auto()
    )  # Require thread safety docs for manager/engine classes

    # === Include Order Rules (WARNING - organization) ===
    INCLUDE_ORDER_WRONG = auto()  # Includes should be ordered correctly
    INCLUDE_ANGLE_BRACKET_FORBIDDEN = auto()  # Local includes should use quotes

    # === Modern C++ Rules (INFO - optional improvements) ===
    MODERN_MISSING_NOEXCEPT = auto()  # Consider adding noexcept
    MODERN_MISSING_CONST = auto()  # Consider making method const
    MODERN_NODISCARD_MISSING = auto()  #  [[nodiscard] checking
    MODERN_SMART_PTR_BY_REF = auto()  # Pass smart pointers by const reference

    # === Code Quality Rules (WARNING - maintainability) ===
    QUALITY_MAGIC_NUMBERS = auto()  # Avoid magic numbers, use named constants

    # === Logging Rules (WARNING - proper logging practices) ===
    LOGGING_FORBIDDEN_OUTPUT = (
        auto()
    )  # Forbid std::cout, std::cerr, printf, fprintf

    # === Safety Rules (ERROR - memory/type safety) ===
    SAFETY_UNSAFE_CAST = auto()  # Forbid reinterpret_cast and C-style casts
    SAFETY_RANGE_LOOP_MISSING = auto()  # Prefer range-based for loops
    SAFETY_RAW_POINTER_RETURN = auto()  # Forbid raw pointer return types
    SAFETY_RAW_POINTER_PARAM = auto()  # Forbid raw pointer parameters

    # === Class Organization Rules (WARNING - code structure) ===
    CLASS_ACCESS_SPECIFIER_ORDER = (
        auto()
    )  # Enforce public/protected/private order
    CLASS_MEMBER_ORGANIZATION = auto()  # Enforce member variable placement
    CLASS_MEMBER_ORDER = auto()  # Enhanced member order checking
    CLASS_TRAIT_STATIC = (
        auto()
    )  # Static class trait requirements for utility classes

    # === File Organization Rules (WARNING - file structure) ===
    FILE_HEADER_COPYRIGHT = auto()  # Require copyright headers
    FILE_READ_ERROR = auto()  # Handle file read errors gracefully
    FILE_NAMING_CONVENTION = (
        auto()
    )  # File naming conventions (CamelCase.h/.cpp)
    FILE_ORGANIZATION_HEADER = (
        auto()
    )  # Header files should be in csrc/include/ structure
    FILE_ORGANIZATION_TEST = (
        auto()
    )  # Test files should be in csrc/test/ structure

    # === Header Rules (WARNING - header file requirements) ===
    HEADER_PRAGMA_ONCE = auto()  # Detect missing #pragma once in headers
    HEADER_COPYRIGHT = auto()  # Enhanced copyright header checking

    # === Namespace Rules (WARNING - namespace organization) ===
    NAMESPACE_OLD_STYLE = (
        auto()
    )  # Detect old-style nested namespace declarations
    NAMESPACE_USING_FORBIDDEN = (
        auto()
    )  # Forbid "using namespace" in header files
    NAMESPACE_LONG_USAGE = (
        auto()
    )  # Detect repeated long namespace usage patterns

    def __str__(self) -> str:
        """Convert rule ID to string format (kebab-case)."""
        return self.name.lower().replace("_", "-")

    @property
    def category(self) -> str:
        """Get the category this rule belongs to."""
        name = self.name
        if name.startswith("TYPE_"):
            return "type-system"
        elif name.startswith("CLASS_TRAIT_"):
            return "class-traits"
        elif name.startswith("CLASS_"):
            return "class-organization"
        elif name.startswith("NAMING_"):
            return "naming"
        elif name.startswith("DOC_"):
            return "documentation"
        elif name.startswith("INCLUDE_"):
            return "includes"
        elif name.startswith("HEADER_"):
            return "headers"
        elif name.startswith("MODERN_"):
            return "modern-cpp"
        elif name.startswith("QUALITY_"):
            return "code-quality"
        elif name.startswith("LOGGING_"):
            return "logging"
        elif name.startswith("IMPORT_"):
            return "import-organization"
        elif name.startswith("FILE_"):
            return "file-organization"
        elif name.startswith("SAFETY_"):
            return "safety"
        elif name.startswith("NAMESPACE_"):
            return "namespace"
        else:
            return "misc"

    @property
    def default_severity(self):
        """Get the default severity for this rule."""
        # Import here to avoid circular imports
        try:
            from .rule_definition import get_rule_definition

            return get_rule_definition(self).severity
        except ImportError:
            # Fallback to old logic if rule_definition not available
            from ..core.severity import Severity

            name = self.name
            if name.startswith("TYPE_"):
                return Severity.ERROR
            elif name.startswith("CLASS_TRAIT_MISSING"):
                return Severity.ERROR
            elif name.startswith("CLASS_TRAIT_SUGGESTED"):
                return Severity.INFO
            elif name.startswith(
                (
                    "NAMING_",
                    "DOC_",
                    "INCLUDE_",
                    "QUALITY_",
                    "IMPORT_",
                    "NAMESPACE_",
                )
            ):
                return Severity.WARNING
            elif name.startswith("MODERN_"):
                return Severity.INFO
            else:
                return Severity.WARNING

    @property
    def is_mandatory(self) -> bool:
        """Check if this rule represents a mandatory fix vs optional suggestion."""
        # Import here to avoid circular imports
        from ..core.severity import Severity

        return self.default_severity in (Severity.ERROR, Severity.WARNING)

    @property
    def definition(self):
        """Get the complete rule definition."""
        try:
            from .rule_definition import get_rule_definition

            return get_rule_definition(self)
        except ImportError:
            return None
