"""Console script for django_msteams_notify."""

import typer
from rich.console import Console

from django_msteams_notify import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for django_msteams_notify."""
    console.print("Replace this message by putting your code into "
               "django_msteams_notify.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
