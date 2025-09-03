"""Implements section for Ruff."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section


@dataclass
class Ruff(Section):
    NAME: ClassVar[str] = "ruff"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = ["line-length"]
    line_length: ConfigurationFileParameter[int | None]
