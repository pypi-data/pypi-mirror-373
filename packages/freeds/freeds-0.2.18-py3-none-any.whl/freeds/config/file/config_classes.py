import os
from pathlib import Path
from typing import Any, Optional

import yaml

import freeds.utils.log as log
from freeds.utils import RootConfig

logger = log.setup_logging(__name__)


class ConfigFile:
    """Class to facade single config file"""

    def __init__(self, file_path: Path, config_set: "ConfigSet", source:str) -> None:
        self.source = source
        self.config_set = config_set
        self.source_file_path = file_path
        self.data: dict[str,Any] = None
        self.load()

    @property
    def config_name(self):
        return self.source_file_path.stem

    @property
    def is_local(self)->bool:
        return self.source=='locals'

    def load(self) -> None:
        if not self.source_file_path.exists():
            raise FileNotFoundError(f"Config file {self.source_file_path} does not exists.")
        with open(self.source_file_path, "r") as file:
            data: dict[str, Any] = yaml.safe_load(file)
            self.data = data
        self.validate()
        if self.data is None:
            raise ValueError(f"Config file malformed or empty (data is None) {self.source_file_path}")

    def validate(self, raise_for_error: bool = True) -> bool:
        """Check that format is valid, returns true if data is None."""
        message = None
        if self.data is None:
            return True

        if message is None and not self.data.get("config"):
            message = "The config has no 'config' root key."

        if raise_for_error and message:
            raise (ValueError(message))
        return message is None

    def get_config(self) -> dict[str, Any]:
        """Get the content of the "config" element in the data"""
        if not self.data:
            self.load()
        data: dict[str, Any] = self.data["config"]  # type: ignore[index]
        return data
    def __str__(self):
        return(f'{self.config_name} ({self.source})')
    def __repr__(self):
        return(f'<ConfigFile {self.__str__()}>')

class ConfigSet:
    """Class for scanning a single set of config files.
    locals override configs
    """

    def __init__(self, configs_path: Path, locals_path: Path) -> None:
        self.configs_path = configs_path
        self.locals_path = locals_path

        configs = self.list_files(path=configs_path, source='configs')
        locals =  self.list_files(path=locals_path, source='locals')
        self.config_set = configs | locals

    def list_files(self, path:Path, source:str) -> dict[str, ConfigFile]:
        result: dict[str, ConfigFile]= {}
        if not isinstance(path, Path):
            path = Path(path)
        for f in path.iterdir():
            if not (f.suffix in {".yaml", ".yml"} and f.is_file()):
                continue
            cfg = ConfigFile(file_path=f, config_set=self, source=source)
            result[cfg.config_name] = cfg
        return result



def freeds_config_set() -> ConfigSet:
    """Get the freeds config set (from config folder in the root freeds folder)."""
    cfg = RootConfig()
    cfg_set = ConfigSet(configs_path=cfg.configs_path, locals_path=cfg.locals_path)
    return cfg_set


def get_current_config_set() -> ConfigSet:
    """get all configured configs, which for now is only freeds"""
    return freeds_config_set()


def get_config(config_name: str) -> Optional[ConfigFile]:
    """Get config object for the config_name"""
    cfg_set = get_current_config_set().config_set
    cfg = cfg_set.get(config_name)
    if cfg:
        cfg.load()
    return cfg
