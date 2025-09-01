from pathlib import Path
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError
from tinydb import Query, TinyDB
from xdg_base_dirs import xdg_data_home


class DuplicateTemplateId(Exception):
    """When a template with that id already exists in the database"""

    pass


class TemplateNotFound(Exception):
    """When we can't find a template in the db"""

    pass


class CorruptedTemplate(Exception):
    """When we're not able to construct a Template from a DB record"""


class Template(BaseModel):
    """
    The model for the templates copied over to the clipboard. Contains the
    template identifier as well as the template string.

    Note that the id may contain only alphanumeric characters or `-` and `_`
    """

    identifier: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    template: str = Field(min_length=1)

    def display(self) -> Tuple[str, str]:
        """
        Display returns the identifier and template marked up for insertion into
        a rich.print() statement
        """
        template_formatted = self.template.replace(
            r"{}", r"[magenta]{}[/magenta]"
        )
        return (
            f"[bold blue]{self.identifier}[/bold blue]",
            f"{template_formatted}",
        )


class DB:
    """
    Convenience interface from the json "database" to Templates and back
    """

    data_dir: Path = xdg_data_home() / "tmplcl"
    db: TinyDB

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir:  # testing helper
            self.data_dir = data_dir

        if not self.data_dir.is_dir():
            self.data_dir.mkdir()

        self.db = TinyDB(self.data_dir / "data.json")

    def insert(self, template: Template):
        if template not in self.get_all():
            self.db.insert(template.model_dump())
        else:
            raise DuplicateTemplateId

    def get(self, identifier) -> Tuple[Template, int]:
        match = self.db.search(Query().identifier == identifier)
        if match:
            try:
                return Template(**match[0]), match[0].doc_id
            except ValidationError:
                raise CorruptedTemplate
        else:
            raise TemplateNotFound

    def get_all(self) -> List[Template]:
        return [Template(**item) for item in self.db.all()]

    def update(self, identifier: str, template_str: str):
        template, id = self.get(identifier)
        updated = Template(
            identifier=template.identifier, template=template_str
        )
        self.db.update(updated.model_dump(), doc_ids=[id])

    def delete(self, identifier):
        self.db.remove(Query().identifier == identifier)
