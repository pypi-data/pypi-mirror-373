"""Implements Pylint configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import WhereToolDefault
from pyvelocity.configurations.files.sections import is_not_none_value
from pyvelocity.configurations.files.sections import pylint
from pyvelocity.configurations.tools import Tool

if TYPE_CHECKING:
    from pyvelocity.configurations.files.aggregation import ConfigurationFiles


class Format(Tool):
    """Pylint configurations."""

    NAME = "Pylint"

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.max_line_length = ConfigurationFileParameter(
            WhereToolDefault(self),
            ConfigurationFileParameter.NAME_TOOL_DEFAULT + " max-line-length",
            100,
        )
        if configuration_files.setup_cfg and configuration_files.setup_cfg.pylint:
            self.overwrite(configuration_files.setup_cfg.pylint.format)
        if configuration_files.py_project_toml and configuration_files.py_project_toml.pylint:
            self.overwrite(configuration_files.py_project_toml.pylint.format)

    def overwrite(self, pylint_format: pylint.Format | None) -> None:
        if pylint_format and is_not_none_value(pylint_format.max_line_length):
            self.max_line_length = pylint_format.max_line_length


# Reason: Aggregation of Pylint sections. pylint: disable=too-few-public-methods
class Pylint:
    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.format = Format(configuration_files)
