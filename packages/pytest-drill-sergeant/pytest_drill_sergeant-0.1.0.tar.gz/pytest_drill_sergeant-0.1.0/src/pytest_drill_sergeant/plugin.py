"""Pytest Drill Sergeant - Enforce test quality standards.

A pytest plugin that enforces test quality standards by:
- Auto-detecting test markers based on directory structure
- Enforcing AAA (Arrange-Act-Assert) structure with descriptive comments
- Providing comprehensive error reporting for violations
"""

import inspect
import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Default AAA synonyms for flexible recognition
DEFAULT_AAA_SYNONYMS = {
    "arrange": [
        "Setup",
        "Given",
        "Prepare",
        "Initialize",
        "Configure",
        "Create",
        "Build",
    ],
    "act": ["Call", "Execute", "Run", "Invoke", "Perform", "Trigger", "When"],
    "assert": ["Verify", "Check", "Expect", "Validate", "Confirm", "Ensure", "Then"],
}


@dataclass
class ValidationIssue:
    """Represents a single test validation issue."""

    issue_type: str  # "marker" or "aaa"
    message: str
    suggestion: str


@dataclass
class DrillSergeantConfig:
    """Configuration for pytest-drill-sergeant plugin."""

    enabled: bool = True
    enforce_markers: bool = True
    enforce_aaa: bool = True
    auto_detect_markers: bool = True
    min_description_length: int = 3
    marker_mappings: dict[str, str] = field(default_factory=dict)

    # AAA Synonym Recognition
    aaa_synonyms_enabled: bool = False
    aaa_builtin_synonyms: bool = True
    aaa_arrange_synonyms: list[str] = field(default_factory=list)
    aaa_act_synonyms: list[str] = field(default_factory=list)
    aaa_assert_synonyms: list[str] = field(default_factory=list)

    @classmethod
    def from_pytest_config(cls, config: pytest.Config) -> "DrillSergeantConfig":
        """Create config from pytest configuration and environment variables."""
        # Environment variables take precedence
        enabled = _get_bool_option(
            config,
            "drill_sergeant_enabled",
            env_var="DRILL_SERGEANT_ENABLED",
            default=True,
        )

        # If disabled globally, return early
        if not enabled:
            return cls(enabled=False)

        enforce_markers = _get_bool_option(
            config,
            "drill_sergeant_enforce_markers",
            env_var="DRILL_SERGEANT_ENFORCE_MARKERS",
            default=True,
        )

        enforce_aaa = _get_bool_option(
            config,
            "drill_sergeant_enforce_aaa",
            env_var="DRILL_SERGEANT_ENFORCE_AAA",
            default=True,
        )

        auto_detect_markers = _get_bool_option(
            config,
            "drill_sergeant_auto_detect_markers",
            env_var="DRILL_SERGEANT_AUTO_DETECT_MARKERS",
            default=True,
        )

        min_description_length = _get_int_option(
            config,
            "drill_sergeant_min_description_length",
            env_var="DRILL_SERGEANT_MIN_DESCRIPTION_LENGTH",
            default=3,
        )

        # Get custom marker mappings from TOML configuration
        marker_mappings = _get_marker_mappings(config)

        # AAA Synonym Recognition settings
        aaa_synonyms_enabled = _get_bool_option(
            config,
            "drill_sergeant_aaa_synonyms_enabled",
            env_var="DRILL_SERGEANT_AAA_SYNONYMS_ENABLED",
            default=False,
        )

        aaa_builtin_synonyms = _get_bool_option(
            config,
            "drill_sergeant_aaa_builtin_synonyms",
            env_var="DRILL_SERGEANT_AAA_BUILTIN_SYNONYMS",
            default=True,
        )

        aaa_arrange_synonyms = _get_synonym_list(
            config,
            "drill_sergeant_aaa_arrange_synonyms",
            "DRILL_SERGEANT_AAA_ARRANGE_SYNONYMS",
        )

        aaa_act_synonyms = _get_synonym_list(
            config,
            "drill_sergeant_aaa_act_synonyms",
            "DRILL_SERGEANT_AAA_ACT_SYNONYMS",
        )

        aaa_assert_synonyms = _get_synonym_list(
            config,
            "drill_sergeant_aaa_assert_synonyms",
            "DRILL_SERGEANT_AAA_ASSERT_SYNONYMS",
        )

        return cls(
            enabled=enabled,
            enforce_markers=enforce_markers,
            enforce_aaa=enforce_aaa,
            auto_detect_markers=auto_detect_markers,
            min_description_length=min_description_length,
            marker_mappings=marker_mappings,
            aaa_synonyms_enabled=aaa_synonyms_enabled,
            aaa_builtin_synonyms=aaa_builtin_synonyms,
            aaa_arrange_synonyms=aaa_arrange_synonyms,
            aaa_act_synonyms=aaa_act_synonyms,
            aaa_assert_synonyms=aaa_assert_synonyms,
        )


def _get_bool_option(
    config: pytest.Config, ini_name: str, env_var: str, default: bool
) -> bool:
    """Get boolean option from pytest config or environment variable."""
    # Environment variable takes precedence
    env_val = os.getenv(env_var)
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes", "on")

    # Then pytest config
    if hasattr(config, "getini"):
        try:
            ini_val = config.getini(ini_name)
            if ini_val is not None:
                return str(ini_val).lower() in ("true", "1", "yes", "on")
        except (ValueError, AttributeError):
            pass

    return default


def _get_int_option(
    config: pytest.Config, ini_name: str, env_var: str, default: int
) -> int:
    """Get integer option from pytest config or environment variable."""
    # Environment variable takes precedence
    env_val = os.getenv(env_var)
    if env_val is not None:
        try:
            return int(env_val)
        except ValueError:
            pass

    # Then pytest config
    if hasattr(config, "getini"):
        try:
            ini_val = config.getini(ini_name)
            if ini_val is not None:
                return int(ini_val)
        except (ValueError, AttributeError):
            pass

    return default


def _get_synonym_list(config: pytest.Config, ini_name: str, env_var: str) -> list[str]:
    """Get comma-separated synonym list from pytest config or environment variable."""
    # Environment variable takes precedence
    env_val = os.getenv(env_var)
    if env_val:
        return [synonym.strip() for synonym in env_val.split(",") if synonym.strip()]

    # Then pytest config
    if hasattr(config, "getini"):
        try:
            ini_val = config.getini(ini_name)
            if ini_val:
                return [
                    synonym.strip() for synonym in ini_val.split(",") if synonym.strip()
                ]
        except (ValueError, AttributeError):
            pass

    return []


def _get_marker_mappings(config: pytest.Config) -> dict[str, str]:
    """Get marker mappings with proper layered priority: env vars > pytest.ini.

    Each layer builds on the previous one, allowing selective overrides
    rather than complete replacement.
    """
    mappings = {}

    try:
        # Layer 1: Base mappings from pytest.ini
        if hasattr(config, "getini"):
            try:
                mappings_str = config.getini("drill_sergeant_marker_mappings")
                if mappings_str:
                    # Parse the mappings string
                    # Format: "dir1=marker1,dir2=marker2"
                    for mapping in mappings_str.split(","):
                        if "=" in mapping:
                            dir_name, marker_name = mapping.split("=", 1)
                            mappings[dir_name.strip()] = marker_name.strip()
            except (ValueError, AttributeError):
                pass

        # Layer 2: Environment variable overrides (highest priority)
        # This ADDS to or OVERRIDES specific mappings from pytest.ini
        env_mappings = os.getenv("DRILL_SERGEANT_MARKER_MAPPINGS")
        if env_mappings:
            # Format: "dir1=marker1,dir2=marker2"
            for mapping in env_mappings.split(","):
                if "=" in mapping:
                    dir_name, marker_name = mapping.split("=", 1)
                    mappings[dir_name.strip()] = marker_name.strip()

        # TODO: Add proper TOML parsing for [tool.drill_sergeant.marker_mappings]
        # This requires more sophisticated TOML handling that we can add later

        return mappings
    except Exception:
        return {}


def _get_available_markers(item: pytest.Item) -> set[str]:
    """Get available markers from pytest configuration or environment variable."""
    # Check environment variable first (highest priority)
    env_markers = os.getenv("DRILL_SERGEANT_MARKERS")
    if env_markers:
        markers = {m.strip() for m in env_markers.split(",") if m.strip()}
        if markers:
            return markers

    # Try to get markers from pytest config
    markers = _extract_markers_from_config(item.config)

    # Fallback to common markers if none found
    return (
        markers
        if markers
        else {"unit", "integration", "functional", "e2e", "performance"}
    )


def _extract_markers_from_config(config: pytest.Config) -> set[str]:
    """Extract marker names from pytest configuration."""
    try:
        markers = set()
        if hasattr(config, "_getini"):
            marker_entries = config._getini("markers") or []
            for marker_entry in marker_entries:
                # Marker format: "name: description"
                marker_name = marker_entry.split(":")[0].strip()
                if marker_name:
                    markers.add(marker_name)
        return markers
    except Exception:
        return set()


def _get_default_marker_mappings() -> dict[str, str]:
    """Get the default directory-to-marker mappings when no config is available."""
    return {
        # Standard test types
        "unit": "unit",
        "integration": "integration",
        "functional": "functional",
        "e2e": "e2e",
        "performance": "performance",
        # Common aliases
        "fixtures": "unit",  # Test fixtures are typically unit-level
        "func": "functional",  # Common shorthand
        "end2end": "e2e",  # Alternative naming
        "perf": "performance",  # Common shorthand
        "load": "performance",  # Load testing is performance testing
        "benchmark": "performance",  # Benchmarking is performance testing
        # Common alternate names
        "api": "integration",  # API tests are typically integration
        "smoke": "integration",  # Smoke tests are typically integration
        "acceptance": "e2e",  # Acceptance tests are typically e2e
        "contract": "integration",  # Contract tests are typically integration
        "system": "e2e",  # System tests are typically e2e
    }


def _detect_test_type_from_path(
    item: pytest.Item, config: DrillSergeantConfig
) -> str | None:
    """Detect test type based on the test file's package location.

    Uses available markers, custom mappings, and default mappings.
    Returns the appropriate marker name or None if detection fails.
    """
    try:
        # Get available markers from pytest config
        available_markers = _get_available_markers(item)

        # Get the test file path
        test_file = Path(item.fspath)

        # Check if we're in a test directory structure
        if "tests" in test_file.parts:
            # Find the tests directory and get the subdirectory
            tests_index = test_file.parts.index("tests")
            if tests_index + 1 < len(test_file.parts):
                test_type = test_file.parts[tests_index + 1]

                # 1. First try custom mappings from configuration (highest priority)
                if config.marker_mappings and test_type in config.marker_mappings:
                    custom_marker = config.marker_mappings[test_type]
                    if custom_marker in available_markers:
                        return custom_marker

                # 2. Then try exact match with available markers
                if test_type in available_markers:
                    return test_type

                # 3. Finally try default mappings (built-in intelligent defaults)
                default_mappings = _get_default_marker_mappings()
                if test_type in default_mappings:
                    default_marker = default_mappings[test_type]
                    if default_marker in available_markers:
                        return default_marker

        return None
    except Exception:
        return None


def _validate_markers(
    item: pytest.Item, config: DrillSergeantConfig
) -> list[ValidationIssue]:
    """Validate markers and return issues (don't fail immediately)."""
    issues: list[ValidationIssue] = []

    if any(item.iter_markers()):
        return issues  # Test already has markers, no issues

    # Try auto-detection if enabled
    detected_type = None
    if config.auto_detect_markers:
        detected_type = _detect_test_type_from_path(item, config)

    if detected_type:
        # Auto-decorate with helpful logging
        marker = getattr(pytest.mark, detected_type)
        item.function = marker(item.function)  # type: ignore[attr-defined]
        print(f"🔍 Auto-decorated test '{item.name}' with @pytest.mark.{detected_type}")
        return issues  # No issues, auto-fixed

    # Collect the issue if no marker found
    available_markers = _get_available_markers(item)
    marker_examples = ", ".join(
        f"@pytest.mark.{m}" for m in sorted(list(available_markers)[:3])
    )

    issues.append(
        ValidationIssue(
            issue_type="marker",
            message=f"Test '{item.name}' must have at least one marker",
            suggestion=f"Add {marker_examples} or move test to appropriate directory structure",
        )
    )

    return issues


def _has_descriptive_comment(line: str, min_length: int = 3) -> bool:
    """Check if a comment line has a descriptive dash and text."""
    # Remove the comment marker and check for dash and text
    comment_part = line.lstrip("#").strip()

    # Must have a dash followed by meaningful text
    if " - " not in comment_part:
        return False

    description = comment_part.split(" - ")[1].strip()
    return len(description) >= min_length


def _validate_aaa_structure(
    item: pytest.Item, config: DrillSergeantConfig
) -> list[ValidationIssue]:
    """Validate AAA structure and return issues (don't fail immediately)."""
    issues = []

    try:
        source_lines = inspect.getsource(item.function).split("\n")  # type: ignore[attr-defined]
        aaa_status = _check_aaa_sections(source_lines, item.name, config)
        issues.extend(aaa_status.issues)

        # Check for missing sections and add appropriate issues
        _add_missing_section_issues(aaa_status, item.name, issues)

    except OSError:
        # Can't get source (e.g., dynamic tests), skip AAA validation
        pass

    return issues


def _check_aaa_sections(
    source_lines: list[str], test_name: str, config: DrillSergeantConfig
) -> "_AAAStatus":
    """Check for AAA sections in source lines and validate descriptive comments."""
    status = _AAAStatus()

    for source_line in source_lines:
        line = source_line.strip()

        # Only check comment lines
        if not line.startswith("#"):
            continue

        # Check each AAA section
        status.update_from_line(line, test_name, config)

    return status


def _build_aaa_keyword_lists(config: DrillSergeantConfig) -> dict[str, list[str]]:
    """Build complete keyword lists for AAA detection including synonyms."""
    keywords = {"arrange": ["Arrange"], "act": ["Act"], "assert": ["Assert"]}

    # Add synonyms if enabled
    if config.aaa_synonyms_enabled:
        # Add built-in synonyms
        if config.aaa_builtin_synonyms:
            keywords["arrange"].extend(DEFAULT_AAA_SYNONYMS["arrange"])
            keywords["act"].extend(DEFAULT_AAA_SYNONYMS["act"])
            keywords["assert"].extend(DEFAULT_AAA_SYNONYMS["assert"])

        # Add custom synonyms
        keywords["arrange"].extend(config.aaa_arrange_synonyms)
        keywords["act"].extend(config.aaa_act_synonyms)
        keywords["assert"].extend(config.aaa_assert_synonyms)

    return keywords


def _add_missing_section_issues(
    aaa_status: "_AAAStatus", test_name: str, issues: list[ValidationIssue]
) -> None:
    """Add issues for missing AAA sections."""
    if not aaa_status.arrange_found:
        issues.append(
            ValidationIssue(
                issue_type="aaa",
                message=f"Test '{test_name}' is missing 'Arrange' section",
                suggestion="Add '# Arrange - description of what is being set up' comment before test setup",
            )
        )

    if not aaa_status.act_found:
        issues.append(
            ValidationIssue(
                issue_type="aaa",
                message=f"Test '{test_name}' is missing 'Act' section",
                suggestion="Add '# Act - description of what action is being performed' comment before test action",
            )
        )

    if not aaa_status.assert_found:
        issues.append(
            ValidationIssue(
                issue_type="aaa",
                message=f"Test '{test_name}' is missing 'Assert' section",
                suggestion="Add '# Assert - description of what is being verified' comment before test verification",
            )
        )


@dataclass
class _AAAStatus:
    """Track AAA section status and validation issues."""

    arrange_found: bool = False
    act_found: bool = False
    assert_found: bool = False
    issues: list[ValidationIssue] = field(default_factory=list)

    def update_from_line(
        self, line: str, test_name: str, config: DrillSergeantConfig
    ) -> None:
        """Update AAA status from a comment line with synonym support."""
        keywords = _build_aaa_keyword_lists(config)

        # Check each AAA section using helper
        self._check_section(
            line, test_name, config, (keywords["arrange"], "arrange", "set up")
        )
        self._check_section(
            line,
            test_name,
            config,
            (keywords["act"], "act", "action is being performed"),
        )
        self._check_section(
            line, test_name, config, (keywords["assert"], "assert", "is being verified")
        )

    def _check_section(
        self,
        line: str,
        test_name: str,
        config: DrillSergeantConfig,
        section_info: tuple[list[str], str, str],
    ) -> None:
        """Check if line contains keywords for a specific AAA section."""
        section_keywords, section_name, description = section_info
        if any(keyword in line for keyword in section_keywords):
            # Set the appropriate flag
            setattr(self, f"{section_name}_found", True)
            # Find matched keyword for feedback
            matched_keyword = next(k for k in section_keywords if k in line)
            self._check_descriptive_comment(
                line, test_name, matched_keyword, description, config
            )

    def _check_descriptive_comment(
        self,
        line: str,
        test_name: str,
        section: str,
        description: str,
        config: DrillSergeantConfig,
    ) -> None:
        """Check if a comment line has descriptive content."""
        if not _has_descriptive_comment(line, config.min_description_length):
            self.issues.append(
                ValidationIssue(
                    issue_type="aaa",
                    message=f"Test '{test_name}' has '{section}' but missing descriptive comment",
                    suggestion=f"Add '# {section} - description of what {description}' with at least {config.min_description_length} characters",
                )
            )


def _report_all_issues(item: pytest.Item, issues: list[ValidationIssue]) -> None:
    """Report validation issues using Google-style comprehensive error reporting."""
    lines: list[str] = []

    # Categorize issues
    marker_issues = [i for i in issues if i.issue_type == "marker"]
    aaa_issues = [i for i in issues if i.issue_type == "aaa"]

    # Build header
    _add_error_header(lines, item.name, marker_issues, aaa_issues, len(issues))

    # Add specific issue details
    _add_issue_details(lines, marker_issues, aaa_issues)

    # Add footer with requirements explanation
    _add_error_footer(lines)

    pytest.fail("\n".join(lines))


def _add_error_header(
    lines: list[str],
    test_name: str,
    marker_issues: list[ValidationIssue],
    aaa_issues: list[ValidationIssue],
    total_issues: int,
) -> None:
    """Add error message header."""
    violations = []
    if marker_issues:
        violations.append("missing test annotations")
    if aaa_issues:
        violations.append("missing AAA structure")

    violation_text = " and ".join(violations)
    lines.append(
        f"❌ CODE QUALITY: Test '{test_name}' violates project standards by {violation_text}"
    )
    lines.append(
        f"📋 {total_issues} requirement(s) must be fixed before this test can run:"
    )
    lines.append("")


def _add_issue_details(
    lines: list[str],
    marker_issues: list[ValidationIssue],
    aaa_issues: list[ValidationIssue],
) -> None:
    """Add specific issue details to error message."""
    if marker_issues:
        lines.append("🏷️  MISSING TEST CLASSIFICATION:")
        lines.extend(f"   • {issue.suggestion}" for issue in marker_issues)
        lines.append("")

    if aaa_issues:
        lines.append("📝 MISSING AAA STRUCTURE (Arrange-Act-Assert):")
        lines.extend(f"   • {issue.suggestion}" for issue in aaa_issues)
        lines.append("")


def _add_error_footer(lines: list[str]) -> None:
    """Add error message footer with requirements explanation."""
    lines.append("ℹ️  This is a PROJECT REQUIREMENT for all tests to ensure:")
    lines.append("   • Consistent test structure and readability")
    lines.append("   • Proper test categorization for CI/CD pipelines")
    lines.append("   • Maintainable test suite following industry standards")
    lines.append("")
    lines.append("📚 For examples and detailed requirements:")
    lines.append("   • https://github.com/jeffrichley/pytest-drill-sergeant")
    lines.append("   • pytest.ini (for valid markers)")


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Auto-decorate tests with markers AND enforce AAA structure - report ALL issues."""
    try:
        # Skip non-function items (like classes, modules)
        if not hasattr(item, "function") or not getattr(item, "function", None):
            return

        # Get configuration
        config = DrillSergeantConfig.from_pytest_config(item.config)

        # Skip if disabled
        if not config.enabled:
            return

        issues: list[ValidationIssue] = []

        # Phase 1: Collect marker issues (if enabled)
        if config.enforce_markers:
            marker_issues = _validate_markers(item, config)
        issues.extend(marker_issues)

        # Phase 2: Collect AAA structure issues (if enabled)
        if config.enforce_aaa:
            aaa_issues = _validate_aaa_structure(item, config)
        issues.extend(aaa_issues)

        # Phase 3: Report ALL issues at once
        if issues:
            _report_all_issues(item, issues)

    except Exception as e:
        # If there's any error, just skip the check to avoid breaking tests
        print(f"Warning: Test validation failed for {item.name}: {e}")
        pass
