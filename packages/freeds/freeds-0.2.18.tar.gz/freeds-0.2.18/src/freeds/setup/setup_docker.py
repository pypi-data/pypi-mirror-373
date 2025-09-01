import docker

import freeds.setup.utils as utils
import freeds.utils.log as log

logger = log.setup_logging(__name__)


def is_docker_running() -> bool:
    try:
        client = docker.from_env()
        client.ping()  # Will raise an exception if Docker is not running
        return True
    except Exception as s:
        print(s)
        return False


def prompt_try_again() -> bool:
    return utils.prompt_yesno(description="The Docker daemon is not running.", question="Fix it and we try again?")


def setup_docker() -> bool:
    utils.log_header("Setting up FreeDS docker", "-")
    while not is_docker_running():
        if not prompt_try_again():
            return False
    network_name = "freeds-network"
    client = docker.from_env()

    networks = client.networks.list(names=[network_name])
    if networks:
        logger.info(f"✅ Network '{network_name}' already exists.")
    else:
        logger.info(f"Creating the docker network '{network_name}'")
        client.networks.create(network_name, driver="bridge")
        logger.info(f"✅ Network '{network_name}' created.")
    utils.log_header(title="🟢 Docker setup completed successfully 🌟", char=" ")
    return True


if __name__ == "__main__":
    setup_docker()
