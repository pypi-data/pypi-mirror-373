"""Implements aggregation of checks."""

from collections.abc import Generator

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.checks.classifiers import Classifiers
from pyvelocity.checks.line_length import LineLength
from pyvelocity.checks.readme import Readme
from pyvelocity.checks.requires_python import RequiresPython
from pyvelocity.checks.typed import Typed
from pyvelocity.checks.using_py_project_toml import UsingPyProjectToml
from pyvelocity.checks.zip_safe_false import ZipSafeFalse
from pyvelocity.configurations.aggregation import Configurations
from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Results:
    """Aggregation of Result."""

    def __init__(self, results: list[Result]) -> None:
        self.results = results

    @property
    def message(self) -> str:
        return "\n".join([result.message for result in self.results if result.message])

    @property
    def is_ok(self) -> bool:
        return all(result.is_ok for result in self.results)


class Checks:
    """Aggregation of Check."""

    def __init__(self, configuration_files: ConfigurationFiles, configurations: Configurations) -> None:
        check_classes: list[type[Check]] = [
            UsingPyProjectToml,
            LineLength,
            Readme,
            RequiresPython,
            Classifiers,
            ZipSafeFalse,
            Typed,
        ]
        self.checks = (
            check_class(configuration_files, configurations)
            for check_class in check_classes
            if check_class.ID not in configurations.pyvelocity.filter.value
        )

    def execute(self) -> Generator[Result, None, None]:
        return (check.execute() for check in self.checks)
