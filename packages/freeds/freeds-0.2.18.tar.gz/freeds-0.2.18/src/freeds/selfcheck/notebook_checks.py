"""RUnning checks defined in notebooks to get them running inside the docker network."""

import json
import os
import shutil
from importlib import resources
from pathlib import Path
from typing import List

import docker
import nbformat

from freeds.selfcheck.check_classes import (
    Check,
    CheckList,
    CheckResult,
    ExceptionCheckResult,
    MisconfiguredCheckResult,
    PluginCheckResult,
)


def get_all_notebooks() -> List[Path]:
    """
    Get a list of all notebook paths in the specified package's notebooks directory.
    """
    # Get the notebooks directory as a resources Traversable
    notebooks_dir = resources.files("freeds").joinpath("notebooks")

    # use as_file to get a Path object
    with resources.as_file(notebooks_dir) as notebooks_path:
        # we know they're not zipped so we can use the filenames
        return list(notebooks_path.rglob("*.ipynb"))


def get_result(output_nb: Path) -> CheckResult:
    """Open the output notebook, extract the result of the last cell (assumed to be JSON), and parse it to a dict."""
    nb = nbformat.read(output_nb, as_version=4)

    last_cell = nb.cells[-1]
    outputs = last_cell.get("outputs", [])
    result_dict = {}

    for output in outputs:
        # The result is usually in 'text' or 'data' fields
        try:
            if "text" in output:
                result_dict = json.loads(output["text"])
                break
            elif "data" in output and "text/plain" in output["data"]:
                result_dict = json.loads(output["data"]["text/plain"])
                break
        except json.JSONDecodeError as e:
            return ExceptionCheckResult(
                message=f"Notebook: {output_nb.name}, Invalid json in last cell:\n{output}", exception=e
            )
    if result_dict is None:
        return MisconfiguredCheckResult(
            message="Notebook: {output_nb.name}, No result found in last cell, it might not have run."
        )
    message = result_dict.get("message")
    passed = bool(result_dict.get("passed"))
    if not message or passed is None:
        return MisconfiguredCheckResult(
            message=f"Mandatory key message or passed i smissing in last cell output: {result_dict}."
        )
    plugin = result_dict.get("plugin")
    description = result_dict.get("description", "Notebook output failed to provide a description.")
    area = result_dict.get("area", "notebook")
    chk = Check(name=output_nb.name, area=area, description=description)
    result: CheckResult = (
        PluginCheckResult(passed=passed, message=message, plugin_name=plugin)
        if plugin
        else CheckResult(passed=passed, message=message)
    )
    chk.add_results(result)
    return result


def run_book(notebook_path: Path, tmp_dir: Path) -> CheckResult:
    print(f"Running notebook {notebook_path}")
    input_dir = tmp_dir / "in"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir = tmp_dir / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(notebook_path, input_dir)

    cmd = ["papermill", f"/tmp/input/{notebook_path.name}", f"/tmp/output/{notebook_path.name}"]

    env_vars = {
        "FREEDS_CONFIG_URL": os.environ.get("FREEDS_CONFIG_URL", "http://freeds-config:8005/api/configs"),
    }

    client = docker.from_env()
    try:
        volumes = {
            str(input_dir): {"bind": "/tmp/input", "mode": "rw"},
            str(output_dir): {"bind": "/tmp/output", "mode": "rw"},
        }

        container = client.containers.run(
            image="freeds/jupyter-spark:latest",
            name=f"check-{notebook_path.name}",
            command=cmd,
            auto_remove=True,
            network="freeds-network",
            environment=env_vars,
            volumes=volumes,
            tty=False,
            detach=True,
        )

        for line in container.logs(stream=True):
            print(line.decode().strip())
        result = container.wait()
        if result.get("StatusCode", 1) != 0:
            raise RuntimeError(f"Notebook container exited with code {result['StatusCode']}")
        return get_result(output_dir / notebook_path.name)

    except docker.errors.DockerException as e:
        print(f"Docker error: {e}")
        raise
    finally:
        client.close()


def checks(tmp_dir: Path = Path("/tmp/freeds")) -> CheckList:
    check_list = CheckList("notebook")

    nb_paths = get_all_notebooks()
    nb_paths.sort()

    for nb_path in nb_paths:
        check_result = run_book(notebook_path=nb_path, tmp_dir=tmp_dir)
        if not check_result.check:
            check_result.check = Check(
                name=nb_path.name,
                description="Notebook check failed: {nb_path.name}",
                area="notebook",
                results=[check_result],
            )
        check_list.checks.append(check_result.check)

    return check_list


if __name__ == "__main__":
    run_book(
        notebook_path=Path("/Users/jens/src/FreeDS/src/freeds/notebooks/100.basics/a.hello_world.ipynb"),
        tmp_dir=Path("/tmp/freeds"),
    )
