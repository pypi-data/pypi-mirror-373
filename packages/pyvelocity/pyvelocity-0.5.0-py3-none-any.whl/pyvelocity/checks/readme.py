"""Implements readme check."""

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.configurations.files.sections.project import Project


class Readme(Check):
    """Checks that readme = "README.md" in project section."""

    ID = "readme"

    def execute(self) -> Result:
        if self.configuration_files.py_project_toml is None:
            return Result(self.ID, is_ok=False, message="pyproject.toml is required for readme check")

        if self.configuration_files.py_project_toml.project is None:
            return Result(self.ID, is_ok=False, message="Project section is missing in pyproject.toml")
        return self.check_readme(self.configuration_files.py_project_toml.project)

    def check_readme(self, project: Project) -> Result:
        """Checks that readme = "README.md" in project section."""
        readme_value = project.readme.value
        if readme_value is None:
            return Result(
                self.ID,
                is_ok=False,
                message="readme field is missing in [project] section of pyproject.toml",
            )

        if readme_value != "README.md":
            message = (
                f'readme should be "README.md", but found "{readme_value}" in [project] section of pyproject.toml'
            )
            return Result(self.ID, is_ok=False, message=message)

        return Result(self.ID, is_ok=True, message="")
