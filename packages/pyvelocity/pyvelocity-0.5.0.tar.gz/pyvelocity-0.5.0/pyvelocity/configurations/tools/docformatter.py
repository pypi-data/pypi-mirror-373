"""Implements docformatter configurations.

see:
  - Welcome to docformatter! — docformatter documentation
    https://docformatter.readthedocs.io/en/latest/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import WhereToolDefault
from pyvelocity.configurations.files.sections import docformatter
from pyvelocity.configurations.files.sections import is_not_none_value
from pyvelocity.configurations.tools import Tool

if TYPE_CHECKING:
    from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Docformatter(Tool):
    """Docformatter configurations."""

    NAME = "docformatter"

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        where_tool_default = WhereToolDefault(self)
        self.wrap_descriptions = ConfigurationFileParameter(
            where_tool_default,
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " wrap descriptions",
            72,
        )
        self.wrap_summaries = ConfigurationFileParameter(
            where_tool_default,
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " wrap summaries",
            79,
        )
        if configuration_files.setup_cfg:
            self.overwrite(configuration_files.setup_cfg.docformatter)
        if configuration_files.py_project_toml:
            self.overwrite(configuration_files.py_project_toml.docformatter)

    def overwrite(self, section_docformatter: docformatter.Docformatter | None) -> None:
        if section_docformatter:
            if is_not_none_value(section_docformatter.wrap_descriptions):
                self.wrap_descriptions = section_docformatter.wrap_descriptions
            if is_not_none_value(section_docformatter.wrap_summaries):
                self.wrap_summaries = section_docformatter.wrap_summaries
