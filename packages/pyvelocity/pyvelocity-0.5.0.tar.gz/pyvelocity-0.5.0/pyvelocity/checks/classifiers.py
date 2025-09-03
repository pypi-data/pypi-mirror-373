"""Implements classifiers check."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pyvelocity.checks import Check
from pyvelocity.checks import Result

if TYPE_CHECKING:
    from pyvelocity.configurations.files.sections.project import Project


class Classifiers(Check):
    """Check that classifiers are consistent with requires-python."""

    ID = "classifiers"

    def execute(self) -> Result:
        if self.configuration_files.py_project_toml is None:
            return Result(self.ID, is_ok=False, message="pyproject.toml is required for classifiers check")

        if self.configuration_files.py_project_toml.project is None:
            return Result(self.ID, is_ok=False, message="Project section is missing in pyproject.toml")

        return self._check_classifiers(self.configuration_files.py_project_toml.project)

    def _check_classifiers(self, project: Project) -> Result:
        """Check that classifiers are consistent with requires-python."""
        classifiers_value = project.classifiers.value
        if classifiers_value is None:
            return Result(
                self.ID,
                is_ok=False,
                message="classifiers field is missing in [project] section of pyproject.toml",
            )

        if not isinstance(classifiers_value, list):
            return Result(
                self.ID,
                is_ok=False,
                message="classifiers field must be a list in [project] section of pyproject.toml",
            )
        return self.compare_classifiers_with_requires_python(project, classifiers_value)

    def compare_classifiers_with_requires_python(self, project: Project, classifiers_value: list[str]) -> Result:
        """Compare classifiers against requires-python to ensure consistency."""
        requires_python_value = project.requires_python.value
        if requires_python_value is None:  # pylint: disable=duplicate-code
            return Result(
                self.ID,
                is_ok=False,
                message="requires-python field is missing in [project] section of pyproject.toml",
            )

        supported_versions = project.get_requires_python_supported_versions(project)
        if not supported_versions:
            return Result(
                self.ID,
                is_ok=False,
                message=(
                    f"Could not parse requires-python '{requires_python_value}' in [project] section of pyproject.toml"
                ),
            )

        classifier_versions = self.get_classifier_python_versions(classifiers_value)
        return self._validate_version_consistency(supported_versions, classifier_versions, requires_python_value)

    def _validate_version_consistency(
        self,
        supported_versions: set[str],
        classifier_versions: set[str],
        requires_python_value: str,
    ) -> Result:
        """Validate that classifier versions match supported versions."""
        missing_versions = supported_versions - classifier_versions
        extra_versions = classifier_versions - supported_versions

        if not missing_versions and not extra_versions:
            return Result(self.ID, is_ok=True, message="")

        error_parts = self._build_error_message_parts(missing_versions, extra_versions)
        message = (
            "Python version classifiers don't match requires-python "
            f"'{requires_python_value}': {'; '.join(error_parts)}"
        )
        return Result(self.ID, is_ok=False, message=message)

    def _build_error_message_parts(self, missing_versions: set[str], extra_versions: set[str]) -> list[str]:
        """Build error message parts for missing and extra versions."""
        error_parts = []
        if missing_versions:
            sorted_missing = sorted(missing_versions, key=lambda v: tuple(map(int, v.split("."))))
            missing_classifiers = [f"Programming Language :: Python :: {v}" for v in sorted_missing]
            error_parts.append(f"missing classifiers: {', '.join(missing_classifiers)}")
        if extra_versions:
            sorted_extra = sorted(extra_versions, key=lambda v: tuple(map(int, v.split("."))))
            extra_classifiers = [f"Programming Language :: Python :: {v}" for v in sorted_extra]
            error_parts.append(f"extra classifiers: {', '.join(extra_classifiers)}")
        return error_parts

    def get_classifier_python_versions(self, classifiers: list[str]) -> set[str]:
        """Extract Python versions from Programming Language :: Python :: X.Y classifiers."""
        versions = set()
        python_version_pattern = r"^Programming Language :: Python :: (\d+\.\d+)$"

        for classifier in classifiers:
            match = re.match(python_version_pattern, classifier.strip())
            if match:
                versions.add(match.group(1))

        return versions
