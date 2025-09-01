import datetime as dt
from pathlib import Path

from freeds.s3 import (
    bucket_exists,
    create_bucket,
    delete_bucket,
    delete_prefix,
    get_file,
    list_files,
    list_files_for_dates,
    make_date_prefix,
    put_file,
)
from freeds.selfcheck.check_classes import (
    AllGoodCheckResult,
    CheckList,
    CheckResult,
    ExceptionCheckResult,
)


def s3_check() -> CheckResult:

    bucket = "self-check-bucket"
    date = dt.date.fromisoformat("20250102")
    date_prefix = make_date_prefix(date)
    root_prefix = "s3_check"
    full_prefix = f"{root_prefix}/{date_prefix}"
    tmp_dir = Path("/tmp/freeds/selfcheck")
    source_dir: Path = tmp_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    target_dir: Path = tmp_dir / "target"
    target_dir.mkdir(parents=True, exist_ok=True)
    file_name = "test.txt"

    with open(source_dir / file_name, "w") as f:
        f.write("hello s3")
    current_command = "setting up test"
    try:
        current_command = "create_bucket"
        create_bucket(bucket)

        current_command = "bucket_exists after create"
        if not bucket_exists(bucket):
            return CheckResult(
                passed=False, message=f"bucket_exists did not return true for newly created bucket {bucket}."
            )

        current_command = "put_file"

        put_file(local_path=(source_dir / file_name), bucket=bucket, prefix=full_prefix, file_name=file_name)
        expected_file_name = f"{full_prefix}/{file_name}"
        current_command = "list_files"
        files = list_files(bucket_name=bucket, prefix=full_prefix)
        if files != [expected_file_name]:
            return CheckResult(
                passed=False, message=f"Error in list_files, expected: [{expected_file_name}] got: {files}."
            )

        current_command = "list_files_for_dates"
        files = list_files_for_dates(dates=[date], root_prefix=root_prefix, bucket_name=bucket)
        if files != [expected_file_name]:
            return CheckResult(
                passed=False, message=f"Error in list_files_for_dates, expected: [{expected_file_name}] got: {files}."
            )

        current_command = "get_file"
        get_file(local_path=target_dir / file_name, bucket=bucket, prefix=full_prefix, file_name=file_name)
        if not (target_dir / file_name).is_file() or (target_dir / file_name).stat().st_size == 0:
            return CheckResult(
                passed=False,
                message=f"Could not find file: {str(target_dir / file_name)} after download or size is zero.",
            )

        current_command = "delete_prefix"
        delete_prefix(bucket=bucket, prefix=root_prefix)
        files = list_files(bucket_name=bucket, prefix=root_prefix)
        if files != []:
            return CheckResult(passed=False, message=f"Error in list_files, expected an empty list, got: {files}.")

        current_command = "delete_bucket"
        delete_bucket(bucket)

        current_command = "bucket_exists after delete"
        if bucket_exists(bucket):
            return CheckResult(passed=False, message=f"bucket_exists returns true for deleted bucket {bucket}.")

        return AllGoodCheckResult(message="Executed create+delete bucket, upload+download of file.")
    except Exception as ex:
        return ExceptionCheckResult(message=f"S3 tests failed while executing {current_command}", exception=ex)


def checks() -> CheckList:
    """Get all checks related to web ui:s."""
    checklst = CheckList(area=__name__)

    checklst.add(
        name="S3 operations check",
        description="Perform most of the s3 operations.",
        method=s3_check,
    )
    return checklst


if __name__ == "__main__":
    print(s3_check())
