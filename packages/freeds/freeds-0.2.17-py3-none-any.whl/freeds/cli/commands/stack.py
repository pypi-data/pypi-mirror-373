import typer

from freeds.cli.helpers.stackutils import get_current_stack_name, set_current_stack
from freeds.config import get_config

cfg_app = typer.Typer(help="Manage freeds stacks.")


@cfg_app.command()  # type: ignore
def ls() -> None:
    """List all stacks."""

    cfg = get_config("stacks")
    current_stack = get_current_stack_name()
    if current_stack is None:
        typer.echo("No current stack set,use 'freeds setstack <name>' to set one.")
    for stack in cfg.keys():
        if stack == current_stack:
            typer.echo(f"** stack: {stack} ** (current)")
        else:
            typer.echo(f"stack: {stack}")
        for service in cfg[stack].get("plugins", []):
            typer.echo(f"  - {service}")


@cfg_app.command()  # type: ignore
def set(
    stack: str = typer.Argument(..., help="Stack name to set as current"),
) -> None:
    """Set freeds to use the provided stack."""
    set_current_stack(stack_name=stack)
