"""Implements Flake8 configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import WhereToolDefault
from pyvelocity.configurations.files.sections import flake8
from pyvelocity.configurations.files.sections import is_not_none_value
from pyvelocity.configurations.tools import Tool

if TYPE_CHECKING:
    from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Flake8(Tool):
    """Flake8 configurations."""

    NAME = "Flake8"

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.max_line_length = ConfigurationFileParameter(
            WhereToolDefault(self),
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " max-line-length",
            79,
        )
        if configuration_files.setup_cfg:
            self.overwrite(configuration_files.setup_cfg.flake8)
        if configuration_files.py_project_toml:
            self.overwrite(configuration_files.py_project_toml.flake8)

    def overwrite(self, section_flake8: flake8.Flake8 | None) -> None:
        if section_flake8 and is_not_none_value(section_flake8.max_line_length):
            self.max_line_length = section_flake8.max_line_length
