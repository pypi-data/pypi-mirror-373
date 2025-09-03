"""Implements using pyproject.toml check."""

from pyvelocity.checks import Check
from pyvelocity.checks import Result


class UsingPyProjectToml(Check):
    ID = "using-py-project-toml"

    def execute(self) -> Result:
        is_ok = self.configuration_files.py_project_toml is not None
        message = "" if is_ok else ("It's recommended to use pyproject.toml to gather settings for project.")
        return Result(self.ID, is_ok, message)
