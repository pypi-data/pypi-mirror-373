"""Implements section factory."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import TypeVar

from pyvelocity.configurations.files.sections import ConfigurationFileParameter
from pyvelocity.configurations.files.sections import Section
from pyvelocity.configurations.files.sections import WhereFile

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import MutableMapping

    from pyvelocity.configurations.files import ConfigurationFile
    from pyvelocity.configurations.files.py_project_toml import PyProjectToml
    from pyvelocity.configurations.files.setup_cfg import SetupCfg

TypeVarSection = TypeVar("TypeVarSection", bound=Section)


class SectionFactory(Generic[TypeVarSection]):
    """Factory for Section instance."""

    def __init__(
        self,
        configuration_file: ConfigurationFile,
        node: str | None,
        class_section: type[TypeVarSection],
        config: dict[str, str],
    ) -> None:
        self.configuration_file = configuration_file
        self.node = node
        self.class_section = class_section
        self.config = config

    def create_section(self) -> TypeVarSection:
        configurations = [
            self.create_configuration_parameter(parameter_name)
            for parameter_name in self.class_section.LIST_PARAMETER_NAME
        ]
        return self.class_section(self.configuration_file, *configurations)

    def create_configuration_parameter(self, parameter_name: str) -> ConfigurationFileParameter[str | None]:
        return ConfigurationFileParameter(
            WhereFile(self.configuration_file, self.class_section, self.node),
            parameter_name,
            self.config.get(parameter_name),
        )


class SectionFactoryForPyProjectToml(SectionFactory[TypeVarSection]):
    """Factory for Section instance for PyProjectToml."""

    def create_configuration_parameter(
        self,
        parameter_name: str,
    ) -> ConfigurationFileParameter[str | None]:
        try:
            parameter: str | None = self.config[parameter_name]
        except KeyError:
            parameter = self.config.get(parameter_name.replace("-", "_"))
        return ConfigurationFileParameter(
            WhereFile(self.configuration_file, self.class_section, self.node),
            parameter_name,
            parameter,
        )


class PyProjectTomlSectionFactory:
    """Factory for Section instance for PyProjectToml."""

    @classmethod
    def create(
        cls,
        py_project_toml: PyProjectToml,
        node: str | None,
        class_configuration: type[TypeVarSection],
        tool: dict[str, dict[str, Any] | None],
    ) -> TypeVarSection | None:
        """Creates Section instance for PyProjectToml."""
        config = tool.get(class_configuration.NAME)
        if config is None:
            return None
        return SectionFactoryForPyProjectToml(py_project_toml, node, class_configuration, config).create_section()


class SetupCfgSectionFactory:
    """Factory for Section instance for SetupCfg."""

    @classmethod
    def create(
        cls,
        setup_cfg: SetupCfg,
        node: str | None,
        class_configuration: type[TypeVarSection],
        config_parser: MutableMapping[str, Any],
    ) -> TypeVarSection | None:
        """Creates Section instance for SetupCfg."""
        try:
            config = dict(config_parser[f"{node}.{class_configuration.NAME}" if node else class_configuration.NAME])
        except KeyError:
            return None
        return SectionFactory(setup_cfg, node, class_configuration, config).create_section()
