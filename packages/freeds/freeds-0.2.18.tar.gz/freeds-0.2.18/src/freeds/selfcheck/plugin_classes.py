import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from freeds.config import get_config


class PluginError(Exception):
    pass


def get_repo_dir(repo: str) -> Path:
    start = Path.cwd()
    while True:
        if start.name == repo:
            return start
        if (start / repo).exists():
            return start / repo
        if start.parent is None:
            return None
        start = start.parent


def is_ip(s: str) -> bool:
    # Determine wheter a string is an ip address, accepts IPv4 or IPv6 (in brackets).
    if s.startswith("[") and s.endswith("]"):
        return True
    if s.count(".") == 3 and all(p.isdigit() and 0 <= int(p) <= 255 for p in s.split(".")):
        return True
    return False


class PortMapping:
    """
    Parses Docker Compose port mapping strings.
    Examples:
        127.0.0.1:1234:1234
        1234:1234
        127.0.0.1:1234:0.0.0.0:4321
        1234:0.0.0.0:1234
        127.0.0.1:1234:0.0.0.1:1234/udp
        [::1]:1234:1234
        1234:[::1]:1234
        [::1]:1234:[::2]:4321/udp
    """

    def __init__(self, mapping: str) -> None:
        self.mapping = mapping
        self.host_ip: Optional[str] = None
        self.host_port: int = -1
        self.container_ip: Optional[str] = None
        self.container_port: int = -1
        self.protocol: Optional[str] = None
        self._parse()

    def _parse(self) -> None:
        # Accepts IPv4 and IPv6 addresses in port mapping strings
        # Handles:
        #   [::1]:1234:1234
        #   1234:[::1]:1234
        #   [::1]:1234:[::2]:4321/udp
        mapping = self.mapping
        if "/" in mapping:
            mapping, self.protocol = mapping.rsplit("/", 1)
        # Replace IPv6 colons with a placeholder to avoid splitting inside IPv6
        mapping = re.sub(r"(\[[^\]]+\])", lambda m: m.group(1).replace(":", "#"), mapping)
        parts = mapping.split(":")
        # Restore colons in IPv6 addresses
        parts = [p.replace("#", ":") for p in parts]

        if len(parts) == 2:
            self.host_port = int(parts[0])
            self.container_port = int(parts[1])
        elif len(parts) == 3:
            if is_ip(parts[1]):
                self.host_port = int(parts[0])
                self.container_ip = parts[1]
                self.container_port = int(parts[2])
            else:
                self.host_ip = parts[0]
                self.host_port = int(parts[1])
                self.container_port = int(parts[2])
        elif len(parts) == 4:
            self.host_ip = parts[0]
            self.host_port = int(parts[1])
            self.container_ip = parts[2]
            self.container_port = int(parts[3])
        else:
            raise ValueError(f"Invalid port mapping format: {self.mapping}")

    def __str__(self) -> str:
        return f"{port.host_ip}:{port.host_port} -> {port.container_ip}:{port.container_port} ({port.protocol})"

    def __repr__(self) -> str:
        return (
            f"PortMapping(host_ip={self.host_ip}, host_port={self.host_port}, "
            f"container_ip={self.container_ip}, container_port={self.container_port}, protocol={self.protocol})"
        )


class Repo:
    def __init__(self, name: str):
        self.name = name
        cfg = get_config("repos")
        for repo in cfg.get("repos", []):
            if repo.get("name") == self.name:
                self.config = repo
                break
        else:
            raise PluginError(f"Repo {self.name} not found in configuration.")
        self.path = get_repo_dir(self.name)
        if self.path is None or not self.path.exists():
            raise PluginError(f"No dir found for {self}, looking from {Path.cwd()}.")

    def get_plugins(self) -> List["Plugin"]:
        """Get all plugins in this repo."""
        plugins_config = self.config.get("plugin_config")
        if not plugins_config:
            raise PluginError(f"Config for {self.name} has no plugin_config key.")
        cfg = get_config(plugins_config)
        if cfg.get("plugins") is None:
            raise PluginError(f"Config {plugins_config} for {self} has no plugins key.")
        return [Plugin(repo=self, config=plugin) for plugin in cfg["plugins"]]

    def __str__(self) -> str:
        return f"Repo: {self.name} "

    def __repr__(self) -> str:
        return f"Repo(name={self.name})"


class Plugin:
    def __init__(self, repo: Repo, config: Dict[str, Any]):
        self.name = str(config.get("name"))
        if not self.name:
            raise PluginError("Plugin name is missing in the configuration.")
        self.config = config
        self.repo = repo
        self.path = self.repo.path / self.name
        if not self.path.exists():
            raise PluginError(f"Plugin directory {self.name} not found in {self.repo} expected location: {self.path}.")

    def __str__(self) -> str:
        return f"{self.repo}.{self.name})"

    def __repr__(self) -> str:
        return f"Plugin(name={self.name}, repo={self.repo})"
        pass


class DockerComposeService:
    """
    Information about a docker compose service.
    """

    def __init__(self, docker_compose_info: "DockerComposeInfo", name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.docker_compose_info = docker_compose_info
        self.ports: List[PortMapping] = [PortMapping(port_mapping) for port_mapping in self.config.get("ports", [])]

    def host_name(self) -> Optional[str]:
        """Get the host name for this service."""
        if "hostname" in self.config:
            return str(self.config["hostname"])
        if "container_name" in self.config:
            return str(self.config["container_name"])
        return self.name


class DockerComposeInfo:
    """
    Information about a docker compose file.
    """

    def __init__(self, plugin: "Plugin") -> None:
        self.plugin = plugin
        self.config: Dict[str, Any]
        self.path = self.plugin.path / "docker-compose.yaml"
        if not self.path.exists():
            raise PluginError(f"Docker compose file {self.path} does not exist for plugin {self.plugin.name}.")
        self.services: Dict[str, DockerComposeService] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load the docker compose configuration from the file."""
        from ruamel.yaml import YAML

        yaml = YAML(typ="safe")
        with open(self.path, "r") as file:
            self.config = yaml.load(file)
            srv = self.config.get("services", {})
            if srv is None:
                raise PluginError(
                    f"No services found in docker compose file {self.path} for plugin {self.plugin.name}."
                )
            for name, service_config in srv.items():
                self.services[name] = DockerComposeService(docker_compose_info=self, name=name, config=service_config)


def get_repos() -> List[Repo]:
    """Get all repos defined in the configuration."""
    cfg = get_config("repos")
    repos: List[Repo] = []
    for repo in cfg.get("repos", []):
        repos.append(Repo(name=repo.get("name")))
    return repos


def get_plugins() -> List[Plugin]:
    """Get all plugins defined in the configuration."""
    plugins: List[Plugin] = []
    for repo in get_repos():
        plugins.extend(repo.get_plugins())
    return plugins


def get_docker_compose_infos() -> List[DockerComposeInfo]:
    """Get all plugins defined in the configuration."""
    return [DockerComposeInfo(plugin=p) for p in get_plugins()]


def get_docker_compose_services() -> List[DockerComposeService]:
    """Get all docker compose services defined in the configuration."""
    services: List[DockerComposeService] = []
    for dc_info in get_docker_compose_infos():
        services.extend(dc_info.services.values())
    return services


if __name__ == "__main__":
    tst = get_plugins()
    for p in tst:
        dc = DockerComposeInfo(p)
        print(f"Plugin: {p.name}, Docker Compose Services: {list(dc.services.keys())}")
        for service_name, service in dc.services.items():
            print(f"  Service: {service_name}, Ports: ")
            for port in service.ports:
                print(f"      {port}")
# This code is part of the FREEDS CLI self-check plugin system.
