"""Implements setup.cfg."""

from configparser import ConfigParser
from pathlib import Path

from pyvelocity.configurations.files import ConfigurationFile
from pyvelocity.configurations.files.sections.docformatter import Docformatter
from pyvelocity.configurations.files.sections.factory import SetupCfgSectionFactory
from pyvelocity.configurations.files.sections.flake8 import Flake8
from pyvelocity.configurations.files.sections.isort import Isort
from pyvelocity.configurations.files.sections.pylint import SetupCfgPylintFactory

WHERE_SETUP_CFG = "setup.cfg"


class SetupCfg(ConfigurationFile):
    """setup.cfg."""

    def __init__(self, path_setup_cfg: Path) -> None:
        super().__init__()
        config_parser = ConfigParser()
        config_parser.read(path_setup_cfg)
        self.docformatter = SetupCfgSectionFactory.create(self, None, Docformatter, config_parser)
        self.flake8 = SetupCfgSectionFactory.create(self, None, Flake8, config_parser)
        self.isort = SetupCfgSectionFactory.create(self, None, Isort, config_parser)
        self.pylint = SetupCfgPylintFactory.create(self, config_parser)

    @property
    def name(self) -> str:
        return WHERE_SETUP_CFG
