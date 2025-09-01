import typer

from freeds.cli.helpers import deploy_notebooks
from freeds.config import get_config
from freeds.s3 import delete_prefix, list_files

nb_app = typer.Typer(help="Manage notebooks on S3.")


@nb_app.command()  # type: ignore
def deploy(
    repo: str = typer.Option("all", "--repo", help="Deploy a single repo only."),
    normalize: bool = typer.Option(False, "--normalize", help="Normalize source file before deploying."),
) -> None:
    """Deploy notbooks to S3 from repo(s), timestamping and tagging them with git revision.
    Optionally you can use this command to upgrade the notebook formats to 4.5, silencing the id warning."""
    if normalize:
        print("Normalizing source files before deployment...")
    deploy_notebooks(repo=repo, normalize_source=normalize)


@nb_app.command()  # type: ignore
def cfg() -> None:
    """Show repo config."""
    cfg = get_config("nbdeploy")
    for repo in cfg.get("repos", []):
        print(f"Repo: {repo['name']}")
        print("Directories:")
        for folder in repo.get("directories", []):
            print(f"  - {folder}")


@nb_app.command()  # type: ignore
def ls(prefix: str = typer.Argument(None, help="List files under this prefix")) -> None:
    """List all notebooks on S3."""
    cfg = get_config("nbdeploy")
    bucket = cfg.get("bucket", "notebooks")
    if prefix:
        print(f"Files under prefix '{prefix}' in bucket {bucket}:")
        books = list_files(bucket_name=bucket, prefix=prefix)
        for book in books:
            print(f"  - {book}")
        return

    for repo in cfg.get("repos", []):
        books = list_files(bucket_name="notebooks", prefix=repo["name"])
        print(f"Repo {repo['name']} has {len(books)} files in bucket {bucket}:")
        for book in books:
            print(f"  - {book}")


@nb_app.command()  # type: ignore
def delprefix(prefix: str = typer.Argument(..., help="Delete all files under this prefix")) -> None:
    """Delete all files under an S3 prefix."""
    cfg = get_config("nbdeploy")
    bucket = cfg.get("bucket", "notebooks")
    books = list_files(bucket_name="notebooks", prefix=prefix)
    for book in books:
        print(f"  - {book}")
    if not typer.confirm(f"{len(books)} files under prefix {prefix} in bucket {bucket} will be deleted. Continue?"):
        print("Deletion cancelled.")
        return
    delete_prefix(bucket=bucket, prefix=prefix)


# deploy("all")
# delprefix("pipe-dreams")
