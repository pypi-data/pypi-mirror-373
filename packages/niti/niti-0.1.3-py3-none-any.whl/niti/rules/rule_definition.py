"""Rule definition system with comprehensive metadata."""

from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..core.severity import Severity
from .rule_id import RuleId


@dataclass
class RuleDefinition:
    """Complete definition of a linting rule with all metadata."""

    rule_id: RuleId
    name: str
    description: str
    severity: Severity
    category: str

    # Rule behavior
    enabled_by_default: bool = True
    conflicts_with_pch: bool = False
    requires_ast: bool = True

    # Style guide references
    style_guide_section: Optional[str] = None
    rationale: Optional[str] = None

    # Examples
    good_examples: List[str] = field(default_factory=list)
    bad_examples: List[str] = field(default_factory=list)

    # Technical details
    performance_impact: str = "low"  # low, medium, high
    false_positive_risk: str = "low"  # low, medium, high
    auto_fixable: bool = False

    # Dependencies
    depends_on_rules: Set[RuleId] = field(default_factory=set)
    conflicts_with_rules: Set[RuleId] = field(default_factory=set)

    @property
    def is_mandatory(self) -> bool:
        """Check if this rule is mandatory (ERROR/WARNING) vs optional (INFO)."""
        return self.severity in (Severity.ERROR, Severity.ERROR)

    def should_be_enabled_for_project(
        self, project_phase: str = "mature"
    ) -> bool:
        """Determine if rule should be enabled based on project phase."""
        if project_phase == "legacy":
            # Only critical rules for legacy codebases
            return self.severity == Severity.ERROR
        elif project_phase == "migration":
            # Error and high-priority warnings
            return (
                self.severity in (Severity.ERROR, Severity.ERROR)
                and self.false_positive_risk == "low"
            )
        else:  # mature
            # All mandatory rules
            return self.is_mandatory


# Comprehensive rule definitions
RULE_DEFINITIONS = {
    # === Type System Rules (CRITICAL) ===
    RuleId.TYPE_FORBIDDEN_INT: RuleDefinition(
        rule_id=RuleId.TYPE_FORBIDDEN_INT,
        name="Forbidden Integer Types",
        description="Require fixed-width integer types (std::int32_t) instead of 'int'",
        severity=Severity.ERROR,
        category="type-system",
        style_guide_section="§3.2 - Integer Types",
        rationale="Platform independence and explicit size requirements",
        requires_ast=False,
        auto_fixable=True,
        good_examples=[
            "std::int32_t count = 0;",
            "std::uint64_t size = buffer.size();",
        ],
        bad_examples=["int count = 0;", "unsigned int flags = 0;"],
    ),
    # === Class Trait Rules (ARCHITECTURAL) ===
    RuleId.CLASS_TRAIT_MISSING: RuleDefinition(
        rule_id=RuleId.CLASS_TRAIT_MISSING,
        name="Missing Class Traits",
        description="Classes must inherit from appropriate trait base classes",
        severity=Severity.ERROR,
        category="class-traits",
        style_guide_section="§4.1 - Class Design",
        rationale="Explicit copy/move semantics and architectural consistency",
        good_examples=[
            "class Manager : public NonCopyable { };",
            "class Value : public CopyableMovable { };",
        ],
        bad_examples=["class Manager { };  // Missing trait inheritance"],
    ),
    # === Naming Convention Rules ===
    RuleId.NAMING_FUNCTION_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_FUNCTION_CASE,
        name="Function Naming Case",
        description="Functions should use CamelCase naming",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.1 - Naming Conventions",
        rationale="Consistent API style across the codebase",
        auto_fixable=True,
        good_examples=["void ProcessData();", "bool IsValid() const;"],
        bad_examples=["void process_data();", "bool isValid() const;"],
    ),
    RuleId.NAMING_CLASS_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_CLASS_CASE,
        name="Class Naming Case",
        description="Classes should use CamelCase naming",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.1 - Naming Conventions",
        rationale="Consistent type naming across the codebase",
        auto_fixable=True,
        good_examples=["class SequenceManager;", "struct DataBuffer;"],
        bad_examples=["class sequence_manager;", "struct data_buffer;"],
    ),
    RuleId.NAMING_VARIABLE_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_VARIABLE_CASE,
        name="Variable Naming Case",
        description="Variables should use snake_case naming",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.1 - Naming Conventions",
        rationale="Distinguish variables from types and functions",
        auto_fixable=True,
        good_examples=[
            "std::int32_t buffer_size = 1024;",
            "const std::string& file_name = GetFileName();",
        ],
        bad_examples=[
            "std::int32_t bufferSize = 1024;",
            "const std::string& fileName = GetFileName();",
        ],
    ),
    RuleId.NAMING_CONSTANT_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_CONSTANT_CASE,
        name="Constant Naming Case",
        description="Constants should use kCamelCase naming",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.1 - Naming Conventions",
        rationale="Distinguish constants from variables",
        auto_fixable=True,
        good_examples=[
            "const std::int32_t kDefaultBufferSize = 1024;",
            "constexpr std::int32_t kMaxRetries = 3;",
        ],
        bad_examples=[
            "const std::int32_t DEFAULT_BUFFER_SIZE = 1024;",
            "constexpr std::int32_t max_retries = 3;",
        ],
    ),
    # === Code Quality Rules ===
    RuleId.QUALITY_MAGIC_NUMBERS: RuleDefinition(
        rule_id=RuleId.QUALITY_MAGIC_NUMBERS,
        name="Magic Numbers Detection",
        description="Replace magic numbers with named constants",
        severity=Severity.ERROR,
        category="code-quality",
        enabled_by_default=False,  # Can be noisy
        style_guide_section="§6.2 - Code Clarity",
        rationale="Improve code readability and maintainability",
        false_positive_risk="medium",
        good_examples=[
            "const std::int32_t kBufferSize = 1024;",
            "for (std::int32_t i = 0; i < kMaxIterations; ++i)",
        ],
        bad_examples=[
            "std::vector<int> buffer(1024);  // Magic number",
            "if (retries > 5) break;  // Magic number",
        ],
    ),
    # === Safety Rules (CRITICAL) ===
    RuleId.SAFETY_UNSAFE_CAST: RuleDefinition(
        rule_id=RuleId.SAFETY_UNSAFE_CAST,
        name="Unsafe Cast Detection",
        description="Forbid dangerous casting operations that can cause undefined behavior",
        severity=Severity.ERROR,
        category="safety",
        style_guide_section="§8.1 - Type Safety",
        rationale="Prevent memory corruption, type confusion, and undefined behavior",
        good_examples=[
            "static_cast<std::int32_t>(value);",
            "dynamic_cast<Derived*>(base_ptr);",
            "auto* derived = dynamic_cast<Derived*>(base);",
        ],
        bad_examples=[
            "reinterpret_cast<std::int32_t*>(&value);  // Dangerous type punning",
            "(std::int32_t*)ptr;  // C-style cast, no safety checks",
            "const_cast<std::int32_t*>(const_ptr);  // Violates const correctness",
        ],
    ),
    RuleId.SAFETY_RANGE_LOOP_MISSING: RuleDefinition(
        rule_id=RuleId.SAFETY_RANGE_LOOP_MISSING,
        name="Range-Based Loop Preference",
        description="Prefer range-based for loops over traditional index-based loops",
        severity=Severity.ERROR,
        category="safety",
        style_guide_section="§8.2 - Iterator Safety",
        rationale="Prevent buffer overruns, off-by-one errors, and improve readability",
        good_examples=[
            "for (const auto& item : container) { process(item); }",
            "for (auto& item : container) { modify(item); }",
            "for (std::size_t i : std::views::iota(0u, count)) { ... }",
        ],
        bad_examples=[
            "for (std::size_t i = 0; i < container.size(); ++i) { process(container[i]); }",
            "for (auto it = container.begin(); it != container.end(); ++it) { process(*it); }",
        ],
    ),
    # === Modern C++ Rules (Optional) ===
    RuleId.MODERN_MISSING_NOEXCEPT: RuleDefinition(
        rule_id=RuleId.MODERN_MISSING_NOEXCEPT,
        name="Missing noexcept",
        description="Consider adding noexcept to non-throwing functions",
        severity=Severity.ERROR,
        category="modern-cpp",
        enabled_by_default=True,
        style_guide_section="§7.1 - Exception Safety",
        rationale="Performance optimization and exception safety documentation",
        false_positive_risk="medium",
        performance_impact="medium",
    ),
    RuleId.MODERN_MISSING_CONST: RuleDefinition(
        rule_id=RuleId.MODERN_MISSING_CONST,
        name="Missing const",
        description="Consider making methods const when possible",
        severity=Severity.ERROR,
        category="modern-cpp",
        enabled_by_default=False,
        style_guide_section="§7.2 - Const Correctness",
        rationale="Interface clarity and optimization opportunities",
        false_positive_risk="high",
    ),
    # === Documentation Rules ===
    RuleId.DOC_PARAM_DIRECTION_MISSING: RuleDefinition(
        rule_id=RuleId.DOC_PARAM_DIRECTION_MISSING,
        name="Parameter Direction Annotations",
        description="Parameters must have direction annotations (/*[in]*/, /*[out]*/, /*[inout]*/)",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.1 - Parameter Documentation",
        rationale="Clear parameter intent prevents misuse and aids understanding",
        good_examples=[
            "void ProcessData(const std::string& input /*[in]*/, std::vector<int>& results /*[out]*/);"
        ],
        bad_examples=[
            "void ProcessData(const std::string& input, std::vector<int>& results);"
        ],
    ),
    RuleId.DOC_FUNCTION_MISSING: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_MISSING,
        name="Function Documentation",
        description="Public functions must have Doxygen documentation",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.2 - Function Documentation",
        rationale="API documentation is essential for maintainability",
        good_examples=[
            "/** @brief Process the input data. */\nvoid ProcessData();"
        ],
        bad_examples=["void ProcessData();  // No documentation"],
    ),
    RuleId.DOC_CLASS_MISSING: RuleDefinition(
        rule_id=RuleId.DOC_CLASS_MISSING,
        name="Class Documentation",
        description="Classes must have Doxygen documentation",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.3 - Class Documentation",
        rationale="Class purpose and usage should be documented",
        good_examples=[
            "/** @brief Manages data processing operations. */\nclass DataProcessor;"
        ],
        bad_examples=["class DataProcessor;  // No documentation"],
    ),
    # === Enhanced Documentation Rules ===
    RuleId.DOC_FUNCTION_MISSING_PARAM_DOCS: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_MISSING_PARAM_DOCS,
        name="Function Parameter Documentation",
        description="Functions must document all parameters with @param tags",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.6 - Parameter Documentation",
        rationale="Each parameter's purpose and constraints should be documented for clear API usage",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "/**\n * @brief Process data.\n * @param input The input data to process\n * @param output The processed results\n */\nvoid ProcessData(const std::string& input, std::vector<int>& output);",
            "/**\n * @brief Calculate sum.\n * @param values Array of values to sum\n * @param count Number of values in array\n * @return Sum of all values\n */\nstd::int32_t Sum(const std::int32_t* values, std::size_t count);",
        ],
        bad_examples=[
            "/** @brief Process data. */\nvoid ProcessData(const std::string& input, std::vector<int>& output);  // Missing @param docs",
            "/**\n * @brief Calculate sum.\n * @param values Array of values\n */\nstd::int32_t Sum(const std::int32_t* values, std::size_t count);  // Missing @param count",
        ],
    ),
    RuleId.DOC_FUNCTION_MISSING_RETURN_DOCS: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_MISSING_RETURN_DOCS,
        name="Function Return Documentation",
        description="Non-void functions must document return values with @return tag",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.7 - Return Value Documentation",
        rationale="Return value meaning and constraints should be documented for clear API usage",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "/**\n * @brief Get buffer size.\n * @return Current buffer size in bytes\n */\nstd::size_t GetBufferSize() const;",
            "/**\n * @brief Validate input.\n * @param input Data to validate\n * @return true if valid, false otherwise\n */\nbool Validate(const std::string& input);",
        ],
        bad_examples=[
            "/** @brief Get buffer size. */\nstd::size_t GetBufferSize() const;  // Missing @return",
            "/** @brief Validate input. */\nbool Validate(const std::string& input);  // Missing @return",
        ],
    ),
    RuleId.DOC_FUNCTION_MISSING_THROWS_DOCS: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_MISSING_THROWS_DOCS,
        name="Function Exception Documentation",
        description="Functions that can throw exceptions must document them with @throws tag",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.8 - Exception Documentation",
        rationale="Exception types and conditions should be documented for proper error handling",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="high",  # Heuristic detection of throwing functions
        good_examples=[
            "/**\n * @brief Open file.\n * @param path File path to open\n * @throws std::runtime_error If file cannot be opened\n */\nvoid OpenFile(const std::string& path);",
            "/**\n * @brief Allocate buffer.\n * @param size Buffer size in bytes\n * @throws std::bad_alloc If allocation fails\n */\nvoid* AllocateBuffer(std::size_t size);",
        ],
        bad_examples=[
            "/** @brief Open file. */\nvoid OpenFile(const std::string& path);  // Can throw but no @throws",
            "/** @brief Allocate buffer. */\nvoid* AllocateBuffer(std::size_t size);  // Uses 'new' but no @throws",
        ],
    ),
    RuleId.DOC_FUNCTION_EXTRA_PARAM_DOCS: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_EXTRA_PARAM_DOCS,
        name="Extra Parameter Documentation",
        description="Functions should not have @param documentation for non-existent parameters",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.9 - Documentation Accuracy",
        rationale="Documentation should match actual function signature to avoid confusion",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "/**\n * @brief Process data.\n * @param input The input data\n */\nvoid ProcessData(const std::string& input);",
        ],
        bad_examples=[
            "/**\n * @brief Process data.\n * @param input The input data\n * @param output The results  // Parameter doesn't exist!\n */\nvoid ProcessData(const std::string& input);",
            "/**\n * @param old_param Outdated parameter  // Function signature changed\n */\nvoid ProcessData(const std::string& new_param);",
        ],
    ),
    RuleId.DOC_FUNCTION_PARAM_DESC_QUALITY: RuleDefinition(
        rule_id=RuleId.DOC_FUNCTION_PARAM_DESC_QUALITY,
        name="Parameter Description Quality",
        description="Parameter descriptions should be meaningful, not generic placeholders",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.10 - Documentation Quality",
        rationale="High-quality parameter descriptions help developers understand API usage and constraints",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "/**\n * @param buffer_size Maximum number of bytes to allocate for the buffer\n * @param timeout_ms Maximum time to wait for operation completion in milliseconds\n */",
            "/**\n * @param file_path Absolute path to the configuration file to load\n * @param encoding Character encoding to use when reading the file (default: UTF-8)\n */",
        ],
        bad_examples=[
            "/**\n * @param buffer_size the buffer_size  // Just repeats parameter name\n * @param timeout_ms a parameter  // Generic description\n */",
            "/**\n * @param file_path input  // Too vague\n * @param encoding data  // Meaningless description\n */",
        ],
    ),
    RuleId.DOC_CLASS_DOCSTRING_BRIEF: RuleDefinition(
        rule_id=RuleId.DOC_CLASS_DOCSTRING_BRIEF,
        name="Class Documentation Brief Tag",
        description="Class documentation must include @brief tag for clear summaries",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.11 - Class Brief Documentation",
        rationale="@brief tags provide concise summaries that improve API documentation readability",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "/**\n * @brief Manages sequence processing operations.\n * \n * Detailed description of the class purpose and usage.\n */\nclass SequenceManager;",
            "/**\n * @brief Thread-safe cache for storing computation results.\n */\nclass ResultCache;",
        ],
        bad_examples=[
            "/**\n * Manages sequence processing operations.  // Missing @brief\n */\nclass SequenceManager;",
            "/**\n * This class does sequence stuff.  // No @brief tag\n */\nclass SequenceManager;",
        ],
    ),
    RuleId.DOC_CLASS_DOCSTRING_THREAD_SAFETY: RuleDefinition(
        rule_id=RuleId.DOC_CLASS_DOCSTRING_THREAD_SAFETY,
        name="Manager/Engine Thread Safety Documentation",
        description="Manager and Engine classes must document thread safety characteristics",
        severity=Severity.ERROR,
        category="documentation",
        style_guide_section="§4.12 - Thread Safety Documentation",
        rationale="Thread safety is critical for manager and engine classes that may be used concurrently",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "/**\n * @brief Manages worker thread pool.\n * @note Thread-safe: All methods can be called concurrently.\n */\nclass WorkerManager;",
            "/**\n * @brief Processes inference requests.\n * @warning Not thread-safe: External synchronization required.\n */\nclass InferenceEngine;",
            "/**\n * @brief Caches model weights.\n * @note Thread-safe for read operations, write operations require external locking.\n */\nclass ModelCache;",
        ],
        bad_examples=[
            "/**\n * @brief Manages worker threads.  // No thread safety info\n */\nclass WorkerManager;",
            "/**\n * @brief Processes requests.  // Missing thread safety documentation\n */\nclass InferenceEngine;",
        ],
    ),
    # === Class Organization Rules ===
    RuleId.CLASS_ACCESS_SPECIFIER_ORDER: RuleDefinition(
        rule_id=RuleId.CLASS_ACCESS_SPECIFIER_ORDER,
        name="Access Specifier Order",
        description="Class sections should be ordered: public, protected, private",
        severity=Severity.ERROR,
        category="class-organization",
        style_guide_section="§5.1 - Class Organization",
        rationale="Consistent organization improves readability",
        good_examples=[
            "class Example {\npublic:\n  void PublicMethod();\nprotected:\n  void ProtectedMethod();\nprivate:\n  void PrivateMethod();\n};"
        ],
        bad_examples=[
            "class Example {\nprivate:\n  void PrivateMethod();\npublic:\n  void PublicMethod();\n};"
        ],
    ),
    RuleId.CLASS_MEMBER_ORGANIZATION: RuleDefinition(
        rule_id=RuleId.CLASS_MEMBER_ORGANIZATION,
        name="Member Organization",
        description="Members should be ordered: types, constructors, methods, variables (with trailing _)",
        severity=Severity.ERROR,
        category="class-organization",
        style_guide_section="§5.2 - Member Organization",
        rationale="Consistent member organization and naming improves code navigation",
        good_examples=[
            "class Example {\npublic:\n  Example();\n  void Method();\nprivate:\n  std::int32_t member_;\n};"
        ],
        bad_examples=[
            "class Example {\npublic:\n  std::int32_t member;  // No trailing underscore\n  Example();  // Constructor after variable\n};"
        ],
    ),
    # === Function Naming Rules ===
    RuleId.NAMING_FUNCTION_VERB: RuleDefinition(
        rule_id=RuleId.NAMING_FUNCTION_VERB,
        name="Function Verb Naming",
        description="Functions should start with action verbs",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§3.2 - Function Naming",
        rationale="Verb-based names clearly indicate function purpose",
        good_examples=[
            "void ProcessData();",
            "std::int32_t GetSize();",
            "bool IsValid();",
        ],
        bad_examples=["void data();", "std::int32_t size();", "bool valid();"],
    ),
    # === Include Rules ===
    RuleId.INCLUDE_ORDER_WRONG: RuleDefinition(
        rule_id=RuleId.INCLUDE_ORDER_WRONG,
        name="Include Order",
        description="Includes should be ordered: C std, C++ std, third-party, project",
        severity=Severity.ERROR,
        category="includes",
        style_guide_section="§2.1 - Include Organization",
        rationale="Consistent include order improves maintainability",
        auto_fixable=True,
    ),
    RuleId.INCLUDE_ANGLE_BRACKET_FORBIDDEN: RuleDefinition(
        rule_id=RuleId.INCLUDE_ANGLE_BRACKET_FORBIDDEN,
        name="Local Include Style",
        description="Local project files should use quotes, not angle brackets",
        severity=Severity.ERROR,
        category="includes",
        style_guide_section="§2.1 - Include Style",
        rationale="Distinguish between system and project headers",
        auto_fixable=True,
        good_examples=[
            '#include "project/header.h"',
            "#include <system/header.h>",
        ],
        bad_examples=["#include <project/header.h>  // Should use quotes"],
    ),
    # === File Organization Rules ===
    RuleId.FILE_HEADER_COPYRIGHT: RuleDefinition(
        rule_id=RuleId.FILE_HEADER_COPYRIGHT,
        name="Copyright Header",
        description="Source files should have copyright headers",
        severity=Severity.ERROR,
        category="file-organization",
        style_guide_section="§1.1 - File Headers",
        rationale="Legal compliance and code ownership clarity",
        enabled_by_default=False,  # Project-specific
    ),
    # === Enhanced Naming Convention Rules ===
    RuleId.NAMING_ENUM_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_ENUM_CASE,
        name="Enum Naming Case",
        description="Enforce naming conventions for enums (CamelCase for enum class, snake_case for C-style)",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.2 - Enum Naming",
        rationale="Different enum styles should follow different naming conventions for clarity",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "enum class SequenceStatus { Waiting, Running };",
            "enum sequence_status { WAITING, RUNNING };",
        ],
        bad_examples=[
            "enum class sequence_status { Waiting, Running };  // Should be CamelCase",
            "enum SequenceStatus { WAITING, RUNNING };  // Should be snake_case",
        ],
    ),
    RuleId.NAMING_ENUM_VALUE_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_ENUM_VALUE_CASE,
        name="Enum Value Naming Case",
        description="Enforce naming conventions for enum values (CamelCase for enum class, UPPER_CASE for C-style)",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.2 - Enum Value Naming",
        rationale="Enum values should follow consistent naming based on enum type",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "enum class SequenceStatus { Waiting, Running, Completed };",
            "enum sequence_status { WAITING, RUNNING, COMPLETED };",
        ],
        bad_examples=[
            "enum class SequenceStatus { waiting, running };  // Should be CamelCase",
            "enum sequence_status { Waiting, Running };  // Should be UPPER_CASE",
        ],
    ),
    RuleId.NAMING_STRUCT_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_STRUCT_CASE,
        name="Struct Naming Case",
        description="Structs should use CamelCase naming",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.1 - Type Naming",
        rationale="Consistent with class naming conventions",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "struct SequenceConfig { std::int32_t max_length; };",
            "struct Point { std::int32_t x, y; };",
        ],
        bad_examples=[
            "struct sequence_config { std::int32_t max_length; };  // Should be CamelCase",
            "struct point { std::int32_t x, y; };  // Should be CamelCase",
        ],
    ),
    RuleId.NAMING_MEMBER_CASE: RuleDefinition(
        rule_id=RuleId.NAMING_MEMBER_CASE,
        name="Member Variable Naming",
        description="Private/protected member variables should use snake_case_ with trailing underscore",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.3 - Member Variable Naming",
        rationale="Distinguish member variables from local variables and parameters",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "class MyClass {\nprivate:\n  std::int32_t sequence_id_;\n  std::string buffer_name_;\n};",
            "class Example {\nprotected:\n  std::size_t count_;\n};",
        ],
        bad_examples=[
            "class MyClass {\nprivate:\n  std::int32_t sequence_id;  // Missing trailing underscore\n  std::string bufferName;   // Wrong case and missing underscore\n};"
        ],
    ),
    RuleId.NAMING_HUNGARIAN_NOTATION: RuleDefinition(
        rule_id=RuleId.NAMING_HUNGARIAN_NOTATION,
        name="Hungarian Notation Forbidden",
        description="Detect and forbid Hungarian notation (strName, intCount, etc.)",
        severity=Severity.ERROR,
        category="naming",
        style_guide_section="§5.5 - Forbidden Naming Patterns",
        rationale="Hungarian notation reduces readability and is unnecessary with modern IDEs and type systems",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            'std::string name = "example";',
            "std::int32_t count = 0;",
            "bool is_valid = true;",
        ],
        bad_examples=[
            'std::string strName = "example";  // Hungarian notation forbidden',
            "std::int32_t intCount = 0;  // Hungarian notation forbidden",
            "bool bIsValid = true;  // Hungarian notation forbidden",
        ],
    ),
    # === New Rules Implementation ===
    # Type System Rules
    RuleId.TYPE_PAIR_TUPLE: RuleDefinition(
        rule_id=RuleId.TYPE_PAIR_TUPLE,
        name="Pair/Tuple Usage Detection",
        description="Detect std::pair/tuple usage and suggest named struct alternatives",
        severity=Severity.ERROR,
        category="type-system",
        style_guide_section="§3.3 - Semantic Types",
        rationale="Named structs improve code readability and maintainability over generic pairs/tuples",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "struct Point { std::int32_t x; std::int32_t y; };",
            "struct KeyValue { std::string key; std::int32_t value; };",
            "struct Result { bool success; std::string error_message; };",
        ],
        bad_examples=[
            "std::pair<std::int32_t, std::int32_t> point;  // Use named struct",
            "std::tuple<std::string, std::int32_t> kv_pair;  // Use named struct",
            "std::tuple<bool, std::string, std::int32_t> result;  // Too many fields",
        ],
    ),
    # Header Rules
    RuleId.HEADER_PRAGMA_ONCE: RuleDefinition(
        rule_id=RuleId.HEADER_PRAGMA_ONCE,
        name="Pragma Once Detection",
        description="Detect missing #pragma once in header files",
        severity=Severity.ERROR,
        category="headers",
        style_guide_section="§2.1 - Header Protection",
        rationale="#pragma once is more reliable and faster than traditional include guards",
        requires_ast=False,
        auto_fixable=True,
        performance_impact="medium",  # Affects compilation speed
        false_positive_risk="low",
        good_examples=[
            "#pragma once\n\nclass MyClass {\n  // class definition\n};",
        ],
        bad_examples=[
            "// Missing #pragma once\nclass MyClass {\n  // class definition\n};",
            "#ifndef MY_CLASS_H\n#define MY_CLASS_H\n// Traditional guards (should use pragma once)\n#endif",
        ],
    ),
    RuleId.HEADER_COPYRIGHT: RuleDefinition(
        rule_id=RuleId.HEADER_COPYRIGHT,
        name="Enhanced Copyright Header",
        description="Enhanced copyright header checking with year and owner validation",
        severity=Severity.ERROR,
        category="headers",
        style_guide_section="§1.1 - File Headers",
        rationale="Proper copyright headers ensure legal compliance and code ownership clarity",
        requires_ast=False,
        auto_fixable=False,
        enabled_by_default=False,  # Project-specific requirement
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "// Copyright (C) 2024 Your Organization\n// Licensed under Apache 2.0",
            "/* Copyright (C) 2023-2024 Company Name\n * All rights reserved. */",
            "// © 2024 Organization Name",
        ],
        bad_examples=[
            "// No copyright header",
            "// Copyright without year",
            "// Copyright (C) 2024  // Missing owner",
        ],
    ),
    # Include Rules
    # File Organization Rules
    RuleId.FILE_READ_ERROR: RuleDefinition(
        rule_id=RuleId.FILE_READ_ERROR,
        name="File Read Error Handling",
        description="Handle file read errors gracefully during linting",
        severity=Severity.ERROR,
        category="file-organization",
        style_guide_section="§9.1 - Error Handling",
        rationale="Graceful error handling prevents linter crashes and provides useful diagnostics",
        requires_ast=False,
        auto_fixable=False,
        enabled_by_default=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "// Properly encoded UTF-8 text files",
            "// Files with reasonable size (< 1MB)",
            "// Text files with normal line lengths",
        ],
        bad_examples=[
            "// Binary files processed as text",
            "// Files with encoding issues (replacement characters)",
            "// Extremely large files that cause memory issues",
            "// Files with lines exceeding 10,000 characters",
        ],
    ),
    # === Namespace Rules ===
    RuleId.NAMESPACE_OLD_STYLE: RuleDefinition(
        rule_id=RuleId.NAMESPACE_OLD_STYLE,
        name="Old-Style Namespace Declaration",
        description="Detect old-style nested namespace declarations and suggest C++17 style",
        severity=Severity.ERROR,
        category="namespace",
        style_guide_section="§6.1 - Namespace Organization",
        rationale="C++17 nested namespace declarations are more concise and readable",
        requires_ast=True,
        auto_fixable=True,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "namespace vajra::native::core {\n  // content\n}",
            "namespace company::project::module {\n  class MyClass;\n}",
        ],
        bad_examples=[
            "namespace vajra {\nnamespace native {\nnamespace core {\n  // content\n}}}"
        ],
    ),
    RuleId.NAMESPACE_USING_FORBIDDEN: RuleDefinition(
        rule_id=RuleId.NAMESPACE_USING_FORBIDDEN,
        name="Using Namespace Forbidden in Headers",
        description="Forbid 'using namespace' directives in header files",
        severity=Severity.ERROR,
        category="namespace",
        style_guide_section="§6.2 - Namespace Pollution",
        rationale="Using namespace in headers can cause namespace pollution and naming conflicts",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "// In header files:\nstd::vector<int> data;\nvajra::native::Config config;",
            "// In source files:\nusing namespace std;\nusing namespace vajra::native;",
        ],
        bad_examples=[
            "// In header files:\nusing namespace std;\nusing namespace vajra::native;\nvector<int> data;  // Pollutes global namespace"
        ],
    ),
    RuleId.NAMESPACE_LONG_USAGE: RuleDefinition(
        rule_id=RuleId.NAMESPACE_LONG_USAGE,
        name="Repeated Long Namespace Usage",
        description="Detect repeated long namespace usage patterns and suggest using directive",
        severity=Severity.ERROR,
        category="namespace",
        style_guide_section="§6.3 - Namespace Usage Patterns",
        rationale="Repeated long namespace usage reduces readability and can be simplified with using directives",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "using vajra::native::core::scheduler;\nSequenceManager manager;\nBatchScheduler scheduler;\nPriorityQueue queue;",
            "// For short namespaces or infrequent usage:\nvajra::Config config;\nother::Thing thing;",
        ],
        bad_examples=[
            "vajra::native::core::scheduler::SequenceManager manager;\nvajra::native::core::scheduler::BatchScheduler scheduler;\nvajra::native::core::scheduler::PriorityQueue queue;"
        ],
    ),
    # === Enhanced Class Organization Rules ===
    RuleId.CLASS_MEMBER_ORDER: RuleDefinition(
        rule_id=RuleId.CLASS_MEMBER_ORDER,
        name="Enhanced Member Order",
        description="Enhanced member order checking with detailed type categorization",
        severity=Severity.ERROR,
        category="class-organization",
        style_guide_section="§5.2 - Member Organization",
        rationale="Detailed member ordering with proper categorization improves code navigation",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "class Example {\npublic:\n  using ValueType = int;\n  Example();\n  ~Example();\n  void Method();\nprivate:\n  int member_variable_;\n};"
        ],
        bad_examples=[
            "class Example {\npublic:\n  int member_variable_;  // Variable before constructor\n  Example();\n  using ValueType = int;  // Type alias after constructor\n};"
        ],
    ),
    RuleId.CLASS_TRAIT_STATIC: RuleDefinition(
        rule_id=RuleId.CLASS_TRAIT_STATIC,
        name="Static Class Trait Requirements",
        description="Utility classes with only static methods should inherit from StaticClass trait",
        severity=Severity.ERROR,
        category="class-traits",
        style_guide_section="§4.1 - Class Design",
        rationale="Explicit static class traits prevent instantiation and clarify intent",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "class Utils : public StaticClass {\npublic:\n  static void Helper();\n  static int Calculate(int value);\n};",
            "class MathUtils : public StaticClass {\npublic:\n  static double Sqrt(double x);\n  static double Pow(double base, double exp);\nprivate:\n  Utils() = delete;  // Prevent instantiation\n};",
        ],
        bad_examples=[
            "class Utils {  // Missing StaticClass trait\npublic:\n  static void Helper();\n  static int Calculate(int value);\n};",
            "class MathUtils {  // Utility class without trait\npublic:\n  static double Sqrt(double x);\n  static double Pow(double base, double exp);\n};",
        ],
    ),
    # === File Organization Rules ===
    RuleId.FILE_NAMING_CONVENTION: RuleDefinition(
        rule_id=RuleId.FILE_NAMING_CONVENTION,
        name="File Naming Convention",
        description="Header and source files should use PascalCase naming convention",
        severity=Severity.ERROR,
        category="file-organization",
        style_guide_section="§1.2 - File Naming",
        rationale="Consistent file naming improves project organization and maintainability",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "MyClass.h",
            "DataProcessor.cpp",
            "SequenceManager.hpp",
            "NetworkUtils.cc",
        ],
        bad_examples=[
            "my_class.h  // Should be PascalCase",
            "data_processor.cpp  // Should be PascalCase",
            "sequence-manager.hpp  // Should not use hyphens",
            "networkutils.cc  // Should have proper capitalization",
        ],
    ),
    RuleId.FILE_ORGANIZATION_HEADER: RuleDefinition(
        rule_id=RuleId.FILE_ORGANIZATION_HEADER,
        name="Header File Organization",
        description="Header files should be organized in csrc/include/ directory structure",
        severity=Severity.ERROR,
        category="file-organization",
        style_guide_section="§1.3 - Directory Structure",
        rationale="Proper header organization improves build system efficiency and maintainability",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "csrc/include/vajra/native/core/Scheduler.h",
            "csrc/include/vajra/commons/Logging.h",
            "csrc/include/vajra/kernels/ops.h",
            "csrc/test/utilities/TestHelper.h",
        ],
        bad_examples=[
            "src/native/core/Scheduler.h  // Should be in csrc/include/",
            "vajra/native/Scheduler.h  // Missing csrc/include/ prefix",
            "include/Scheduler.h  // Missing vajra namespace structure",
        ],
    ),
    RuleId.FILE_ORGANIZATION_TEST: RuleDefinition(
        rule_id=RuleId.FILE_ORGANIZATION_TEST,
        name="Test File Organization",
        description="Test files should be organized in csrc/test/ directory structure",
        severity=Severity.ERROR,
        category="file-organization",
        style_guide_section="§1.4 - Test Organization",
        rationale="Proper test organization mirrors source structure and improves maintainability",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "csrc/test/native/core/SchedulerTest.cpp",
            "csrc/test/commons/LoggingTest.cpp",
            "csrc/test/kernels/ops_test.cpp",
            "csrc/test/integration/EndToEndTest.cpp",
        ],
        bad_examples=[
            "src/test/SchedulerTest.cpp  // Should be in csrc/test/",
            "test/native/SchedulerTest.cpp  // Missing csrc/ prefix",
            "csrc/native/test/SchedulerTest.cpp  // Should mirror include structure",
        ],
    ),
    # === New Rules Implementation ===
    # Safety Rules - Raw Pointer Detection
    RuleId.SAFETY_RAW_POINTER_RETURN: RuleDefinition(
        rule_id=RuleId.SAFETY_RAW_POINTER_RETURN,
        name="Raw Pointer Return Types",
        description="Forbid raw pointer return types, suggest smart pointers or references",
        severity=Severity.ERROR,
        category="safety",
        style_guide_section="§8.3 - Memory Safety",
        rationale="Raw pointer returns create unclear ownership semantics and potential memory leaks",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "std::unique_ptr<Sequence> CreateSequence();",
            "std::shared_ptr<Buffer> GetBuffer();",
            "const char* GetCString();  // Exception for C strings",
            "void* GetRawMemory();  // Exception for low-level APIs",
        ],
        bad_examples=[
            "Sequence* CreateSequence();  // Unclear ownership",
            "Buffer* GetBuffer();  // Who owns the returned buffer?",
            "Data* ProcessData();  // Memory management unclear",
        ],
    ),
    RuleId.SAFETY_RAW_POINTER_PARAM: RuleDefinition(
        rule_id=RuleId.SAFETY_RAW_POINTER_PARAM,
        name="Raw Pointer Parameters",
        description="Discourage raw pointer parameters, suggest smart pointers or references",
        severity=Severity.ERROR,
        category="safety",
        style_guide_section="§8.4 - Parameter Safety",
        rationale="Raw pointer parameters create unclear ownership and lifetime semantics",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "void ProcessData(const std::unique_ptr<Data>& data);",
            "void UpdateBuffer(std::shared_ptr<Buffer> buffer);",
            "void HandleData(const Data& data);  // Reference for non-owning access",
            "void ProcessCString(const char* str);  // Exception for C strings",
        ],
        bad_examples=[
            "void ProcessData(Data* data);  // Ownership unclear",
            "void UpdateBuffer(Buffer* buffer);  // Who manages lifetime?",
            "void HandleSequence(Sequence* seq);  // Prefer reference or smart pointer",
        ],
    ),
    RuleId.MODERN_NODISCARD_MISSING: RuleDefinition(
        rule_id=RuleId.MODERN_NODISCARD_MISSING,
        name="Enhanced Missing Nodiscard",
        description="Enhanced detection of functions that should be [[nodiscard]]",
        severity=Severity.ERROR,
        category="modern-cpp",
        style_guide_section="§7.5 - Return Value Safety",
        rationale="Important return values should not be accidentally ignored, preventing bugs and improving code clarity",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="medium",
        good_examples=[
            "[[nodiscard]] std::unique_ptr<Data> CreateData();",
            "[[nodiscard]] bool Validate(const std::string& input);",
            "[[nodiscard]] std::optional<Result> TryParse();",
            "[[nodiscard]] Status Connect();",
        ],
        bad_examples=[
            "std::unique_ptr<Data> CreateData();  // Return should not be ignored",
            "bool Validate(const std::string& input);  // Validation result important",
            "std::optional<Result> TryParse();  // Parse result should be checked",
            "Status Connect();  // Connection status should be checked",
        ],
    ),
    RuleId.MODERN_SMART_PTR_BY_REF: RuleDefinition(
        rule_id=RuleId.MODERN_SMART_PTR_BY_REF,
        name="Smart Pointer By Value",
        description="Pass smart pointers by value for clear ownership transfer semantics",
        severity=Severity.ERROR,
        category="modern-cpp",
        style_guide_section="§7.3 - Smart Pointer Usage",
        rationale="Passing smart pointers by value makes ownership transfer explicit and follows modern C++ best practices",
        requires_ast=True,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            "void ProcessData(std::unique_ptr<Data> data);  // Clear ownership transfer",
            "void UpdateBuffer(std::shared_ptr<Buffer> buffer);  // Clear shared ownership",
            "void TakeOwnership(std::unique_ptr<Data>&& data);  // Move is also OK",
            "void ProcessRawPtr(Data* data);  // Raw pointer for observation",
        ],
        bad_examples=[
            "void ProcessData(const std::unique_ptr<Data>& data);  // Unclear ownership",
            "void UpdateBuffer(const std::shared_ptr<Buffer>& buffer);  // No ownership transfer",
            "void HandleWeakPtr(const std::weak_ptr<Data>& weak);  // Should be by value",
        ],
    ),
    # Logging Rules
    RuleId.LOGGING_FORBIDDEN_OUTPUT: RuleDefinition(
        rule_id=RuleId.LOGGING_FORBIDDEN_OUTPUT,
        name="Forbidden Direct Output",
        description="Forbid std::cout, std::cerr, printf, fprintf - use LOG_* macros instead",
        severity=Severity.ERROR,
        category="logging",
        style_guide_section="§9.1 - Logging Standards",
        rationale="Structured logging provides better control, filtering, and consistency across the codebase",
        requires_ast=False,
        auto_fixable=False,
        performance_impact="low",
        false_positive_risk="low",
        good_examples=[
            'LOG_INFO("Processing data with size: {}", data.size());',
            'LOG_ERROR("Failed to open file: {}", filename);',
            'LOG_DEBUG("Cache hit for key: {}", key);',
            'LOG_WARNING("Deprecated API used: {}", api_name);',
        ],
        bad_examples=[
            'std::cout << "Processing data" << std::endl;',
            'std::cerr << "Error: " << error_msg << std::endl;',
            'printf("Debug: %s\\n", debug_info);',
            'fprintf(stderr, "Critical error: %s\\n", error);',
        ],
    ),
}


def get_rule_definition(rule_id: RuleId) -> RuleDefinition:
    """Get the complete definition for a rule."""
    if rule_id not in RULE_DEFINITIONS:
        # Create a minimal definition for undefined rules
        return RuleDefinition(
            rule_id=rule_id,
            name=str(rule_id),
            description=f"Rule {rule_id} (definition missing)",
            severity=Severity.ERROR,
            category="misc",
        )
    return RULE_DEFINITIONS[rule_id]


def get_rules_by_category(category: str) -> List[RuleDefinition]:
    """Get all rules in a specific category."""
    return [
        rule_def
        for rule_def in RULE_DEFINITIONS.values()
        if rule_def.category == category
    ]


def get_mandatory_rules() -> List[RuleDefinition]:
    """Get all mandatory rules (ERROR/WARNING severity)."""
    return [
        rule_def
        for rule_def in RULE_DEFINITIONS.values()
        if rule_def.is_mandatory
    ]


def get_enabled_rules_for_project(
    project_phase: str = "mature",
) -> List[RuleDefinition]:
    """Get rules that should be enabled for a given project phase."""
    return [
        rule_def
        for rule_def in RULE_DEFINITIONS.values()
        if rule_def.should_be_enabled_for_project(project_phase)
    ]
