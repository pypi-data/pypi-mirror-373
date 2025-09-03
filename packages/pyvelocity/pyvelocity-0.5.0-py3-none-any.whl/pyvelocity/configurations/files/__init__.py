"""Implements configuration files."""

from abc import ABC
from abc import abstractmethod


class ConfigurationFile(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError  # pragma: no cover
