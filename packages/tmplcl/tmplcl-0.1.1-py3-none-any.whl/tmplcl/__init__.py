import typer

from tmplcl.app import app
from tmplcl.commands import copy_template


def main():  # pragma: nocover
    """
    Passthrough to run the app
    """
    app()


def copy():  # pragma: nocover
    """
    Passthrough to run just the copy command for convenience
    """
    typer.run(copy_template)
