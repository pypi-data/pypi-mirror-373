import typer

from freeds.cli.helpers import execute_docker_compose, get_plugins

app = typer.Typer()


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})  # type: ignore[misc]
def dc(
    ctx: typer.Context,
    single: str = typer.Option(None, "-s", "--single", help="Folder to run docker compose in"),
    # args: list[str] = typer.Argument(None, help="Arguments to pass to docker compose")
) -> int:
    """
    Call docker compose with the supplied parameters for all freeds plugins in the current stack.
    """
    args = ctx.args
    if not args:
        print("Error: docker compose command must be given")
        return 1

    plugins: list[str] = []
    if single is None:
        plugins = get_plugins()
        print(f"Found plugins: {plugins}")
    else:
        plugins = [single]

    execute_docker_compose(params=args, plugins=plugins)
    return 0
