import os
import subprocess
from pathlib import Path
from typing import List, Optional, cast

import freeds.utils.log as log
from freeds.cli.helpers.stackutils import (
    get_current_stack_config,
    get_current_stack_name,
)
from freeds.config import set_env
from freeds.utils import RootConfig

logger = log.setup_logging(__name__)


def get_plugins() -> Optional[List[str]]:
    set_env()
    current_stack = get_current_stack_name()

    if current_stack is None:
        print("Error: No current stack set. Use `freeds setstack <stackname>` to set a stack.")
        return None

    current_stack_cfg = get_current_stack_config()
    if current_stack_cfg is None:
        print(f"Error: No configuration found for current stack '{current_stack}'.")
        return None

    plugins = current_stack_cfg.get("plugins")
    if not plugins:
        print(f"Error: malformed config, 'plugins' key is missing on current stack '{current_stack}'.")
        return None

    return cast(List[str], plugins)


def execute_docker_compose(params: List[str], plugins: List[str]) -> None:
    set_env()
    start_dir = Path.cwd()

    run_in_current_dir = plugins == ["."]

    plugin_root = RootConfig().root_path / "the-free-data-stack"
    command = params[0]
    if command in ["down", "stop"]:
        plugins = list(reversed(plugins))
    if command in ["up", "start"] and "-d" not in params:
        params.append("-d")

    dc = ["docker", "compose", *params]

    # Execute the command for each plugin
    print(f"Running '{' '.join(dc)}' for plugins: {plugins}")
    for plugin in plugins:
        if not run_in_current_dir:
            plugin_dir = plugin_root / plugin
            if not plugin_dir.exists():
                print(f"Warning: Plugin directory '{plugin_dir}' does not exist. Skipping.")
                continue

            os.chdir(plugin_dir)

        try:
            print(f"Executing in: {Path.cwd()}")
            subprocess.run(dc, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to execute 'docker compose {command}' for plugin '{plugin}':{e}.")
        finally:
            os.chdir(start_dir)
