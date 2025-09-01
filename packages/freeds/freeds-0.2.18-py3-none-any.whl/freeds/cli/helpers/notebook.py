import datetime as dt
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Optional, cast

import git
import nbformat

from freeds.config import get_config
from freeds.s3 import put_file


def find_dir(dir_name: str) -> Path:
    """Find the specified directory in the current working directory or its parent directories."""
    looked_in = []
    p = Path(dir_name)
    # find repo and notebooks directories
    for i in range(4):
        looked_in.append(p.absolute())
        if p.exists():
            return p.resolve()
        p = Path("..") / p
    else:
        raise FileNotFoundError(f"Error: directory '{dir_name}' not found, looked in:\n{looked_in}")


def get_repo_config(repo: str) -> dict[str, Any]:
    cfg = get_config("nbdeploy")
    for r in cfg.get("repos", []):
        if r.get("name") == repo:
            return cast(dict[str, Any], r)
    return {}


def get_git_info() -> dict[str, str]:
    """Get Git information using GitPython."""
    try:
        repo = git.Repo(".")
        head = repo.head.commit
        url = repo.remotes.origin.url
        if url is None:
            url = "No remote URL found"
        else:
            url = f"{url.rstrip('.git')}/commit/{head.hexsha}"
        return {
            "repo": repo.working_tree_dir,
            "branch": repo.active_branch.name,
            "revision": head.hexsha[:7],  # Short hash
            "commit_date": head.committed_datetime.isoformat(),
            "author": f"{head.author.name}",
            "deployed": dt.datetime.now(dt.timezone.utc).isoformat(),
            "url": url,
        }
    except git.InvalidGitRepositoryError:
        print("Error: Not a git repository")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting git info: {e}")
        sys.exit(1)


def format_md(git_info: dict[str, str], input_path: str) -> str:
    """
    Format the Git information into a markdown string.
    """
    # Create the revision markdown content
    url = git_info["url"]
    return (
        f"# Notebook: {os.path.basename(input_path)}\n\n"
        f"> **Git Revision**: `{git_info['revision']}` | **Branch**: `{git_info['branch']}`\n\n"
        f"> **Commit Date**: {git_info['commit_date']} | **Author**: {git_info['author']}\n\n"
        f"> **Deployed**: {git_info['deployed']}\n\n"
        f"> [{url}]({url})"
    )


def find_cell_by_tag(notebook: nbformat.NotebookNode, tag: str) -> nbformat.NotebookNode:
    """
    Find a cell in the notebook with the specified tag.
    Returns the cell if found, otherwise None.
    """
    for cell in notebook.cells:
        if "metadata" in cell and "tags" in cell.metadata and tag in cell.metadata.tags:
            return cell
    return None


class NotebookFile:
    def __init__(self, repo: str, repo_path: str, notebook_dir: str, dir: str, file: str) -> None:
        self.repo = repo
        self.notebook_dir = notebook_dir
        self.repo_path = repo_path
        self.dir = None if dir == "." else dir
        self.file = file

    def s3_prefix(self) -> str:
        """
        Return the S3 prefix for this notebook file.
        """
        if self.dir:
            return f"{self.repo}/{self.dir}"
        return f"{self.repo}/{self.notebook_dir}"

    def local_prefix(self) -> str:
        """
        Return the directory path for this notebook file relative (and including) the repository.
        """
        if self.dir:
            return os.path.join(self.repo, self.dir)
        return os.path.join(self.repo, self.notebook_dir)

    def temp_file_path(self, temp_dir: str) -> str:
        """
        Return the local path for this notebook file in the temporary directory.
        """
        return os.path.join(temp_dir, self.local_prefix(), self.file)

    def local_file_path(self) -> str:
        """
        Return the local path for this notebook file.
        """
        if self.dir:
            return os.path.join(self.repo_path, self.dir, self.file)
        else:
            return os.path.join(self.repo_path, self.notebook_dir, self.file)

    def s3_file_path(self) -> str:
        """
        Return the s3 path for this notebook file.
        """
        return os.path.join(self.s3_prefix(), self.file)


def list_files(repo: str, notebook_dir: str) -> list[NotebookFile]:
    """
    List all notebook files in the specified directory of the repository.
    Returns a list of NotebookFile objects.
    """
    repo_dir = find_dir(repo)
    if repo_dir is None:
        print(f"Error: repository '{repo}' not found")
        return []

    notebook_path = os.path.join(repo_dir, notebook_dir)
    if not os.path.exists(notebook_path):
        print(f"Notebook directory '{notebook_dir}' not found in '{repo_dir}'")
        return []

    notebook_files = []
    for dirpath, _, files in os.walk(notebook_path):
        rel_dir = os.path.relpath(dirpath, start=repo_dir)
        for file in files:
            if file.endswith(".ipynb"):
                notebook_files.append(
                    NotebookFile(repo=repo, repo_path=str(repo_dir), notebook_dir=notebook_dir, dir=rel_dir, file=file)
                )
    return notebook_files


def stamp_notebook(input_path: str, output_path: str) -> Optional[nbformat.NotebookNode]:
    """
    Add Git revision information to notebook metadata and2
    insert/update a markdown cell at the top with revision info.
    Uses cell tags to identify the Git info cell.
    """
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise ValueError("Input and output paths must be different to avoid overwriting the original notebook.")
    try:
        git_info = get_git_info()
        # Load the notebook
        with open(input_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Look for a cell with the 'gitinfo' tag
        revision_cell = find_cell_by_tag(notebook, "gitinfo")
        if revision_cell is None:
            # If no existing cell found, create a new one
            revision_cell = nbformat.v4.new_markdown_cell()
            notebook.cells.insert(0, revision_cell)

        # Set the gitinfo on the cell metadata and content
        if "metadata" not in revision_cell:
            revision_cell["metadata"] = {}
        if "tags" not in revision_cell["metadata"]:
            revision_cell["metadata"]["tags"] = []
        revision_cell["metadata"]["tags"].append("gitinfo")
        revision_cell["source"] = format_md(git_info, input_path)

        print(f"Writing a copy of the notebook to: {output_path}.")
        containing_dir = os.path.dirname(output_path)
        os.makedirs(containing_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"Notebook {input_path} stamped with Git info and saved to {output_path}.")
        return notebook
    except Exception as e:
        print(f"Error processing notebook {input_path}: {e}")
        return None


def normalize(files: list[NotebookFile]) -> None:
    """
    Normalize the source files to verrsion 4.5.
    """
    for file in files:
        print(f"Normalizing notebook: {file.local_file_path()}.")
        with open(file.local_file_path(), "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        nbformat.validator.normalize(nb, version=4, version_minor=5)
        current_major = nb.get("nbformat")
        if not current_major or int(current_major) < 4:
            nb["nbformat"] = 4
        current_minor = nb.get("nbformat_minor")
        if not current_minor or int(current_minor) < 5:
            nb["nbformat_minor"] = 5

        with open(file.local_file_path(), "w", encoding="utf-8") as f:
            nbformat.write(nb, f)


def deploy_dir(repo: str, notebook_dir: str, normalize_source: bool) -> None:
    """
    Process each notebook in the specified directory, stamp it with Git info,
    and upload it to S3.
    """
    cfg = get_config("nbdeploy")
    temp_dir = cfg.get("temp_dir")
    if temp_dir is None:
        raise ValueError("nbdeploy config has no value for temp_dir")
    preserve_temp = cfg.get("preserve_temp", False)
    bucket = cfg.get("bucket")
    if bucket is None:
        raise ValueError("nbdeploy config has no value for bucket")
    print(f"Deploying notebooks from {repo}/{notebook_dir} to S3 bucket {bucket}")

    # get files to stamp
    notebook_files = list_files(repo, notebook_dir)
    if normalize_source:
        normalize(notebook_files)
    for nbfile in notebook_files:
        print(f"Stamping and uploading notebook: {nbfile.local_file_path()}.")
        stamped_path = nbfile.temp_file_path(temp_dir)
        if not os.path.exists(os.path.dirname(stamped_path)):
            os.makedirs(os.path.dirname(stamped_path), exist_ok=True)
        stamp_notebook(nbfile.local_file_path(), stamped_path)
        put_file(local_path=stamped_path, bucket=bucket, file_name=nbfile.s3_file_path())
        if not preserve_temp:
            os.remove(stamped_path)  # Clean up local copy after upload


def deploy_repo(repo_name: str, normalize_source: bool) -> None:
    """
    Deploy all notebooks in the specified repo, timestamping and tagging them with git revision.
    """
    # find repo
    repo_dir = find_dir(repo_name)
    if not repo_dir:
        print(f"Error: git repo '{repo_name}' not found")
        return
    os.chdir(repo_dir)
    repo_cfg = get_repo_config(repo_name)

    for dir in repo_cfg.get("directories", []):
        notebooks_dir = os.path.join(repo_dir, dir)
        if not os.path.exists(notebooks_dir):
            print(f"Error: notebooks dir '{notebooks_dir}' not found in {repo_dir}")
            continue
        deploy_dir(repo=repo_name, notebook_dir=dir, normalize_source=normalize_source)


def deploy_notebooks(repo: str = "all", normalize_source: bool = False) -> None:
    """Deploy notebooks to S3 from configured repo(s), timestamping and tagging them with git revision."""
    start_dir = os.getcwd()

    cfg = get_config("nbdeploy")
    temp_dir = cfg.get("temp_dir")
    if temp_dir is None:
        raise ValueError("nbdeploy config has no value for temp_dir")
    create_temp_dir = not os.path.exists(temp_dir)
    preserve_temp = bool(cfg.get("preserve_temp", False))
    if create_temp_dir:
        os.makedirs(temp_dir, exist_ok=True)

    if repo != "all":
        deploy_repo(repo_name=repo, normalize_source=normalize_source)
    else:
        for r in cfg.get("repos", []):
            deploy_repo(repo_name=r["name"], normalize_source=normalize_source)

    # cleanup
    os.chdir(start_dir)
    if create_temp_dir and not preserve_temp:
        for _, _, files in os.walk(temp_dir):
            if files:
                raise FileExistsError(f"{temp_dir} is not empty: {files}")
        print(f"removing temp dir: {temp_dir}")
        shutil.rmtree(temp_dir)
    print("Deployment complete!")
