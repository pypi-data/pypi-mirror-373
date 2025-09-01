"""Configuration file access functions"""

import fcntl
from pathlib import Path
from typing import Any, Union, cast

import yaml

from freeds.config.file import freeds_root


def strip_yaml(config_name: Union[str, Path]) -> str:
    """Strip the .yaml or .yml extension from the config name."""
    if isinstance(config_name, Path):
        config_name = config_name.name

    if config_name.endswith(".yaml"):
        return config_name[:-5]
    if config_name.endswith(".yml"):
        return config_name[:-4]
    return config_name


def get_file_name(config_name: str) -> Path:
    """Get a file path for a config, searching in secrets and config folders."""
    config_name = strip_yaml(config_name)
    attempt = freeds_root() / "secrets" / (config_name + ".yaml")
    if attempt.is_file():
        return attempt
    return freeds_root() / "config" / (config_name + ".yaml")


def config_exists(config_name: str) -> bool:
    """Check if a config file exists."""
    if config_name is None:
        raise ValueError("Config name cannot be None")
    file_path = get_file_name(config_name)
    return file_path.is_file()


def read_config(config_name: str) -> dict[str, Any]:
    """Read a configuration file, returning the config data as a dict."""
    if config_name is None:
        raise ValueError("Config name cannot be None")
    file_path = get_file_name(config_name)
    if not file_path.is_file():
        raise ValueError(f"Config '{config_name}' not found in config nor secrets. Looked in {file_path}.")

    with open(file_path, "r") as file:
        config: dict[str, str] = yaml.safe_load(file)
    if not config:
        raise ValueError(f"Config '{config_name}' in {file_path} is empty or invalid.")
    if config.get("config") is None:
        raise ValueError(f"Config '{config_name}' in {file_path} does not have a 'config' key.")
    return config


def write_config_to_file(config_name: str, config: dict[str, Any]) -> None:
    """Write a configuration file, meta key is stripped if present."""
    file_path = get_file_name(config_name)
    config.pop("meta", None)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(config, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)


def delete_config(config_name: str) -> None:
    """Delete a configuration file."""
    file_path = get_file_name(config_name)
    if file_path.exists():
        file_path.unlink()
    else:
        print(f"Configuration '{file_path}' not found.")


def list_files(path: Union[str, Path]) -> list[Path]:
    """List all files in a directory."""
    try:
        if isinstance(path, str):
            path = Path(path)
        return [f for f in path.iterdir() if f.is_file()]
    except FileNotFoundError:
        return []


def list_configs() -> list[str]:
    """List all available configurations (including the secrets)."""
    cfg_list = list_files(freeds_root() / "config")
    sec_list = list_files(freeds_root() / "secrets")
    return [strip_yaml(f.name) for f in cfg_list + sec_list if f.suffix in (".yaml", ".yml")]


def get_config_from_file(config_name: str) -> dict[str, Any]:
    """Get the a config key from a file while validating the file."""
    cfg = read_config(config_name=config_name)["config"]
    return cast(dict[str, Any], cfg)


if __name__ == "__main__":
    print(read_config("currentstack"))
