"""Implements checks."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from pyvelocity.configurations.aggregation import Configurations
from pyvelocity.configurations.files.aggregation import ConfigurationFiles


@dataclass
class Result:
    # Reason: No problem. pylint: disable=invalid-name
    id: str
    is_ok: bool
    message: str


class Check(ABC):
    """Abstract check class."""

    ID: ClassVar[str]

    def __init__(self, configuration_files: ConfigurationFiles, configurations: Configurations) -> None:
        self.configuration_files = configuration_files
        self.configurations = configurations

    @abstractmethod
    def execute(self) -> Result:
        raise NotImplementedError  # pragma: no cover
