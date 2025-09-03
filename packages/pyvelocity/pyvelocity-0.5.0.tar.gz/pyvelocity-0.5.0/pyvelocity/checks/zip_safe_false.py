"""Implements zip-safe-false check."""

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.configurations.files.sections.setuptools import Setuptools


class ZipSafeFalse(Check):
    """Check that zip-safe is set to false in setuptools configuration."""

    ID = "zip-safe-false"

    def execute(self) -> Result:
        """Execute the zip-safe-false check."""
        if self.configuration_files.py_project_toml is None:
            return Result(self.ID, is_ok=False, message="pyproject.toml is required for zip-safe-false check")

        if self.configuration_files.py_project_toml.setuptools is None:
            return Result(
                self.ID,
                is_ok=False,
                message="[tool.setuptools] section is missing in pyproject.toml",
            )

        return self.check_zip_safe(self.configuration_files.py_project_toml.setuptools)

    def check_zip_safe(self, setuptools: Setuptools) -> Result:
        """Check that zip-safe is set to false."""
        zip_safe_value = setuptools.zip_safe.value

        if zip_safe_value is None:
            return Result(
                self.ID,
                is_ok=False,
                message="zip-safe field is missing in [tool.setuptools] section of pyproject.toml",
            )

        # Convert to string and lowercase for comparison to handle both "false", "False", bool values, etc.
        if str(zip_safe_value).lower() != "false":
            message = (
                f'zip-safe should be "false", but found "{zip_safe_value}" '
                "in [tool.setuptools] section of pyproject.toml. "
                "New users of setuptools should not attempt to create egg files "
                "using the deprecated build_egg command."
            )
            return Result(self.ID, is_ok=False, message=message)

        return Result(self.ID, is_ok=True, message="")
