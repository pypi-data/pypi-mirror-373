"""Pytest Drill Sergeant - Enforce test quality standards.

A pytest plugin that enforces test quality standards by:
- Auto-detecting test markers based on directory structure
- Enforcing AAA (Arrange-Act-Assert) structure with descriptive comments
- Providing comprehensive error reporting for violations
"""

__version__ = "0.1.0"
__author__ = "Jeff Richley"
__email__ = "jeffrichley@gmail.com"

# Import main plugin functionality
from pytest_drill_sergeant.plugin import ValidationIssue, pytest_runtest_setup

__all__ = [
    "ValidationIssue",
    "__author__",
    "__email__",
    "__version__",
    "pytest_runtest_setup",
]
