"""Implements aggregation of configuration files."""

from pathlib import Path

from pyvelocity.configurations.files.py_project_toml import WHERE_PY_PROJECT_TOML
from pyvelocity.configurations.files.py_project_toml import PyProjectToml
from pyvelocity.configurations.files.setup_cfg import WHERE_SETUP_CFG
from pyvelocity.configurations.files.setup_cfg import SetupCfg


# Reason: Aggregation class. pylint: disable=too-few-public-methods
class ConfigurationFiles:
    def __init__(self) -> None:
        path_py_project_toml = Path(WHERE_PY_PROJECT_TOML)
        self.py_project_toml = PyProjectToml(path_py_project_toml) if path_py_project_toml.exists() else None
        path_setup_cfg = Path(WHERE_SETUP_CFG)
        self.setup_cfg = SetupCfg(path_setup_cfg) if path_setup_cfg.exists() else None
