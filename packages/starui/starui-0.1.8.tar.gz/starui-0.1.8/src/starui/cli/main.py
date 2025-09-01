import typer
from rich import print as rich_print

from starui import __version__

from .add import add_command
from .build import build_command
from .dev import dev_command
from .init import init_command
from .list import list_command

app = typer.Typer(
    name="star",
    help="Python-first UI component library for StarHTML applications",
    rich_markup_mode="rich",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    if value:
        rich_print(f"[bold blue]star {__version__}[/bold blue]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Python-first UI component library for StarHTML applications."""


app.command("add")(add_command)
app.command("init")(init_command)
app.command("dev")(dev_command)
app.command("build")(build_command)
app.command("list")(list_command)


if __name__ == "__main__":
    app()
