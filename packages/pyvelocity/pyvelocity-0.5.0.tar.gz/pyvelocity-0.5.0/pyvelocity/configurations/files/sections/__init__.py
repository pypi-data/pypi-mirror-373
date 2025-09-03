"""Implements configuration file sections."""

from __future__ import annotations

import sys
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from pyvelocity.configurations.files import ConfigurationFile
    from pyvelocity.configurations.tools import Tool

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard  # pragma: no cover


@dataclass
class Section(ABC):
    NAME: ClassVar[str]
    LIST_PARAMETER_NAME: ClassVar[list[str]]
    configuration_file: ConfigurationFile


@dataclass
class Where(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


@dataclass
class WhereFile(Where):
    """Information of where about file."""

    file: ConfigurationFile
    section: type[Section]
    node: str | None

    def __str__(self) -> str:
        if self.node:
            return f"{self.file.name} {self.node}.{self.section.NAME}"
        return f"{self.file.name} {self.section.NAME}"


@dataclass
class WhereToolDefault(Where):
    tool: Tool

    def __str__(self) -> str:
        return self.tool.NAME


T = TypeVar("T")


@dataclass
class ConfigurationFileParameter(Generic[T]):
    """The parameter of configuration file."""

    NAME_TOOL_DEFAULT = "tool default"
    where: Where
    name: str
    value: T

    @property
    def full_name(self) -> str:
        return f"{self.where} {self.name}"


def is_not_none_value(instance: ConfigurationFileParameter[T | None]) -> TypeGuard[ConfigurationFileParameter[T]]:
    """This function can't be implemented as instance method.

    Since TypeGuard does not narrow types of self or cls implicit arguments.

    see:
    - Type narrowing - mypy 0.980+dev.c2949e969ffcba848595d0851a9193fe1bc3e0a1.dirty documentation
      https://mypy.readthedocs.io/en/latest/type_narrowing.html#typeguards-as-methods
    """
    return instance.value is not None
