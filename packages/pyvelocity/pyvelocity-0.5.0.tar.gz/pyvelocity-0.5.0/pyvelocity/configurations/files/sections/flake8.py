"""Implements section for Flake8."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section


@dataclass
class Flake8(Section):
    """Section of flake8."""

    NAME: ClassVar[str] = "flake8"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = ["max-line-length"]
    _max_line_length: ConfigurationFileParameter[str | None]

    @property
    def max_line_length(self) -> ConfigurationFileParameter[int | None]:
        return ConfigurationFileParameter(
            self._max_line_length.where,
            self._max_line_length.name,
            None if self._max_line_length.value is None else int(self._max_line_length.value),
        )
