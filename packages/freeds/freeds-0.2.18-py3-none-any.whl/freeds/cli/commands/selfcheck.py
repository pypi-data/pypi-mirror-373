from typing import List

import typer

from freeds.selfcheck import (
    airflow_checks,
    directory_checks,
    docker_checks,
    network_checks,
    notebook_checks,
    s3_checks,
)
from freeds.selfcheck.check_classes import (
    CheckList,
    CheckResult,
    ExceptionCheckResult,
)


def selfcheck(
    no_nb: bool = typer.Option(False, "--no-nb", help="Skip the notebook based checks(spark)."),
    no_airflow: bool = typer.Option(False, "--no-airflow", help="Skip the airflow check."),
) -> int:
    """
    Perform all self checks.
    """

    checklists: List[CheckList] = [
        docker_checks.checks(),
        directory_checks.checks(),
        network_checks.checks(),
        s3_checks.checks(),
    ]
    if not no_nb:
        checklists.append(notebook_checks.checks())
    if not no_airflow:
        checklists.append(airflow_checks.checks())

    results: List[CheckResult] = []
    for checklist in checklists:
        try:
            checklist.execute()
            results.extend(checklist.results)
        except Exception as e:
            results.append(ExceptionCheckResult(message="A checklist execution raised an exception.", exception=e))

    for result in results:
        typer.echo(result)
    return 0


if __name__ == "__main__":
    selfcheck(no_airflow=True, no_nb=True)
