"""check that all the freeds directories are in place."""

from typing import List

from freeds.utils import RootConfig
from freeds.selfcheck.check_classes import (
    AllGoodCheckResult,
    CheckList,
    CheckResult,
    PluginCheckResult,
)
from freeds.selfcheck.plugin_classes import get_plugins


def docker_compose_exists_check() -> list[CheckResult]:
    """Check that all docker compose files that should exist actually do."""
    result: list[CheckResult] = []
    for p in get_plugins():
        if not (p.path / "docker-compose.yaml").exists():
            result.append(
                PluginCheckResult(
                    passed=False,
                    plugin_name=p.name,
                    message=f"Plugin {p.name} in {p.path} does not have a docker-compose.yaml file.",
                )
            )
    if len(result) == 0:
        result.append(AllGoodCheckResult("All plugins have a docker-compose.yaml file."))
    return result


def readme_exists_check() -> list[CheckResult]:
    """Check that all plugins have a readme file."""
    result: list[CheckResult] = []
    for p in get_plugins():
        if not (p.path / "README.md").exists():
            result.append(
                PluginCheckResult(
                    passed=False,
                    plugin_name=p.name,
                    message=f"Plugin {p.name} in {p.path} does not have a README.md file.",
                )
            )
    if len(result) == 0:
        result.append(AllGoodCheckResult("All plugins have a README.md file."))
    return result


def check_directories_exist() -> List[CheckResult]:
    """
    check all the freeds folders are in place.
    """
    result: List[CheckResult] = []
    root = RootConfig().root_path
    expected_dirs = [
        ".",
        "local_configs",
        "freeds-config",
        "freeds-config/configs",
        "the-free-data-stack",
        "plugins/airflow",
        "plugins/airflow/config",
        "plugins/airflow/plugins",
        "plugins/airflow/dags",
        "plugins/spark",
        "plugins/spark/jars",
        "plugins/spark/conf",
        "plugins/postgres",
        "plugins/postgres/init",
        "logs",
        "data",
        "data/minio",
        "data/spark",
        "data/local-pypi",
    ]
    for dir_name in expected_dirs:
        dir_path = root / dir_name
        if not dir_path.exists():
            result.append(CheckResult(passed=False, message=f"Directory {dir_path} does not exist."))
    if len(result) == 0:
        result.append(AllGoodCheckResult(message=f"All expected directories are present in {root}."))
    return result


def checks() -> CheckList:
    """Get all checks related to web ui:s."""
    checklst = CheckList(area=__name__)

    checklst.add(
        name="Check freeds directories",
        description="Check that freeds directories and loinks exist, like config, secrets etc.",
        method=check_directories_exist,
    )
    checklst.add(
        name="Missing Docker Compose files",
        description="Check that all plugins have a docker-compose.yaml file.",
        method=docker_compose_exists_check,
    )
    checklst.add(
        name="Missing README.md files",
        description="Check that all plugins have a documentaiton file REAME.md.",
        method=readme_exists_check,
    )
    return checklst
