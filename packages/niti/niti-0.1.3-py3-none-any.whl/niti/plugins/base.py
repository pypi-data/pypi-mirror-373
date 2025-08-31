"""Base classes for Niti plugins."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from ..core.severity import Severity
from ..rules.base import BaseRule


class PluginRuleDefinition:
    """Definition of a plugin rule."""

    def __init__(
        self,
        rule_id: str,
        rule_class: Type[BaseRule],
        default_severity: Severity = Severity.WARNING,
        default_enabled: bool = True,
        description: str = "",
    ):
        """Initialize a plugin rule definition.

        Args:
            rule_id: Unique identifier for the rule (without plugin namespace)
            rule_class: The rule implementation class
            default_severity: Default severity level for the rule
            default_enabled: Whether the rule is enabled by default
            description: Human-readable description of the rule
        """
        self.rule_id = rule_id
        self.rule_class = rule_class
        self.default_severity = default_severity
        self.default_enabled = default_enabled
        self.description = description


class NitiPlugin(ABC):
    """Abstract base class for all Niti plugins.

    Plugins must implement this interface to be recognized by Niti.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (used for namespacing).

        This should be a short, lowercase identifier without spaces.
        It will be used as a prefix for all rule IDs from this plugin.
        """

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version.

        Should follow semantic versioning (e.g., "1.0.0").
        """

    @property
    def description(self) -> str:
        """Human-readable plugin description."""
        return ""

    @property
    def min_niti_version(self) -> str:
        """Minimum compatible Niti version.

        Defaults to "1.0.0". Override if your plugin requires
        specific Niti features.
        """
        return "1.0.0"

    @abstractmethod
    def get_rules(self) -> List[PluginRuleDefinition]:
        """Return list of rules provided by this plugin.

        Returns:
            List of PluginRuleDefinition objects defining the plugin's rules.
        """

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.

        Called once during plugin loading. The config parameter contains
        plugin-specific settings from the .nitirc file.

        Args:
            config: Plugin-specific configuration from .nitirc
        """
