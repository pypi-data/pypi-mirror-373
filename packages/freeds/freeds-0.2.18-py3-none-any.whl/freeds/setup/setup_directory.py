
from pathlib import Path
import sys
import git
import yaml

import freeds.setup.utils as utils
from freeds.utils.root_config import RootConfig
import freeds.utils.log as log

logger = log.setup_logging(__name__)

def prompt_continue(user_dir: Path, this_dir: Path) -> bool:
    return utils.prompt_yesno(
        description=(
            f"Current folder: ({Path.cwd()})\n"
            f"Some repos will be cloned to this folder and we'll setup the config dir here.\n"
            f"One config file '.freeds' will be created in your user directory: {str(user_dir)}.\n"
            f"No other changes will be made outside this current folder unless you configure it."
        ),
        question="Shall we proceed",
    )


def prompt_keep_existing_config_file(file: Path) -> bool:
    if not file.exists():
        return True
    return


def setup_root_dir() -> bool:
    utils.log_header("Setting up the FreeDS root directory", "-")
    # this is the root folder, we're cloning repos and setting up lgos configs etc in this folder.
    root_path = Path.cwd()

    if not prompt_continue(user_dir=Path.home(), this_dir=root_path):
        return False

    git_repos = {
        "freeds-config": "https://github.com/jens-koster/freeds-config.git",
        "the-free-data-stack": "https://github.com/jens-koster/the-free-data-stack.git",
        "freeds-lab-databrickish": "https://github.com/jens-koster/freeds-lab-databrickish.git",
    }
    logger.info("Cloning git repos...")
    for name, url in git_repos.items():
        if (root_path / name).exists():
            logger.info(f"✅ Repo {name} already exists, skipping.")
            continue
        logger.info(f"Cloning repo: {url} into {name}...")
        logger.info(f"✅ Repo {name} cloned.")
        git.Repo.clone_from(url, name)

    root_config = RootConfig()

    if root_config.is_loaded:
        if not utils.prompt_yesno(
            description=f"The freeds config file already exists: {str(root_config.freeds_file_path())}.", question="Keep the existing config"
        ):
            root_config.set_default(root_path=root_path)

    logger.info(f"✅ Loaded config file: {root_config.freeds_file_path()}")
    logger.info(f"✅ Freeds root path: {root_config.root_path}")
    logger.info(f"✅ Config path (normally the config repo): {root_config.configs_path}")
    logger.info(f"✅ Locals (secrets) path: {root_config.locals_path}")

    logger.info("Creating directory structure")
    tfds_repo_root = root_path / "the-free-data-stack"
    data_root = root_path / "data"
    plugins_root = root_path / "plugins"

    paths = [
        plugins_root,
        plugins_root / "airflow",
        plugins_root / "airflow/logs",
        plugins_root / "postgres",
        plugins_root / "spark",
        data_root / "minio",
        data_root / "spark",
        data_root / "postgres",
        data_root / "local-pypi",
    ]

    for path in paths:
        logger.info(f"Creating {path}.")
        path.mkdir(parents=True, exist_ok=True)

    # Airflow
    airflow_symlink_root = plugins_root / "airflow"
    airflow_target_root = tfds_repo_root / "airflow"
    utils.relink(symlink=airflow_symlink_root / "dags", target=airflow_target_root / "dags")
    utils.relink(symlink=airflow_symlink_root / "config", target=airflow_target_root / "config")
    utils.relink(symlink=airflow_symlink_root / "plugins", target=airflow_target_root / "plugins")

    # postgres
    utils.relink(symlink=plugins_root / "postgres" / "init", target=tfds_repo_root / "postgres" / "init")

    # spark
    spark_root = plugins_root / "spark"
    utils.relink(symlink=spark_root / "conf", target=tfds_repo_root / "spark" / "conf")
    utils.relink(symlink=spark_root / "jars", target=tfds_repo_root / "spark" / "jars")

    logger.info(f"Setting up config dir for secrets: {root_config.locals_path}")
    # configs stay in the repo dir and are normally not changed.
    # we just copy the secrets files to locals which.
    root_config.locals_path.mkdir(parents=True, exist_ok=True)
    local_files = ["s3.yaml", "minio.yaml", "airflow.yaml", "postgres.yaml"]
    for file in local_files:
        utils.soft_copy(
            source=root_config.configs_path / file,
            target=root_config.locals_path / file
        )
    utils.log_header(title="🟢 Directory setup completed successfully 🌟", char=" ")
    return True

if __name__ == "__main__":
    setup_root_dir()
