"""Configuration management for the C++ linter."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from ..rules.plugin_registry import plugin_registry
from ..rules.rule_id import RuleId
from .severity import Severity


@dataclass
class LinterConfig:
    """Configuration for the modern C++ linter.

    This class provides a clean, consistent configuration system where:
    - All rules are enabled by default based on their category (mandatory vs optional)
    - Rules can be explicitly disabled via disabled_rules
    - No redundant preference flags that conflict with rule enablement
    - Clear separation between project metadata and rule configuration
    """

    # === Project Metadata ===
    copyright_holders: List[str] = field(
        default_factory=lambda: ["Your Organization"]
    )

    # === File Organization ===
    header_extensions: List[str] = field(
        default_factory=lambda: [".h", ".hpp", ".hxx", ".cuh"]
    )
    source_extensions: List[str] = field(
        default_factory=lambda: [".cpp", ".cc", ".cxx", ".cu"]
    )
    precompiled_header_paths: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(
        default_factory=lambda: ["/kernels/", "/test/"]
    )

    # === Documentation Requirements ===
    documentation_style: str = "doxygen"  # doxygen, javadoc, plain

    # === Rule Configuration ===
    disabled_rules: Set[str] = field(default_factory=set)
    enabled_rules: Set[str] = field(
        default_factory=set
    )  # Explicitly enabled rules
    rule_severities: Dict[str, str] = field(
        default_factory=dict
    )  # Override default severities

    # Store raw config data for plugin system
    _config: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Initialize rule configuration after dataclass creation."""
        # Convert string rule IDs to RuleId enums and validate
        validated_disabled = set()
        for rule_str in self.disabled_rules:
            # Convert string to RuleId enum
            self._string_to_rule_id(rule_str)
            validated_disabled.add(rule_str)

        validated_enabled = set()
        for rule_str in self.enabled_rules:
            # Convert string to RuleId enum
            self._string_to_rule_id(rule_str)
            validated_enabled.add(rule_str)

        self.disabled_rules = validated_disabled
        self.enabled_rules = validated_enabled

        # Apply configuration to registry
        self._apply_to_registry()

    def _string_to_rule_id(self, rule_str: str) -> RuleId:
        """Convert string rule identifier to RuleId enum."""
        # Handle both formats: "type-forbidden-int" and "TYPE_FORBIDDEN_INT"
        normalized = rule_str.upper().replace("-", "_")
        return RuleId[normalized]

    def _apply_to_registry(self):
        """Apply configuration settings to the global rule registry."""
        # First, reset to defaults
        for rule_id in RuleId:
            if rule_id.is_mandatory:
                plugin_registry.enable_rule(rule_id)
            else:
                plugin_registry.disable_rule(rule_id)
            plugin_registry.set_rule_severity(rule_id, rule_id.default_severity)

        # Apply explicitly enabled rules (override defaults)
        for rule_str in self.enabled_rules:
            rule_id = self._string_to_rule_id(rule_str)
            plugin_registry.enable_rule(rule_id)

        # Apply disabled rules (can override enabled rules)
        for rule_str in self.disabled_rules:
            rule_id = self._string_to_rule_id(rule_str)
            plugin_registry.disable_rule(rule_id)

        # Apply severity overrides
        for rule_str, severity_str in self.rule_severities.items():
            rule_id = self._string_to_rule_id(rule_str)
            severity = Severity(severity_str.lower())
            plugin_registry.set_rule_severity(rule_id, severity)

    @classmethod
    def load(cls, config_path: str) -> "LinterConfig":
        """Load configuration from YAML or JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            LinterConfig instance with loaded settings
        """
        if config_path is None:
            # Return a default config if no path is provided
            return cls()

        config_file = Path(config_path)
        if not config_file.exists():
            print(
                f"Warning: Config file {config_path} not found, using defaults"
            )
            return cls()

        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Convert disabled_rules list to set if needed
        if "disabled_rules" in config_data and isinstance(
            config_data["disabled_rules"], list
        ):
            config_data["disabled_rules"] = set(config_data["disabled_rules"])

        # Filter out unknown fields to avoid dataclass errors
        valid_fields = {
            f.name
            for f in cls.__dataclass_fields__.values()
            if f.name != "_config"
        }
        filtered_data = {
            k: v for k, v in config_data.items() if k in valid_fields
        }

        # Create instance and store raw config
        instance = cls(**filtered_data)
        instance._config = config_data
        return instance

    def save(self, config_path: str) -> None:
        """Save configuration to YAML or JSON file.

        Args:
            config_path: Path where to save configuration
        """
        # Convert sets to lists for serialization
        config_dict = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, set):
                config_dict[field_name] = sorted(list(field_value))
            else:
                config_dict[field_name] = field_value

        config_file = Path(config_path)
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def disable_rule(self, rule_id: str) -> None:
        """Disable a specific rule."""
        self.disabled_rules.add(rule_id)
        self.enabled_rules.discard(rule_id)
        self._apply_to_registry()

    def enable_rule(self, rule_id: str) -> None:
        """Enable a specific rule."""
        self.disabled_rules.discard(rule_id)
        self.enabled_rules.add(rule_id)
        self._apply_to_registry()

    def set_rule_severity(self, rule_id: str, severity: str) -> None:
        """Override the severity for a specific rule."""
        self.rule_severities[rule_id] = severity
        self._apply_to_registry()

    def get_enabled_rules(self) -> Set[RuleId]:
        """Get all currently enabled rules."""
        return plugin_registry.get_enabled_rules()

    def is_rule_enabled(self, rule_id: RuleId) -> bool:
        """Check if a specific rule is enabled."""
        return rule_id in plugin_registry.get_enabled_rules()
