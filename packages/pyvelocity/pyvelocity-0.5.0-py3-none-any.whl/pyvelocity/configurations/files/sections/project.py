"""Implements section for project."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section
from pyvelocity.constants import LATEST_PYTHON_VERSION


class RequiresPythonAnalyzer:
    """Represents the requires-python field in pyproject.toml."""

    def __init__(self, value: str) -> None:
        self.value = value
        self.greater_than = self.handle_equals_or_greater_than() if ">=" in self.value else None
        self.same_major = self.handle_same_major_version() if "~=" in self.value else None
        self.exact = self.handle_exact_version_specifications()

    def minimum_version(self) -> str | None:
        """Extract minimum Python version from requires-python specification."""
        if self.greater_than:
            return self.greater_than
        if self.same_major:
            return self.same_major
        return self.exact

    def handle_equals_or_greater_than(self) -> str | None:
        """Handle >= version specifications."""
        ge_match = re.search(r">=(\d+)\.(\d+)", self.value)
        if ge_match:
            return f"{ge_match.group(1)}.{ge_match.group(2)}"
        return None

    def handle_same_major_version(self) -> str | None:
        """Handle same major version specifications."""
        compat_match = re.search(r"~=(\d+)\.(\d+)", self.value)
        if compat_match:
            return f"{compat_match.group(1)}.{compat_match.group(2)}"
        return None

    def handle_exact_version_specifications(self) -> str | None:
        """Handle exact version specifications."""
        exact_match = re.search(r"^(\d+)\.(\d+)$", self.value.strip())
        if exact_match:
            return f"{exact_match.group(1)}.{exact_match.group(2)}"
        return None

    def get_requires_python_supported_versions(self) -> set[str]:
        """Extract supported Python versions from requires-python specification."""
        min_version = self.minimum_version()
        if not min_version:
            return set()

        all_versions = self._generate_version_range(min_version)
        return self._filter_supported_versions(all_versions, self.value)

    def _generate_version_range(self, min_version: str) -> list[str]:
        """Generate all Python versions from minimum to latest."""
        min_major, min_minor = map(int, min_version.split("."))
        latest_major, latest_minor = map(int, LATEST_PYTHON_VERSION.split("."))

        all_versions = []
        for major in range(min_major, latest_major + 1):
            start_minor = min_minor if major == min_major else 0
            for minor in range(start_minor, 100):
                if (major, minor) > (latest_major, latest_minor):
                    break
                all_versions.append(f"{major}.{minor}")
        return all_versions

    def _filter_supported_versions(self, all_versions: list[str], requires_python: str) -> set[str]:
        """Filter versions that satisfy the requires-python constraint."""
        supported = set()
        for version in all_versions:
            if self.version_satisfies_requirement(version, requires_python):
                supported.add(version)
        return supported

    def version_satisfies_requirement(self, version: str, requirement: str) -> bool:
        """Check if a version satisfies the requires-python requirement."""
        major, minor = map(int, version.split("."))

        if ">=" in requirement:
            return self._check_greater_equal_requirement(major, minor, requirement)
        if "~=" in requirement:
            return self._check_compatible_release_requirement(major, minor, requirement)
        return self._check_exact_version_requirement(major, minor, requirement)

    def _check_greater_equal_requirement(self, major: int, minor: int, requirement: str) -> bool:
        """Check if version satisfies >= requirement with optional upper bound."""
        ge_match = re.search(r">=(\d+)\.(\d+)", requirement)
        if not ge_match:
            return False

        req_major, req_minor = map(int, ge_match.groups())
        if (major, minor) < (req_major, req_minor):
            return False

        return self._check_upper_bound_constraint(major, minor, requirement)

    def _check_upper_bound_constraint(self, major: int, minor: int, requirement: str) -> bool:
        """Check upper bound constraint if present."""
        if "<" not in requirement:
            return True

        lt_match = re.search(r"<(\d+)\.(\d+)", requirement)
        if not lt_match:
            return True

        max_major, max_minor = map(int, lt_match.groups())
        return (major, minor) < (max_major, max_minor)

    def _check_compatible_release_requirement(self, major: int, minor: int, requirement: str) -> bool:
        """Check if version satisfies ~= compatible release requirement."""
        compat_match = re.search(r"~=(\d+)\.(\d+)", requirement)
        if not compat_match:
            return False

        compat_major, compat_minor = map(int, compat_match.groups())
        return major == compat_major and minor == compat_minor

    def _check_exact_version_requirement(self, major: int, minor: int, requirement: str) -> bool:
        """Check if version satisfies exact version requirement."""
        exact_match = re.search(r"^(\d+)\.(\d+)$", requirement.strip())
        if not exact_match:
            return False

        req_major, req_minor = map(int, exact_match.groups())
        return (major, minor) == (req_major, req_minor)


@dataclass
class Project(Section):
    """Represents the [project] section in pyproject.toml configuration files."""

    NAME: ClassVar[str] = "project"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = ["readme", "requires-python", "classifiers"]
    readme: ConfigurationFileParameter[str | None]
    requires_python: ConfigurationFileParameter[str | None]
    classifiers: ConfigurationFileParameter[list[str] | None]

    def requires_python_minimum_version(self) -> str | None:
        """Extract the minimum version from requires-python specification."""
        value = self.requires_python.value
        if not value:
            return None
        return RequiresPythonAnalyzer(value).minimum_version()

    def get_requires_python_supported_versions(self, project: Project) -> set[str]:
        """Extract supported Python versions from requires-python specification."""
        value = project.requires_python.value
        if value is None:
            return set()

        return RequiresPythonAnalyzer(value).get_requires_python_supported_versions()
