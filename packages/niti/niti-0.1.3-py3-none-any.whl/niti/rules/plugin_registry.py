"""Plugin integration for the rule registry."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..core.severity import Severity
from ..plugins.loader import PluginLoader
from .registry import registry  # Use the global registry instance
from .rule_id import RuleId

if TYPE_CHECKING:
    pass


class PluginRegistryWrapper:
    """Wrapper to add plugin functionality to the base registry."""

    def __init__(self):
        self._registry = registry  # Use the global registry
        self._plugin_loader: Optional[PluginLoader] = None

    def load_plugins(
        self, plugin_config: Dict[str, Any], niti_version: str = "1.0.0"
    ) -> None:
        """Load configured plugins and their rules.

        Args:
            plugin_config: Plugin configuration from .nitirc
            niti_version: Current Niti version for compatibility checking
        """
        if not self._plugin_loader:
            self._plugin_loader = PluginLoader(niti_version)

        enabled_plugins = plugin_config.get("enabled", [])
        plugin_configs = plugin_config.get("config", {})

        # Load all enabled plugins
        self._plugin_loader.load_all_plugins(enabled_plugins, plugin_configs)

        # Register plugin rules in the base registry
        for rule_id, rule_def in self._plugin_loader.get_all_rules().items():
            self._registry.register_plugin_rule(
                rule_id,
                rule_def.rule_class,
                rule_def.default_severity,
                rule_def.default_enabled,
            )

    def apply_rule_config(
        self, rules_config: Dict[str, Dict[str, Any]]
    ) -> None:
        """Apply rule configuration from .nitirc.

        Args:
            rules_config: Rules section from configuration file
        """
        for rule_id_str, rule_config in rules_config.items():
            # Check if it's a core rule
            try:
                # Try to get RuleId enum
                rule_id_enum = None
                for rid in RuleId:
                    if str(rid) == rule_id_str:
                        rule_id_enum = rid
                        break

                if rule_id_enum:
                    # Core rule - use base registry methods
                    if "enabled" in rule_config:
                        if rule_config["enabled"]:
                            self._registry.enable_rule(rule_id_enum)
                        else:
                            self._registry.disable_rule(rule_id_enum)
                    if "severity" in rule_config:
                        severity = Severity[rule_config["severity"].upper()]
                        self._registry.set_rule_severity(rule_id_enum, severity)
                elif "/" in rule_id_str or rule_id_str in self._registry._rules:
                    # Plugin rule (has namespace) or registered plugin rule
                    if "enabled" in rule_config:
                        if rule_config["enabled"]:
                            self._registry.enable_rule_by_id(rule_id_str)
                        else:
                            self._registry.disable_rule_by_id(rule_id_str)
                    if "severity" in rule_config:
                        severity = Severity[rule_config["severity"].upper()]
                        self._registry.set_severity_by_id(rule_id_str, severity)
            except Exception as e:
                # Log warning about unknown rule
                import logging

                logging.getLogger(__name__).warning(
                    f"Unknown rule in config: {rule_id_str} - {e}"
                )

    def get_plugin_rules(self) -> List[str]:
        """Get list of all registered plugin rules.

        Returns:
            List of namespaced plugin rule IDs
        """
        return [
            rule_id
            for rule_id in self._registry._rules.keys()
            if isinstance(rule_id, str)
        ]

    # Delegate all other methods to the base registry
    def __getattr__(self, name):
        """Delegate all other method calls to the base registry."""
        return getattr(self._registry, name)


# Create a global plugin-aware wrapper instance
plugin_registry = PluginRegistryWrapper()
