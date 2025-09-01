from typing import Any

import docker

from freeds.config import get_config
from freeds.selfcheck.check_classes import (
    AllGoodCheckResult,
    CheckList,
    CheckResult,
    MisconfiguredCheckResult,
    PluginCheckResult,
)


def find_key(data: Any, target_key: str) -> Any:
    """
    Recursively traverse a nested dict/list and yield all values for target_key.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                yield value
            if isinstance(value, (dict, list)):
                yield from find_key(value, target_key)
    elif isinstance(data, list):
        for item in data:
            yield from find_key(item, target_key)


def get_merged_list(data: dict[str, Any], key: str) -> list[str]:

    lists = find_key(data, key)
    values = []
    for value in lists:
        if isinstance(value, list):
            values.extend(value)
        else:
            print(f"Warning: Expected only lists for key '{key}', but got {type(value).__name__}.")
    return values


def check_duplicate_ports() -> list[CheckResult]:
    """
    Check if there are duplicate ports in the plugins configuration.
    :return: List of PluginCheckResult indicating if there are duplicate ports.
    """
    cfg = get_config("plugins")
    results: list[CheckResult] = []
    port_index: dict[str, Any] = {}
    for plugin in cfg.get("plugins", []):
        ports = plugin.get("ports", [])
        for port in ports:
            port_number = port.get("number")
            if not port_number:
                results.append(
                    MisconfiguredCheckResult(
                        message=f"Port number is missing in config: '{port}'.", plugin_name=plugin.get("name")
                    )
                )
                continue
            pl = port_index.get(port_number)
            if not pl:
                port_index[port_number] = [plugin]
            else:
                pl.append(plugin)

    for key, value in port_index.items():
        if len(value) == 1:
            continue
        pluginstr = ", ".join([p.get("name") for p in value])
        for plugin in value:
            results.append(
                PluginCheckResult(False, f"Duplicate port found in {pluginstr}: {key}", plugin_name=plugin.get("name"))
            )
    if len(results) == 0:
        results.append(AllGoodCheckResult("No duplicate ports found."))

    return results


def check_duplicate_container_names() -> list[CheckResult]:
    """
    Check if there are duplicate containers in the plugins configuration.
    :return: List of PluginCheckResult indicating if there are duplicate containers.
    """
    cfg = get_config("plugins")
    results: list[CheckResult] = []
    container_index: dict[str, Any] = {}
    for plugin in cfg.get("plugins", []):
        containers = plugin.get("containers", [])
        for container in containers:
            pl = container_index.get(container)
            if not pl:
                container_index[container] = [plugin]
            else:
                pl.append(plugin)

    for key, value in container_index.items():
        if len(value) == 1:
            continue
        pluginstr = ", ".join([p.get("name") for p in value])
        for plugin in value:
            results.append(
                PluginCheckResult(
                    False, f"Duplicate container found in {pluginstr}: {key}", plugin_name=plugin.get("name")
                )
            )
    if len(results) == 0:
        results.append(AllGoodCheckResult("No duplicate containers found."))

    return results


def check_missing_containers() -> list[CheckResult]:
    """
    Check if all containers in the list are running.
    :param container_names: List of container names or IDs.
    :return: True if all are running, False otherwise.
    """
    cfg = get_config("plugins")
    running_containers = [
        container.name for container in docker.from_env().containers.list() if container.status == "running"
    ]
    results: list[CheckResult] = []
    for plugin in cfg.get("plugins", []):
        containers = plugin.get("containers", [])
        if not containers:
            results.append(
                PluginCheckResult(
                    False,
                    f"No containers specified in plugins.yaml for plugin'{plugin.get('name')}'.",
                    plugin_name=plugin.get("name"),
                )
            )
            continue
        for container in plugin.get("containers", []):
            if container in running_containers:
                results.append(
                    PluginCheckResult(True, f"Container '{container}' is running.", plugin_name=plugin.get("name"))
                )
            else:
                results.append(
                    PluginCheckResult(
                        False, f"Expected container '{container}' is not running.", plugin_name=plugin.get("name")
                    )
                )
    return results


def checks() -> CheckList:
    """Run all checks related to docker."""
    checklst = CheckList(__name__)
    checklst.add(
        name="Expected Docker Containers",
        description="Check if all expected Docker containers are running.",
        method=check_missing_containers,
    )

    checklst.add(
        name="Duplicate Ports",
        description="Check that no plugins claim the same ports.",
        method=check_duplicate_ports,
    )

    checklst.add(
        name="Duplicate Container Names",
        description="Check that no plugins claim the same container name.",
        method=check_duplicate_container_names,
    )
    return checklst
