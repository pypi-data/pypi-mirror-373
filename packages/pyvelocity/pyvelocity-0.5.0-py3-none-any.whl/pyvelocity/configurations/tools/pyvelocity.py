"""Implements pyvelocity configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import WhereToolDefault
from pyvelocity.configurations.files.sections import is_not_none_value
from pyvelocity.configurations.files.sections import pyvelocity
from pyvelocity.configurations.tools import Tool

if TYPE_CHECKING:
    from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Pyvelocity(Tool):
    """Pyvelocity configurations."""

    NAME = "pyvelocity"

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.filter: ConfigurationFileParameter[list[str]] = ConfigurationFileParameter(
            WhereToolDefault(self),
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " filter",
            [],
        )
        if configuration_files.py_project_toml:
            self.overwrite(configuration_files.py_project_toml.pyvelocity)

    def overwrite(self, section_pyvelocity: pyvelocity.Pyvelocity | None) -> None:
        if section_pyvelocity and is_not_none_value(section_pyvelocity.filter):
            self.filter = section_pyvelocity.filter
