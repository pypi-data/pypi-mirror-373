"""Implements sections for Pylint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section
from pyvelocity.configurations.files.sections.factory import PyProjectTomlSectionFactory
from pyvelocity.configurations.files.sections.factory import SetupCfgSectionFactory

if TYPE_CHECKING:  # pragma: no cover
    from configparser import ConfigParser

    from pyvelocity.configurations.files.py_project_toml import PyProjectToml
    from pyvelocity.configurations.files.setup_cfg import SetupCfg


@dataclass
class Format(Section):
    NAME: ClassVar[str] = "format"
    LIST_PARAMETER_NAME: ClassVar[list[str]] = ["max-line-length"]
    max_line_length: ConfigurationFileParameter[int | None]


# Reason: Aggregation class. pylint: disable=too-many-instance-attributes
@dataclass
class Pylint:
    """Node of pylint."""

    NAME: ClassVar[str] = "pylint"
    main: None
    basic: None
    classes: None
    design: None
    exceptions: None
    format: Format | None
    imports: None
    logging: None
    method_args: None
    miscellaneous: None
    refactoring: None
    similarities: None
    spelling: None
    string: None
    typecheck: None
    variables: None
    broad_try_clause: None
    code_style: None
    deprecated_builtins: None
    parameter_documentation: None
    typing: None


class PyProjectTomlPylintFactory:
    """Factory for pylint node."""

    @staticmethod
    def create(
        py_project_toml: PyProjectToml,
        node: str,
        tool: dict[str, dict[str, Any] | None],
    ) -> Pylint | None:
        """Creates node of Pylint."""
        config = tool.get(Pylint.NAME)
        if not config:
            return None
        return Pylint(
            None,
            None,
            None,
            None,
            None,
            PyProjectTomlSectionFactory.create(py_project_toml, f"{node}.{Pylint.NAME}", Format, config),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )


class SetupCfgPylintFactory:
    """Factory for pylint node."""

    @staticmethod
    def create(setup_cfg: SetupCfg, config_parser: ConfigParser) -> Pylint | None:
        """Creates node of Pylint."""
        pylint = Pylint(
            None,
            None,
            None,
            None,
            None,
            SetupCfgSectionFactory.create(setup_cfg, Pylint.NAME, Format, config_parser),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        if all(v is None for v in pylint.__dict__.values()):
            return None
        return pylint
