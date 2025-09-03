"""Implements section for isort."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section


@dataclass
class Isort(Section):
    NAME: ClassVar[str] = "isort"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = ["line_length"]
    line_length: ConfigurationFileParameter[int | None]
