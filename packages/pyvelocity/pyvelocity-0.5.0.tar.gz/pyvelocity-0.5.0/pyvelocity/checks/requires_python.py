"""Implements requires-python check."""

import re

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.configurations.files.sections.project import Project
from pyvelocity.constants import LATEST_PYTHON_VERSION


class RequiresPython(Check):
    """Check that requires-python includes the latest Python version."""

    ID = "requires-python"

    def execute(self) -> Result:
        if self.configuration_files.py_project_toml is None:
            return Result(self.ID, is_ok=False, message="pyproject.toml is required for requires-python check")

        if self.configuration_files.py_project_toml.project is None:
            return Result(self.ID, is_ok=False, message="Project section is missing in pyproject.toml")

        return self._check_requires_python(self.configuration_files.py_project_toml.project)

    def _check_requires_python(self, project: Project) -> Result:
        """Check that requires-python includes the latest Python version."""
        requires_python_value = project.requires_python.value
        if requires_python_value is None:
            return Result(
                self.ID,
                is_ok=False,
                message="requires-python field is missing in [project] section of pyproject.toml",
            )

        if not self.supports_latest_python(requires_python_value):
            message = (
                f"requires-python should support Python {LATEST_PYTHON_VERSION}, "
                f'but found "{requires_python_value}" in [project] section of pyproject.toml'
            )
            return Result(self.ID, is_ok=False, message=message)

        return Result(self.ID, is_ok=True, message="")

    def supports_latest_python(self, requires_python: str) -> bool:
        """Check if the requires-python specification supports the latest Python version."""
        latest_major, latest_minor = map(int, LATEST_PYTHON_VERSION.split("."))

        if ">=" in requires_python:
            return self._check_greater_equal_support(latest_major, latest_minor, requires_python)
        if "~=" in requires_python:
            return self._check_compatible_release_support(latest_major, latest_minor, requires_python)
        return self._check_exact_version_support(latest_major, latest_minor, requires_python)

    def _check_greater_equal_support(self, latest_major: int, latest_minor: int, requires_python: str) -> bool:
        """Check if latest Python version satisfies >= requirement with optional upper bound."""
        ge_match = re.search(r">=(\d+)\.(\d+)", requires_python)
        if not ge_match:
            return False

        min_major, min_minor = map(int, ge_match.groups())
        if (latest_major, latest_minor) < (min_major, min_minor):
            return False

        return self._check_upper_bound_support(latest_major, latest_minor, requires_python)

    def _check_upper_bound_support(self, latest_major: int, latest_minor: int, requires_python: str) -> bool:
        """Check if latest Python version is within upper bound constraint."""
        if "<" not in requires_python:
            return True

        lt_match = re.search(r"<(\d+)\.(\d+)", requires_python)
        if not lt_match:
            return True

        max_major, max_minor = map(int, lt_match.groups())
        return (latest_major, latest_minor) < (max_major, max_minor)

    def _check_compatible_release_support(self, latest_major: int, latest_minor: int, requires_python: str) -> bool:
        """Check if latest Python version satisfies ~= compatible release requirement."""
        compat_match = re.search(r"~=(\d+)\.(\d+)", requires_python)
        if not compat_match:
            return False

        compat_major, compat_minor = map(int, compat_match.groups())
        return latest_major == compat_major and latest_minor == compat_minor

    def _check_exact_version_support(self, latest_major: int, latest_minor: int, requires_python: str) -> bool:
        """Check if latest Python version matches exact version requirement."""
        exact_match = re.search(r"^(\d+)\.(\d+)$", requires_python.strip())
        if not exact_match:
            return False

        req_major, req_minor = map(int, exact_match.groups())
        return (latest_major, latest_minor) == (req_major, req_minor)
