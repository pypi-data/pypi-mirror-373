"""Plugin system for Niti linter."""

from .base import NitiPlugin, PluginRuleDefinition
from .loader import PluginLoader

__all__ = ["NitiPlugin", "PluginRuleDefinition", "PluginLoader"]
