import typer

from freeds.cli.commands import dc, env, nb, selfcheck, stack
from freeds.config import set_env

set_env()


app = typer.Typer()

app.add_typer(dc.app)  # <-- Add this line)
app.command()(env.env)
app.command()(selfcheck.selfcheck)
app.add_typer(nb.nb_app, name="nb")
app.add_typer(stack.cfg_app, name="stack")


if __name__ == "__main__":
    app()
