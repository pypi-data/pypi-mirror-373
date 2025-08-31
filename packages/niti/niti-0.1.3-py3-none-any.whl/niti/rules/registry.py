"""Rule registry that loads and manages all linting rules."""

from .base_registry import BaseRegistry
from .rule_id import RuleId


class RuleRegistry(BaseRegistry):
    """Registry that loads and manages all core linting rules.
    
    This class extends BaseRegistry and is responsible for importing
    all rule modules and registering their rule classes.
    """

    def __init__(self):
        super().__init__()
        self._load_all_rules()

    def _load_all_rules(self) -> None:
        """Load and register all core rules."""
        # Import all rule classes
        from .naming import (
            NamingClassCaseRule,
            NamingConstantCaseRule,
            NamingEnumCaseRule,
            NamingEnumValueCaseRule,
            NamingFunctionCaseRule,
            NamingFunctionVerbRule,
            NamingHungarianNotationRule,
            NamingMemberCaseRule,
            NamingStructCaseRule,
            NamingVariableCaseRule,
        )
        from .types import TypeForbiddenIntRule, TypePairTupleRule
        from .class_traits import ClassTraitMissingRule, ClassTraitStaticRule
        from .documentation import (
            DocClassDocstringBriefRule,
            DocClassDocstringThreadSafetyRule,
            DocFunctionExtraParamDocsRule,
            DocFunctionMissingParamDocsRule,
            DocFunctionMissingReturnDocsRule,
            DocFunctionMissingRule,
            DocFunctionMissingThrowsDocsRule,
            DocFunctionParamDescQualityRule,
            DocMissingDeclarationCommentRule,
            DocParamDirectionMissingRule,
        )
        from .includes import (
            HeaderCopyrightRule,
            HeaderPragmaOnceRule,
            IncludeAngleBracketForbiddenRule,
            IncludeOrderWrongRule,
        )
        from .modern_cpp import (
            ModernMissingConstRule,
            ModernMissingNoexceptRule,
            ModernNodiscardMissingRule,
            ModernSmartPtrByRefRule,
        )
        from .code_quality import QualityMagicNumbersRule
        from .logging import LoggingForbiddenOutputRule
        from .safety import (
            SafetyRangeLoopMissingRule,
            SafetyRawPointerParamRule,
            SafetyRawPointerReturnRule,
            SafetyUnsafeCastRule,
        )
        from .class_organization import (
            ClassAccessSpecifierOrderRule,
            ClassMemberOrderRule,
            ClassMemberOrganizationRule,
        )
        from .file_organization import (
            FileHeaderCopyrightRule,
            FileNamingConventionRule,
            FileOrganizationHeaderRule,
            FileOrganizationTestRule,
            FileReadErrorRule,
        )
        from .namespace import (
            NamespaceLongUsageRule,
            NamespaceOldStyleRule,
            NamespaceUsingForbiddenRule,
        )

        # Register naming rules
        self.register(RuleId.NAMING_CLASS_CASE, NamingClassCaseRule)
        self.register(RuleId.NAMING_CONSTANT_CASE, NamingConstantCaseRule)
        self.register(RuleId.NAMING_ENUM_CASE, NamingEnumCaseRule)
        self.register(RuleId.NAMING_ENUM_VALUE_CASE, NamingEnumValueCaseRule)
        self.register(RuleId.NAMING_FUNCTION_CASE, NamingFunctionCaseRule)
        self.register(RuleId.NAMING_FUNCTION_VERB, NamingFunctionVerbRule)
        self.register(RuleId.NAMING_HUNGARIAN_NOTATION, NamingHungarianNotationRule)
        self.register(RuleId.NAMING_MEMBER_CASE, NamingMemberCaseRule)
        self.register(RuleId.NAMING_STRUCT_CASE, NamingStructCaseRule)
        self.register(RuleId.NAMING_VARIABLE_CASE, NamingVariableCaseRule)

        # Register type system rules
        self.register(RuleId.TYPE_FORBIDDEN_INT, TypeForbiddenIntRule)
        self.register(RuleId.TYPE_PAIR_TUPLE, TypePairTupleRule)

        # Register class trait rules
        self.register(RuleId.CLASS_TRAIT_MISSING, ClassTraitMissingRule)
        self.register(RuleId.CLASS_TRAIT_STATIC, ClassTraitStaticRule)

        # Register documentation rules
        self.register(RuleId.DOC_CLASS_DOCSTRING_BRIEF, DocClassDocstringBriefRule)
        self.register(RuleId.DOC_CLASS_DOCSTRING_THREAD_SAFETY, DocClassDocstringThreadSafetyRule)
        self.register(RuleId.DOC_FUNCTION_EXTRA_PARAM_DOCS, DocFunctionExtraParamDocsRule)
        self.register(RuleId.DOC_FUNCTION_MISSING, DocFunctionMissingRule)
        self.register(RuleId.DOC_FUNCTION_MISSING_PARAM_DOCS, DocFunctionMissingParamDocsRule)
        self.register(RuleId.DOC_FUNCTION_MISSING_RETURN_DOCS, DocFunctionMissingReturnDocsRule)
        self.register(RuleId.DOC_FUNCTION_MISSING_THROWS_DOCS, DocFunctionMissingThrowsDocsRule)
        self.register(RuleId.DOC_FUNCTION_PARAM_DESC_QUALITY, DocFunctionParamDescQualityRule)
        self.register(RuleId.DOC_CLASS_MISSING, DocMissingDeclarationCommentRule)
        self.register(RuleId.DOC_PARAM_DIRECTION_MISSING, DocParamDirectionMissingRule)

        # Register include/header rules
        self.register(RuleId.HEADER_COPYRIGHT, HeaderCopyrightRule)
        self.register(RuleId.HEADER_PRAGMA_ONCE, HeaderPragmaOnceRule)
        self.register(RuleId.INCLUDE_ANGLE_BRACKET_FORBIDDEN, IncludeAngleBracketForbiddenRule)
        self.register(RuleId.INCLUDE_ORDER_WRONG, IncludeOrderWrongRule)

        # Register modern C++ rules
        self.register(RuleId.MODERN_MISSING_CONST, ModernMissingConstRule)
        self.register(RuleId.MODERN_MISSING_NOEXCEPT, ModernMissingNoexceptRule)
        self.register(RuleId.MODERN_NODISCARD_MISSING, ModernNodiscardMissingRule)
        self.register(RuleId.MODERN_SMART_PTR_BY_REF, ModernSmartPtrByRefRule)

        # Register code quality rules
        self.register(RuleId.QUALITY_MAGIC_NUMBERS, QualityMagicNumbersRule)

        # Register logging rules
        self.register(RuleId.LOGGING_FORBIDDEN_OUTPUT, LoggingForbiddenOutputRule)

        # Register safety rules
        self.register(RuleId.SAFETY_RANGE_LOOP_MISSING, SafetyRangeLoopMissingRule)
        self.register(RuleId.SAFETY_RAW_POINTER_PARAM, SafetyRawPointerParamRule)
        self.register(RuleId.SAFETY_RAW_POINTER_RETURN, SafetyRawPointerReturnRule)
        self.register(RuleId.SAFETY_UNSAFE_CAST, SafetyUnsafeCastRule)

        # Register class organization rules
        self.register(RuleId.CLASS_ACCESS_SPECIFIER_ORDER, ClassAccessSpecifierOrderRule)
        self.register(RuleId.CLASS_MEMBER_ORDER, ClassMemberOrderRule)
        self.register(RuleId.CLASS_MEMBER_ORGANIZATION, ClassMemberOrganizationRule)

        # Register file organization rules
        self.register(RuleId.FILE_HEADER_COPYRIGHT, FileHeaderCopyrightRule)
        self.register(RuleId.FILE_NAMING_CONVENTION, FileNamingConventionRule)
        self.register(RuleId.FILE_ORGANIZATION_HEADER, FileOrganizationHeaderRule)
        self.register(RuleId.FILE_ORGANIZATION_TEST, FileOrganizationTestRule)
        self.register(RuleId.FILE_READ_ERROR, FileReadErrorRule)

        # Register namespace rules
        self.register(RuleId.NAMESPACE_LONG_USAGE, NamespaceLongUsageRule)
        self.register(RuleId.NAMESPACE_OLD_STYLE, NamespaceOldStyleRule)
        self.register(RuleId.NAMESPACE_USING_FORBIDDEN, NamespaceUsingForbiddenRule)


# Global rule registry instance
registry = RuleRegistry()