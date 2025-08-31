"""Rules package for the C++ linter.

This package contains all the linting rules for the C++ linter. 
All rule registration is handled centrally in the RuleRegistry class.

The registry pattern provides:
- Centralized rule management and registration
- Dynamic enabling/disabling of rules
- Plugin support through the plugin_registry wrapper
- Consistent rule configuration
"""

# Import base classes and registries
from .base import ASTRule, BaseRule, RegexRule
from .base_registry import BaseRegistry
from .plugin_registry import plugin_registry
from .registry import registry
from .rule_id import RuleId

# Public API - what gets exposed when someone does "from niti.rules import ..."
__all__ = [
    # Core types and enums
    "RuleId",
    # Registry instances
    "registry",
    "plugin_registry",
    "BaseRegistry",
    # Base classes for rule implementation
    "BaseRule",
    "ASTRule",
    "RegexRule",
]
