"""Assume all ports 8000-8999 are http servers, if the plugin does not respond by http, the port should be changed on the plugin"""

from typing import List

import requests

from freeds.selfcheck.check_classes import (
    AllGoodCheckResult,
    CheckList,
    CheckResult,
    PluginCheckResult,
)
from freeds.selfcheck.plugin_classes import get_docker_compose_services


def check_web_uis_localhost() -> List[CheckResult]:
    """
    Check if the web UI is running and accessible.
    :return: None
    """
    result: List[CheckResult] = []
    for service in get_docker_compose_services():
        for port_mapping in service.ports:
            if 8000 <= port_mapping.host_port <= 8999:
                try:
                    url = f"http://127.0.0.1:{port_mapping.host_port}"
                    response = requests.head(url)
                    result.append(
                        PluginCheckResult(
                            passed=True,
                            message=f"Http response for url {url} is {response.status_code}. {service.docker_compose_info.plugin}, service {service.name}.",
                            plugin_name=service.docker_compose_info.plugin.name,
                        )
                    )
                except requests.exceptions.RequestException:
                    result.append(
                        PluginCheckResult(
                            passed=False,
                            message=f"Failed to connect to url {url}. {service.docker_compose_info.plugin} service: {service.name}.",
                            plugin_name=service.docker_compose_info.plugin.name,
                        )
                    )
    return result


def check_port_mapped_to_localhost() -> List[CheckResult]:
    """
    Check if the ports are mapped to localhost.
    :return: List of CheckResult objects.
    """
    result: List[CheckResult] = []
    for service in get_docker_compose_services():
        for port_mapping in service.ports:
            if port_mapping.host_ip != "127.0.0.1":
                result.append(
                    PluginCheckResult(
                        passed=False,
                        message=f"Service {service.name} is not mapped to localhost, host IP is {port_mapping.host_ip}.",
                        plugin_name=service.docker_compose_info.plugin.name,
                    )
                )
    if len(result) == 0:
        result.append(
            AllGoodCheckResult(
                message="All ports are mapped to 127.0.0.1, i.e. no conteiner ports accessible from outside.",
            )
        )
    return result


def checks() -> CheckList:
    """Get all checks related to web ui:s."""
    checklst = CheckList(area=__name__)

    checklst.add(
        name="HTTP server health",
        description="Check if web UIs and other http servers are running and accessible, accepting any http response as valid.",
        method=check_web_uis_localhost,
    )
    checklst.add(
        name="Ports mapped to localhost",
        description="Check that no ports mapped fgrom conatiners are accessible from outsid the host machine, i.e. all ports are mapped to 127.0.0.1:nnnn",
        method=check_port_mapped_to_localhost,
    )
    return checklst
