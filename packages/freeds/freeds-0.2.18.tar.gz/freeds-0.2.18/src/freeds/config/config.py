import logging
import os
from typing import Any

from freeds.config.api import get_config_from_api, is_api_avaiable
from freeds.config.file.config_classes import get_config as get_config_from_file
from freeds.config.file.config_classes import get_current_config_set
from freeds.utils import RootConfig

logger = logging.getLogger(__name__)


def get_config(config_name: str) -> dict[str, Any]:
    """Get a config, from api server if available or from file if avaiable."""
    if not config_name:
        raise ValueError("A config_name must be provided.")

    if is_api_avaiable():
        logger.debug("Using API to get config: %s", config_name)
        cfg = get_config_from_api(config_name)
        if cfg is None:
            raise FileNotFoundError(f"Config {config_name} not found in API.")
        return cfg
    else:
        logger.debug("Reading config from file: %s", config_name)
        cfg_file = get_config_from_file(config_name)
        if cfg_file is None:
            raise FileNotFoundError(f"Config {config_name} not found in files.")
        return cfg_file.get_config()


def get_env() -> dict[str, str]:
    """Get all envs as a dict.
    Root path and config url are always envs.
    Additionally any string value in the locals folder is converted to a env value, which should provide all secrets."""
    rcfg = RootConfig()

    envs = {
        "FREEDS_ROOT_PATH": str(rcfg.root_path),
        "FREEDS_CONFIGS_PATH": str(rcfg.configs_path),
        "FREEDS_LOCALS_PATH": str(rcfg.locals_path),
        "FREEDS_CONFIG_URL": "http://freeds-config:8005/api/configs/"
        }
    cfg_set = get_current_config_set()
    for cfg_file in (f for f in cfg_set.config_set.values() if f.is_local):
        for key, value in cfg_file.get_config().items():
            if isinstance(value, list) or isinstance(value, dict):
                continue
            env_name = f"FREEDS_{cfg_file.config_name.upper()}_{key.upper()}"
            envs[env_name] = str(value)
    return envs


def set_env() -> None:
    """set all env values"""
    for key, value in get_env().items():
        os.environ[key] = value

if __name__ == '__main__':
    print(get_env())
