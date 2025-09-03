"""Implements aggregation of tools."""

from pyvelocity.configurations.files.aggregation import ConfigurationFiles
from pyvelocity.configurations.tools.black import Black
from pyvelocity.configurations.tools.docformatter import Docformatter
from pyvelocity.configurations.tools.flake8 import Flake8
from pyvelocity.configurations.tools.isort import Isort
from pyvelocity.configurations.tools.pylint import Pylint
from pyvelocity.configurations.tools.pyvelocity import Pyvelocity
from pyvelocity.configurations.tools.ruff import Ruff


# Reason: Aggregation class. pylint: disable=too-few-public-methods
class Configurations:
    """Aggregation of tools."""

    def __init__(self, configuration_files: ConfigurationFiles) -> None:
        self.black = Black(configuration_files)
        self.docformatter = Docformatter(configuration_files)
        self.flake8 = Flake8(configuration_files)
        self.isort = Isort(configuration_files)
        self.pylint = Pylint(configuration_files)
        self.pyvelocity = Pyvelocity(configuration_files)
        self.ruff = Ruff(configuration_files)
