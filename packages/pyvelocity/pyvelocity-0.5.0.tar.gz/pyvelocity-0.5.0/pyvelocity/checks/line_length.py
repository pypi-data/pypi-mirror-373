"""Implements line length check."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING
from typing import Any

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.configurations.files.sections.flake8 import Flake8 as SectionFlake8
from pyvelocity.configurations.tools.flake8 import Flake8 as ToolFlake8

if TYPE_CHECKING:
    from pyvelocity.configurations.files.sections import ConfigurationFileParameter


class Parameter:
    """Configuration parameter wrapper."""

    def __init__(self, parameter: ConfigurationFileParameter[int]) -> None:
        self.parameter = parameter

    @property
    def value(self) -> int:
        return self.parameter.value

    @property
    def message(self) -> str:
        return f"{self.parameter.full_name} = {self.parameter.value!s}"


class Flake8Parameter(Parameter):
    """Flake8 specific parameter with B950 calculation."""

    @property
    def value(self) -> int:
        return self.calculate_bugbear_b950_detection()

    def calculate_bugbear_b950_detection(self) -> int:
        return round(self.parameter.value * 1.1)

    @property
    def message(self) -> str:
        return super().message + f" (B950 in flake8-bugbear detects: {self.value!s})"


class ParameterFactory:
    """Factory for creating parameter instances."""

    @classmethod
    def create(cls, configuration: ConfigurationFileParameter[int]) -> Parameter:
        if cls.is_flake8(configuration):
            return Flake8Parameter(configuration)
        return Parameter(configuration)

    @staticmethod
    def is_flake8(configuration: ConfigurationFileParameter[int]) -> bool:
        where_string = str(configuration.where)
        return SectionFlake8.NAME in where_string or ToolFlake8.NAME in where_string


class Error:
    """Line length consistency error."""

    def __init__(
        self,
        most_common: tuple[Any | None, int],
        parameters: list[Parameter],
    ) -> None:
        self.most_common = most_common
        self.parameters = parameters

    def build_message(self) -> str:
        """Builds message."""
        parameters = (param for param in self.parameters if param.value != self.most_common[0])
        messages = [param.message for param in parameters]
        return f"Line length are not consistent.\n\tMost common = {self.most_common[0]}\n\t" + "\n\t".join(messages)


class LineLength(Check):
    """Check about line length."""

    ID = "line-length"

    def execute(self) -> Result:
        target_parameters: list[ConfigurationFileParameter[int]] = []
        target_parameters = [
            self.configurations.docformatter.wrap_descriptions,
            self.configurations.docformatter.wrap_summaries,
            self.configurations.flake8.max_line_length,
            self.configurations.pylint.format.max_line_length,
            self.configurations.ruff.line_length,
        ]
        parameters = [ParameterFactory.create(parameter) for parameter in target_parameters]
        counter = Counter(parameter.value for parameter in parameters)
        most_common = counter.most_common()[0]
        is_ok = most_common[1] == len(target_parameters)
        message = "" if is_ok else (Error(most_common, parameters).build_message())
        return Result(self.ID, is_ok, message)
