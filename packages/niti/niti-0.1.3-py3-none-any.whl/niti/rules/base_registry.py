"""Base registry class for managing rules."""

from typing import TYPE_CHECKING, Dict, Set, Type, Union

if TYPE_CHECKING:
    from .base import BaseRule

from ..core.severity import Severity
from .rule_id import RuleId


class BaseRegistry:
    """Base registry for managing rule implementations and metadata.
    
    This class provides the core functionality for rule registration,
    enabling/disabling, and severity management. It can be extended
    to add specific rule loading logic.
    """

    def __init__(self):
        # Unified storage for both core and plugin rules
        self._rules: Dict[Union[RuleId, str], Type["BaseRule"]] = {}
        self._enabled_rules: Set[Union[RuleId, str]] = set()
        self._rule_severities: Dict[Union[RuleId, str], Severity] = {}

        # Initialize default settings for all RuleId enums
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize default settings for all rules."""
        for rule_id in RuleId:
            if rule_id.is_mandatory:
                self._enabled_rules.add(rule_id)
            self._rule_severities[rule_id] = rule_id.default_severity

    def register(
        self, rule_id: Union[RuleId, str], rule_class: Type["BaseRule"]
    ) -> None:
        """Register a rule implementation (core or plugin)."""
        self._rules[rule_id] = rule_class

    def enable_rule(self, rule_id: RuleId) -> None:
        """Enable a specific rule."""
        self._enabled_rules.add(rule_id)

    def disable_rule(self, rule_id: RuleId) -> None:
        """Disable a specific rule."""
        self._enabled_rules.discard(rule_id)

    def set_rule_severity(self, rule_id: RuleId, severity: Severity) -> None:
        """Override the default severity for a rule."""
        self._rule_severities[rule_id] = severity

    def get_enabled_rules(self) -> Set[RuleId]:
        """Get all currently enabled rules."""
        return self._enabled_rules.copy()

    def get_rule_class(self, rule_id: RuleId) -> Type["BaseRule"]:
        """Get the implementation class for a rule."""
        if rule_id not in self._rules:
            raise ValueError(f"Rule {rule_id} not registered")
        return self._rules[rule_id]

    def get_rule_severity(self, rule_id: RuleId) -> Severity:
        """Get the current severity for a rule."""
        return self._rule_severities[rule_id]

    def get_mandatory_rules(self) -> Set[RuleId]:
        """Get all rules that represent mandatory fixes."""
        return {rule_id for rule_id in RuleId if rule_id.is_mandatory}

    def get_suggestion_rules(self) -> Set[RuleId]:
        """Get all rules that represent optional suggestions."""
        return {rule_id for rule_id in RuleId if not rule_id.is_mandatory}

    # Plugin-specific methods
    def register_plugin_rule(
        self,
        rule_id: str,
        rule_class: Type["BaseRule"],
        severity: Severity,
        enabled: bool = True,
    ) -> None:
        """Register a plugin rule."""
        self._rules[rule_id] = rule_class
        self._rule_severities[rule_id] = severity
        if enabled:
            self._enabled_rules.add(rule_id)

    def get_all_enabled_rules(
        self,
    ) -> Dict[Union[RuleId, str], Type["BaseRule"]]:
        """Get all enabled rules (both core and plugin)."""
        return {
            rule_id: self._rules[rule_id]
            for rule_id in self._enabled_rules
            if rule_id in self._rules
        }

    def get_rule_by_id(self, rule_id: Union[RuleId, str]) -> Type["BaseRule"]:
        """Get rule class by ID (supports both core and plugin rules)."""
        if rule_id not in self._rules:
            raise ValueError(f"Rule {rule_id} not registered")
        return self._rules[rule_id]

    def get_severity_by_id(self, rule_id: Union[RuleId, str]) -> Severity:
        """Get rule severity by ID (supports both core and plugin rules)."""
        if rule_id not in self._rule_severities:
            raise ValueError(f"Rule {rule_id} not registered")
        return self._rule_severities[rule_id]

    def is_rule_enabled(self, rule_id: Union[RuleId, str]) -> bool:
        """Check if a rule is enabled."""
        return rule_id in self._enabled_rules

    def enable_rule_by_id(self, rule_id: Union[RuleId, str]) -> None:
        """Enable a rule by ID (supports both core and plugin rules)."""
        if rule_id in self._rules:
            self._enabled_rules.add(rule_id)

    def disable_rule_by_id(self, rule_id: Union[RuleId, str]) -> None:
        """Disable a rule by ID (supports both core and plugin rules)."""
        self._enabled_rules.discard(rule_id)

    def set_severity_by_id(
        self, rule_id: Union[RuleId, str], severity: Severity
    ) -> None:
        """Set severity for a rule by ID (supports both core and plugin rules)."""
        if rule_id in self._rules:
            self._rule_severities[rule_id] = severity