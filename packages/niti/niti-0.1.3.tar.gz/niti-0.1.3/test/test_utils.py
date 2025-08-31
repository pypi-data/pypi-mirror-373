"""Test utilities and base classes for Niti tests."""

import os
import tempfile
import unittest
from typing import List, Optional

from niti.core.config import LinterConfig
from niti.core.engine import LintingEngine
from niti.core.issue import LintIssue
from niti.core.severity import Severity
from niti.rules.registry import registry
from niti.rules.rule_id import RuleId


class NitiTestCase(unittest.TestCase):
    """Base test case for all Niti tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LinterConfig()
        self.engine = LintingEngine(self.config)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, content: str, filename: str = "test.cpp") -> str:
        """Create a temporary test file with given content."""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def lint_content(
        self,
        content: str,
        filename: str = "test.cpp",
        enable_rules: Optional[List[str]] = None,
        disable_rules: Optional[List[str]] = None,
    ) -> List[LintIssue]:
        """Lint content and return issues."""
        config = LinterConfig()

        # Disable all rules first if specific rules are requested
        if enable_rules:
            for rule in RuleId:
                config.disable_rule(str(rule))
            for rule in enable_rules:
                config.enable_rule(rule)

        # Apply any specific disable rules
        if disable_rules:
            for rule in disable_rules:
                config.disable_rule(rule)

        engine = LintingEngine(config)
        file_path = self.create_test_file(content, filename)
        return engine.lint_paths([file_path])

    def assert_has_rule(
        self, issues: List[LintIssue], rule_id: str, count: Optional[int] = None
    ):
        """Assert that issues contain a specific rule violation."""
        rule_issues = [issue for issue in issues if issue.rule_id == rule_id]
        rule_count = len(rule_issues)

        if count is None:
            self.assertGreater(
                rule_count,
                0,
                f"Expected rule {rule_id} but found none. "
                f"All rules found: {[issue.rule_id for issue in issues]}",
            )
        else:
            self.assertEqual(
                rule_count,
                count,
                f"Expected {count} instances of rule {rule_id} but found {rule_count}. "
                f"All rules found: {[issue.rule_id for issue in issues]}",
            )

    def assert_no_rule(self, issues: List[LintIssue], rule_id: str):
        """Assert that issues do not contain a specific rule violation."""
        rule_ids = [issue.rule_id for issue in issues]
        self.assertNotIn(
            rule_id, rule_ids, f"Unexpected rule {rule_id} in: {rule_ids}"
        )

    def assert_issue_at_line(
        self, issues: List[LintIssue], rule_id: str, line_number: int
    ):
        """Assert that a specific rule violation occurs at a specific line."""
        rule_issues = [issue for issue in issues if issue.rule_id == rule_id]
        line_numbers = [issue.line_number for issue in rule_issues]

        self.assertIn(
            line_number,
            line_numbers,
            f"Expected rule {rule_id} at line {line_number} but found at lines: {line_numbers}",
        )

    def assert_no_issues(self, issues: List[LintIssue]):
        """Assert that no issues were found."""
        self.assertEqual(
            len(issues),
            0,
            f"Expected no issues but found {len(issues)}: "
            f"{[f'{issue.rule_id} at line {issue.line_number}' for issue in issues]}",
        )

    def get_issues_by_rule(
        self, issues: List[LintIssue], rule_id: str
    ) -> List[LintIssue]:
        """Get all issues for a specific rule."""
        return [issue for issue in issues if issue.rule_id == rule_id]

    def get_issues_by_severity(
        self, issues: List[LintIssue], severity: Severity
    ) -> List[LintIssue]:
        """Get all issues with a specific severity."""
        return [issue for issue in issues if issue.severity == severity]


class RuleTestCase(NitiTestCase):
    """Base test case for testing individual rules."""

    rule_id: Optional[str] = None  # Override in subclasses

    def test_rule_registered(self):
        """Test that the rule is properly registered."""
        if self.rule_id:
            rule_enum = RuleId[self.rule_id.upper().replace("-", "_")]
            self.assertIn(
                rule_enum,
                registry._rules,
                f"Rule {self.rule_id} not registered in registry",
            )

    def lint_only_this_rule(
        self, content: str, filename: str = "test.cpp"
    ) -> List[LintIssue]:
        """Lint content with only this rule enabled."""
        if not self.rule_id:
            raise ValueError("rule_id must be set in subclass")
        return self.lint_content(content, filename, enable_rules=[self.rule_id])
