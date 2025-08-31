"""Main linting engine that orchestrates rule execution."""

from pathlib import Path
from typing import Dict, List

import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

from ..rules.base import AutofixResult
from ..rules.plugin_registry import plugin_registry
from .config import LinterConfig
from .issue import LintIssue


class LintingEngine:
    """Main engine that coordinates file processing and rule execution."""

    def __init__(self, config: LinterConfig):
        self.config = config

        # Initialize tree-sitter parser
        self.cpp_language = Language(tscpp.language())
        self.parser = Parser(self.cpp_language)

        # Track all issues found
        self.all_issues: List[LintIssue] = []

        # Track autofix results
        self.autofix_results: Dict[str, List[AutofixResult]] = {}

        # Load plugins if configured
        if "plugins" in config._config:
            plugin_registry.load_plugins(
                config._config["plugins"], niti_version="1.0.0"
            )

        # Apply rule configuration (including plugin rules)
        if "rules" in config._config:
            plugin_registry.apply_rule_config(config._config["rules"])

    def lint_paths(
        self, paths: List[str], autofix: bool = False
    ) -> List[LintIssue]:
        """Lint the specified paths (files or directories).

        Args:
            paths: List of file or directory paths to lint

        Returns:
            List of all issues found across all files
        """
        self.all_issues = []

        # Collect all C++ files to process
        cpp_files = []
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                if self._is_cpp_file(path):
                    cpp_files.append(path)
            elif path.is_dir():
                cpp_files.extend(self._find_cpp_files(path))
            else:
                print(f"Warning: Path not found: {path}")

        if not cpp_files:
            print("No C++ files found to lint")
            return []

        print(f"Found configuration file: {self.config.__class__.__name__}")
        print(f"Linting {len(cpp_files)} C++ files...")

        # Process each file
        for file_path in sorted(cpp_files):
            self._lint_file(file_path, autofix=autofix)

        # Print autofix summary if enabled
        if autofix:
            self._print_autofix_summary()

        return self.all_issues

    def _lint_file(self, file_path: Path, autofix: bool = False) -> None:
        """Lint a single C++ file.

        Args:
            file_path: Path to the file to lint
        """
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse with tree-sitter
            tree = self.parser.parse(content.encode("utf-8"))

            # Run all enabled rules (both core and plugin)
            # First check if all enabled rules are registered
            all_enabled_ids = plugin_registry._registry._enabled_rules.copy()
            for rule_id in all_enabled_ids:
                if rule_id not in plugin_registry._registry._rules:
                    raise RuntimeError(
                        f"Configuration error: Rule '{rule_id}' is enabled but not registered. "
                        "This indicates a bug in the linter."
                    )

            enabled_rules = plugin_registry.get_all_enabled_rules()

            for rule_id, rule_class in enabled_rules.items():
                try:
                    # Get rule severity
                    rule_severity = plugin_registry.get_severity_by_id(rule_id)

                    # Create rule instance and run check
                    # For plugin rules, we pass the string ID
                    if isinstance(rule_id, str):
                        # Plugin rule - create without RuleId enum
                        rule_instance = rule_class()
                        # Set the plugin rule ID manually if needed
                        if hasattr(rule_instance, "plugin_rule_id"):
                            rule_instance.plugin_rule_id = rule_id
                    else:
                        # Core rule
                        rule_instance = rule_class(rule_id, rule_severity)

                    issues = rule_instance.check(
                        str(file_path), content, tree, self.config
                    )

                    # Add issues to total
                    self.all_issues.extend(issues)

                    # Apply autofix if enabled and rule supports it
                    if autofix and issues and rule_instance.supports_autofix:
                        result = rule_instance.autofix(
                            str(file_path), content, tree, self.config, issues
                        )

                        if result.success:
                            # Update content for subsequent rules
                            content = result.new_content
                            tree = self.parser.parse(content.encode("utf-8"))

                            # Track autofix results
                            if str(file_path) not in self.autofix_results:
                                self.autofix_results[str(file_path)] = []
                            self.autofix_results[str(file_path)].append(result)

                except ValueError as e:
                    # ValueError - let unregistered rule errors bubble up
                    if "not registered" in str(e):
                        raise  # Let it bubble up to outer handler
                    else:
                        print(
                            f"Configuration error for rule {rule_id} on {file_path}: {e}"
                        )
                except Exception as e:
                    # Other unexpected errors during rule execution
                    print(f"Error running rule {rule_id} on {file_path}: {e}")

            # Write back fixed content if any autofixes were applied
            if autofix and str(file_path) in self.autofix_results:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print(f"Error writing autofix results to {file_path}: {e}")

        except RuntimeError:
            # Re-raise RuntimeError (configuration errors)
            raise
        except ValueError as e:
            # Don't catch rule registration errors - let them bubble up
            if "not registered" in str(e):
                raise RuntimeError(
                    f"Configuration error: Rule is enabled but not registered. This indicates a bug in the linter."
                ) from e
            else:
                print(f"Error processing file {file_path}: {e}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def _print_autofix_summary(self) -> None:
        """Print summary of autofix results."""
        if not self.autofix_results:
            print("\n✅ No autofixable issues found.")
            return

        total_fixes = 0
        for file_path, results in self.autofix_results.items():
            file_fixes = sum(r.issues_fixed for r in results)
            total_fixes += file_fixes
            print(f"Fixed {file_fixes} issues in: {file_path}")

        print(
            f"\n✅ Total issues fixed: {total_fixes} in {len(self.autofix_results)} files"
        )

    def _is_cpp_file(self, file_path: Path) -> bool:
        """Check if a file is a C++ source or header file."""
        suffix = file_path.suffix
        return (
            suffix in self.config.header_extensions
            or suffix in self.config.source_extensions
        )

    def _find_cpp_files(self, directory: Path) -> List[Path]:
        """Recursively find all C++ files in a directory."""
        cpp_files = []

        for file_path in directory.rglob("*"):
            if file_path.is_file() and self._is_cpp_file(file_path):
                # Check if file should be excluded
                if not self._should_exclude_file(file_path):
                    cpp_files.append(file_path)

        return cpp_files

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from linting."""
        file_str = str(file_path)

        for excluded_pattern in self.config.excluded_paths:
            if excluded_pattern in file_str:
                return True

        return False
