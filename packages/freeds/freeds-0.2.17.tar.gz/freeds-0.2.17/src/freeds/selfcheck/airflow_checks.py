import datetime as dt
import logging
import time
from typing import List, Optional, cast

from airflow_client.client.api import dag_api, dag_run_api, task_instance_api
from airflow_client.client.api_client import ApiClient
from airflow_client.client.configuration import Configuration
from airflow_client.client.model.dag_run import DAGRun
from airflow_client.client.model.task_instance import TaskInstance

from freeds.config import get_config
from freeds.selfcheck.check_classes import (
    CheckList,
    CheckResult,
    PluginCheckResult,
)

logger = logging.getLogger(__name__)


def get_dag_is_paused(dag_id: str) -> Optional[bool]:
    """Retrieve the dag enabled/disabled state from airflow."""
    with ApiClient(get_airflow_config()) as api_client:
        dag_api_instance = dag_api.DAGApi(api_client)
        dag = dag_api_instance.get_dag(dag_id)
        is_paused: bool = dag.is_paused
        return is_paused


def set_dag_is_paused(dag_id: str, is_paused: bool) -> Optional[bool]:
    """Set the dag paused/unpaused state in airflow."""
    with ApiClient(get_airflow_config()) as api_client:
        dag_api_instance = dag_api.DAGApi(api_client)
        # The API expects a dict with the key 'is_paused'
        dag_api_instance.patch_dag(dag_id, {"is_paused": is_paused})
        return is_paused == get_dag_is_paused(dag_id=dag_id)


def get_airflow_config() -> Configuration:
    """Create an airflow config objetc using the freeds config."""
    cfg = get_config("airflow")
    url = cfg.get("url")
    user = cfg.get("user")
    password = cfg.get("password")
    if not (url and user and password):
        raise ValueError("Invalid airflow config one or more values are missing (url, user or password).")
    host = f"{cfg['url']}".rstrip("/") + "/api/v1"
    cfg = Configuration(host=host, username=user, password=password)
    return cfg


def get_task_instances(dag_id: str, dag_run_id: str) -> List[TaskInstance]:
    """Get the task instances for a dag run id."""
    with ApiClient(get_airflow_config()) as api_client:
        task_instance_api_instance = task_instance_api.TaskInstanceApi(api_client)
        task_instances = task_instance_api_instance.get_task_instances(dag_id=dag_id, dag_run_id=dag_run_id)
    return cast(List[TaskInstance], task_instances.task_instances)


def get_last_dag_run(dag_id: str) -> Optional[DAGRun]:
    """Get the most recent dag run, regardless of state."""
    with ApiClient(get_airflow_config()) as api_client:
        dag_run_api_instance = dag_run_api.DAGRunApi(api_client)
        dag_runs = dag_run_api_instance.get_dag_runs(dag_id=dag_id, limit=1, order_by="-execution_date")
        if not dag_runs.dag_runs:
            logger.info("No DAG runs found.")
            return None

        latest_run = dag_runs.dag_runs[0]
        logger.info(
            f"Run ID: {latest_run.dag_run_id}, State: {latest_run.state}, Exec Date: {latest_run.execution_date}"
        )
        return latest_run


def trigger_dag_run(dag_id: str) -> DAGRun:
    """Trigger a new run of the dag."""
    with ApiClient(get_airflow_config()) as api_client:
        dag_run_api_instance = dag_run_api.DAGRunApi(api_client)
        dag_run = DAGRun(conf={"reason": "triggered via API"})
        run = dag_run_api_instance.post_dag_run(dag_id=dag_id, dag_run=dag_run)
        logger.info(f"Triggered run_id: {run.dag_run_id} at {run.execution_date}")
        return run


def check_dag_run_state(dag_id: str, dag_run_id: str) -> str:
    """Return the current dag run state for a run id."""
    with ApiClient(get_airflow_config()) as api_client:
        dag_run_api_instance = dag_run_api.DAGRunApi(api_client)
        dag_run = dag_run_api_instance.get_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)
        logger.info(f"DAG Run {dag_run.dag_run_id} state: {dag_run.state}")
        return str(dag_run.state)


def trigger_and_wait_for_airflow_run(dag_id: str, timeout_seconds: int) -> CheckResult:
    """Trigger a new run of the dag and wait for it to complete or the timeout limit is reached."""
    run = trigger_dag_run(dag_id)
    # run = get_last_dag_run(dag_id)
    check_result = PluginCheckResult(passed=False, message="", plugin_name="airflow")
    timeout = dt.datetime.now() + dt.timedelta(seconds=timeout_seconds)
    while (state := check_dag_run_state(dag_id=dag_id, dag_run_id=run.dag_run_id)) in [
        "queued",
        "running",
        "scheduled",
        "up_for_retry",
    ]:
        if state != "success" and dt.datetime.now() > timeout:
            check_result.message = (
                f"Airflow Dag {dag_id} did not complete within {timeout_seconds}, it is currently in state {state}."
            )
            break
        time.sleep(3)

    check_result.passed = state == "success"
    if state == "success":
        check_result.message = f"Airflow Dag {dag_id} completed successfully."
    else:
        check_result.message = f"Airflow Dag {dag_id} completed in state {state}"

    task_instances = get_task_instances(dag_id=dag_id, dag_run_id=run.dag_run_id)
    states = "   " + "\n   ".join([f"Task: {ti.task_id} - State: {ti.state}" for ti in task_instances])

    check_result.message = check_result.message + "\n" + states
    return check_result


_dag_id = "wikipedia_pageview_pipeline"
_timeout_seconds = 5 * 60

# DAG_RUN_STATES = [
#     "queued",
#     "running",
#     "success",
#     "failed",
#     "scheduled",
#     "canceled",
#     "up_for_retry"
# ]


def check_airflow_run() -> CheckResult:
    """Run a full airflow dag using s3, spark and the full monty."""
    global _dag_id, _timeout_seconds
    is_paused = get_dag_is_paused(_dag_id)
    if is_paused:
        set_dag_is_paused(dag_id=_dag_id, is_paused=False)
    result = trigger_and_wait_for_airflow_run(dag_id=_dag_id, timeout_seconds=_timeout_seconds)
    if is_paused:
        set_dag_is_paused(dag_id=_dag_id, is_paused=True)
    return result


def checks() -> CheckList:
    """Get all checks related to web ui:s."""
    global _dag_id
    checklst = CheckList(area=__name__)
    checklst.add(
        name="airflow full run",
        description=f"run an airflow dag end-to-end, currently {_dag_id} is used",
        method=check_airflow_run,
    )
    return checklst
