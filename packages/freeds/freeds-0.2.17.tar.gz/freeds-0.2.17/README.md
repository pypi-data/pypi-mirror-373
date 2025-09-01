# freeds
The free data stack CLI and lib.
The project is managed in `poetry` and uses CLI framework `typer`.

## The freeds CLI
* Setup freeds for first use, create directories, clone repos, collect secrets etc
* Run docker compose commands on the stack in the relevant order, providing the appropriate environment.
* Deploy and manage notebook files on s3.
* Stack and lab operations like inspecting the available labs/stacks and activating a lab/stack.
* Testing freeds stack health by running a set of real but minimal operations.

## The freeds Package
* Unified access to config, as file or via config server.
* Unified view of the plugins.
* Unified view of repos, providing the union of the-free-data-stack and the configured lab. Regarding dags, configs, notebooks etc
* Simplified S3 management, put, get, list files and prefixes, using the freeds config.
* Simplified Spark management, setting up a connection using the freeds config and S3 connectivity.
