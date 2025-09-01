import getpass
import secrets
import shutil
import string
from pathlib import Path
from typing import Any, Optional
from freeds.utils.root_config import RootConfig
import yaml

import freeds.utils.log as log

logger = log.setup_logging(__name__)
header_logger = log.setup_logging("FreeDS")
AUTO_YES = False

def generate_password(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def relink(symlink: Path, target: Path) -> None:
    """Restablish a directory symlink."""
    logger.info(f'symlinking {symlink}->{target}')
    if symlink.is_symlink():
        symlink.unlink()
    symlink.symlink_to(target, target_is_directory=True)


def soft_copy(source: Path, target: Path) -> None:
    if target.exists():
        logger.info(f"{target} already exists, skipping.")
        return
    logger.info(f"copying {source} to {target}.")
    shutil.copy2(source, target)


def prompt_credential(service_desc: str, default_user: str) -> dict[str, Any]:
    """Prompt user for username and password, default username is lower case service name.
    returns a dict: {'config': {'user':'username', 'password':'user entered password'}"""

    if AUTO_YES:
        return {"config": {"user": default_user, "password": generate_password()}}

    user = input(f"Enter a username for {service_desc} [{default_user}]: ") or default_user
    password = getpass.getpass(f"Enter password for {service_desc} [auto generate]: ")
    if not password:
        password = generate_password()

    return {"config": {"user": user, "password": password}}


def prompt_press_any(description: str) -> None:
    """Print text and ask user to press any key ot continue."""
    if AUTO_YES:
        return
    input("ℹ️ " + description + "\nPress ENTER to continue")


def prompt_yesno(description: str, question: str) -> bool:
    """Provide descripiton and question, then prompt user for yes or no answer."""
    if AUTO_YES:
        return True
    prompt = f"\n❓{description}\n{question}❓ [Y/n]"
    answer = input(prompt).strip().lower()
    return answer in("y","")


def log_header(title: str, char: str, space: int = 10, vert_char: Optional[str] = None) -> None:
    """Log message in a "box" using the FreeDS logger, a bit nicer output for starting a section of actions."""
    if vert_char is None:
        vert_char = char
    width = len(title) + space * 2
    header_logger.info(char * width)
    row = vert_char + " " * (space - 1) + title + " " * (space - 1) + vert_char
    header_logger.info(row)
    header_logger.info(char * width)


def read_local_config(config_name: str) -> Optional[dict[str, Any]]:
    root_config = RootConfig()

    file_path = root_config.locals_path / (config_name + ".yaml")
    if not file_path.exists():
        return None
    with open(file_path, "r") as file:
        config: dict[str, str] = yaml.safe_load(file)
    return config


def write_local_config(config_name: str, data: dict[str, Any]) -> None:
    root_config = RootConfig()
    file_path = root_config.locals_path / (config_name + ".yaml")
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


# if __name__ == '__main__':
#     log_header('This is a header', '=', 20, '-')
#     log_header('This is a header', '-')
#     log_header('This is a header', ' ')
#     logger.info('regular logging')
