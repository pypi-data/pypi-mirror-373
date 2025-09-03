"""Implements tools."""

from abc import ABC


# Reason: abstruct class. pylint: disable=too-few-public-methods
class Tool(ABC):
    NAME: str
