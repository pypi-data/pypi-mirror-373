"""S3 managemnent functions.
Let's see how we refactor this to transparently use config from file or api server."""

import datetime as dt
from pathlib import Path
from typing import Union

import boto3
from botocore.exceptions import ClientError

from freeds.config import get_config


def get_s3_client() -> boto3.client:
    """Get an S3 client using config from the config api"""
    cfg = get_config("s3")
    if cfg is None or cfg.get("url") is None:
        raise ValueError("s3 config not found")
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        endpoint_url=cfg["url"],
    )
    return s3_client


def is_s3_service_available() -> bool:
    """Simple check if s3 works. A negative response might indicate service down or invalid credentials."""
    try:
        get_s3_client().list_buckets()
        return True
    except Exception:
        print(
            "S3 service not responding, this might be due to s3 service not started, invalid credentials or faulty/missing configuration."
        )
        return False


def bucket_exists(bucket_name: str) -> bool:
    """Check if an S3 bucket exists."""
    response = get_s3_client().list_buckets()
    for bucket in response.get("Buckets", []):
        if bucket["Name"] == bucket_name:
            return True

    return False


def file_exists(bucket_name: str, file_name: str, prefix: Union[str, None] = None) -> bool:
    """Check if a file exists on S3."""
    try:
        key = f"{prefix}/{file_name}" if prefix else file_name
        get_s3_client().head_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            print(f"Error checking file: {e}")
            raise


def create_bucket(bucket_name: str) -> bool:
    """Create an S3 bucket if does not exist."""

    try:
        if bucket_exists(bucket_name):
            print(f"S3 bucket {bucket_name} already exists.")
            return True
        s3_client = get_s3_client()
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created.")
        return True
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        return False


def delete_bucket(bucket_name: str) -> None:
    """Delete S3 bucket if it exists."""
    if not bucket_exists(bucket_name):
        return
    s3_client = get_s3_client()
    s3_client.delete_bucket(Bucket=bucket_name)


def delete_prefix(bucket: str, prefix: str) -> None:
    """Delete all files with a given prefix in a bucket."""
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" in page:
            objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
            s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})


def put_file(local_path: Union[str, Path], bucket: str, file_name: str, prefix: Union[str, None] = None) -> bool:
    """Upload a file to S3."""

    s3_client = get_s3_client()
    if prefix and not prefix.endswith("/"):
        prefix = prefix + "/"
    s3_key = prefix + file_name if prefix else file_name

    try:
        text = f"{local_path} to bucket '{bucket}' as '{s3_key}'"
        print(f"Intitating upload: {text}.")
        s3_client.upload_file(local_path, bucket, s3_key)
        print(f"Upload succeeded: {text}.")
        return True
    except Exception as e:
        print(f"Upload failed {text}: {e}")
        return False


def get_file(local_path: Union[str, Path], bucket: str, file_name: str, prefix: Union[str, None] = None) -> bool:
    """Download a file from S3."""
    source_object_name = f"{prefix}/{file_name}" if prefix else file_name
    text = f"{source_object_name} to {local_path}"
    print(f"Intitating download: {text}.")
    try:
        s3_client = get_s3_client()
        s3_client.download_file(bucket, source_object_name, local_path)
        print(f"Download completed: {text}.")
        return True
    except ClientError as e:
        print(f"Download failed {source_object_name} from s3: {e}")
        return False


def make_date_prefix(date: Union[dt.datetime, dt.date]) -> str:
    """Make a freeds standard prefix for the given date."""
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return f"{year}/{year}-{month}/{day}"


def as_urls(files: list[str], bucket_name: str) -> list[str]:
    return [f"s3a://{bucket_name}/{f}" for f in files]


def list_files(prefix: str, bucket_name: str) -> list[str]:
    """Expand s3 path and return all files under the given prefix, prefix should not contain any part of the filename or wildcards."""
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    all_files = []
    for page in pages:
        for obj in page.get("Contents", []):
            all_files.append(obj["Key"])
    return all_files


def list_files_for_dates(dates: list[Union[dt.datetime, dt.date]], root_prefix: str, bucket_name: str) -> list[str]:
    """List all files in the s3 freeds standard date paths for the given dates.
    Spark doesn't resolve wildcards so we need to list the files individually.
    Filenames are returned as haddoop compatible uri:s 's3a://bucket/prefix/filename'."""
    all_files = []
    for date in dates:
        prefix = make_date_prefix(date)
        files = list_files(f"{root_prefix}/{prefix}", bucket_name)
        all_files.extend(files)
    return all_files

if __name__ == '__main__':
    print(get_s3_client())