"""Implements Ruff configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import WhereToolDefault
from pyvelocity.configurations.files.sections import is_not_none_value
from pyvelocity.configurations.files.sections import ruff
from pyvelocity.configurations.tools import Tool

if TYPE_CHECKING:
    from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Ruff(Tool):
    """Ruff configurations."""

    NAME = "Ruff"

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.line_length = ConfigurationFileParameter(
            WhereToolDefault(self),
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " line-length",
            88,
        )
        if configuration_files.py_project_toml:
            self.overwrite(configuration_files.py_project_toml.ruff)

    def overwrite(self, section_ruff: ruff.Ruff | None) -> None:
        if section_ruff and is_not_none_value(section_ruff.line_length):
            self.line_length = section_ruff.line_length
