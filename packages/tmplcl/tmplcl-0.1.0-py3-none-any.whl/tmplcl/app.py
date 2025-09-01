from typing import Optional
from typing_extensions import Annotated
import typer
from pydantic import ValidationError

from tmplcl.commands import (
    add_template,
    copy_template,
    delete_template,
    list_templates,
    show_template,
    update_template,
)
from tmplcl.models import DB, CorruptedTemplate, TemplateNotFound

app = typer.Typer()
db = DB()


@app.command()
def copy(template: str):
    """Copies the requested template to your clipboard"""
    try:
        copy_template(template, db)
    except TemplateNotFound:
        print(
            "[red bold]Error[/red bold]: Unable to find the requested "
            f'template "[magenta bold]{template}[/magenta bold]" in '
            "the database."
        )
        raise typer.Exit(code=1)

    except CorruptedTemplate:
        print(
            "[red bold]Error[/red bold]: The requested template "
            f'"[bold]{template}[/bold]" appears to have been corrupted.'
            f"Please either remove or fix the entry in [italic]{db.data_dir}"
            "/data.json[/italic]."
        )
        raise typer.Exit(code=1)


@app.command()
def delete(template: str):
    """Deletes the template with the provided identifier"""
    delete_template(template, db)


@app.command()
def add(
    template_name: Annotated[
        str,
        typer.Argument(
            help="The name that you'll use to retreive this template"
        ),
    ],
    template_string: Annotated[
        str,
        typer.Argument(
            help="The actual string that will be copied to your clipboard"
        ),
    ],
):
    """Adds a template with the provided identifier and string"""
    add_template(template_name, template_string, db)


@app.command()
def list(
    show_chars: Annotated[
        Optional[int],
        typer.Option(
            help=(
                "An interger value for the number of characters "
                "you want to see in each preview"
            )
        ),
    ] = None,
):
    """
    Lists all available templates, including a preview of each
    """
    if show_chars:
        list_templates(db, show_chars)
    else:
        list_templates(db)


@app.command()
def show(template: str):
    """
    Displays the full text of a given template
    """
    try:
        show_template(template, db)
    except TemplateNotFound:
        print(
            "[red bold]Error[/red bold]: Unable to find the requested "
            f'template "[magenta bold]{template}[/magenta bold]" in '
            "the database."
        )
        raise typer.Exit(code=1)
    except CorruptedTemplate:
        print(
            "[red bold]Error[/red bold]: The requested template "
            f'"[bold]{template}[/bold]" appears to have been corrupted.'
            f"Please either remove or fix the entry in [italic]{db.data_dir}"
            "/data.json[/italic]."
        )
        raise typer.Exit(code=1)


@app.command()
def update(
    template: Annotated[
        str,
        typer.Argument(help="The name of the template you want to update"),
    ],
    template_string: Annotated[
        str,
        typer.Argument(
            help="The string that you want to update this template to"
        ),
    ],
):
    """Updates a given template with a new string"""
    try:
        update_template(template, template_string, db)
    except TemplateNotFound:
        print(
            "[red bold]Error[/red bold]: Unable to find the requested "
            f'template "[magenta bold]{template}[/magenta bold]" in '
            "the database."
        )
        raise typer.Exit(code=1)
    except ValidationError:
        print("[red bold]Error[/red bold]: Invalid replacement template string")
        raise typer.Exit(code=1)
