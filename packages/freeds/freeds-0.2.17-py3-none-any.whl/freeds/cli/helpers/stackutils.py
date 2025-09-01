#!/usr/bin/env python3
from typing import Any, Optional, Union, cast

from freeds.config import get_config
from freeds.setup.utils import write_local_config
def get_current_stack_name() -> Union[None, str]:
    """Get the current stack name from the currentstack.yaml file."""
    cur_stack = get_config("currentstack")
    if not cur_stack:
        return None
    stack = cur_stack.get("current_stack")
    return None if stack is None else str(stack)


def get_stack_config(stack_name: str) -> Optional[dict[str, Any]]:
    if stack_name is None:
        return None
    cfg = get_config("stacks")
    return cast(dict[str, Any], cfg.get(stack_name))


def get_current_stack_config() -> Optional[dict[str, Any]]:
    """Get the current stack config from the currentstack.yaml file."""
    cur_stack = get_current_stack_name()
    if not cur_stack:
        return None
    return get_stack_config(cur_stack)


def get_plugins(current_only: bool = True) -> list[dict[str, Any]]:
    """Get a list the plugin info for current stack or all plugins."""
    plugins = get_config("plugins").get("plugins", [])
    if not current_only:
        return cast(list[dict[str, Any]], plugins)

    current_cfg = get_current_stack_config()
    if not current_cfg:
        raise ValueError("No current stack set or no stack config defined.")
    current_plugins = current_cfg.get("plugins", [])

    return list(p for p in plugins if p["name"] in current_plugins)


def get_stack_names() -> list[str]:
    """Get a list of stacknames"""
    stacks = get_config("stacks")
    return list(stacks.keys())


def set_current_stack(stack_name: str) -> None:
    """Set freeds to use the provided stack."""
    stack_found = False
    for name in get_stack_names():
        if stack_name == name:
            stack_found = True
            break
    if not stack_found:
        print(f"Error: Stack '{stack_name}' not found, use `freeds ls` to see available stacks.")

    # Lock the file to prevent race conditions
    config = {
        "annotation": "the current stack for freeds cli, use setstack to change it, editing here is fine too",
        "config": {"current_stack": stack_name},
    }

    write_local_config(config_name="currentstack", data=config)
    print(f"Current stack set to '{stack_name}'.")
