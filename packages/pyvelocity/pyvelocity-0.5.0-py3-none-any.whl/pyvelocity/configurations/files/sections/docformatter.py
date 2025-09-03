"""Implements section for docformatter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section


@dataclass
class Docformatter(Section):
    """Section of docformatter."""

    NAME: ClassVar[str] = "docformatter"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = [
        "wrap-descriptions",
        "wrap-summaries",
    ]
    wrap_descriptions: ConfigurationFileParameter[int | None]
    wrap_summaries: ConfigurationFileParameter[int | None]
