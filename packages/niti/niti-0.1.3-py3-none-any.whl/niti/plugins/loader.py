"""Plugin discovery and loading for Niti."""

import logging
import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from importlib.metadata import entry_points
else:
    # Fallback for Python 3.7
    import pkg_resources

    def entry_points():
        """Compatibility wrapper for entry points."""
        # Convert pkg_resources entry points to a dict-like structure
        eps = {}
        for group, entries in pkg_resources.iter_entry_points():
            eps[group] = list(entries)
        return eps


from packaging import version

from .base import NitiPlugin, PluginRuleDefinition

logger = logging.getLogger(__name__)


class PluginLoader:
    """Handles plugin discovery and loading via entry points."""

    ENTRY_POINT_GROUP = "niti.plugins"

    def __init__(self, niti_version: str = "1.0.0"):
        """Initialize the plugin loader.

        Args:
            niti_version: Current Niti version for compatibility checking
        """
        self.niti_version = niti_version
        self._plugins: Dict[str, NitiPlugin] = {}
        self._plugin_rules: Dict[str, PluginRuleDefinition] = {}

    def discover_plugins(self) -> List[str]:
        """Discover all installed plugins via entry points.

        Returns:
            List of discovered plugin names
        """
        discovered = []

        try:
            # Get entry points for our group
            eps = entry_points()

            if hasattr(eps, "select"):
                # Python 3.10+
                plugin_eps = eps.select(group=self.ENTRY_POINT_GROUP)
            elif hasattr(eps, "get"):
                # Python 3.8-3.9
                plugin_eps = eps.get(self.ENTRY_POINT_GROUP, [])
            else:
                # Fallback
                plugin_eps = []
                for group_name in eps:
                    if group_name == self.ENTRY_POINT_GROUP:
                        plugin_eps = eps[group_name]
                        break

            for entry_point in plugin_eps:
                discovered.append(entry_point.name)
                logger.debug(f"Discovered plugin: {entry_point.name}")

        except Exception as e:
            logger.error(f"Error discovering plugins: {e}")

        return discovered

    def load_plugin(
        self, plugin_name: str, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Load a specific plugin by name.

        Args:
            plugin_name: Name of the plugin to load (entry point name)
            config: Plugin-specific configuration

        Returns:
            True if plugin loaded successfully, False otherwise
        """
        try:
            # Get entry points
            eps = entry_points()

            if hasattr(eps, "select"):
                # Python 3.10+
                plugin_eps = eps.select(group=self.ENTRY_POINT_GROUP)
            elif hasattr(eps, "get"):
                # Python 3.8-3.9
                plugin_eps = eps.get(self.ENTRY_POINT_GROUP, [])
            else:
                # Fallback
                plugin_eps = []
                for group_name in eps:
                    if group_name == self.ENTRY_POINT_GROUP:
                        plugin_eps = eps[group_name]
                        break

            # Find the specific plugin
            for entry_point in plugin_eps:
                if entry_point.name == plugin_name:
                    # Load the plugin class
                    plugin_class = entry_point.load()
                    plugin = plugin_class()

                    # Validate plugin
                    validation_errors = self._validate_plugin(plugin)
                    if validation_errors:
                        for error in validation_errors:
                            logger.error(
                                f"Plugin '{plugin_name}' validation error: {error}"
                            )
                        return False

                    # Version compatibility check
                    if not self._check_compatibility(plugin):
                        logger.error(
                            f"Plugin '{plugin.name}' requires Niti >= {plugin.min_niti_version}, "
                            f"but current version is {self.niti_version}"
                        )
                        return False

                    # Initialize plugin with config
                    plugin_config = config or {}
                    plugin.initialize(plugin_config)

                    # Register plugin and its rules
                    self._register_plugin(plugin)
                    logger.info(
                        f"Loaded plugin: {plugin.name} v{plugin.version}"
                    )
                    return True

            logger.error(
                f"Plugin '{plugin_name}' not found in installed packages"
            )
            return False

        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return False

    def load_all_plugins(
        self,
        enabled_plugins: List[str],
        plugin_configs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """Load multiple plugins.

        Args:
            enabled_plugins: List of plugin names to load
            plugin_configs: Dict mapping plugin names to their configurations
        """
        plugin_configs = plugin_configs or {}

        for plugin_name in enabled_plugins:
            config = plugin_configs.get(plugin_name, {})
            self.load_plugin_safe(plugin_name, config)

    def load_plugin_safe(
        self, plugin_name: str, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Load plugin with error isolation.

        Args:
            plugin_name: Name of the plugin to load
            config: Plugin-specific configuration

        Returns:
            True if plugin loaded successfully, False otherwise
        """
        try:
            return self.load_plugin(plugin_name, config)
        except Exception as e:
            logger.error(f"Plugin '{plugin_name}' failed to load: {e}")
            # Continue without the plugin
            return False

    def _check_compatibility(self, plugin: NitiPlugin) -> bool:
        """Check if plugin is compatible with current Niti version.

        Args:
            plugin: Plugin instance to check

        Returns:
            True if compatible, False otherwise
        """
        try:
            min_version = version.parse(plugin.min_niti_version)
            current_version = version.parse(self.niti_version)
            return current_version >= min_version
        except Exception as e:
            logger.warning(f"Error checking version compatibility: {e}")
            return True  # Allow plugin if version check fails

    def _validate_plugin(self, plugin: NitiPlugin) -> List[str]:
        """Validate plugin implementation.

        Args:
            plugin: Plugin instance to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check required attributes
        if not plugin.name:
            errors.append("Plugin must have a name")

        if not plugin.version:
            errors.append("Plugin must have a version")

        # Check name format
        if plugin.name and (" " in plugin.name or "/" in plugin.name):
            errors.append(
                f"Plugin name '{plugin.name}' should not contain spaces or slashes"
            )

        # Check for rule ID conflicts within the plugin
        try:
            rules = plugin.get_rules()
            rule_ids = set()
            for rule_def in rules:
                if "/" in rule_def.rule_id:
                    errors.append(
                        f"Rule ID '{rule_def.rule_id}' should not contain '/'"
                    )
                if rule_def.rule_id in rule_ids:
                    errors.append(
                        f"Duplicate rule ID '{rule_def.rule_id}' in plugin"
                    )
                rule_ids.add(rule_def.rule_id)
        except Exception as e:
            errors.append(f"Error getting plugin rules: {e}")

        return errors

    def _register_plugin(self, plugin: NitiPlugin) -> None:
        """Register a plugin and its rules.

        Args:
            plugin: Plugin instance to register
        """
        self._plugins[plugin.name] = plugin

        # Register each rule with namespaced ID
        for rule_def in plugin.get_rules():
            namespaced_id = f"{plugin.name}/{rule_def.rule_id}"
            self._plugin_rules[namespaced_id] = rule_def
            logger.debug(f"Registered plugin rule: {namespaced_id}")

    def get_all_rules(self) -> Dict[str, PluginRuleDefinition]:
        """Get all rules from loaded plugins.

        Returns:
            Dict mapping namespaced rule IDs to their definitions
        """
        return self._plugin_rules.copy()

    def get_loaded_plugins(self) -> Dict[str, NitiPlugin]:
        """Get all loaded plugins.

        Returns:
            Dict mapping plugin names to their instances
        """
        return self._plugins.copy()
